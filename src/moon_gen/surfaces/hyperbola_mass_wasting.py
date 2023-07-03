import numpy as np
from scipy.ndimage import gaussian_filter

from moon_gen.surfaces.hyperbola_multiple import radius_probability, make_crater


def waste(z: np.ndarray, duration: float) -> np.ndarray:
    '''simulate mass wasting between impacts.'''
    return 0.5*(z+gaussian_filter(z, sigma=5*duration))


def surface(n=513) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nx = ny = n
    size = 10

    # generate the initial flat terrain
    x = np.linspace(-size, size, nx)
    y = np.linspace(-size, size, ny)
    z = np.random.normal(scale=0.05, size=(nx, ny))

    nb_craters = np.random.random_integers(10, 50)
    print(f"generating {nb_craters} craters")

    for i in range(nb_craters):
        # make the crater
        z = make_crater(x, y, z)
        # apply mass wasting
        z = waste(z, np.random.random()/5)

    # finally, apply micro-meteorite impacts
    z += np.random.normal(scale=0.001, size=z.shape)

    return x, y, z
