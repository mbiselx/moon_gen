import numpy as np
from scipy.ndimage import gaussian_filter

from moon_gen.surfaces.hyperbola_generator import make_crater, make_ejecta
from moon_gen.surfaces.hyperbola_multiple import scale_probability


def waste(z: np.ndarray, duration: float) -> np.ndarray:
    '''simulate mass wasting between impacts.'''
    return 0.5*(z+gaussian_filter(z, sigma=5*duration))


def surface(n=250) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nx = ny = n
    size = 10
    step = 2*size/n

    # generate the initial flat terrain
    x = np.linspace(-size, size, nx)
    y = np.linspace(-size, size, ny)
    z = np.random.normal(scale=0.05, size=(nx, ny))

    nb_craters = np.random.random_integers(10, 50)
    print(f"generating {nb_craters} craters")

    for i in range(nb_craters):
        # center
        center = tuple(2*size*(np.random.random((2,))-.5))
        # scale
        scale = scale_probability()
        # elevation
        elevation = z[np.abs(x-center[0]) < step,
                      np.abs(y-center[1]) < step].mean()

        # apply ejecta to the ground
        ejecta = make_ejecta(x, y, center, scale, elevation)
        z = z + ejecta

        # dig the creater
        crater = make_crater(x, y, center, scale, elevation)
        z = np.minimum(z, crater)

        # apply mass wasting
        z = waste(z, np.random.random()/5)

    return x, y, z
