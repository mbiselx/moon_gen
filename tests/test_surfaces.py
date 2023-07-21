
import os
import sys
import types
import importlib

import unittest

import numpy as np

import moon_gen.surfaces


def load_surface_submodules():
    '''load all the submodules in the `surfaces` module '''
    modules = []
    dirname = os.path.dirname(moon_gen.surfaces.__file__)

    for file in os.listdir(dirname):

        # remove files we don't care about
        if not file.endswith('.py') or file == '__init__.py':
            continue

        # get the name of this module
        modulename = moon_gen.surfaces.__name__ + \
            "." + file.removesuffix('.py')

        try:
            # try to reload the module if it exists
            module = importlib.reload(sys.modules[modulename])
        except KeyError:
            # otherwise load it for the first time
            module = importlib.import_module(modulename)

        modules.append(module)

    return modules


class Suppressor():
    '''
    suppress output to `stdout`
    https://stackoverflow.com/a/40054132/21688300 
    '''

    def __enter__(self):
        self.stdout = sys.stdout
        sys.stdout = self

    def __exit__(self, exception_type, value, traceback):
        sys.stdout = self.stdout
        if exception_type is not None:
            raise  # Do normal exception handling

    def write(self, x): pass

    def flush(self): pass


class TestSurfaces(unittest.TestCase):
    def __init__(self, surface_module: types.ModuleType) -> None:
        super().__init__()
        self.module = surface_module

    def runTest(self):
        '''test to make sure this submodule produces a valid surface'''

        self.surface_exists = hasattr(
            self.module, 'surface') and callable(self.module.surface)

        self.assertTrue(
            self.surface_exists,
            f"Module `{self.module.__name__}` is missing a `surface` method"
        )

        with Suppressor():
            X, Y, Z, *C = self.module.surface()

        self.assertIsInstance(
            X, np.ndarray, f"In {self.module.__name__} : X is expected to be a numpy array, not {type(X)}")
        self.assertIsInstance(
            Y, np.ndarray, f"In {self.module.__name__} : Y is expected to be a numpy array, not {type(Y)}")
        self.assertIsInstance(
            Z, np.ndarray, f"In {self.module.__name__} : Z is expected to be a numpy array, not {type(Z)}")

        self.assertEqual(
            X.shape[0], Z.shape[0], f"In {self.module.__name__} : Mismatch X and Z shapes for surface")
        self.assertEqual(
            Y.shape[0], Z.shape[1], f"In {self.module.__name__} : Mismatch Y and Z shapes for surface")


def suite():
    modules = load_surface_submodules()
    return unittest.TestSuite(TestSurfaces(m) for m in modules)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
