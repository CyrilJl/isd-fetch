[![PyPI version](https://badge.fury.io/py/isd-fetch.svg)](https://badge.fury.io/py/isd-fetch)
[![Unit tests](https://github.com/CyrilJl/isd-fetch/actions/workflows/pytest.yml/badge.svg)](https://github.com/CyrilJl/isd-fetch/actions/workflows/pytest.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/cdc692322be649cea8b8b6760bfb333e)](https://app.codacy.com/gh/CyrilJl/isd-fetch/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

# PyISD: A Python Package for NOAA's ISD Lite Dataset

**PyISD** is a Python package designed for loading and processing NOAA's ISD Lite dataset. The dataset, as described by NOAA, is a streamlined version of the full Integrated Surface Database (ISD). It includes eight common surface parameters in a fixed-width format, free of duplicate values, sub-hourly data, and complicated flags, making it suitable for general research and scientific purposes. For more details, visit the [official ISD homepage](https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database).

## Installation
```bash
pip install isd-fetch
```

## **Features**
- Load and query the ISD Lite dataset with ease.
- Retrieve and process metadata for stations worldwide.
- Filter data based on spatial and temporal constraints.

## **Example Usage**

### **1. Importing and Loading Metadata**
You can start by importing the `IsdLite` module, fetching metadata for weather stations worldwide and displaying a sample of the station metadata:

```python
from pyisd import IsdLite

CRS = 4326

module = IsdLite(crs=CRS, verbose=True)
module.raw_metadata.sample(5)
```

The output displays station metadata including station name, latitude, longitude, elevation, and the period of available records:

```
         USAF   WBAN         STATION NAME CTRY   ST  ...      BEGIN        END       x       y                geometry
5416   172650  99999             ADIYAMAN   TU  NaN  ... 2007-01-27 2024-11-17  38.283  37.750    POINT (38.283 37.75)
1362   032130  99999             ESKMEALS   UK  NaN  ... 1973-01-02 1997-12-26  -3.400  54.317     POINT (-3.4 54.317)
4729   153150  99999              SEMENIC   RO  NaN  ... 1973-07-21 2024-11-17  22.050  45.183    POINT (22.05 45.183)
28589  999999  13855  TULLAHOMA AEDC SITE   US   TN  ... 1963-01-01 1969-08-01 -86.233  35.383  POINT (-86.233 35.383)
6422   268530  99999             BEREZINO   BO  NaN  ... 1960-04-01 2024-11-17  28.983  53.833   POINT (28.983 53.833)
```

The available stations locations can be visualized :

![map_isd](https://github.com/CyrilJl/pyisd/blob/main/assets/noaa_isd_locations.png?raw=true)

### **2. Fetching and Visualizing Data**
To retrieve data, you can specify the time period and spatial constraints. Here, we fetch temperature data (`temp`) for the bounding box around Paris between January 1, 2023, and November 20, 2024:

```python
from pyisd.misc import get_box

geometry = get_box(place='Paris', width=1., crs=CRS)

data = module.get_data(start=20230101, end=20241120, geometry=geometry, organize_by='field')
data.keys()
# dict_keys(['temp', 'dewtemp', 'pressure', 'winddirection', 'windspeed', 'skycoverage', 'precipitation-1h', 'precipitation-6h'])

data['temp'].plot(figsize=(10, 4), legend=False, c='grey', lw=0.6)
```

![time_series](https://github.com/CyrilJl/pyisd/blob/main/assets/temp_time_series.png?raw=true)

#### **Flexibility of `geometry`**
The `geometry` parameter is highly flexible and can be set in different ways:

1. **Bounding Box**: Use the `get_box()` function as shown above to define a simple rectangular bounding box around a location.
2. **Custom Geometries**: You can pass any `shapely.geometry` object (e.g., `Polygon`, `MultiPolygon`) or a `geopandas` `GeoDataFrame` to define more specific regions of interest.
3. **`None`**: If `geometry` is set to `None`, the function retrieves data for all available stations globally.  
   ⚠️ **Note**: Setting `geometry=None` is **not advised** unless strictly necessary, as the download time and data size can be extremely large.

By carefully specifying `geometry`, you can focus on the data most relevant to your study while avoiding unnecessarily large downloads.
