import pytest

from pyisd import IsdLite
from pyisd.misc import get_box


@pytest.fixture
def crs():
    return 4326


def test_isdlite_location(crs):
    geometry = get_box(place='Paris', width=1., crs=crs)
    module = IsdLite(verbose=True)
    data = module.get_data(start=20230101, end=20241231, geometry=geometry, organize_by='location')
    assert data[list(data.keys())[0]].size > 0


def test_isdlite_field(crs):
    geometry = get_box(place='Paris', width=1., crs=crs)
    module = IsdLite(verbose=True)
    data = module.get_data(start=20230101, end=20241231, geometry=geometry, organize_by='field')
    assert data['temp'].size > 0
