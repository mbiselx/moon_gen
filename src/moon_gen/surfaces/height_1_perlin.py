import numpy as np

from moon_gen.lib.utils import SurfaceType
from moon_gen.lib.heightmaps import perlin_grid, _perlin_grid

__depends__ = [
    "moon_gen.lib.utils",
    "moon_gen.lib.heightmaps"
]


def surface(n=100) -> SurfaceType:
    '''
    generate two perlin noise heightmaps using different techniques.
    One uses a point-wise method, the other uses as numpy method.
    '''
    nx = ny = n
    ax = ay = n/10

    x = np.linspace(-ax/2, ax/2, nx)
    y = np.linspace(-ay/2, ay/2, ny)

    z1 = _perlin_grid(x[n//2:], y)
    z2 = perlin_grid(x[n//2:], y)
    z = np.vstack((z1, z2))
    print("done")
    return x, y, z


if __name__ == "__main__":
    import timeit

    setup = '''
import numpy as np
from moon_gen.surfaces.perlin_simplescale import perlin_grid, noise_grid
x = np.linspace(-10, 10, 200)
y = np.linspace(-10, 10, 200)
'''
    N = 10
    tn = timeit.timeit("perlin_grid(x,y)", setup, number=N)
    print("using numpy:", tn)
    tm = timeit.timeit("_perlin_grid(x,y)", setup, number=N)
    print("using math:", tm)
