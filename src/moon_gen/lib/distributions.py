'''
DISTRIBUTIONS:PY

This sub-module contains the probabilites and distributions to draw from
for the different surface generators.
'''

import math
import random

# The following two ratio values are taken from
# LUNAR SURFACE MODELS, Marshall Space Center, p 16
# https://ntrs.nasa.gov/api/citations/19700009596/downloads/19700009596.pdf

DDR = 0.23  # fresh crater : 0.23 - 0.25
'''depth-to-diameter ratio'''
# HDR = 0.06  # fresh crater : 0.022 - 0.06
HDR = 0.075  # for aesthetics -- less looks bad ???
'''height-to-diameter ratio'''


def radius_probability(*, minimum: float = .1, maximum: float = 50) -> float:
    '''
    return a radius, roughly based on
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
    x = random.random()
    return min(max(minimum, math.sqrt((1-x)/(50*x))), maximum)


def surface_psd_nominal(f: float) -> float:
    '''
    return a surface Power Spectral Density value for a given frequency,
    roughly based on LUNAR SURFACE MODELS, Marshall Space Center, p 20
    https://ntrs.nasa.gov/api/citations/19700009596/downloads/19700009596.pdf

    (meters**2/cycles/meter) -> (cycles/meter)
    '''
    return 3 / (2e5 * f**3.35 + 1)


def surface_psd_rough(f: float) -> float:
    '''
    return a surface Power Spectral Density value for a given frequency,
    roughly based on LUNAR SURFACE MODELS, Marshall Space Center, p 20
    https://ntrs.nasa.gov/api/citations/19700009596/downloads/19700009596.pdf

    (meters**2/cycles/meter) -> (cycles/meter)
    '''
    return 4 / (8e4 * f**3 + 1) + 1/(3e3 * f**2 + 50)
