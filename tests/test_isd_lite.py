from urllib.error import HTTPError, URLError

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, box

from pyisd import DataDownloadError, IsdLite, MetadataDownloadError
from tests.helpers import get_box


@pytest.fixture
def crs():
    return 4326


def make_metadata(usaf_id="723270", wban_id="13897", country="US"):
    return gpd.GeoDataFrame(
        {
            "USAF": [usaf_id],
            "WBAN": [wban_id],
            "CTRY": [country],
            "BEGIN": [pd.Timestamp("2020-01-01")],
            "END": [pd.Timestamp("2024-12-31")],
            "x": [-86.6782],
            "y": [36.1245],
        },
        geometry=gpd.points_from_xy([-86.6782], [36.1245], crs=4326),
    )


def test_isdlite_init_is_lazy(monkeypatch):
    calls = []

    def fake_download(self):
        calls.append("download")
        return ""

    monkeypatch.setattr(IsdLite, "_download_metadata_text", fake_download)

    module = IsdLite()

    assert module._raw_metadata is None
    assert calls == []


def test_raw_metadata_is_loaded_once(monkeypatch):
    downloads = []
    metadata = make_metadata()

    def fake_download(self):
        downloads.append("download")
        return "metadata"

    def fake_parse(self, content):
        assert content == "metadata"
        return metadata

    monkeypatch.setattr(IsdLite, "_download_metadata_text", fake_download)
    monkeypatch.setattr(IsdLite, "_parse_metadata", fake_parse)

    module = IsdLite()

    first = module.raw_metadata
    second = module.raw_metadata

    assert first is metadata
    assert second is metadata
    assert downloads == ["download"]


def test_refresh_metadata_forces_reload(monkeypatch):
    downloads = []

    def fake_download(self):
        downloads.append("download")
        return f"metadata-{len(downloads)}"

    def fake_parse(self, content):
        suffix = content.rsplit("-", 1)[1]
        return make_metadata(usaf_id=f"station-{suffix}")

    monkeypatch.setattr(IsdLite, "_download_metadata_text", fake_download)
    monkeypatch.setattr(IsdLite, "_parse_metadata", fake_parse)

    module = IsdLite()

    first = module.raw_metadata
    refreshed = module.refresh_metadata()

    assert downloads == ["download", "download"]
    assert first["USAF"].iloc[0] == "station-1"
    assert refreshed["USAF"].iloc[0] == "station-2"


def test_station_id_does_not_load_metadata(monkeypatch):
    module = IsdLite()
    sample = pd.DataFrame({"temp": [1.0]}, index=pd.DatetimeIndex([pd.Timestamp("2023-01-01 00:00:00")]))

    def fail_metadata_load(self):
        raise AssertionError("metadata should not be loaded for station_id requests")

    monkeypatch.setattr(IsdLite, "_download_metadata_text", fail_metadata_load)
    module._download_data_id = lambda usaf_id, wban_id, years: sample

    data = module.get_data(start="2023-01-01", end="2023-01-01", station_id="123456-78901", organize_by="location")

    assert "123456-78901" in data
    assert data["123456-78901"]["temp"].iloc[0] == 1.0


def test_metadata_download_error_uses_retry_backoff(monkeypatch):
    delays = []
    attempts = []

    def fail_download(self):
        attempts.append("download")
        raise URLError("boom")

    monkeypatch.setattr(IsdLite, "_download_metadata_text", fail_download)
    monkeypatch.setattr("pyisd._isd_lite.sleep", lambda delay: delays.append(delay))

    module = IsdLite(metadata_retries=3, metadata_retry_delay=1)

    with pytest.raises(MetadataDownloadError, match="after 3 attempts"):
        _ = module.raw_metadata

    assert attempts == ["download", "download", "download"]
    assert delays == [1, 2]


def test_download_data_id_ignores_missing_year_files(monkeypatch):
    sample = pd.DataFrame({"temp": [1.0]}, index=pd.DatetimeIndex([pd.Timestamp("2024-01-01 00:00:00")]))

    def fake_download(url):
        if url.endswith("2023.gz"):
            raise HTTPError(url, 404, "Not Found", hdrs=None, fp=None)
        return sample

    monkeypatch.setattr(IsdLite, "_download_read", classmethod(lambda cls, url: fake_download(url)))

    result = IsdLite._download_data_id("123456", "78901", [2023, 2024])

    assert result.equals(sample)


def test_download_data_id_raises_on_transport_error(monkeypatch):
    def fail_download(url):
        raise URLError("network down")

    monkeypatch.setattr(IsdLite, "_download_read", classmethod(lambda cls, url: fail_download(url)))

    with pytest.raises(DataDownloadError, match="123456-78901"):
        IsdLite._download_data_id("123456", "78901", [2024])


def test_download_data_id_raises_on_parse_error(monkeypatch):
    def fail_parse(url):
        raise ValueError("bad payload")

    monkeypatch.setattr(IsdLite, "_download_read", classmethod(lambda cls, url: fail_parse(url)))

    with pytest.raises(DataDownloadError, match="2024"):
        IsdLite._download_data_id("123456", "78901", [2024])


@pytest.mark.parametrize(
    ("stations", "download_data"),
    [
        ([], None),
        ([("123456", "78901")], lambda usaf_id, wban_id, years: pd.DataFrame()),
    ],
)
def test_field_mode_returns_empty_frames_when_no_data(stations, download_data):
    module = IsdLite()
    expected_index = pd.date_range("2023-01-01", "2023-01-02", freq="h", inclusive="left")

    module._filter_metadata = lambda countries, geometry: stations
    if download_data is not None:
        module._download_data_id = download_data
    result = module.get_data(start="2023-01-01", end="2023-01-01", organize_by="field")

    assert set(result) == set(module.fields)
    for frame in result.values():
        assert frame.empty
        assert frame.index.equals(expected_index)


def test_filter_metadata_applies_country_and_geometry_together():
    module = IsdLite()
    module.raw_metadata = gpd.GeoDataFrame(
        {
            "USAF": ["100001", "100002", "100003"],
            "WBAN": ["00001", "00002", "00003"],
            "CTRY": ["FR", "US", "FR"],
        },
        geometry=[Point(0, 0), Point(1, 1), Point(10, 10)],
        crs=4326,
    )

    result = module._filter_metadata(countries="FR", geometry=box(-1, -1, 2, 2))

    assert result == [("100001", "00001")]


def test_filter_metadata_returns_empty_when_combined_filters_do_not_overlap():
    module = IsdLite()
    module.raw_metadata = gpd.GeoDataFrame(
        {
            "USAF": ["100001", "100002"],
            "WBAN": ["00001", "00002"],
            "CTRY": ["FR", "US"],
        },
        geometry=[Point(0, 0), Point(1, 1)],
        crs=4326,
    )

    result = module._filter_metadata(countries="FR", geometry=box(5, 5, 6, 6))

    assert result == []


@pytest.mark.integration
@pytest.mark.parametrize(
    ("place", "organize_by", "station_id", "expected_key"),
    [
        ("Paris", "location", None, None),
        ("Paris", "field", None, None),
        ("Nashville", "location", None, "723270-13897"),
        (None, "location", "723270-13897", "723270-13897"),
    ],
)
def test_isdlite_live_fetch(crs, place, organize_by, station_id, expected_key):
    module = IsdLite(verbose=True)
    kwargs = {"start": 20230101, "end": 20241231, "organize_by": organize_by}

    if place is not None:
        kwargs["geometry"] = get_box(place=place, width=1.0, crs=crs)
    if station_id is not None:
        kwargs["station_id"] = station_id

    data = module.get_data(**kwargs)

    if organize_by == "field":
        assert data["temp"].size > 0
        return

    if expected_key is None:
        expected_key = next(iter(data))
    assert expected_key in data
    assert data[expected_key].size > 0


@pytest.mark.integration
def test_isdlite_wban_leading_zero():
    usaf_id = "722692"
    wban_id = "00367"
    module = IsdLite(verbose=True)
    meta = module.raw_metadata
    station_meta = meta[(meta["USAF"] == usaf_id) & (meta["WBAN"] == wban_id)]
    assert not station_meta.empty, f"No metadata found for {usaf_id}-{wban_id}"
