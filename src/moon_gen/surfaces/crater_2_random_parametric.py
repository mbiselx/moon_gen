import numpy as np

from moon_gen.lib.utils import SurfaceType
from moon_gen.lib.craters import (  # noqa: F401
    make_crater,
    crater_density_fresh, crater_density_young,
    crater_density_mature, crater_density_old,
)

__depends__ = [
    "moon_gen.lib.utils",
    "moon_gen.lib.craters"
]


def surface(n=257) -> SurfaceType:
    '''
    creates a surface with a random number of simple (parabolic) craters
    '''
    nx = ny = n
    size = 10

    # generate the initial flat terrain
    x = np.linspace(-size, size, nx)
    y = np.linspace(-size, size, ny)
    z = .005*np.random.random((nx, ny))

    distribution = crater_density_young
    distribution.d_min = 4*size/n

    nb_craters = distribution.number(x, y)
    print(f"generating {nb_craters} craters")

    for _ in range(nb_craters):
        d = distribution.diameter(np.random.random())
        center = (np.ptp(x) * np.random.random() + x.min(),
                  np.ptp(y) * np.random.random() + y.min())
        z = make_crater(x, y, z, d/2, center)

    print("done")

    return x, y, z
