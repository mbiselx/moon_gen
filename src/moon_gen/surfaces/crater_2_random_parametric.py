import numpy as np

from moon_gen.lib.utils import SurfaceType
from moon_gen.lib.craters import make_random_crater

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

    # generate the initial flat terrain
    x = np.linspace(-size, size, nx)
    y = np.linspace(-size, size, ny)
    z = .005*np.random.random((nx, ny))

    nb_craters = np.random.randint(50, 100)
    print(f"generating {nb_craters} craters")

    for i in range(nb_craters):
        z = make_random_crater(x, y, z)

    return x, y, z
