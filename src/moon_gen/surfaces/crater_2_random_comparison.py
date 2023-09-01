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
    x = np.linspace(-size/2, size/2, nx)
    y = np.linspace(-size/2, size/2, ny)
    yy = np.linspace(-2*size, 2*size, 4*ny)
    z = .005*np.random.random((nx, 4*ny))

    for i, distribution in enumerate((crater_density_fresh,
                                      crater_density_young,
                                     crater_density_mature,
                                     crater_density_old)):
        distribution.d_min = 4*size/n
        nb_craters = distribution.number(x, y)
        print(f"generating {nb_craters} craters")

        for _ in range(nb_craters):
            d = distribution.diameter(np.random.random())
            center = (x.ptp() * np.random.random() + x.min(),
                      y.ptp() * np.random.random() + y.min())
            z[:, i*ny:(i+1)*ny] = make_crater(x, y,
                                              z[:, i*ny:(i+1)*ny], d/2, center)

    print("done")

    return x, yy, z
