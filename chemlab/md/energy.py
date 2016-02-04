'''
Calculate potential energy terms
'''

# Electric conversion factor
F = 138.935485

def lennard_jones(sigma, eps, distance):
    A = (sigma/distance)**12
    B = (sigma/distance)**6
    return 4.0 * eps * (A - B)


def electrostatic(q1, q2, distance):
    return F * q1 * q2 / distance


def lorentz_berthelot(sigma1, sigma2, eps1, eps2):
    return (sigma1 + sigma2)/2, (eps1*eps2)**0.5

def half_rmin_to_sigma(half_rmin, unit='ang'):
    if not unit in ('ang', 'nm'):
        raise ValueError('unsupported unit')
    
    if unit == 'ang':
        half_rmin /= 10
    
    return 2**(5.0/6.0) * (half_rmin)

def kcal_to_kj(kcal):
    return 4.184 * kcal
