#!/usr/bin/env python
'''
A file defining a test surface
'''
import numpy as np


def surface(*args) -> tuple[np.ndarray, np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x = np.linspace(-8, 8, 50)
    y = np.linspace(-8, 8, 50)
    z = 0.1 * ((x.reshape(50, 1) ** 2) - (y.reshape(1, 50) ** 2))

    return x, y, z
