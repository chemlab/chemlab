from __future__ import print_function
import numpy as np
import math
import numba as nb
from numpy.linalg import norm
from .interactions import _dist, _str_dict_to_htable, vectorized_hash, F
from .energy import  tosi_fumi

@nb.jit
def reciprocal_vectors(box_vectors):
    a, b, c = box_vectors
    norm = a.dot(np.cross(b, c))
    u = 2 * np.pi * np.cross(b,c)/norm
    v = 2 * np.pi * np.cross(c,a)/norm
    w = 2 * np.pi * np.cross(a,b)/norm
    return np.array([u, v, w])

@nb.jit(nopython=False)
def _real(coords1, charges1, coords2, charges2, rcut, alpha, box):
    """Calculate ewald real part. Box has to be a cuboidal box you should
    transform any other box shape to a cuboidal box before using this.
    
    """
    n = coords1.shape[0]
    m = coords2.shape[0]
    # Unit vectors
    a = box[0]
    b = box[1]
    c = box[2]
    
    
    # This is helpful to add the correct number of boxes
    l_max = int(np.ceil(2.0 * rcut / np.min(np.trace(box))))
    result = np.zeros(n)
    
    
    for i in range(n):
        q_i = charges1[i]
        r_i = coords1[i]

        for j in range(m):
            q_j = charges2[j]
            r_j = coords2[j]

            for l_i in range(-l_max, l_max + 1):
                for l_j in range(-l_max, l_max + 1):
                    for l_k in range(-l_max, l_max + 1):
                        nv = l_i * a + l_j * b + l_k * c
                        r_j_n = r_j + nv
                        
                        r_ij = _dist(r_i, r_j_n)
                        if r_ij < 1e-10 or r_ij > rcut:
                            continue
                        value = q_i * q_j * math.erfc(alpha * r_ij) / r_ij
                        result[i] += value

    return result

@nb.jit(nopython=True)
def sqsum(r):
    return (r * r).sum()
import cmath

@nb.jit
def reciprocal_vectors(box):
    a, b, c = box
    
    const = 2.0 * np.pi
    k_a = const * np.cross(b, c) / np.dot(a, np.cross(b, c))
    k_b = const * np.cross(c, a) / np.dot(b, np.cross(c, a))
    k_c = const * np.cross(a, b) / np.dot(c, np.cross(a, b))
    return np.array([k_a, k_b, k_c])
    
@nb.jit
def box_volume(box):
    a, b, c = box
    return np.dot(a, np.cross(b, c))

@nb.jit
def _reciprocal(coords1, charges1, coords2, charges2, kmax, kappa, box):
    """Calculate ewald reciprocal part. Box has to be a cuboidal box you should
    transform any other box shape to a cuboidal box before using this.
    
    """
    n = coords1.shape[0]
    m = coords2.shape[0]
    result = np.zeros(n, dtype=np.float64)
    need_self = np.zeros(n, dtype=np.uint8)

    # Reciprocal unit vectors
    g1, g2, g3 = reciprocal_vectors(box)
    
    V = box_volume(box)
    
    prefac = 1.0 / (np.pi * V)
    for i in range(n):
        q_i = charges1[i]
        r_i = coords1[i]
        
        for j in range(m):
            q_j = charges2[j]
            r_j = coords2[j]
            
            r_ij = _dist(r_i, r_j)
            if r_ij < 1e-10:
                need_self[i] = 1
        
            for k_i in range(-kmax, kmax + 1):
                for k_j in range(-kmax, kmax + 1):
                    for k_k in range(-kmax, kmax + 1):
                        if k_i == 0 and k_j == 0 and k_k == 0:
                            continue
                        # Reciprocal vector
                        k = k_i * g1 + k_j * g2 + k_k * g3
                        
                        k_sq = sqsum(k)
                        
                        result[i] += (prefac * q_i * q_j *
                                      4.0 * np.pi ** 2 / k_sq *
                                      math.exp(-k_sq / (4.0 * kappa ** 2)) *
                                      math.cos(np.dot(k, r_i - r_j)))
        
    # Self-energy correction
    # I had to do some FUCKED UP stuff because NUMBA SUCKS BALLS and 
    # breaks compatibility with simple expressions such as that one
    # apparently doing result -= something is too hard in numba
    self_energy = 2 * (need_self * kappa * charges1 ** 2) / (np.pi**0.5)
    return result - self_energy


class Ewald(object):

    def __init__(self, charges, rcut, alpha=None, kmax=None):
        self._table = _str_dict_to_htable(charges)
        self.rcut = rcut
        self.alpha = alpha if alpha is not None else (5.0/rcut)**2
        self.kmax = kmax if kmax is not None else 7

    def _preproc(self, coords1, types1, coords2, types2, box):
        if box.shape not in [(3,), (3, 3)]:
            raise ValueError("Box shape should be (3,) or (3, 3)")
        
        coords1 = np.array(coords1, dtype='float64')
        coords2 = np.array(coords2, dtype='float64')

        if box.shape == (3,):
            box = np.diag(box).astype('float64')
        else:
            box = np.array(box, dtype='float64')

        # We basically hash the values
        types1_int = vectorized_hash(np.array(types1, dtype=np.str_))
        types2_int = vectorized_hash(np.array(types2, dtype=np.str_))

        charges1 = self._table.map(types1_int)
        charges2 = self._table.map(types2_int)
        return coords1, charges1, coords2, charges2, box

    def real(self, coords1, types1, coords2, types2, box):
        coords1, charges1, coords2, charges2, box = self._preproc(
            coords1, types1, coords2, types2, box)
        return F * _real(coords1, charges1, coords2, charges2, self.rcut, self.alpha, box)

    def reciprocal(self, coords1, types1, coords2, types2, box):
        coords1, charges1, coords2, charges2, box = self._preproc(
            coords1, types1, coords2, types2, box)
        
        return F * _reciprocal(coords1, charges1, coords2, charges2, self.kmax, self.alpha, box)

    def interaction(self, coords1, types1, coords2, types2, box):
        return self.real(coords2, types2, coords2, types2, box) + self.reciprocal(coords1, types1, coords2, types2, box)

    def dipole_correction(self, coords1, types1, box):
        types1_int = vectorized_hash(np.array(types1, np.str_))
        charges1 = self._table.map(types1_int)
        
        dipole = (coords1 * charges1[:, np.newaxis]).sum(axis=0)
        return F * 2 * np.pi / (3 * np.prod(box)) * (dipole * dipole).sum()
