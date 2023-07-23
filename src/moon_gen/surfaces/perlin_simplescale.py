import math
import typing

import numpy as np


def cash(x_coord: int | np.ndarray, y_coord: int | np.ndarray, seed: int | np.ndarray = 0):
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
def interpolate(low: np.ndarray, high: np.ndarray, w: np.ndarray) -> np.ndarray:
    ...


def interpolate(low: float | np.ndarray, high: float | np.ndarray, w: float | np.ndarray):
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


def _perlin_grid(x: np.ndarray, y: np.ndarray):
    z = np.zeros((len(y), len(x)))
    for row, y_coord in enumerate(y):
        for col, x_coord in enumerate(x):
            z[row, col] = perlin(x_coord, y_coord)
    return z


def perlin_grid(x: np.ndarray, y: np.ndarray):
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


def surface(n=100) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nx = ny = n
    ax = ay = n/10

    x = np.linspace(-ax/2, ax/2, nx)
    y = np.linspace(-ay/2, ay/2, ny)

    z1 = _perlin_grid(x[n//2:], y)
    z2 = perlin_grid(x[n//2:], y)
    z = np.hstack((z1, z2))
    print("done")
    return x, y, z


if __name__ == "__main__":
    import timeit

    setup = '''
import numpy as np
from moon_gen.surfaces.perlin_simplescale import perlin_grid, noise_grid
x = np.linspace(-10, 10, 200)
y = np.linspace(-10, 10, 200)
'''
    N = 10
    tn = timeit.timeit("perlin_grid(x,y)", setup, number=N)
    print("using numpy:", tn)
    tm = timeit.timeit("_perlin_grid(x,y)", setup, number=N)
    print("using math:", tm)
