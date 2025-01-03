[![PyPI version](https://badge.fury.io/py/isd-fetch.svg)](https://badge.fury.io/py/isd-fetch)
[![Unit tests](https://github.com/CyrilJl/isd-fetch/actions/workflows/pytest.yml/badge.svg)](https://github.com/CyrilJl/isd-fetch/actions/workflows/pytest.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/cdc692322be649cea8b8b6760bfb333e)](https://app.codacy.com/gh/CyrilJl/isd-fetch/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

# PyISD: A Python Package for NOAA's ISD Lite Dataset

**PyISD** is a Python package designed for efficiently accessing and processing NOAA's ISD Lite dataset. The ISD Lite dataset, a streamlined version of the full Integrated Surface Database (ISD), provides hourly weather observations worldwide. It includes eight essential surface parameters in a fixed-width format, free of duplicate values, sub-hourly data, and complex flags. For more information, visit the [official ISD homepage](https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database).

## Installation

```bash
pip install isd-fetch
```

## Features

- Easy access to global weather station data with spatial and temporal filtering
- Support for various coordinate reference systems (CRS)
- Parallel data downloading for improved performance
- Flexible data organization by location or weather variable
- Comprehensive station metadata handling

## Quick Start Guide

### Basic Usage

```python
from pyisd import IsdLite

# Initialize the client
isd = IsdLite(crs=4326, verbose=True)

# View available stations
isd.raw_metadata.sample(5)
```

```
         USAF   WBAN         STATION NAME CTRY   ST  ...      BEGIN        END       x       y                geometry
5416   172650  99999             ADIYAMAN   TU  NaN  ... 2007-01-27 2024-11-17  38.283  37.750    POINT (38.283 37.75)
1362   032130  99999             ESKMEALS   UK  NaN  ... 1973-01-02 1997-12-26  -3.400  54.317     POINT (-3.4 54.317)
4729   153150  99999              SEMENIC   RO  NaN  ... 1973-07-21 2024-11-17  22.050  45.183    POINT (22.05 45.183)
28589  999999  13855  TULLAHOMA AEDC SITE   US   TN  ... 1963-01-01 1969-08-01 -86.233  35.383  POINT (-86.233 35.383)
6422   268530  99999             BEREZINO   BO  NaN  ... 1960-04-01 2024-11-17  28.983  53.833   POINT (28.983 53.833)
```

### Fetching Weather Data

There are multiple ways to fetch data based on your needs:

```python
# Get data for all French weather stations
france_data = isd.get_data(
    start='2023-01-01',
    end='2023-12-31',
    countries='FR',  # ISO country code for France
    organize_by='field'  # Organize data by weather variable
)

# Access temperature data from all French stations
france_data['temp'].sample(4)
```

```
                     070200  070240  070270  ...  077680  077750  077700
2023-05-12 09:00:00    11.4    11.6    13.1  ...    19.7    19.7    16.5
2024-06-26 15:00:00    21.8    25.8    26.7  ...    25.8    25.4    23.2
2023-10-09 18:00:00    18.0    16.7    17.9  ...    22.0    20.9    21.8
2023-12-19 14:00:00     NaN    12.0    11.8  ...    14.6    15.7    13.6
```

```python
# You can also query multiple countries
european_data = isd.get_data(
    start='2023-01-01',
    end='2023-12-31',
    countries=['FR', 'DE', 'IT'],  # France, Germany, Italy
    organize_by='field'
)
```

## Spatial Filtering Options

PyISD offers flexible spatial filtering through the `geometry` parameter:

1. **Bounding Box**: Using coordinates (xmin, ymin, xmax, ymax)

```python
geometry = (-2.5, 48.5, 2.5, 49.5)  # Paris region
```

2. **GeoDataFrame/Geometry**: Using any shapely or geopandas geometry

```python
import geopandas as gpd
city = gpd.read_file('city_boundary.geojson')
data = isd.get_data(geometry=city)
```

3. **Place Name**: Using the `get_box()` helper function

```python
geometry = get_box('London', width=2.0, crs=4326)
```

4. **Global Data**: Setting geometry to None (⚠️ use with caution - large downloads)

```python
data = isd.get_data(geometry=None)  # Downloads data for all stations
```

## Available Weather Variables

- `temp`: Air temperature (°C)
- `dewtemp`: Dew point temperature (°C)
- `pressure`: Sea level pressure (hPa)
- `winddirection`: Wind direction (degrees)
- `windspeed`: Wind speed (m/s)
- `skycoverage`: Sky coverage/ceiling (code)
- `precipitation-1h`: One-hour precipitation (mm)
- `precipitation-6h`: Six-hour precipitation (mm)

## Station Coverage

The ISD Lite network includes thousands of weather stations worldwide:

![ISD Station Locations](https://github.com/CyrilJl/pyisd/blob/main/assets/noaa_isd_locations.png?raw=true)
