import pytest

from pyisd import IsdLite
from pyisd.misc import get_box


@pytest.fixture
def crs():
    return 4326


def test_isdlite_location(crs):
    geometry = get_box(place="Paris", width=1.0, crs=crs)
    module = IsdLite(verbose=True)
    data = module.get_data(start=20230101, end=20241231, geometry=geometry, organize_by="location")
    assert data[list(data.keys())[0]].size > 0


def test_isdlite_field(crs):
    geometry = get_box(place="Paris", width=1.0, crs=crs)
    module = IsdLite(verbose=True)
    data = module.get_data(start=20230101, end=20241231, geometry=geometry, organize_by="field")
    assert data["temp"].size > 0


def test_isdlite_wban_id(crs):
    geometry = get_box(place="Nashville", width=1.0, crs=crs)
    module = IsdLite(verbose=True)
    data = module.get_data(start=20230101, end=20241231, geometry=geometry, organize_by="location")
    assert "723270-13897" in data
    assert data["723270-13897"].size > 0


def test_isdlite_station_id():
    """
    Test that get_data returns data for a specific station_id in 'USAF-WBAN' format.
    """
    module = IsdLite(verbose=True)
    # Provide station_id override, no spatial filter
    data = module.get_data(start=20230101, end=20241231, station_id="723270-13897", organize_by="location")
    # Ensure the key is the full station_id and data is returned
    assert "723270-13897" in data
    assert data["723270-13897"].size > 0


def test_isdlite_wban_leading_zero():
    usaf_id = "722692"
    wban_id = "00367"
    module = IsdLite(verbose=True)
    meta = module.raw_metadata
    station_meta = meta[(meta["USAF"] == usaf_id) & (meta["WBAN"] == wban_id)]
    assert not station_meta.empty, f"No metadata found for {usaf_id}-{wban_id}"
