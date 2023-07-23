
import numpy as np

from moon_gen.lib.utils import SurfaceType
from moon_gen.lib.heightmaps import perlin_multiscale_grid, surface_psd_rough

__depends__ = [
    "moon_gen.lib.utils",
    "moon_gen.lib.heightmaps"
]


def surface(n=513) -> SurfaceType:
    '''
    generate a multi-scale perlin noise heightmap, with a PSD
    roughly equivalent that that of a rough lunar heighland
    '''
    nx = ny = n
    ax = ay = n/20

    x = np.linspace(-ax/2, ax/2, nx) + np.random.random()
    y = np.linspace(-ay/2, ay/2, ny) + np.random.random()

    z = perlin_multiscale_grid(x, y, octaves=12, psd=surface_psd_rough)
    print("done")
    return x, y, z
