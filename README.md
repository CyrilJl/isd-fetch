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
         USAF   WBAN         STATION NAME CTRY   ST  CALL     LAT      LON  ELEV(M)     BEGIN       END        x       y                geometry
27133  990076  99999   ENVIRON BUOY 31001  NaN  NaN   NaN   0.000  -35.000      0.0  20041110  20041110  -35.000   0.000           POINT (-35 0)
7779   338480  99999              OCHAKOV   UP  NaN   NaN  46.633   31.550     41.0  19600128  20011222   31.550  46.633    POINT (31.55 46.633)
23794  840260  99999  GENERAL RIVADENEIRA   EC  NaN   NaN  -0.983  -79.633     10.0  20040902  20241117  -79.633  -0.983  POINT (-79.633 -0.983)
20203  725489  99999     ORANGE CITY MUNI   US   IA  KORC  42.983  -96.067    431.0  19950423  19971231  -96.067  42.983  POINT (-96.067 42.983)
11356  489250  99999             OUDOMXAY   LA  NaN   NaN  20.683  102.000    550.0  19840701  20241117  102.000  20.683      POINT (102 20.683)
```

### **2. Fetching and Visualizing Data**
To retrieve data, you can specify the time period and spatial constraints. Here, we fetch temperature data (`temp`) for the bounding box around Paris between January 1, 2023, and November 20, 2024:

```python
from pyisd.misc import get_box

geometry = get_box(place='Paris', width=1., crs=CRS)

data = module.get_data(start=20230101, end=20241120, geometry=geometry, organize_by='field')

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
