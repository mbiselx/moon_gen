import numpy as np

from moon_gen.lib.utils import SurfaceType
from moon_gen.lib.craters import make_random_crater, waste_gaussian
from moon_gen.lib.heightmaps import perlin_multiscale_grid, surface_psd_rough

__depends__ = [
    "moon_gen.lib.utils",
    "moon_gen.lib.craters",
    "moon_gen.lib.heightmaps"
]


def surface(n=513) -> SurfaceType:
    '''
    create a random lunar surface using:
     - mutliscale perlin grid with a lunar highland PSD
     - randomly placed craters
     - gaussian-blur style mass wasting
    '''
    nx = ny = n
    ax = ay = n/20
    cx, cy = 100*np.random.random((2,))
    x = np.linspace(-ax/2, ax/2, nx)
    y = np.linspace(-ay/2, ay/2, ny)

    print("generating background")
    z = perlin_multiscale_grid(x+cx, y+cy, psd=surface_psd_rough, octaves=10)

    nb_craters = 40 + np.random.randint(10, 50)
    print(f"generating {nb_craters} craters")

    for i in reversed(range(4)):
        for _ in range(nb_craters//4):
            z = make_random_crater(x, y, z)
        z = waste_gaussian(z, i/10 + np.random.random()/5)

    print("done")

    return x, y, z
