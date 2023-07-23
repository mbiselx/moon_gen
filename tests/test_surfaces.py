
import os
import sys
import types
import importlib

import pytest

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


@pytest.mark.parametrize("module", load_surface_submodules())
def test_suface_module(module: types.ModuleType):
    assert hasattr(module, 'surface'), 'missing a `surface` method'
    assert callable(module.surface), 'missing a `surface` method'

    # silently create the surface
    with Suppressor():
        X, Y, Z, *C = module.surface()

    assert isinstance(X, np.ndarray), "X is expected to be a numpy array"
    assert isinstance(Y, np.ndarray), "Y is expected to be a numpy array"
    assert isinstance(Z, np.ndarray), "Z is expected to be a numpy array"

    assert X.shape[0] == Z.shape[0], "Mismatch X and Z shapes for surface"
    assert Y.shape[0] == Z.shape[1], "Mismatch Y and Z shapes for surface"


if __name__ == "__main__":
    exit(pytest.main())
