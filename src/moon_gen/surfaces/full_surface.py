import numpy as np

from moon_gen.surfaces.hyperbola_mass_wasting import make_crater, waste
from moon_gen.surfaces.perlin_mulitscale import perlin_multiscale_grid, surface_psd_rough


def surface(n=513) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nx = ny = n
    ax = ay = n/20
    cx, cy = 100*np.random.random((2,))
    x = np.linspace(-ax/2, ax/2, nx)
    y = np.linspace(-ay/2, ay/2, ny)

    print("generating background")
    z = perlin_multiscale_grid(x+cx, y+cy, psd=surface_psd_rough, octaves=10)

    nb_craters = 40 + np.random.randint(10, 50)
    print(f"generating {nb_craters} craters")

    for i in reversed(range(4)):
        for _ in range(nb_craters//4):
            z = make_crater(x, y, z)
        z = waste(z, i/10 + np.random.random()/5)

    print("done")

    return x, y, z
