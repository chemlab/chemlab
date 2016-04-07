import numba as nb
import numpy as np

from ..utils.numbaz import Int32HashTable
from .energy import lorentz_berthelot, F

@nb.vectorize(['int32(uint8, uint8)',
               'int64(int64, int64)',
               'int32(int32, int32)'])
def cantor_pair(a, b):
    return (a + b) * (a + b + 1) / 2 + b


def vectorized_hash(array):
    sz = array.dtype.itemsize
    # First we transform them in tuple of integers
    tuplez = array.view(np.uint8).reshape((-1, sz))
    # Then, we cantor-combine them so that every pair is unique
    # I love you, Cantor
    return cantor_pair.reduce(tuplez, 1)


def _str_dict_to_htable(strdict):
    ht = Int32HashTable(64)

    for key in strdict:
        int_key = cantor_pair.reduce([ord(c) for c in key])
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
    return cantor_pair.reduce([ord(c) for c in k])

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
            eps_ij = sigma_table.get(types1[i] + types2[j])
            
            c6 = (sigma_ij / r_ij)**6
            c12 = c6**2
            
            result[i] += 4.0 * eps_ij * (c12 - c6)
            

    return result    

class LennardJones(object):
    
    def __init__(self, params):
        # We need to define an entry for each pairing
        sigma_table = Int32HashTable(64)
        eps_table = Int32HashTable(64)
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
        types1_int = vectorized_hash(np.array(types1))
        types2_int = vectorized_hash(np.array(types2))

        return _lennardjones_interaction(coords1, types1_int, coords2, types2_int, self._sigma_table, self._eps_table)
