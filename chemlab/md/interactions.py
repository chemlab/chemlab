from __future__ import print_function
import numba as nb
import numpy as np

from ..utils.numbaz import Int32HashTable
from .energy import lorentz_berthelot, F, tosi_fumi, tosi_fumi_B, tosi_fumi_beta


@nb.vectorize(['int32(uint8, uint8)',
               'int64(int64, int64)',
               'int32(int32, int32)'])
def modified_cantor_pair(a, b):
    # We need to ignore zeros otherwise zero-padding will result in weird shit
    if a == 0:
        return b
    if b == 0:
        return a
    else:
        return (a + b) * (a + b + 1) / 2 + b


def vectorized_hash(array):
    sz = array.dtype.itemsize
    # First we transform them in tuple of integers
    tuplez = array.view(np.uint8).reshape((-1, sz))

    # Then, we cantor-combine them so that every pair is unique
    # I love you, Cantor
    return modified_cantor_pair.reduce(tuplez, 1)


def _str_dict_to_htable(strdict):
    ht = Int32HashTable(64)

    for key in strdict:
        int_key = modified_cantor_pair.reduce([ord(c) for c in key])
        ht.push(int_key, strdict[key])

    return ht


@nb.jit(nopython=True)
def _dist(coords1, coords2):
    return ((coords1 - coords2) ** 2).sum() ** 0.5


@nb.jit(nopython=True)
def _coulomb_interaction(coords1, charges1, coords2, charges2):
    n = coords1.shape[0]
    m = coords2.shape[0]

    result = np.zeros(n)

    for i in range(n):
        for j in range(m):
            r_ij = _dist(coords1[i], coords2[j])
            # This is because we don't like self_interactions
            if r_ij < 1e-10:
                continue

            result[i] += charges1[i] * charges2[j] / r_ij

    return F * result


class Coulomb(object):

    def __init__(self, charges):
        self.charges = charges

        self._table = _str_dict_to_htable(charges)

    def interaction(self, coords1, types1, coords2, types2):
        coords1 = np.array(coords1, dtype='float64')
        coords2 = np.array(coords2, dtype='float64')

        # We basically hash the values
        types1_int = vectorized_hash(np.array(types1))
        types2_int = vectorized_hash(np.array(types2))

        charges1 = self._table.map(types1_int)
        charges2 = self._table.map(types2_int)

        return _coulomb_interaction(coords1, charges1, coords2, charges2)


def str_to_int(k):
    return modified_cantor_pair.reduce([ord(c) for c in k])


@nb.jit(nopython=True)
def _lennardjones_interaction(coords1, types1, coords2, types2, sigma_table, eps_table):
    n = coords1.shape[0]
    m = coords2.shape[0]

    result = np.zeros(n)

    for i in range(n):
        for j in range(m):
            r_ij = _dist(coords1[i], coords2[j])
            # This is because we don't like self_interactions
            if r_ij < 1e-10:
                continue

            sigma_ij = sigma_table.get(types1[i] + types2[j])
            eps_ij = eps_table.get(types1[i] + types2[j])
            c6 = (sigma_ij / r_ij) ** 6
            c12 = (sigma_ij / r_ij) ** 12

            result[i] += 4 * eps_ij * (c12 - c6)

    return result


@nb.jit(nopython=True)
def _tosifumi_interaction(coords1, types1, coords2, types2, B_table, C_table, D_table, alpha_table):
    n = coords1.shape[0]
    m = coords2.shape[0]

    result = np.zeros(n)

    for i in range(n):
        for j in range(m):
            r_ij = _dist(coords1[i], coords2[j])
            # This is because we don't like self_interactions
            if r_ij < 1e-10:
                continue

            B_ij = B_table.get(types1[i] + types2[j])
            C_ij = C_table.get(types1[i] + types2[j])
            D_ij = D_table.get(types1[i] + types2[j])
            alpha_ij = alpha_table.get(types1[i] + types2[j])

            result[i] += tosi_fumi(r_ij, B_ij, C_ij, D_ij, alpha_ij)

    return result


class LennardJones(object):

    def __init__(self, params):
        # We need to define an entry for each pairing
        sigma_table = Int32HashTable(1024)
        eps_table = Int32HashTable(1024)

        for k_i, v_i in params.items():
            for k_j, v_j in params.items():
                key = str_to_int(k_i) + str_to_int(k_j)
                sigma, eps = lorentz_berthelot(v_i['sigma'], v_j['sigma'],
                                               v_i['eps'], v_j['eps'])

                sigma_table.push(key, sigma)
                eps_table.push(key, eps)

        self._sigma_table = sigma_table
        self._eps_table = eps_table

    def interaction(self, coords1, types1, coords2, types2):
        coords1 = np.array(coords1, dtype='float64')
        coords2 = np.array(coords2, dtype='float64')

        # We basically hash the values
        types1_int = vectorized_hash(np.array(types1, dtype=np.str_))
        types2_int = vectorized_hash(np.array(types2, dtype=np.str_))

        return _lennardjones_interaction(coords1, types1_int, coords2, types2_int, self._sigma_table, self._eps_table)


class TosiFumi(object):

    def __init__(self, params):
        """A tosi-fumi parameter specification, for example:
        units = pint.UnitRegistry()
        c_unit = 1e-19 * units.joule * units.angstrom**6
        d_unit = 1e-19 * units.joule * units.angstrom**8

        "sigma" :  [0.816 * units.angstrom, 1.585 * units.angstrom],
        "q" : [1, -1],
        'valence': [2, 8],
        "C": [0.073 * c_unit, 2.0 * c_unit, 111.0 * c_unit],
        "D": [0.03 * d_unit, 2.4 * d_unit, 223.0 * d_unit],
        "b": 0.338e-12 * units.erg,
        "alpha" : 2.92 / units.angstrom

        """
        B_table = Int32HashTable(1024)
        C_table = Int32HashTable(1024)
        D_table = Int32HashTable(1024)
        alpha_table = Int32HashTable(1024)

        for k_pair, spec in params.items():
            # Here we need to develop the pair-parameters, there's
            # 3 combinations: ++ +- and --.
            for combination in range(3):
                i, j = {0: [0, 0], 1: [0, 1], 2: [1, 1]}[combination]

                # This is the pair we're handling now
                k_i, k_j = k_pair[i], k_pair[j]

                sigma = [spec['sigma'][i], spec['sigma'][j]]
                q = [spec['q'][i], spec['q'][j]]
                valence = [spec['valence'][i], spec['valence'][j]]

                B = tosi_fumi_B(tosi_fumi_beta(valence, q),
                                spec['b'],
                                sigma,
                                spec['alpha'])
                C = spec['C'][combination]
                D = spec['D'][combination]
                alpha = spec['alpha']

                key = str_to_int(k_i) + str_to_int(k_j)
                
                B_table.push(key, B)
                C_table.push(key, C)
                D_table.push(key, D)
                alpha_table.push(key, alpha)

        self._B_table = B_table
        self._C_table = C_table
        self._D_table = D_table
        self._alpha_table = alpha_table

    def interaction(self, coords1, types1, coords2, types2):
        coords1 = np.array(coords1, dtype='float64')
        coords2 = np.array(coords2, dtype='float64')

        # We basically hash the values
        types1_int = vectorized_hash(np.array(types1, dtype=np.str_))
        types2_int = vectorized_hash(np.array(types2, dtype=np.str_))

        return _tosifumi_interaction(coords1, types1_int, coords2, types2_int,
                                     self._B_table, self._C_table, self._D_table, self._alpha_table)
