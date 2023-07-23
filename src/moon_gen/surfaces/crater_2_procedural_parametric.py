import numpy as np

from moon_gen.lib.utils import SurfaceType
from moon_gen.lib.craters import make_procedural_craters

__depends__ = [
    "moon_gen.lib.utils",
    "moon_gen.lib.craters"
]


def surface(n=150) -> SurfaceType:
    '''
    creates a surface with a random number of simple (hyperbolic) craters
    '''
    nx = ny = n
    size = 10

    ny += 1

    # generate the initial flat terrain
    x = np.linspace(-size, size, nx)
    y = np.linspace(-size, size, ny)
    z = .005*np.random.random((nx, ny))

    thresh = np.random.random()/100 + 99/100
    # thresh = .9987
    z = make_procedural_craters(x, y, z, thresh)
    print("done")

    return x, y, z


if __name__ == "__main__":
    surface()
