"""\
  pgbf.py Perform basic operations over primitive
    gaussian basis functions. The equations herein are based upon
    'Gaussian Expansion Methods for Molecular Orbitals.' H. Taketa,
    S. Huzinaga, and K. O-ohata. H. Phys. Soc. Japan, 21, 2313, 1966.
    [THO paper].

  For the purposes of this routine, a gaussian is defined as:

    g(x,y,z) = A*(x^i)*(y^j)*(z^k)*exp{-a*(r-ro)^2}

 This program is part of the PyQuante quantum chemistry program suite.

"""

import numpy as np

def fact2(n):
    """
    fact2(n) - n!!, double factorial of n
    >>> fact2(0)
    1
    >>> fact2(1)
    1
    >>> fact2(3)
    3
    >>> fact2(8)
    384
    >>> fact2(-1)
    1
    """
    return reduce(int.__mul__,range(n,0,-2),1)

def norm2(a): return np.dot(a,a)


class pgbf(object):
    """
    Construct a primitive gaussian basis functions.
    >>> s = pgbf(1.0)
    >>> np.isclose(s(0,0,0),0.712705)
    True
    >>> px = pgbf(1.0,powers=(1,0,0))
    >>> np.isclose(px(0,0,0),0.0)
    True
    """
    contracted = False
    def __init__(self,exponent,origin=(0,0,0),powers=(0,0,0)):
        self.norm = 1
        assert len(origin) == 3
        assert len(powers) == 3
        self.exponent = float(exponent)
        self.origin = np.array(origin,'d')
        self.powers = powers
        self._normalize()

    def __repr__(self): return "pgbf(%f,%s,%s)" % (self.exponent,tuple(self.origin),self.powers)

    def __call__(self,x,y,z):
        "Compute the amplitude of the PGBF at point x,y,z"
        I,J,K = self.powers
        dx,dy,dz = x-self.origin[0],y-self.origin[1],z-self.origin[2]
        d2 = dx**2 + dy**2 + dz**2
        return self.norm*dx**I*dy**J*dz**K*np.exp(-self.exponent*d2)

    def mesh(self,xyzs):
        """
        Evaluate basis function on a mesh of points *xyz*.
        """
        I,J,K = self.powers
        d = np.asarray(xyzs,'d')-self.origin
        # Got help from stackoverflow user @unutbu with this.
        # See: http://stackoverflow.com/questions/17391052/compute-square-distances-from-numpy-array
        d2 = np.einsum('ij,ij -> i',d,d)
        return self.norm*d[:,0]**I*d[:,1]**J*d[:,2]**K*np.exp(-self.exponent*d2)

    def _normalize(self):
        "Normalize basis function. From THO eq. 2.2"
        l,m,n = self.powers
        self.norm = np.sqrt(pow(2,2*(l+m+n)+1.5)*
                            pow(self.exponent,l+m+n+1.5)/
                            fact2(2*l-1)/fact2(2*m-1)/
                            fact2(2*n-1)/pow(np.pi,1.5))
        return

if __name__ == '__main__':
    import doctest
    doctest.testmod()
