import math
from typing import Iterable, Callable

import numpy as np

from moon_gen.surfaces.perlin_simplescale import perlin_grid


def surface_psd_nominal(f: float) -> float:
    '''
    return a surface Power Spectral Density value for a given frequency,
    roughly based on LUNAR SURFACE MODELS, Marshall Space Center, p 20
    https://ntrs.nasa.gov/api/citations/19700009596/downloads/19700009596.pdf

    (meters**2/cycles/meter) -> (cycles/meter) : 
    '''
    return 3 / (2e5 * f**3.35 + 1)


def surface_psd_rough(f: float) -> float:
    '''
    return a surface Power Spectral Density value for a given frequency,
    roughly based on LUNAR SURFACE MODELS, Marshall Space Center, p 20
    https://ntrs.nasa.gov/api/citations/19700009596/downloads/19700009596.pdf

    (meters**2/cycles/meter) -> (cycles/meter) : 
    '''
    return 4 / (8e4 * f**3 + 1) + 1/(3e3 * f**2 + 50)


def perlin_multiscale_grid(x: np.ndarray, y: np.ndarray, octaves: int = 8, psd: Callable[[float], float] = surface_psd_rough, starting_frequency: float | None = None) -> np.ndarray:
    '''
    generate multiscale perlin noise with a given power spectral density 

    Arguments : 
        x   :   x coordinates 
        y   :   y coordinates
        psd :   desired power spectral density -- starting with the lowest (nonzero) frequency 
    '''
    x0, y0 = x.min(), y.min()
    rx, ry = x.ptp(), y.ptp()
    nx, ny = len(x), len(y)

    r = ry / rx

    a = 1/32
    grids = []
    for _ in range(octaves):
        a *= 2

        xx = np.linspace(-a+x0, a+x0, nx)
        yy = np.linspace(-r*a+y0, r*a+y0, ny)

        weight = math.sqrt(psd(2*a/rx))

        grids.append(weight * perlin_grid(xx, yy))

    return sum(grids, start=np.zeros((len(x), len(x))))


def surface(n=513) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nx = ny = n
    ax = ay = n/20

    x = np.linspace(-ax/2, ax/2, nx) + np.random.random()
    y = np.linspace(-ay/2, ay/2, ny) + np.random.random()

    # z = perlin_multiscale_grid(x, y, [3, 2, 1, .5, .25, 0, 0, 0])
    z = perlin_multiscale_grid(x, y, 12, surface_psd_rough)
    print("done")
    return x, y, z
