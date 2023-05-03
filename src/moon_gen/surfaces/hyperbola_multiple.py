import numpy as np

from moon_gen.surfaces.hyperbola_generator import make_crater, make_ejecta


def scale_probability() -> float:
    '''return a scale'''
    # return np.random.random()*99/100 + .01
    return 1/np.exp(15*np.random.random()) + .05
    # return 1/4


def surface(n=150) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nx = ny = n
    size = 10
    step = 2*size/n

    # generate the initial flat terrain
    x = np.linspace(-size, size, nx)
    y = np.linspace(-size, size, ny)
    z = .005*np.random.random((nx, ny))

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

    return x, y, z
