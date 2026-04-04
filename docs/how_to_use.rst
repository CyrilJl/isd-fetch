.. _how_to_use:

How to use
==========

Quick Start Guide
-----------------

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    from pyisd import IsdLite

    # Initialize the client
    isd = IsdLite(crs=4326, verbose=True)

    # View available stations
    isd.raw_metadata.sample(5)

The ``raw_metadata`` property is loaded lazily on first access and cached in memory. If you want to refresh it from
NOAA explicitly, call ``isd.refresh_metadata()``.

Fetching Weather Data
~~~~~~~~~~~~~~~~~~~~~

There are multiple ways to fetch data based on your needs:

.. code-block:: python

    # Get data for all French weather stations
    france_data = isd.get_data(
        start='2023-01-01',
        end='2023-12-31',
        countries='FR',  # ISO country code for France
        organize_by='field'  # Organize data by weather variable
    )

    # Access temperature data from all French stations
    france_data['temp'].sample(4)

.. code-block:: python

    # You can also query multiple countries
    european_data = isd.get_data(
        start='2023-01-01',
        end='2023-12-31',
        countries=['FR', 'DE', 'IT'],  # France, Germany, Italy
        organize_by='field'
    )

.. code-block:: python

    # If you already know a station id, you can fetch it directly
    station_data = isd.get_data(
        start='2024-01-01',
        end='2024-01-07',
        station_id='723270-13897',
        organize_by='location'
    )

    station_data['723270-13897'][['temp', 'pressure']].head()

Understanding The Output Shape
------------------------------

``organize_by='location'`` returns one dataframe per station:

.. code-block:: python

    data = isd.get_data(
        start='2024-01-01',
        end='2024-01-02',
        countries='FR',
        organize_by='location'
    )

    first_station_id = next(iter(data))
    data[first_station_id].columns

``organize_by='field'`` pivots the result so each weather field contains one dataframe with station ids as columns:

.. code-block:: python

    data = isd.get_data(
        start='2024-01-01',
        end='2024-01-02',
        countries='FR',
        organize_by='field'
    )

    data['temp'].head()

Spatial Filtering Options
-------------------------

PyISD offers flexible spatial filtering through the ``geometry`` parameter:

1. **Bounding Box**: Using coordinates (xmin, ymin, xmax, ymax)

.. code-block:: python

    geometry = (-2.5, 48.5, 2.5, 49.5)  # Paris region
    data = isd.get_data(start='2023-01-01', geometry=geometry)

2. **GeoDataFrame/Geometry**: Using any shapely or geopandas geometry

.. code-block:: python

    import geopandas as gpd
    from pyisd import IsdLite
    isd = IsdLite()
    # city = gpd.read_file('city_boundary.geojson')
    # data = isd.get_data(start='2023-01-01', geometry=city)

3. **Global Data**: Setting geometry to None (use with caution for large downloads)

.. code-block:: python

    from pyisd import IsdLite
    isd = IsdLite()
    data = isd.get_data(start='2023-01-01', geometry=None)  # Downloads data for all stations

Handling Download Errors
------------------------

``pyisd`` exposes dedicated exceptions for NOAA download failures:

.. code-block:: python

    from pyisd import DataDownloadError, IsdLite, MetadataDownloadError

    isd = IsdLite()

    try:
        data = isd.get_data(start='2024-01-01', station_id='723270-13897')
    except MetadataDownloadError:
        print('Station metadata could not be downloaded.')
    except DataDownloadError:
        print('Station data could not be downloaded or parsed.')
