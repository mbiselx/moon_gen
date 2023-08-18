'''
HEIGHTMAPS.PY

This submodule contains functions useful for generating random or
procedural heightmaps based on perlin noise.
'''

import math
import typing

import numpy as np
from numpy.typing import NDArray

from moon_gen.lib.distributions import (
    cash,
    surface_psd_rough, surface_psd_nominal, surface_psd_smooth
)


@typing.overload
def interpolate(low: float, high: float, w: float) -> float:
    ...


@typing.overload
def interpolate(
    low: NDArray[np.float64],
    high: NDArray[np.float64],
    w: NDArray[np.float64]
) -> NDArray[np.float64]:
    ...


def interpolate(low, high, w):
    '''interpolate a point `w` between `low` and `high`'''
    # return (a1 - a0) * w + a0
    return (high - low) * (3.0 - w * 2.0) * w * w + low


def random_gradient(ix: int, iy: int, seed: int = 0):
    r = cash(ix, iy, seed)
    return math.cos(r), math.sin(r)


def dot_grid_gradient(ix: int, iy: int, x: float, y: float):
    gx, gy = random_gradient(ix, iy)
    dx = x-ix
    dy = y-iy
    return (dx*gx + dy*gy)


def perlin(x: float, y: float):
    '''
    create perlin noise point-by-point, as shown on Wikipedia.

    very inefficient in Python.
    '''
    x0, y0 = math.floor(x), math.floor(y)
    x1, y1 = x0+1, y0+1
    wx, wy = x-x0, y-y0

    n0 = dot_grid_gradient(x0, y0, x, y)
    n1 = dot_grid_gradient(x1, y0, x, y)
    ix0 = interpolate(n0, n1, wx)

    n0 = dot_grid_gradient(x0, y1, x, y)
    n1 = dot_grid_gradient(x1, y1, x, y)
    ix1 = interpolate(n0, n1, wx)

    i = interpolate(ix0, ix1, wy)
    return i


def _perlin_grid(x: NDArray, y: NDArray) -> NDArray:
    '''
    create a perlin grid, using a point-wise method.
    not recommended, as it is very slow.
    '''
    z = np.zeros((len(y), len(x)))
    for row, y_coord in enumerate(y):
        for col, x_coord in enumerate(x):
            z[row, col] = perlin(x_coord, y_coord)
    return z


def perlin_grid(x: NDArray[np.float_],
                y: NDArray[np.float_]) -> NDArray[np.float_]:
    '''
    generate a perlin noise grid using numpy.
    Fast-ish, but consumes a lot of memory.
    '''
    x0, y0 = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    x1, y1 = x0+1, y0+1
    dx0, dy0 = x-x0, y-y0
    dx1, dy1 = x-x1, y-y1

    # get a "noise vector angle thing" for each gridpoint
    c00 = cash(*np.meshgrid(x0, y0), seed=0)
    c01 = cash(*np.meshgrid(x0, y1), seed=0)
    c10 = cash(*np.meshgrid(x1, y0), seed=0)
    c11 = cash(*np.meshgrid(x1, y1), seed=0)

    # get the noise values at each grid point
    n00 = (np.cos(c00)*dx0) + (np.sin(c00).T*dy0).T
    n01 = (np.cos(c01)*dx0) + (np.sin(c01).T*dy1).T
    n10 = (np.cos(c10)*dx1) + (np.sin(c10).T*dy0).T
    n11 = (np.cos(c11)*dx1) + (np.sin(c11).T*dy1).T

    # interpolate
    nx0 = interpolate(n00, n10, dx0)
    nx1 = interpolate(n01, n11, dx0)
    n = interpolate(nx0.T, nx1.T, dy0).T

    return n


def perlin_multiscale_grid(
        x: NDArray[np.float_],
        y: NDArray[np.float_],
        octaves: int = 8,
        psd: typing.Callable[[float], float] = surface_psd_rough
) -> NDArray[np.float_]:
    '''
    generate multiscale perlin noise with a given power spectral density
    the DC component (zero-frequency) is ignored.

    Arguments :
        x   :   x coordinates
        y   :   y coordinates
        psd :   desired power spectral density function
    '''

    cycle_max = max(x.ptp(), y.ptp())
    cycle = cycle_max
    grids: list[NDArray[np.float_]] = []
    for _ in range(octaves):

        xx = 2*x/cycle
        yy = 2*y/cycle
        # print(f"fs={len(xx)/xx.ptp()}, ptp={xx.ptp()}")
        weight = math.sqrt(psd(1/cycle))
        weight *= math.sqrt(10*x.ptp()/cycle)  # heuristic ????
        print(f"f={1/cycle:6.3f} /m\t{weight=:05.3f}\t({cycle=:7.2f} m)")

        grids.append(weight * perlin_grid(xx, yy))
        cycle /= 2

    return sum(grids, start=np.zeros((len(y), len(x))))


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    a = 2000
    x = np.linspace(-a/2, a/2, 10000, endpoint=True)
    y = np.linspace(0, 10, 50, endpoint=True)

    ff = np.logspace(-3, 2)

    def terrain_fft(x: NDArray, y: NDArray, psd) -> tuple[NDArray, NDArray]:
        n = len(x)
        z = perlin_multiscale_grid(x, y, octaves=12, psd=psd)
        f = np.fft.fftfreq(n, x.ptp()/n)[:n//2]
        dft_z = np.fft.fft(z)[:, :n//2]
        fz = (2/n * np.abs(dft_z).mean(axis=0))**2
        return f, fz

    fig, ax = plt.subplots()
    plotfun = ax.loglog
    # plotfun = ax.semilogy

    plotfun(*terrain_fft(x, y, surface_psd_rough),
            'r-', label="rough mare (sim)")
    plotfun(ff, surface_psd_rough(ff),
            'k-', label="rough mare")

    plotfun(*terrain_fft(x, y, surface_psd_nominal),
            'r--', label="rough updland (sim)")
    plotfun(ff, surface_psd_nominal(ff),
            'k--', label="rough upland")

    plotfun(*terrain_fft(x, y, surface_psd_smooth),
            'r-.', label="smooth mare (sim)")
    plotfun(ff, surface_psd_smooth(ff),
            'k-.', label="smooth mare")

    ax.set_xlim(1e-2, 1e2)
    ax.set_xlabel("Frequency [cycles/meter]")
    ax.set_ylim(1e-4, 1e1)
    ax.set_ylabel("PSD [meters$^2$/cycles/meter]")
    ax.set_title("Surface roughness PSD")
    ax.legend()

    plt.show()
