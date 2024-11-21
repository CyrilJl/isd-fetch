from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
from urllib.parse import urljoin

import geopandas as gpd
import pandas as pd
from tqdm.auto import tqdm

from .misc import check_params, daterange, proj, to_crs


class IsdLite:
    raw_metadata_url = 'https://www.ncei.noaa.gov/pub/data/noaa/isd-history.txt'
    data_url = "https://www.ncei.noaa.gov/pub/data/noaa/isd-lite/{year}/"
    fields = ('temp', 'dewtemp', 'pressure', 'winddirection', 'windspeed', 'skycoverage', 'precipitation-1h', 'precipitation-6h')
    max_retries = 5

    def __init__(self, crs=4326, verbose=0):
        self.crs = to_crs(crs)
        self._get_raw_metadata()
        self.verbose = verbose

    def _get_raw_metadata(self):
        for attempt in range(self.max_retries):
            try:
                metadata = pd.read_fwf(self.raw_metadata_url, skiprows=19)
                metadata = metadata.dropna(subset=['LAT', 'LON'])
                metadata['x'], metadata['y'] = proj(metadata['LON'], metadata['LAT'], 4326, self.crs)
                self._raw_metadata = gpd.GeoDataFrame(metadata, geometry=gpd.points_from_xy(metadata.x, metadata.y, crs=self.crs))
            except Exception as e:
                if attempt < self.max_retries - 1:
                    sleep(2)
                else:
                    raise RuntimeError(f"Failed to download metadata after {self.max_retries} attempts.") from e

    def _filter_metadata(self, geometry):
        if geometry is None:
            return self._raw_metadata['USAF'].unique()
        else:
            return gpd.clip(self._raw_metadata, geometry)['USAF'].unique()

    @classmethod
    def _download_read(cls, url):
        time_features = ['year', 'month', 'day', 'hour']
        df = pd.read_csv(url, sep='\\s+', header=None, na_values=-9999)
        df.columns = time_features + list(cls.fields)
        df[['temp', 'dewtemp', 'pressure', 'windspeed']] /= 10.
        df.index = pd.to_datetime(df[time_features])
        df = df.drop(columns=time_features)
        return df

    @classmethod
    def _download_data_id(cls, usaf_id, years):
        ret = []
        for year in years:
            try:
                df = cls._download_read(urljoin(cls.data_url.format(year=year), f'{usaf_id}-99999-{year}.gz'))
                ret.append(df)
            except Exception as e:
                pass

        if ret:
            return pd.concat(ret)
        else:
            return pd.DataFrame()

    def get_data(self, start, end=None, geometry=None, organize_by='location', n_jobs=8):
        """
        Fetches weather data from the ISD-Lite dataset for the specified time range and location.

        Args:
            start (datetime): The start date for the data retrieval.
            end (datetime, optional): The end date for the data retrieval. If not provided, defaults to the start date.
            geometry (GeoSeries, optional): A GeoSeries or geometry object to filter stations by spatial location.
                If None, data for all stations will be retrieved. Defaults to None.
            organize_by (str, optional): Determines how the resulting data is organized. Options are:
                - 'location': Organize data by weather station.
                - 'field': Organize data by weather variable.
                Defaults to 'location'.
            n_jobs (int, optional): The number of threads to use for parallel data downloads. Defaults to 8.

        Returns:
            dict: A dictionary containing the weather data. The structure of the dictionary depends on the
            `organize_by` parameter:
                - If 'location': Keys are station IDs, and values are DataFrames with weather data.
                - If 'field': Keys are weather variables, and values are DataFrames with stations as columns.

        Raises:
            ValueError: If `organize_by` is not one of the allowed options.
        """
        check_params(param=organize_by, params=('field', 'location'))
        time = daterange(start, end, freq='h')
        years = time.year.unique()
        usaf_ids = self._filter_metadata(geometry=geometry)

        def fetch_data(usaf_id):
            return usaf_id, self._download_data_id(usaf_id=usaf_id, years=years).reindex(index=time)

        ret = {}
        with ThreadPoolExecutor(max_workers=n_jobs) as executor:
            futures = {executor.submit(fetch_data, usaf_id): usaf_id for usaf_id in usaf_ids}

            for future in tqdm(as_completed(futures), total=len(futures), disable=(not self.verbose)):
                usaf_id, data = future.result()
                if data.size > 0:
                    ret[usaf_id] = data

        if organize_by == 'field':
            ret = {field: pd.concat([ret[usaf_id][field].rename(usaf_id) for usaf_id in ret], axis=1) for field in self.fields}

        return ret
