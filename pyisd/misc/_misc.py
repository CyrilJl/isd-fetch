from time import sleep
from typing import Iterable, Tuple, Union

import numpy as np
import pandas as pd
import pyproj
from shapely.geometry import box


def check_params(param, params=None, types=None):
    """Checks a parameter. Tests if ``param`` belongs to ``params`` and/or if type(param)
    belongs to ``types``.

    This function performs checks on the parameter ``param`` to verify if it belongs to a set
    of acceptable parameters ``params`` and/or if it has a type belonging to a set of acceptable types ``types``.

    Args:
        param:
            The parameter to test.
        params (iterable, optional):
            The set of acceptable parameters. If specified, ``param`` must belong to this set.
            Default: None.
        types (type or iterable of types, optional):
            The set of acceptable types. If specified, the type of ``param`` must belong to this set.
            Default: None.

    Raises:
        ValueError:
            If the parameter ``param`` does not satisfy the conditions defined by ``params`` and/or ``types``.
        TypeError:
            If the parameter ``param`` has an unacceptable type.

    Returns:
        The initial parameter ``param``.

    Example:
        .. code-block:: python

            check_params(5, params=[1, 2, 3, 4, 5])
            >>> 5
            check_params('hello', types=str)
            >>> 'hello'

    Note:
        - If ``params`` is specified, ``param`` must be an element of ``params``.
        - If ``types`` is specified, the type of ``param`` must be an element of ``types``.
        - If both ``params`` and ``types`` are specified, ``param`` must satisfy both conditions.
        - If ``params`` and ``types`` are None, no checks are performed, and ``param`` is returned unchanged.
    """
    if (types is not None) and (not isinstance(param, types)):
        if isinstance(types, type):
            accepted = f'{types}'
        else:
            accepted = f"{', '.join([str(t) for t in types])}"
        msg = f"`{param}` is not of an acceptable type, must be of type {accepted}!"
        raise TypeError(msg)
    if (params is not None) and (param not in params):
        msg = f"`{param}` is not a recognized argument, must be one of {', '.join(sorted(params))}!"
        raise ValueError(msg)
    return param


def daterange(date_start, date_end=None, freq='h') -> pd.DatetimeIndex:
    """
    Creates a date range with a given frequency between `date_start` and `date_end`.

    Args:
        date_start (int or str):
            The start date as an integer in "yyyymmdd" format or as a string.
        date_end (int or str or None, optional):
            The end date as an integer in "yyyymmdd" format or as a string.
            If `None`, the end date will equal the start date.
            Default: None.
        freq (str, optional):
            The frequency of the dates in the range. For example, 'H' for hours, 'D' for days, 'M' for months, etc.
            Default: 'H'.

    Returns:
        pd.DatetimeIndex:
            A DatetimeIndex object containing the dates in the specified range with the given frequency.

    Examples:
        .. code-block:: python

            daterange(20220306, 20220307, freq='D')
            >>> DatetimeIndex(['2022-03-06', '2022-03-07'], dtype='datetime64[ns]', freq='D')

        .. code-block:: python

            daterange(20220306)
            >>> DatetimeIndex(['2022-03-06 00:00:00', '2022-03-06 01:00:00', ...],
                               dtype='datetime64[ns]', freq='h')
    """
    start = pd.to_datetime(str(date_start))
    end = start if date_end is None else pd.to_datetime(str(date_end))
    return pd.date_range(start, end+pd.Timedelta(hours=24), freq=freq, inclusive='left')


def get_coordinates(place, crs=4326, retries=10, retry_delay=1, errors='raise'):
    """
    Retrieves geographic coordinates (longitude, latitude) for a given place.

    Args:
        place (Union[str, Iterable[str]]): Name of the place or list of place names.
        crs (Union[str, int, pyproj.CRS], optional): The coordinate projection to use.
                                                     Default: 4326 (WGS 84).
        retries (int, optional): Number of retries in case of failure. Default: 10.
        retry_delay (int, optional): Delay between retries in seconds. Default: 1.
        errors (str, optional): Error handling method ('raise' or 'ignore'). Default: 'raise'.

    Returns:
        Union[Tuple[float, float], List[Tuple[float, float]]]:
            - Tuple[float, float]: Geographic coordinates (longitude, latitude) for the place.
            - List[Tuple[float, float]]: List of geographic coordinates for each place.

    Example:
        .. code-block:: python

            get_coordinates("Paris")
            >>> (2.3488, 48.85341)

            places = ["Paris", "Lyon", "Marseille"]
            get_coordinates(places)
            >>> [(2.3488, 48.85341), (4.8357, 45.76404), (5.36978, 43.29695)]
    """
    from geopy.geocoders import Nominatim
    check_params(errors, params=('ignore', 'raise'))
    geolocator = Nominatim(user_agent='pyisd')
    results = []

    def get_coordinates_single(place):
        for k in range(retries):
            try:
                location = geolocator.geocode(place)
                if location:
                    return proj(location.longitude, location.latitude, 4326, crs)
            except Exception:
                if k < retries-1:
                    sleep(retry_delay)
        if errors == 'ignore':
            return (np.nan, np.nan)
        else:
            raise ValueError(f"Failed to retrieve coordinates for '{place}'")

    if isinstance(place, str):
        return get_coordinates_single(place)
    else:
        for p in place:
            results.append(get_coordinates_single(p))
        return results


def get_box(place, width=10e3, crs=4326) -> box:
    """
    Retrieves a bounding box around a given place.

    Args:
        place (Union[str, Iterable[str]]): Name of the place or list of place names.
        width (float, optional): Width of the box in meters. Default: 10,000 meters.
        crs (Union[str, int, pyproj.CRS], optional): Coordinate projection to use.
                                                     Default: 4326 (WGS 84).

    Returns:
        box: A bounding box centered around the specified place.
    """
    x0, y0 = get_coordinates(place, crs=crs)
    return box(x0-width/2, y0-width/2, x0+width/2, y0+width/2)


def proj(x: Union[float, int, Iterable[float]],
         y: Union[float, int, Iterable[float]],
         proj_in: Union[str, int, pyproj.CRS],
         proj_out: Union[str, int, pyproj.CRS]) -> Tuple[Iterable[float], Iterable[float]]:
    """
    Projects coordinates from one coordinate system to another.

    Args:
        x (Union[float, int, Iterable[float]]): x-coordinates to project.
        y (Union[float, int, Iterable[float]]): y-coordinates to project.
        proj_in (Union[str, int, pyproj.CRS]): Input coordinate system.
        proj_out (Union[str, int, pyproj.CRS]): Output coordinate system.

    Returns:
        Tuple[Iterable[float], Iterable[float]]: Projected coordinates (x, y).
    """
    t = pyproj.Transformer.from_crs(crs_from=to_crs(proj_in), crs_to=to_crs(proj_out), always_xy=True)
    return t.transform(x, y)


def to_crs(proj: Union[str, int, pyproj.CRS, pyproj.Proj, None]) -> pyproj.CRS:
    """
    Converts a coordinate system into a pyproj.CRS object.

    Args:
        proj (Union[str, int, pyproj.CRS, pyproj.Proj, None]): The coordinate system to convert.

    Returns:
        pyproj.CRS: The pyproj.CRS object corresponding to the specified coordinate system.

    Example:
        .. code-block:: python

            to_crs('EPSG:4326')
            >>> <pyproj.CRS ...>

            to_crs(27572)
            >>> <pyproj.CRS ...>
    """
    if isinstance(proj, (int, str)):
        return pyproj.CRS(proj)
    if isinstance(proj, pyproj.CRS):
        return proj
    if isinstance(proj, pyproj.Proj):
        return proj.crs
    if proj is None:
        return None
    raise TypeError("The format of `proj` is not recognized!")
