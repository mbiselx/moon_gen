'''
CRATERS:PY

This submodule contains functions useful for generating graters on
a surface
'''

import numpy as np
from numpy.typing import NDArray

from scipy.ndimage import gaussian_filter

from moon_gen.lib.distributions import (  # noqa: F401
    HDR, DDR,
    crater_density_fresh, crater_density_young,
    crater_density_mature, crater_density_old,
    cash, cash_norm
    )


def crater_2D(
        r: NDArray[np.float_],
        center: float,
        radius: float,
        elevation: float | NDArray[np.float_]
) -> NDArray[np.float_]:
    '''the radial shape of an ideal crater'''
    r_square = (r-center)**2

    # figure out the bowl shape
    if isinstance(elevation, np.ndarray):
        avg_elevation = (elevation[r_square < radius**2]).mean()
    else:
        avg_elevation = elevation
    z_bowl = avg_elevation + 2*radius*(HDR-DDR) + 2*DDR/radius * r_square

    # figure out ejecta shape
    z_ejecta = 2*HDR*radius * \
        (2**(radius**2/np.maximum(r_square, radius**2)) - 1)
    z_ejecta += elevation + np.random.normal(scale=0.1*z_ejecta)

    return np.minimum(z_bowl, z_ejecta)


def make_crater(
        x: NDArray[np.float_],
        y: NDArray[np.float_],
        z: NDArray[np.float_],
        radius: float,
        center: tuple[float, float]
) -> NDArray[np.float_]:
    '''
    make a crater in the given `z` surface.
    '''
    # center r
    r = np.sqrt((x-center[0]).reshape((len(x), 1))**2 +
                (y-center[1]).reshape((1, len(y)))**2)
    # use circular symmetry and numpy magic
    z = crater_2D(r, 0, radius, z)
    return z


def waste_gaussian(
    z: NDArray,
    resolution: float,
    duration: float = 1
) -> NDArray:
    '''simulate mass wasting between impacts, using gaussian blur.'''
    gz = gaussian_filter(z, sigma=duration/resolution)
    return gz
    # w = min(1, max(0, duration+.5))
    # return w*gz + (1-w)*z  # type: ignore


def make_procedural_craters(
        x: NDArray[np.float_],
        y: NDArray[np.float_],
        z: NDArray[np.float_],
        thresh: float = .999
) -> NDArray[np.float_]:
    # create a grid based on the millimeter point location
    xx, yy = np.meshgrid(x, y, indexing='ij')
    chaos_grid = cash(
        (1000*xx).astype(np.int64),
        (1000*yy).astype(np.int64),
        1234567890
    )

    # sanity check
    assert z.shape == chaos_grid.shape

    # the areas greater than thresh will have a crater center.
    # NOTE: `np.nonzero returns row, column index`
    row_idx, col_idx = np.nonzero(chaos_grid > thresh*(2**63))

    # the age of the crater will be calculated from the chaos value
    ages = chaos_grid[row_idx, col_idx].argsort()

    cxs, cys = x[row_idx[ages]], y[col_idx[ages]]
    radii = crater_density_young.diameter(
        cash_norm(
            cxs.astype(np.int64),
            cys.astype(np.int64)
        )
    )

    # apply craters in order of appearance : oldest first
    print(f"generating {len(radii)} craters")
    for radius, cx, cy in zip(radii, cxs, cys):
        z = make_crater(x, y, z, radius, (cx, cy))

    return z


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    r = np.linspace(-3, 3, 101)

    original_terrain = np.random.normal(scale=0.01, size=r.shape)
    fresh_crater = crater_2D(r, 0, 1, original_terrain)

    weathering_parameter = (0.15, 0.33, 0.66, 1)
    old_craters = [waste_gaussian(fresh_crater, r.ptp()/len(r), wp)
                   for wp in weathering_parameter]

    fig, ax = plt.subplots()
    t = ax.plot(r, original_terrain, 'k--', label="original terrain")
    c = []
    for wp, z in zip(weathering_parameter, old_craters):
        c += ax.plot(r, z, color="teal", alpha=0.75*(1-wp)+.25,
                     label=f"weathered crater ({wp=:.2f} radii)")
    f = ax.plot(r, fresh_crater, color="red", label="freshly cratered terrain")
    ax.grid(True)
    ax.axis('equal')
    ax.set_xlabel("radial distance $r$ [radii]")
    ax.set_ylabel("elevation $z$ [radii]")
    ax.legend(handles=t + f + c)
    ax.set_title("idealized simple crater profile")

    fig.tight_layout()

    plt.show()
