from typing import Iterable, Optional, Tuple, Union

import pandas as pd
import pyproj


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
            accepted = f"{types}"
        else:
            accepted = f"{', '.join([str(t) for t in types])}"
        msg = f"`{param}` is not of an acceptable type, must be of type {accepted}!"
        raise TypeError(msg)
    if (params is not None) and (param not in params):
        msg = f"`{param}` is not a recognized argument, must be one of {', '.join(sorted(params))}!"
        raise ValueError(msg)
    return param


def daterange(date_start, date_end=None, freq="h") -> pd.DatetimeIndex:
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
    return pd.date_range(start, end + pd.Timedelta(hours=24), freq=freq, inclusive="left")


def proj(
    x: Union[float, int, Iterable[float]],
    y: Union[float, int, Iterable[float]],
    proj_in: Union[str, int, pyproj.CRS],
    proj_out: Union[str, int, pyproj.CRS],
) -> Tuple[Iterable[float], Iterable[float]]:
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


def to_crs(proj: Union[str, int, pyproj.CRS, pyproj.Proj, None]) -> Optional[pyproj.CRS]:
    """
    Converts a coordinate system into a pyproj.CRS object.

    Args:
        proj (Union[str, int, pyproj.CRS, pyproj.Proj, None]): The coordinate system to convert.

    Returns:
        Optional[pyproj.CRS]: The pyproj.CRS object corresponding to the specified coordinate system.

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
