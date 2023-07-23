
import numpy as np

from moon_gen.lib.utils import SurfaceType


def surface(*args) -> SurfaceType:
    '''
    A simple test surface
    '''
    x = np.linspace(-8, 8, 50)
    y = np.linspace(-8, 8, 50)
    z = 0.1 * ((x.reshape(50, 1) ** 2) - (y.reshape(1, 50) ** 2))

    return x, y, z
