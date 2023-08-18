'''
CRATERS:PY

This submodule contains functions useful for generating graters on
a surface
'''

from typing import Callable

import numpy as np
from numpy.typing import NDArray

from scipy.ndimage import gaussian_filter

from .distributions import (
    HDR, DDR,
    crater_density_fresh, crater_density_young, crater_density_mature, crater_density_old,
    cash, cash_norm)


def make_excavation(
        x: NDArray[np.float_],
        y: NDArray[np.float_],
        center: tuple[float, float],
        radius: float = 1,
        elevation: float = 0
) -> NDArray[np.float_]:
    '''
    return the paraboloid corresponding to the excavation of a single crater
    '''
    r_square = ((x-center[0]).reshape((len(x), 1))**2 +
                (y-center[1]).reshape((1, len(y)))**2)
    h = 2*radius*HDR
    d = 2*radius*DDR
    crater = d * r_square / radius ** 2 + (elevation + h-d)
    return crater


def make_ejecta(
        x: NDArray[np.float_],
        y: NDArray[np.float_],
        center: tuple[float, float],
        radius: float = 1,
) -> NDArray[np.float_]:
    '''
    return the elevation corresponding to the ejecta from a single crater
    '''
    r_square = np.maximum(((x-center[0]).reshape((len(x), 1))**2 +
                           (y-center[1]).reshape((1, len(y)))**2), radius**2)
    ejecta_weight = np.exp(np.log(2)*radius**2/r_square) - 1
    ejecta_base = 2*radius*HDR*ejecta_weight
    return ejecta_base + np.random.normal(scale=0.1*ejecta_base)


def make_random_crater(
        x: NDArray[np.float_],
        y: NDArray[np.float_],
        z: NDArray[np.float_],
        radius: float
) -> NDArray[np.float_]:
    '''
    make a random crater in the given `z` surface.
    The position of the crater will be uniformly random along `x` and `y`.
    The radius of the crater will be `r`.
    '''
    step = x.ptp()/len(x)
    # center
    center = (x.ptp() * np.random.random() + x.min(),
              y.ptp() * np.random.random() + y.min())
    # elevation
    elevation = z[np.abs(x-center[0]) < step,
                  np.abs(y-center[1]) < step].mean()

    # apply ejecta to the ground
    ejecta = make_ejecta(x, y, center, radius)
    z = z + ejecta

    # dig the creater
    crater = make_excavation(x, y, center, radius, elevation)
    z = np.minimum(z, crater)

    return z


def waste_gaussian(z: NDArray, duration: float) -> NDArray:
    '''simulate mass wasting between impacts, using gaussian blur.'''
    return 0.5*(z+gaussian_filter(z, sigma=5*duration))


def make_procedural_craters(
        x: NDArray[np.float_],
        y: NDArray[np.float_],
        z: NDArray[np.float_],
        thresh: float = .999
) -> NDArray[np.float_]:
    # create a grid based on the millimeter point location
    xx, yy = np.meshgrid(x, y, indexing='ij')
    chaos_grid = cash(
        (1000*xx).astype(np.int64),
        (1000*yy).astype(np.int64),
        1234567890
    )

    # sanity check
    assert z.shape == chaos_grid.shape

    # the areas greater than thresh will have a crater center.
    # NOTE: `np.nonzero returns row, column index`
    row_idx, col_idx = np.nonzero(chaos_grid > thresh*(2**63))

    # the age of the crater will be calculated from the chaos value
    ages = chaos_grid[row_idx, col_idx].argsort()

    cxs, cys = x[row_idx[ages]], y[col_idx[ages]]
    radii = crater_density_young.diameter(
        cash_norm(
            cxs.astype(np.int64),
            cys.astype(np.int64)
        )
    )

    # apply craters in order of appearance : oldest first
    print(f"generating {len(radii)} craters")
    for radius, cx, cy in zip(radii, cxs, cys):
        elevation = z[
            (xx-cx)**2 + (yy-cy)**2 < radius**2
        ].mean()

        z += make_ejecta(x, y, (cx, cy), radius)
        crater = make_excavation(x, y, (cx, cy), radius, elevation)
        z = np.minimum(z, crater)

    return z
