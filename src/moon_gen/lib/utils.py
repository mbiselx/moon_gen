'''
UTILS:PY

This sub-module contains the geneally uesfuly type definitions
and utility functions for the rest of the project
'''

from typing import Union, Callable

import numpy as np
from numpy.typing import NDArray

SurfaceType = Union[
    tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]],
    tuple[NDArray[np.float64], NDArray[np.float64],
          NDArray[np.float64], NDArray],
]
'''
a surface defined either as
    (`X`, `Y`, `Z`)
or
    (`X`, `Y`, `Z`, `C`)
where `X` and `Y` are one-dimensional arrays, and `Z` and `C` are
two-dimensional arrays
'''

SurfaceFunctionType = Callable[[], SurfaceType]
'''
The expected type of a surface-generating function.
It is expected to optionally take an integer `size` argument, which will
specify the size or resolution of the resulting surface.
Sadly, I can't figure out how to typehint this...
'''
