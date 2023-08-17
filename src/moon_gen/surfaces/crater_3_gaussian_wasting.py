import numpy as np

from moon_gen.lib.utils import SurfaceType
from moon_gen.lib.craters import (
    make_random_crater, waste_gaussian,
    crater_density_fresh, crater_density_young, crater_density_mature, crater_density_old,
)
__depends__ = [
    "moon_gen.lib.utils",
    "moon_gen.lib.craters"
]


def surface(n=257) -> SurfaceType:
    '''
    creates a surface with a random number of simple (hyperbolic) craters,
    which is then subjected to gaussian-blur-type mass wasting.
    '''
    nx = ny = n
    size = 10

    # generate the initial flat terrain
    x = np.linspace(-size, size, nx)
    y = np.linspace(-size, size, ny)
    z = np.random.normal(scale=0.05, size=(nx, ny))

    distribution = crater_density_young
    distribution.d_min = 4*size/n

    nb_craters = distribution.number(x, y)
    print(f"generating {nb_craters} craters")

    for _ in range(nb_craters):
        # make the crater
        d = distribution.diameter(np.random.random())
        z = make_random_crater(x, y, z, d/2)
        # apply mass wasting
        z = waste_gaussian(z, np.random.random()/5)

    # finally, apply micro-meteorite impacts
    z += np.random.normal(scale=0.001, size=z.shape)

    print("done")

    return x, y, z
