import math
import numpy as np


def cash(x: int | np.ndarray, y: int | np.ndarray, seed: int | np.ndarray = 0):
    '''cash stands for chaos hash :D'''
    h = seed + x*374761393 + y*668265263  # all constants are prime
    h = (h ^ (h >> 13))*1274126177
    return h ^ (h >> 16)


def interpolate(a0: float | np.ndarray, a1: float | np.ndarray, w: float) -> float | np.ndarray:
    # return (a1 - a0) * w + a0
    # if w > 1:
    #     return a1
    # if w < 0:
    #     return a0
    return (a1 - a0) * (3.0 - w * 2.0) * w * w + a0


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


def perlin_grid(x: np.ndarray, y: np.ndarray):
    z = np.zeros((x.shape[0], y.shape[0]))
    for i, x_point in enumerate(x):
        for j, y_point in enumerate(y):
            z[i, j] = perlin(x_point, y_point)
    return z


def noise_grid(x: np.ndarray, y: np.ndarray):
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    x1, y1 = x0+1, y0+1
    dx0, dy0 = x-x0, y-y0
    dx1, dy1 = 1-dx0, 1-dy0

    # get a "noise vector angle thing" for each gridpoint
    c = cash(*np.meshgrid(
        np.concatenate((x0, [x0[-1]+1])),
        np.concatenate((y0, [y0[-1]+1])),
        indexing="ij"
    ))
    c00 = cash(*np.meshgrid(x0, y0, indexing="ij"))
    c01 = cash(*np.meshgrid(x0, y1, indexing="ij"))
    c10 = cash(*np.meshgrid(x1, y0, indexing="ij"))
    c11 = cash(*np.meshgrid(x1, y1, indexing="ij"))

    # get the noise values at each grid point
    n00 = (np.cos(c00).T*dx0).T + (np.sin(c00)*dy0)
    n01 = (np.cos(c01).T*dx0).T + (np.sin(c01)*dy1)
    n10 = (np.cos(c10).T*dx1).T + (np.sin(c10)*dy0)
    n11 = (np.cos(c11).T*dx1).T + (np.sin(c11)*dy1)

    # interpolate
    # ny0 = (n01 - n00)*dy0 + n00
    # ny1 = (n11 - n10)*dy0 + n10
    # n = ((ny1-ny0).T*dx0).T + ny0
    ny0 = interpolate(n00, n01, dy0)
    ny1 = interpolate(n10, n11, dy0)
    n = interpolate(ny0.T, ny1.T, dx0).T

    return n


def surface(n=100) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nx = ny = n
    ax = ay = n/10

    x = np.linspace(-ax/2, ax/2, nx)
    y = np.linspace(-ay/2, ay/2, ny)

    z1 = perlin_grid(x[:n//2], y)
    z2 = noise_grid(x[n//2:], y)
    z = np.vstack((z1, z2))
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
    tn = timeit.timeit("noise_grid(x,y)", setup, number=N)
    print("using numpy:", tn)
    tm = timeit.timeit("perlin_grid(x,y)", setup, number=N)
    print("using math:", tm)
