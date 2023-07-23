'''
CRATERS:PY

This submodule contains functions useful for generating graters on
a surface
'''

from typing import Callable

import numpy as np
from numpy.typing import NDArray

from scipy.ndimage import gaussian_filter

from .distributions import radius_probability, HDR, DDR


def make_excavation(
        x: NDArray,
        y: NDArray,
        center: tuple[float, float],
        radius: float = 1,
        elevation: float = 0
) -> NDArray:
    '''
    return the hyperbola corresponding to the excavation of a single crater
    '''
    r_square = ((x-center[0]).reshape((len(x), 1))**2 +
                (y-center[1]).reshape((1, len(y)))**2)
    h = 2*radius*HDR
    d = 2*radius*DDR
    crater = d * r_square / radius ** 2 + (elevation + h-d)
    return crater


def make_ejecta(
        x: NDArray,
        y: NDArray,
        center: tuple[float, float],
        radius: float = 1,
) -> NDArray:
    '''
    return the elevation corresponding to the ejecta from a single crater
    '''
    r_square = np.maximum(((x-center[0]).reshape((len(x), 1))**2 +
                           (y-center[1]).reshape((1, len(y)))**2), radius**2)
    ejecta_weight = np.exp(np.log(2)*radius**2/r_square) - 1
    ejecta_base = 2*radius*HDR*ejecta_weight
    return ejecta_base + np.random.normal(scale=0.1*ejecta_base)


def make_random_crater(
        x: NDArray,
        y: NDArray,
        z: NDArray,
        p: Callable[[], float] = radius_probability
) -> np.ndarray:
    '''
    make a random crater in the given `z` surface.
    The position of the crater will be uniformly random along `x` and `y`.
    The radius of the crater will be given by the probability function `p.
    '''
    step = x.ptp()/len(x)
    # center
    center = (x.ptp() * np.random.random() + x.min(),
              y.ptp() * np.random.random() + y.min())
    # scale
    radius = p()
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
