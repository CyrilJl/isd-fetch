# PyISD: A Python Package for NOAA's ISD Lite Dataset

**PyISD** is a Python package designed for loading and processing NOAA's ISD Lite dataset. The dataset, as described by NOAA, is a streamlined version of the full Integrated Surface Database (ISD). It includes eight common surface parameters in a fixed-width format, free of duplicate values, sub-hourly data, and complicated flags, making it suitable for general research and scientific purposes. For more details, visit the [official ISD homepage](https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database).

## **Features**
- Load and query the ISD Lite dataset with ease.
- Retrieve and process metadata for stations worldwide.
- Filter data based on spatial and temporal constraints.

## **Example Usage**

### **1. Importing and Loading Metadata**
You can start by importing the `IsdLite` module and fetching metadata for weather stations worldwide. Below is an example where we define a bounding box around Paris, France, and display a sample of the station metadata:

```python
from pyisd import IsdLite
from pyisd.misc import get_box

CRS = 4326
geometry = get_box(place='Paris', width=1., crs=CRS)

module = IsdLite(crs=CRS, verbose=True)
module.raw_metadata.sample(5)
```

The output displays station metadata including station name, latitude, longitude, elevation, and the period of available records:

```
         USAF   WBAN             STATION NAME CTRY   ST CALL     LAT      LON  \
8480   377350  99999                   GANDJA   AJ  NaN  NaN  40.717   46.417   
1023   027710  99999  JOUTSA LEIVONMAKI SAVEN   FI  NaN  NaN  61.883   26.100   
11880  545340  99999                 TANGSHAN   CH  NaN  NaN  39.650  118.100   
3795   111900  99999               EISENSTADT   AU  NaN  NaN  47.850   16.533   
26693  957119  99999     WEST WYALONG AIRPORT   AS  NaN  NaN -33.930  147.200   

        ELEV(M)     BEGIN       END        x       y               geometry  
8480     309.0  19320101  20241117   46.417  40.717  POINT (46.417 40.717)  
1023     146.0  20080115  20241112   26.100  61.883    POINT (26.1 61.883)  
11880     29.0  19560820  20241112  118.100  39.650    POINT (118.1 39.65)  
3795     189.3  19730627  20241117   16.533  47.850   POINT (16.533 47.85)  
26693    262.0  19651231  19840629  147.200 -33.930   POINT (147.2 -33.93)  
```

### **2. Fetching and Visualizing Data**
To retrieve data, you can specify the time period and spatial constraints. Here, we fetch temperature data (`temp`) for the bounding box around Paris between January 1, 2023, and November 20, 2024:

```python
data = module.get_data(start=20230101, end=20241120, geometry=geometry, organize_by='field')

data['temp'].plot(figsize=(10, 4), legend=False, c='grey', lw=0.6)
```

![time_series](https://github.com/CyrilJl/pyisd/blob/main/assets/temp_time_series.png?raw=true)
