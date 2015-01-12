"""\
 cgbf.py Perform basic operations over contracted gaussian basis
  functions. Uses the functions in pgbf.py.

 References:
  OHT = K. O-ohata, H. Taketa, S. Huzinaga. J. Phys. Soc. Jap. 21, 2306 (1966).
  THO = Taketa, Huzinaga, O-ohata, J. Phys. Soc. Jap. 21,2313 (1966).

 This program is part of the PyQuante quantum chemistry program suite
"""

import numpy as np
import array

from .pgbf import pgbf
from .one import S

class cgbf(object):
    """
    Class for a contracted Gaussian basis function
    >>> s = cgbf(exps=[1],coefs=[1])
    >>> print(s)
    cgbf((0.0, 0.0, 0.0),(0, 0, 0),[1.0],[1.0000000000000002])
    >>> np.isclose(s(0,0,0),0.712705)
    True
    """
    contracted = True
    def __init__(self,origin=(0,0,0),powers=(0,0,0),exps=[],coefs=[]):
        assert len(origin)==3
        assert len(powers)==3

        self.origin = np.asarray(origin,'d')
        self.powers = powers

        self.pgbfs = []
        self.coefs = array.array('d')
        self.pnorms = array.array('d')
        self.pexps = array.array('d')

        for expn,coef in zip(exps,coefs):
            self.add_pgbf(expn,coef,False)

        if self.pgbfs:
            self.normalize()
        return

    def __getitem__(self,item): return list(zip(self.coefs,self.pgbfs)).__getitem__(item)
    def __call__(self,*args,**kwargs): return sum(c*p(*args,**kwargs) for c,p in self)
    def __repr__(self): return "cgbf(%s,%s,%s,%s)" % (tuple(self.origin),self.powers,list(self.pexps),list(self.coefs))

    def mesh(self,xyzs):
        """
        Evaluate basis function on a mesh of points *xyz*.
        """
        return sum(c*p.mesh(xyzs) for c,p in self)

    def cne_list(self):
        return self.coefs,self.pnorms,self.pexps

    def add_pgbf(self,expn,coef,renormalize=True):

        self.pgbfs.append(pgbf(expn,self.origin,self.powers))
        self.coefs.append(coef)
        
        if renormalize:
            self.normalize()

        p = self.pgbfs[-1]
        self.pnorms.append(p.norm)
        self.pexps.append(p.exponent)
        return

    def normalize(self):
        
        from numpy import sqrt
        Saa = S(self,self)
        Saa_sqrt = sqrt(Saa)
        
        for i in range(len(self.coefs)):
            self.coefs[i] /= Saa_sqrt
        # Is this the right way to do this, or should I have a separate normalization constant?
        return

def sto(zeta,N=1,L=0,M=0,origin=(0,0,0)):
    """
    Use Stewarts STO-6G fits to create a contracted Gaussian approximation to a
    Slater function. Fits of other expansion lengths (1G, 3G, etc) are in the paper.

    Reference: RF Stewart, JCP 52, 431 (1970)

    >>> s = sto(1)
    >>> np.isclose(s(0,0,0),0.530121)
    True
    """
    nlm2powers = {
        (1,0,0) : (0,0,0,0),   # x,y,z,r
        (2,0,0) : (0,0,0,1),
        (3,0,0) : (0,0,0,2),
        (2,1,0) : (1,0,0,0),
        (2,1,1) : (0,1,0,0),
        (2,1,-1) : (0,0,1,0),
        (3,1,0) : (1,0,0,1),
        (3,1,1) : (0,1,0,1),
        (3,1,-1) : (0,0,1,1)
        }

    gexps_1s = [2.310303149e01,4.235915534e00,1.185056519e00,
                4.070988982e-01,1.580884151e-01,6.510953954e-02]
    gcoefs_1s = [9.163596280e-03,4.936149294e-02,1.685383049e-01,
                 3.705627997e-01,4.164915298e-01,1.303340841e-01]
    
    gexps_2s = [2.768496241e01,5.077140627e00,1.426786050e00,
                2.040335729e-01,9.260298399e-02,4.416183978e-02]
    gcoefs_2s = [-4.151277819e-03,-2.067024148e-02,-5.150303337e-02,
                 3.346271174e-01,5.621061301e-01,1.712994697e-01]
    
    gexps_2p = [5.868285913e00,1.530329631e00,5.475665231e-01,
                2.288932733e-01,1.046655969e-01,4.948220127e-02]
    gcoefs_2p = [7.924233646e-03,5.144104825e-02,1.898400060e-01,
                 4.049863191e-01,4.012362861e-01,1.051855189e-01]
    
    gexps_3s = [3.273031938e00,9.200611311e-01,3.593349765e-01,
                8.636686991e-02,4.797373812e-02,2.724741144e-02]
    gcoefs_3s = [-6.775596947e-03,-5.639325779e-02,-1.587856086e-01,
                 5.534527651e-01,5.015351020e-01,7.223633674e-02]
    
    gexps_3p = [5.077973607e00,1.340786940e00,2.248434849e-01,
                1.131741848e-01,6.076408893e-02,3.315424265e-02]
    gcoefs_3p = [-3.329929840e-03,-1.419488340e-02,1.639395770e-01,
                 4.485358256e-01,3.908813050e-01,7.411456232e-02]
    gexps_3d = [2.488296923,7.981487853e-1,3.311327490e-1,
                1.559114463e-1,7.877734732e-2,4.058484363e-2]
    gcoefs_3d = [7.283828112e-3,5.386799363e-2,2.072139149e-1,
                 4.266269092e-1,3.843100204e-1,8.902827546e-2]
    
    gexps_4s = [3.232838646,3.605788802e-1,1.717902487e-1,
                5.277666487e-2,3.163400284e-2,1.874093091e-2]
    gcoefs_4s = [1.374817488e-3,-8.666390043e-2,-3.130627309e-1,
                 7.812787397e-1,4.389247988-1,2.487178756e-2]
    gexps_4p = [2.389722618, 7.960947826e-1,3.415541380e-1,
                8.847434525e-2,4.958248334e-2,2.816929784e-2]
    gcoefs_4p = [-1.665913575e-3,-1.657464971e-2,-5.958513378e-2,
                 4.053115554e-1,5.433958189e-1,1.20970491e-1]
    
    gexps = { # indexed by N,s_or_p:
        (1,0) : gexps_1s,
        (2,0) : gexps_2s,
        (2,1) : gexps_2p,
        (3,0) : gexps_3s,
        (3,1) : gexps_3p
        }

    gcoefs = {  # indexed by N,s_or_p:
        (1,0) : gcoefs_1s,
        (2,0) : gcoefs_2s,
        (2,1) : gcoefs_2p,
        (3,0) : gcoefs_3s,
        (3,1) : gcoefs_3p
        }

    I,J,K,R = nlm2powers[(N,L,M)]
    exps = [zeta**2*expn for expn in gexps[(N,L)]]
    coefs = gcoefs[N,L]
    return cgbf(origin,(I,J,K),exps,coefs)


# Alternatively, I could define pgbf.__getitem__  as [(1,pgbf)] and use the above S for all fns.
# Could be appealing to have a single S,T,V, etc.
# Probably dont want to use this trick for ERIs, though.

if __name__ == '__main__':
    import doctest
    doctest.testmod()
