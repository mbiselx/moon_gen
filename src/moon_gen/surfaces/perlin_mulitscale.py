from typing import Iterable
import numpy as np

from moon_gen.surfaces.perlin_simplescale import perlin_grid


def generate_psd(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    raise NotImplementedError()


def perlin_multiscale_grid(x: np.ndarray, y: np.ndarray, psd: Iterable) -> np.ndarray:
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

    a = .25
    grids = []
    for weight in psd:
        a *= 2
        if weight == 0:  # don't need to generate for this frequency, so we skip
            continue

        xx = np.linspace(-a+x0, a+x0, nx)
        yy = np.linspace(-r*a+y0, r*a+y0, ny)

        grids.append(weight*perlin_grid(xx, yy))

    return sum(grids)


def surface(n=250) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nx = ny = n
    ax = ay = n/10

    x = np.linspace(-ax/2, ax/2, nx)
    y = np.linspace(-ay/2, ay/2, ny)

    z = perlin_multiscale_grid(x, y, [3, 2, 1, .5, .25, 0, 0, 0])
    print("done")
    return x, y, z


if __name__ == "__main__":
    x = np.linspace(-3.2, 3.2, 10)
    y = np.linspace(-2.2, 2.2, 8)

    perlin_multiscale_grid(x, y, [1, 0, 0, 1])
