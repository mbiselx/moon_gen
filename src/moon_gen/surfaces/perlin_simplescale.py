import math
import numpy as np


def cash(x: int | np.ndarray, y: int | np.ndarray, seed: int | np.ndarray = 0):
    '''cash stands for chaos hash :D'''
    h = seed + x*374761393 + y*668265263  # all constants are prime
    h = (h ^ (h >> 13))*1274126177
    return h ^ (h >> 16)


def interpolate(a0: float, a1: float, w):
    # return (a1 - a0) * w + a0
    if w > 1:
        return a1
    if w < 0:
        return a0
    return (a1 - a0) * (3.0 - w * 2.0) * w * w + a0


def random_gradient(ix: int, iy: int, seed: int = 0):
    r = cash(ix, iy, seed)
    return (math.cos(r), math.sin(r))


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
    scale = .9
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    x1, y1 = x0+1, y0+1
    r00 = np.cos(cash(*np.meshgrid(x0, y0)))
    r01 = np.cos(cash(*np.meshgrid(x0, y1)))
    r10 = np.cos(cash(*np.meshgrid(x1, y0)))
    r11 = np.cos(cash(*np.meshgrid(x1, y1)))
    # n = np.fft.ifft2(
    #     np.fft.fft2(r) *
    #     np.fft.fft2(np.exp(-sum(np.meshgrid(x**2, y**2)) /
    #                 2/scale**2)/scale/2/np.pi)
    # )
    # assert np.all(r00[:-1, :-1] == r11[1:, 1:])

    nx0 = r00*(x-x0) + r10*(x-x1)
    nx1 = r01*(x-x0) + r11*(x-x1)
    n = nx0*(y-y0) + nx1*(y-y1)

    n[:-10, :-10] = r00[10:, 10:] - r11[:-10, :-10]
    return n


def surface(n=100) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nx = ny = n
    ax = ay = n/10

    x = np.linspace(-ax/2, ax/2, nx)
    y = np.linspace(-ay/2, ay/2, ny)

    z = perlin_grid(x, y)
    # z = noise_grid(x, y)
    print("done")
    return x, y, z


if __name__ == "__main__":
    x0 = np.array([0, 0, 1, 1, 2, 2], dtype=int)
    y0 = np.array([0, 0, 1, 1, 2, 2], dtype=int)
    x1, y1 = x0+1, y0+1
    c0 = np.cos(cash(*np.meshgrid(x0, y0)))
    c1 = np.cos(cash(*np.meshgrid(x1, y1)))

    print(c0[2:, 2:] - c1[:-2, :-2])

    assert np.all(c0[2:, 2:] == c1[:-2, :-2])
