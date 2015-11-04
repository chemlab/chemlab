import numpy as np
from nose.tools import ok_

def feq_(a, b, eps=1e-5):
    ok_(np.abs(a - b) < eps, '{} != {}'.format(a, b))

def npeq_(a, b):
    assert np.allclose(a, b), '\n{} != {}'.format(a, b)
    
def assert_npequal(a, b):
    assert np.array_equal(a, b), '\n{} != {}'.format(a, b)


def assert_eqbonds(a, b):
    # compare bonds by sorting
    a = np.sort(np.sort(a, axis=0))
    b = np.sort(np.sort(b, axis=0))
    assert_npequal(a, b)


def assert_allclose(a, b):
    assert np.allclose(a, b), '\n{} != {}'.format(a, b)
