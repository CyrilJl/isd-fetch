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

3. **Place Name**: Using the ``get_box()`` helper function

.. code-block:: python

    from pyisd.misc import get_box
    from pyisd import IsdLite
    isd = IsdLite()
    geometry = get_box('London', width=2.0, crs=4326)
    data = isd.get_data(start='2023-01-01', geometry=geometry)

4. **Global Data**: Setting geometry to None (⚠️ use with caution - large downloads)

.. code-block:: python

    from pyisd import IsdLite
    isd = IsdLite()
    data = isd.get_data(start='2023-01-01', geometry=None)  # Downloads data for all stations
