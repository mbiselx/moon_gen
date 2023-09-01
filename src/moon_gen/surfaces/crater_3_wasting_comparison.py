import numpy as np

from moon_gen.lib.utils import SurfaceType
from moon_gen.lib.craters import (  # noqa: F401, E501
    make_crater, waste_gaussian,
)

__depends__ = [
    "moon_gen.lib.utils",
    "moon_gen.lib.craters"
]


def surface(n=257) -> SurfaceType:
    '''
    creates a surface with several simple (parabolic) craters
    and applies increasinggaussian weathering to them
    '''
    nx = ny = n
    size = 20
    radius = 1

    # generate the initial flat terrain
    x = np.linspace(-size/2, size/2, nx)
    y = np.linspace(-size/2, size/2, ny)
    z = np.random.normal(scale=5e-6*size, size=(nx, ny))

    weathering_parameter = (0, 0.15, 0.33, 0.66, 1)
    loc = np.linspace(-size/2+4*radius, size/2-4*radius,
                      len(weathering_parameter),
                      endpoint=True)

    for i, wp in zip(loc, reversed(weathering_parameter)):
        # make crater
        z = make_crater(x, y, z, radius, (i, i))

        # apply weathering
        z = waste_gaussian(z, size/n, wp)

    # finally, apply micro-meteorite impacts
    # z += np.random.normal(scale=0.0002*size, size=z.shape)

    return x, y, z
