import numpy as np

from moon_gen.lib.utils import SurfaceType
from moon_gen.lib.craters import (  # noqa: F401
    make_crater, waste_gaussian,
    crater_density_fresh, crater_density_young,
    crater_density_mature, crater_density_old,
)
from moon_gen.lib.heightmaps import (  # noqa: F401
    perlin_multiscale_grid,
    surface_psd_rough, surface_psd_nominal, surface_psd_smooth,
)

__depends__ = [
    "moon_gen.lib.utils",
    "moon_gen.lib.craters",
    "moon_gen.lib.heightmaps"
]


# def surface(n=1025) -> SurfaceType:
def surface(n=513) -> SurfaceType:
    # def surface(n=257) -> SurfaceType:
    '''
    create a random lunar surface using:
     - mutliscale perlin grid with a lunar highland PSD
     - randomly placed craters
     - gaussian-blur style mass wasting
    '''
    nx = ny = n
    ax = ay = 20
    epochs = 6

    cx, cy = 100*np.random.random((2,))
    x = np.linspace(-ax/2, ax/2, nx)
    y = np.linspace(-ay/2, ay/2, ny)

    print("generating background")
    z = perlin_multiscale_grid(
        x+cx,
        y+cy,
        octaves=6,  # don't need many, bc weathering
        psd=surface_psd_nominal,
        # psd=surface_psd_smooth,
    )

    distribution = crater_density_young
    distribution = crater_density_mature
    # distribution = crater_density_old
    distribution.d_min = 4*ax/n

    nb_craters = distribution.number(x, y)
    print(f"generating {nb_craters} craters")

    # create older craters first and weather them
    for w in reversed(range(epochs)):
        for _ in range(nb_craters//epochs):
            d = distribution.diameter(np.random.random())
            center = (x.ptp() * np.random.random() + x.min(),
                      y.ptp() * np.random.random() + y.min())
            z = make_crater(x, y, z, d/2, center)

        if w > 0:
            z = waste_gaussian(z, ax/nx, w/epochs)

    # apply micro-meteorite impacts
    z += np.random.normal(scale=2e-2*ax/nx, size=z.shape)

    # create the last remaining craters unweathered
    for _ in range(nb_craters % epochs):
        d = distribution.diameter(np.random.random())
        center = (x.ptp() * np.random.random() + x.min(),
                  y.ptp() * np.random.random() + y.min())
        z = make_crater(x, y, z, d/2, center)

    print("done")

    return x, y, z
