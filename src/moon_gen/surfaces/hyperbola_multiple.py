import math
import numpy as np

from moon_gen.surfaces.hyperbola_parametric import make_crater, make_ejecta


def radius_probability(*, minimum: float = .1, maximum: float = 50) -> float:
    '''
    return a radius, roughly based on 
    LUNAR SURFACE MODELS, Marshall Space Center, p 21
    https://ntrs.nasa.gov/api/citations/19700009596/downloads/19700009596.pdf

    number of fresh craters greater than d per square meter : 
        n = 1/(5*d**2+1)
    thus, the probablility of a fresh crater having a diameter d or greater will be :
        p ~ 1/(5*d**2+1)
    turn this into an inverse CDF to generate a random number: 
        icdf(x) = sqrt((1-x)/(5y))
    '''
    x = np.random.random()
    return min(max(minimum, math.sqrt((1-x)/(50*x))), maximum)


def surface(n=150) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nx = ny = n
    size = 10
    step = 2*size/n

    # generate the initial flat terrain
    x = np.linspace(-size, size, nx)
    y = np.linspace(-size, size, ny)
    z = .005*np.random.random((nx, ny))

    nb_craters = np.random.random_integers(50, 100)
    print(f"generating {nb_craters} craters")

    for i in range(nb_craters):
        # center
        center = tuple(2*size*(np.random.random((2,))-.5))
        # scale
        radius = radius_probability()
        # elevation
        elevation = z[np.abs(x-center[0]) < step,
                      np.abs(y-center[1]) < step].mean()

        # apply ejecta to the ground
        ejecta = make_ejecta(x, y, center, radius, elevation)
        z = z + ejecta

        # dig the creater
        crater = make_crater(x, y, center, radius, elevation)
        z = np.minimum(z, crater)

    return x, y, z
