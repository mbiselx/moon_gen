import numpy as np

from moon_gen.lib.utils import SurfaceType
from moon_gen.lib.craters import make_crater

__depends__ = [
    "moon_gen.lib.utils",
    "moon_gen.lib.craters"
]


def surface(n=150) -> SurfaceType:
    '''
    creates a surface with a single simple (parabolic) crater
    '''
    nx = ny = n

    # center
    center = (0., 0.)
    # scale
    radius = 3
    print("radius=", radius)

    # generate the initial flat terrain
    x = np.linspace(-10, 10, nx)
    y = np.linspace(-10, 10, ny)
    ground = np.zeros((nx, ny))

    # apply ejecta to the ground
    z = make_crater(x, y, ground, radius, center)

    return x, y, z
