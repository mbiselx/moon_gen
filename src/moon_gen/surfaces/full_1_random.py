import numpy as np

from moon_gen.lib.utils import SurfaceType
from moon_gen.lib.craters import (
    make_random_crater, waste_gaussian,
    crater_density_fresh, crater_density_young, crater_density_mature, crater_density_old,
)
from moon_gen.lib.heightmaps import (
    perlin_multiscale_grid,
    surface_psd_rough, surface_psd_nominal, surface_psd_smooth,
)

__depends__ = [
    "moon_gen.lib.utils",
    "moon_gen.lib.craters",
    "moon_gen.lib.heightmaps"
]


# def surface(n=513) -> SurfaceType:
def surface(n=257) -> SurfaceType:
    '''
    create a random lunar surface using:
     - mutliscale perlin grid with a lunar highland PSD
     - randomly placed craters
     - gaussian-blur style mass wasting
    '''
    nx = ny = n
    ax = ay = 20
    cx, cy = 100*np.random.random((2,))
    x = np.linspace(-ax/2, ax/2, nx)
    y = np.linspace(-ay/2, ay/2, ny)

    print("generating background")
    z = perlin_multiscale_grid(
        x+cx,
        y+cy,
        octaves=12,
        psd=surface_psd_smooth)

    distribution = crater_density_mature
    distribution.d_min = 4*ax/n

    nb_craters = 40 + np.random.randint(10, 50)
    print(f"generating {nb_craters} craters")

    for i in reversed(range(4)):
        for _ in range(nb_craters//4):
            d = distribution.diameter(np.random.random())
            z = make_random_crater(x, y, z, d/2)
        z = waste_gaussian(z, i/10 + np.random.random()/5)

    print("done")

    return x, y, z
