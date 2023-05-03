import numpy as np


def surface(n=120) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nx = ny = n

    # generate the initial flat terrain
    x = np.linspace(-8, 8, nx)
    y = np.linspace(-8, 8, ny)
    ground = np.ones((nx, ny))

    # the creater
    crater = .4*np.sqrt(x.reshape((nx, 1))**2 + y.reshape((1, ny))**2) - .1

    # the rim
    rim = np.exp(10/(x.reshape((nx, 1))**2 + y.reshape((1, ny))**2))

    # combine the lot
    z = np.minimum(ground, crater)

    return x, y, z
