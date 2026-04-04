[![PyPI version](https://badge.fury.io/py/isd-fetch.svg)](https://badge.fury.io/py/isd-fetch)
[![Unit tests](https://github.com/CyrilJl/isd-fetch/actions/workflows/pytest.yml/badge.svg)](https://github.com/CyrilJl/isd-fetch/actions/workflows/pytest.yml)

# isd-fetch

`isd-fetch` is a Python package for efficiently accessing and processing NOAA's ISD Lite dataset. The project is
distributed as `isd-fetch` and imported as `pyisd`.

For more information, see the [full documentation](https://isd-fetch.readthedocs.io/en/latest/index.html).

## Installation

```bash
pip install isd-fetch
```

## Quick Start

```python
from pyisd import IsdLite

# Initialize the client
isd = IsdLite(crs=4326, verbose=True)

# Get data for all French weather stations for 2023
france_data = isd.get_data(
    start='2023-01-01',
    end='2023-12-31',
    countries='FR',
    organize_by='field'
)

# Access temperature data
temperature = france_data['temp']
temperature.sample(5)
```
