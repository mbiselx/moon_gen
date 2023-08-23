import numpy as np

from moon_gen.lib.utils import SurfaceType
from moon_gen.lib.craters import (  # noqa: F401
    make_crater, waste_gaussian,
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
    epochs = 6

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

        y_idx = slice(i*ny, (i+1)*ny)

        # create older craters first and weather them
        for w in reversed(range(epochs)):
            for _ in range(nb_craters//epochs):
                d = distribution.diameter(np.random.random())
                center = (x.ptp() * np.random.random() + x.min(),
                          y.ptp() * np.random.random() + y.min())
                z[:, y_idx] = make_crater(x, y,
                                          z[:, y_idx], d/2, center)
            z[:, y_idx] = waste_gaussian(z[:, y_idx],
                                         size/ny, w/epochs)

        # create the last remaining craters unweathered
        for _ in range(nb_craters % epochs):
            d = distribution.diameter(np.random.random())
            center = (x.ptp() * np.random.random() + x.min(),
                      y.ptp() * np.random.random() + y.min())
            z[:, y_idx] = make_crater(x, y,
                                      z[:, y_idx], d/2, center)

    print("done")

    return x, yy, z
