[![PyPI version](https://badge.fury.io/py/isd-fetch.svg)](https://badge.fury.io/py/isd-fetch)
[![Unit tests](https://github.com/CyrilJl/isd-fetch/actions/workflows/pytest.yml/badge.svg)](https://github.com/CyrilJl/isd-fetch/actions/workflows/pytest.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/cdc692322be649cea8b8b6760bfb333e)](https://app.codacy.com/gh/CyrilJl/isd-fetch/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

# PyISD: A Python Package for NOAA's ISD Lite Dataset

**PyISD** is a Python package designed for efficiently accessing and processing NOAA's ISD Lite dataset.

For more information, please see the [full documentation]([https://CyrilJl.github.io/pyisd/](https://isd-fetch.readthedocs.io/en/latest/index.html)).

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
