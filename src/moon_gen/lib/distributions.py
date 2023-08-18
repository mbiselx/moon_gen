'''
DISTRIBUTIONS:PY

This sub-module contains the probabilites and distributions to draw from
for the different surface generators.
'''

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


class PowerDistribution:
    '''
    roughly based on LUNAR SURFACE MODELS, Marshall Space Center, p 21
    https://ntrs.nasa.gov/api/citations/19700009596/downloads/19700009596.pdf
    '''

    def __init__(self, intercept: float, power: float = -2.,
                 d_min: float = 0.1) -> None:
        '''
        Args:
        * intercept : the intercept of the x=1 axis in the cumulative
                        distribution chart
        * power :     the power of the distribution
        * d_min :     the minimum admissible diameter
        '''
        self.intercept = intercept
        self.power = power
        self._d_min = d_min
        self.d_min = d_min

    @property
    def d_min(self):
        return self._d_min

    @d_min.setter
    def d_min(self, value: float):
        self._d_min = value
        self._cdf = self.cdf(value)

    @typing.overload
    def cdf(self, d_min: float) -> float:
        ...

    @typing.overload
    def cdf(self, d_min: NDArray) -> NDArray:
        ...

    def cdf(self, d_min):
        return self.intercept * d_min**self.power

    @typing.overload
    def icdf(self, n: float) -> float:
        ...

    def number(self, x: NDArray, y: NDArray) -> int:
        '''
        number of items greater than d_min in a given area, based on cdf
        '''
        return int((x.ptp() * y.ptp()) * self._cdf)

    @typing.overload
    def icdf(self, n: NDArray) -> NDArray:
        ...

    def icdf(self, n):
        return (n/self.intercept)**(1/self.power)

    @typing.overload
    def diameter(self, u: float) -> float:
        ...

    @typing.overload
    def diameter(self, u: NDArray) -> NDArray:
        ...

    def diameter(self, u):
        '''
        a diameter, based on the input u, which is between 0 and 1; and the cdf
        '''
        return self.icdf(u*self._cdf)


crater_density_fresh = PowerDistribution(2e-3, -2.)
crater_density_young = PowerDistribution(2e-2, -2.)
crater_density_mature = PowerDistribution(1e-1, -2.)
crater_density_old = PowerDistribution(2e-1, -2.)


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

    # fig1, ax1 = plt.subplots()
    # f = np.logspace(-2, 1)
    # ax1.loglog(f, surface_psd_rough(f), 'k-', label="rough mare")
    # ax1.loglog(f, surface_psd_nominal(f), 'k--', label="rough upland")
    # ax1.loglog(f, surface_psd_smooth(f), 'k-.', label="smooth mare")
    # ax1.set_xlim(1e-2, 1e2)
    # ax1.set_xlabel("Frequency [cycles/meter]")
    # ax1.set_ylim(1e-4, 1e1)
    # ax1.set_ylabel("PSD [meters$^2$/cycles/meter]")
    # ax1.set_title("Surface roughness PSD")
    # ax1.legend()

    fig2, ax2 = plt.subplots()
    d = np.logspace(0, 3)
    ax2.loglog(d, crater_density_fresh.cdf(d), 'k-',
               label="fresh (97% original relief)")
    ax2.loglog(d, crater_density_young.cdf(d), 'k--',
               label="young (75% original relief)")
    ax2.loglog(d, crater_density_mature.cdf(d), 'k-.',
               label="mature (50% original relief)")
    ax2.loglog(d, crater_density_old.cdf(d), 'k:',
               label="old (0% original relief)")
    ax2.set_xlim(1, 1e3)
    ax2.set_xlabel("Crater Diameter [meter]")
    ax2.set_ylim(1e-7, 1e-2)
    ax2.set_ylabel("cumulative density [number/meter**2]")
    ax2.set_title("Cumulative frequency and relief of craters")
    ax2.legend()
    ax2.grid(True, 'both')

    plt.show()
