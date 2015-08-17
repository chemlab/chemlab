import numpy as np

def assert_npequal(a, b):
    assert np.array_equal(a, b), '\n{} != {}'.format(a, b)


def assert_eqbonds(a, b):
    # compare bonds by sorting
    a = np.sort(np.sort(a, axis=0))
    b = np.sort(np.sort(b, axis=0))
    assert_npequal(a, b)


def assert_allclose(a, b):
    assert np.allclose(a, b), '\n{} != {}'.format(a, b)
