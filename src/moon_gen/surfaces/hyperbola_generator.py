import numpy as np


def make_crater(x: np.ndarray, y: np.ndarray, center: tuple[float, float], scale: float, elevation: float = 0) -> np.ndarray:
    '''return the hyperbola corresponding to a single crater'''
    crater = .1*((x-center[0]).reshape((len(x), 1))**2 +
                 (y-center[1]).reshape((1, len(y)))**2)/scale + (elevation - scale)
    return crater


def make_ejecta(x: np.ndarray, y: np.ndarray, center: tuple[float, float], scale: float, elevation: float = 0) -> np.ndarray:
    '''return the elevation corresponding to the ejecta from a single crater'''
    z = ((x-center[0]).reshape((len(x), 1))**2 +
         (y-center[1]).reshape((1, len(y)))**2) / scale**3
    ejecta_weight = np.exp(10/np.maximum(z, 10/scale)) - 1
    return np.random.normal(scale=.05/scale*ejecta_weight) + ejecta_weight


def surface(n=150) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nx = ny = n

    # center
    center = tuple(10*(np.random.random((2,))-.5))
    # scale
    scale = np.random.random()*99/100 + .01
    print(scale)

    # generate the initial flat terrain
    x = np.linspace(-10, 10, nx)
    y = np.linspace(-10, 10, ny)
    ground = np.zeros((nx, ny))
    ground = .05*np.random.random((nx, ny))

    # apply ejecta to the ground
    ejecta = make_ejecta(x, y, center, scale)
    z = ground + ejecta

    # dig the creater
    crater = make_crater(x, y, center, scale)
    z = np.minimum(z, crater)

    return x, y, z
