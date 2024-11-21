from pyisd import IsdLite
from pyisd.misc import get_box


def test_isdlite():
    CRS = 4326
    geometry = get_box(place='Paris', width=1., crs=CRS)
    module = IsdLite()
    data = module.get_data(start=20230101, end=20241231, geometry=geometry, organize_by='location')
    assert data[list(data.keys())[0]].size > 0
    data = module.get_data(start=20230101, end=20241231, geometry=geometry, organize_by='field')
    assert data['temp'].size > 0
