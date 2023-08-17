
import numpy as np

from moon_gen.lib.utils import SurfaceType
from moon_gen.lib.heightmaps import perlin_multiscale_grid, surface_psd_rough, surface_psd_nominal, surface_psd_smooth

__depends__ = [
    "moon_gen.lib.utils",
    "moon_gen.lib.heightmaps"
]


def surface(n=513) -> SurfaceType:
    '''
    generate a multi-scale perlin noise heightmap, with a PSD
    roughly equivalent that that of a rough lunar heighland
    '''
    nx = ny = 2000
    ax = ay = 100

    x = np.linspace(-ax/2, ax/2, nx)
    y = np.linspace(-ay/2, ay/2, ny)

    z = perlin_multiscale_grid(
        x + 100*np.random.random(),
        y + 100*np.random.random(),
        octaves=12,
        psd=surface_psd_smooth
        # psd=surface_psd_nominal
        # psd=surface_psd_rough
    )
    print("done")
    return x, y, z
