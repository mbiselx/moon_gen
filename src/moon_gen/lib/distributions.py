'''
DISTRIBUTIONS:PY

This sub-module contains the probabilites and distributions to draw from
for the different surface generators.
'''

import random
import typing

import numpy as np
from numpy.typing import NDArray

# The following two ratio values are taken from
# LUNAR SURFACE MODELS, Marshall Space Center, p 16
# https://ntrs.nasa.gov/api/citations/19700009596/downloads/19700009596.pdf

DDR = 0.23  # fresh crater : 0.23 - 0.25
'''depth-to-diameter ratio'''
# HDR = 0.06  # fresh crater : 0.022 - 0.06
HDR = 0.075  # for aesthetics -- less looks bad ???
'''height-to-diameter ratio'''


@typing.overload
def radius_probability(
    x: float, *,
    minimum: float = .1,
    maximum: float = 50
) -> float:
    ...


@typing.overload
def radius_probability(
    x: NDArray[np.float_], *,
    minimum: float = .1,
    maximum: float = 50
) -> NDArray[np.float_]:
    ...


def radius_probability(x, *, minimum: float = .1, maximum: float = 50):
    '''
    for a number between [0 - 1], return a radius, roughly based on
    LUNAR SURFACE MODELS, Marshall Space Center, p 21
    https://ntrs.nasa.gov/api/citations/19700009596/downloads/19700009596.pdf

    number of fresh craters greater than d per square meter :
        n = 1/(5*d**2+1)
    thus, the probablility of a fresh crater having a diameter d or greater
    will be :
        p ~ 1/(5*d**2+1)
    turn this into an inverse CDF to generate a random number:
        icdf(x) = sqrt((1-x)/(5y))
    '''
    return np.clip(np.sqrt((1-x)/(50*x)), minimum, maximum)


def random_radius(*, minimum: float = .1, maximum: float = 50) -> float:
    '''return a radius using the function `radius_probability`'''

    return radius_probability(
        random.random(),
        minimum=minimum,
        maximum=maximum
    )


@typing.overload
def surface_psd_smooth(f: float) -> float:
    ...


@typing.overload
def surface_psd_smooth(f: NDArray[np.float_]) -> NDArray[np.float_]:
    ...


def surface_psd_smooth(f):
    '''
    return a surface Power Spectral Density value for a given frequency,
    roughly based on LUNAR SURFACE MODELS, Marshall Space Center, p 20
    https://ntrs.nasa.gov/api/citations/19700009596/downloads/19700009596.pdf

    (meters**2/cycles/meter) -> (cycles/meter)
    '''
    return 5 / (2e6 * f**3.35 + 10)


@typing.overload
def surface_psd_nominal(f: float) -> float:
    ...


@typing.overload
def surface_psd_nominal(f: NDArray[np.float_]) -> NDArray[np.float_]:
    ...


def surface_psd_nominal(f):
    '''
    return a surface Power Spectral Density value for a given frequency,
    roughly based on LUNAR SURFACE MODELS, Marshall Space Center, p 20
    https://ntrs.nasa.gov/api/citations/19700009596/downloads/19700009596.pdf

    (meters**2/cycles/meter) -> (cycles/meter)
    '''
    return 2.5 / (2e5 * f**3.35 + 1)


@typing.overload
def surface_psd_rough(f: float) -> float:
    ...


@typing.overload
def surface_psd_rough(f: NDArray[np.float_]) -> NDArray[np.float_]:
    ...


def surface_psd_rough(f):
    '''
    return a surface Power Spectral Density value for a given frequency,
    roughly based on LUNAR SURFACE MODELS, Marshall Space Center, p 20
    https://ntrs.nasa.gov/api/citations/19700009596/downloads/19700009596.pdf

    (meters**2/cycles/meter) -> (cycles/meter)
    '''
    return 4 / (8e4 * f**3 + 1) + 1/(3e3 * f**2 + 50)


@typing.overload
def cash(x_coord: int, y_coord: int, seed: int = 0) -> int:
    ...


@typing.overload
def cash(x_coord: NDArray[np.int64], y_coord: NDArray[np.int64],
         seed: int = 0) -> NDArray[np.int64]:
    ...


def cash(x_coord, y_coord, seed: int = 0):
    '''
    cash stands for chaos hash :D

    It's not really a hash, but it's perfect for what i'm doing
    https://stackoverflow.com/a/37221804/21688300
    '''
    h = seed + x_coord*374761393 + y_coord*668265263  # all constants are prime
    h = (h ^ (h >> 13))*1274126177
    return (h ^ (h >> 16))


@typing.overload
def cash_norm(x_coord: int, y_coord: int, seed: int = 0) -> float:
    ...


@typing.overload
def cash_norm(x_coord: NDArray[np.int64], y_coord: NDArray[np.int64],
              seed: int = 0) -> NDArray[np.float64]:
    ...


def cash_norm(x_coord, y_coord, seed: int = 0):
    '''return the output of `cash`, normalized to a range of [0 - 1)'''
    # return (np.cos(cash(x_coord, y_coord, seed=seed)) + 1.)*0.5
    return (cash(x_coord, y_coord, seed=seed)) / 2**63


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    f = np.logspace(-2, 1)

    fig, ax = plt.subplots()
    ax.loglog(f, surface_psd_rough(f), 'k-', label="rough mare")
    ax.loglog(f, surface_psd_nominal(f), 'k--', label="rough upland")
    ax.loglog(f, surface_psd_smooth(f), 'k-.', label="smooth mare")
    ax.set_xlim(1e-2, 1e2)
    ax.set_xlabel("Frequency [cycles/meter]")
    ax.set_ylim(1e-4, 1e1)
    ax.set_ylabel("PSD [meters$^2$/cycles/meter]")
    ax.set_title("Surface roughness PSD")
    ax.legend()

    plt.show()
