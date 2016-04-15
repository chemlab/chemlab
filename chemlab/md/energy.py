'''
Calculate potential energy terms under different potentials
'''
import numpy as np
import numba as nb
# Electric conversion factor
F = 138.935485


def lennard_jones(sigma, eps, distance):
    A = (sigma / distance) ** 12
    B = (sigma / distance) ** 6
    return 4.0 * eps * (A - B)


def electrostatic(q1, q2, distance):
    return F * q1 * q2 / distance


def tosi_fumi_beta(valence, q):
    return 1 + float(q[0]) / valence[0] + float(q[1]) / valence[1]


def tosi_fumi_B(beta, b, sigma, alpha):
    return beta * b * np.exp((sigma[0] + sigma[1]) * alpha)


@nb.jit
def tosi_fumi_repulsive(r, B, alpha):
    return B * np.exp(- alpha * r)

@nb.jit
def tosi_fumi(r, B, C, D, alpha):
    return tosi_fumi_repulsive(r, B, alpha) - C / r ** 6 - D / r ** 8


def lorentz_berthelot(sigma1, sigma2, eps1, eps2):
    return (sigma1 + sigma2) / 2, (eps1 * eps2) ** 0.5


def half_rmin_to_sigma(half_rmin, unit='ang'):
    if not unit in ('ang', 'nm'):
        raise ValueError('unsupported unit')

    if unit == 'ang':
        half_rmin /= 10

    return 2 ** (5.0 / 6.0) * (half_rmin)


def kcal_to_kj(kcal):
    return 4.184 * kcal
