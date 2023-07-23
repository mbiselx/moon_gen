import numpy as np

from moon_gen.lib.utils import SurfaceType

__depends__ = [
    "moon_gen.lib.utils",
]


def surface(n=120) -> SurfaceType:
    '''
    creates a surface with a single simple (conic) crater
    '''
    nx = ny = n

    # generate the initial flat terrain
    x = np.linspace(-8, 8, nx)
    y = np.linspace(-8, 8, ny)

    # the creater
    crater = .4*np.sqrt(x.reshape((nx, 1))**2 + y.reshape((1, ny))**2) - .1

    # the rim
    rim = np.exp(10/(x.reshape((nx, 1))**2 + y.reshape((1, ny))**2))

    # combine the lot
    z = np.minimum(rim, crater)

    return x, y, z
