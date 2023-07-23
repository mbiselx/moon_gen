import numpy as np

# The following two ratio values are taken from
# LUNAR SURFACE MODELS, Marshall Space Center, p 16
# https://ntrs.nasa.gov/api/citations/19700009596/downloads/19700009596.pdf

DDR = 0.23  # fresh crater : 0.23 - 0.25
'''depth-to-diameter ratio'''
# HDR = 0.06  # fresh crater : 0.022 - 0.06
HDR = 0.075  # for aesthetics -- less looks bad ???
'''height-to-diameter ratio'''


def make_excavation(
        x: np.ndarray,
        y: np.ndarray,
        center: tuple[float, float],
        radius: float = 1,
        elevation: float = 0
) -> np.ndarray:
    '''return the hyperbola corresponding to the excavation of a single crater'''
    r_square = ((x-center[0]).reshape((len(x), 1))**2 +
                (y-center[1]).reshape((1, len(y)))**2)
    h = 2*radius*HDR
    d = 2*radius*DDR
    crater = d * r_square / radius ** 2 + (elevation + h-d)
    return crater


def make_ejecta(
        x: np.ndarray,
        y: np.ndarray,
        center: tuple[float, float],
        radius: float = 1,
) -> np.ndarray:
    '''return the elevation corresponding to the ejecta from a single crater'''
    r_square = np.maximum(((x-center[0]).reshape((len(x), 1))**2 +
                           (y-center[1]).reshape((1, len(y)))**2), radius**2)
    ejecta_weight = np.exp(np.log(2)*radius**2/r_square) - 1
    ejecta_base = 2*radius*HDR*ejecta_weight
    return ejecta_base + np.random.normal(scale=0.1*ejecta_base)


def surface(n=150) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nx = ny = n

    # center
    # center = tuple(10*(np.random.random((2,))-.5))
    center = (0., 0.)
    # scale
    # scale = np.random.random()*99/100 + .01
    radius = 3
    print(radius)

    # generate the initial flat terrain
    x = np.linspace(-10, 10, nx)
    y = np.linspace(-10, 10, ny)
    ground = np.zeros((nx, ny))
    # ground = .05*np.random.random((nx, ny))

    # apply ejecta to the ground
    ejecta = make_ejecta(x, y, center, radius)
    z = ground + ejecta
    # z = ground

    # dig the creater
    crater = make_excavation(x, y, center, radius)
    z = np.minimum(z, crater)
    # z = crater

    return x, y, z
