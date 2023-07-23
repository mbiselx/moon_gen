'''
HEIGHTMAPS.PY

This submodule contains functions useful for generating random or
procedural heightmaps based on perlin noise.
'''

import math
import typing

import numpy as np
from numpy.typing import NDArray

from .distributions import surface_psd_rough


@typing.overload
def cash(x_coord: int, y_coord: int, seed: int = 0) -> int:
    ...


@typing.overload
def cash(x_coord: NDArray[np.int_], y_coord: NDArray[np.int_],
         seed: int = 0) -> int | NDArray[np.int_]:
    ...


def cash(x_coord, y_coord, seed: int = 0):
    '''
    cash stands for chaos hash :D

    It's not really a hash, but it's perfect for what i'm doing
    https://stackoverflow.com/a/37221804/21688300
    '''
    h = seed + x_coord*374761393 + y_coord*668265263  # all constants are prime
    h = (h ^ (h >> 13))*1274126177
    return h ^ (h >> 16)


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

    Arguments :
        x   :   x coordinates
        y   :   y coordinates
        psd :   desired power spectral density -- starting with the lowest
                (nonzero) frequency
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
