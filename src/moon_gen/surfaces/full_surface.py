import numpy as np

from moon_gen.surfaces.hyperbola_mass_wasting import make_crater, waste
from moon_gen.surfaces.perlin_mulitscale import perlin_multiscale_grid


def surface(n=513) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nx = ny = n
    ax = ay = n/20
    cx, cy = 100*np.random.random((2,))
    x = np.linspace(-ax/2, ax/2, nx)
    y = np.linspace(-ay/2, ay/2, ny)

    print("generating background")
    z = perlin_multiscale_grid(x+cx, y+cy, [4, 2, 1, .5, .25, .125, 0, 0])

    nb_craters = 40 + np.random.random_integers(10, 50)
    print(f"generating {nb_craters} craters")
    for i in range(nb_craters//2):
        z = make_crater(x, y, z)
    z = waste(z, 0.1 + np.random.random()/5)
    for i in range(nb_craters//2):
        z = make_crater(x, y, z)
    z = waste(z, np.random.random()/5)

    print("done")

    return x, y, z
