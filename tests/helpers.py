from time import sleep

import numpy as np
from geopy.geocoders import Nominatim
from shapely.geometry import box

from pyisd.misc import check_params, proj


def get_coordinates(place, crs=4326, retries=10, retry_delay=1, errors="raise"):
    check_params(errors, params=("ignore", "raise"))
    geolocator = Nominatim(user_agent="pyisd-tests")
    results = []

    def get_coordinates_single(location_name):
        for k in range(retries):
            try:
                location = geolocator.geocode(location_name)
                if location:
                    return proj(location.longitude, location.latitude, 4326, crs)
            except Exception:
                if k < retries - 1:
                    sleep(retry_delay)
        if errors == "ignore":
            return (np.nan, np.nan)
        raise ValueError(f"Failed to retrieve coordinates for '{location_name}'")

    if isinstance(place, str):
        return get_coordinates_single(place)

    for location_name in place:
        results.append(get_coordinates_single(location_name))
    return results


def get_box(place, width=10e3, crs=4326):
    x0, y0 = get_coordinates(place, crs=crs)
    return box(x0 - width / 2, y0 - width / 2, x0 + width / 2, y0 + width / 2)
