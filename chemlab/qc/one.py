"""
One electron integrals.
"""

from numpy import pi,exp,floor,array,isclose
from math import factorial
from .utils import binomial, fact2, Fgamma, norm2

# Notes:
# The versions S,T,V include the normalization constants
# The version overlap,kinetic,nuclear_attraction do not.
# This is so, for example, the kinetic routines can call the potential routines
#  without the normalization constants getting in the way.

def S(a,b):
    """
    Simple interface to the overlap function.
    >>> from pyquante2 import pgbf,cgbf
    >>> s = pgbf(1)
    >>> isclose(S(s,s),1.0)
    True
    >>> sc = cgbf(exps=[1],coefs=[1])
    >>> isclose(S(sc,sc),1.0)
    True

    >>> sc = cgbf(exps=[1],coefs=[1])
    >>> isclose(S(sc,s),1.0)
    True
    >>> isclose(S(s,sc),1.0)
    True

    """
    if b.contracted:
        return sum(cb*S(pb,a) for (cb,pb) in b)
    elif a.contracted:
        return sum(ca*S(b,pa) for (ca,pa) in a)
    return a.norm*b.norm*overlap(a.exponent,a.powers,
                                 a.origin,b.exponent,b.powers,b.origin)

def T(a,b):
    """
    Simple interface to the kinetic function.
    >>> from pyquante2 import pgbf,cgbf
    >>> from pyquante2.basis.pgbf import pgbf
    >>> s = pgbf(1)
    >>> isclose(T(s,s),1.5)
    True

    >>> sc = cgbf(exps=[1],coefs=[1])
    >>> isclose(T(sc,sc),1.5)
    True

    >>> sc = cgbf(exps=[1],coefs=[1])
    >>> isclose(T(sc,s),1.5)
    True
    >>> isclose(T(s,sc),1.5)
    True

    """
    if b.contracted:
        return sum(cb*T(pb,a) for (cb,pb) in b)
    elif a.contracted:
        return sum(ca*T(b,pa) for (ca,pa) in a)
    return a.norm*b.norm*kinetic(a.exponent,a.powers,a.origin,
                                 b.exponent,b.powers,b.origin)

def V(a,b,C):
    """
    Simple interface to the nuclear attraction function.
    >>> from pyquante2 import pgbf,cgbf
    >>> s = pgbf(1)
    >>> isclose(V(s,s,(0,0,0)),-1.595769)
    True

    >>> sc = cgbf(exps=[1],coefs=[1])
    >>> isclose(V(sc,sc,(0,0,0)),-1.595769)
    True

    >>> sc = cgbf(exps=[1],coefs=[1])
    >>> isclose(V(sc,s,(0,0,0)),-1.595769)
    True

    >>> isclose(V(s,sc,(0,0,0)),-1.595769)
    True

    """
    if b.contracted:
        return sum(cb*V(pb,a,C) for (cb,pb) in b)
    elif a.contracted:
        return sum(ca*V(b,pa,C) for (ca,pa) in a)
    return a.norm*b.norm*nuclear_attraction(a.exponent,a.powers,a.origin,
                                            b.exponent,b.powers,b.origin,C)

def overlap(alpha1,lmn1,A,alpha2,lmn2,B):
    """
    Full form of the overlap integral. Taken from THO eq. 2.12
    >>> isclose(overlap(1,(0,0,0),array((0,0,0),'d'),1,(0,0,0),array((0,0,0),'d')),1.968701)
    True
    """
    l1,m1,n1 = lmn1
    l2,m2,n2 = lmn2
    rab2 = norm2(A-B)
    gamma = alpha1+alpha2
    P = gaussian_product_center(alpha1,A,alpha2,B)

    pre = pow(pi/gamma,1.5)*exp(-alpha1*alpha2*rab2/gamma)

    wx = overlap1d(l1,l2,P[0]-A[0],P[0]-B[0],gamma)
    wy = overlap1d(m1,m2,P[1]-A[1],P[1]-B[1],gamma)
    wz = overlap1d(n1,n2,P[2]-A[2],P[2]-B[2],gamma)
    return pre*wx*wy*wz

def overlap1d(l1,l2,PAx,PBx,gamma):
    """
    The one-dimensional component of the overlap integral. Taken from THO eq. 2.12
    >>> isclose(overlap1d(0,0,0,0,1),1.0)
    True
    """
    total = 0
    for i in range(1+int(floor(0.5*(l1+l2)))):
        total += binomial_prefactor(2*i,l1,l2,PAx,PBx)* \
                 fact2(2*i-1)/pow(2*gamma,i)
    return total

def gaussian_product_center(alpha1,A,alpha2,B):
    """
    The center of the Gaussian resulting from the product of two Gaussians:
    >>> gaussian_product_center(1,array((0,0,0),'d'),1,array((0,0,0),'d'))
    array([ 0.,  0.,  0.])
    """
    return (alpha1*A+alpha2*B)/(alpha1+alpha2)

def binomial_prefactor(s,ia,ib,xpa,xpb):
    """
    The integral prefactor containing the binomial coefficients from Augspurger and Dykstra.
    >>> binomial_prefactor(0,0,0,0,0)
    1
    """
    total= 0
    for t in range(s+1):
        if s-ia <= t <= ib:
            total +=  binomial(ia,s-t)*binomial(ib,t)* \
                     pow(xpa,ia-s+t)*pow(xpb,ib-t)
    return total

def kinetic(alpha1,lmn1,A,alpha2,lmn2,B):
    """
    The full form of the kinetic energy integral
    >>> isclose(kinetic(1,(0,0,0),array((0,0,0),'d'),1,(0,0,0),array((0,0,0),'d')),2.953052)
    True
    """
    l1,m1,n1 = lmn1
    l2,m2,n2 = lmn2
    term0 = alpha2*(2*(l2+m2+n2)+3)*\
            overlap(alpha1,(l1,m1,n1),A,\
                           alpha2,(l2,m2,n2),B)
    term1 = -2*pow(alpha2,2)*\
            (overlap(alpha1,(l1,m1,n1),A,
                            alpha2,(l2+2,m2,n2),B)
             + overlap(alpha1,(l1,m1,n1),A,
                              alpha2,(l2,m2+2,n2),B)
             + overlap(alpha1,(l1,m1,n1),A,
                              alpha2,(l2,m2,n2+2),B))
    term2 = -0.5*(l2*(l2-1)*overlap(alpha1,(l1,m1,n1),A,
                                           alpha2,(l2-2,m2,n2),B) +
                  m2*(m2-1)*overlap(alpha1,(l1,m1,n1),A,
                                           alpha2,(l2,m2-2,n2),B) +
                  n2*(n2-1)*overlap(alpha1,(l1,m1,n1),A,
                                           alpha2,(l2,m2,n2-2),B))
    return term0+term1+term2

def nuclear_attraction(alpha1,lmn1,A,alpha2,lmn2,B,C):
    """
    Full form of the nuclear attraction integral
    >>> isclose(nuclear_attraction(1,(0,0,0),array((0,0,0),'d'),1,(0,0,0),array((0,0,0),'d'),array((0,0,0),'d')),-3.141593)
    True
    """
    l1,m1,n1 = lmn1
    l2,m2,n2 = lmn2
    gamma = alpha1+alpha2

    P = gaussian_product_center(alpha1,A,alpha2,B)
    rab2 = norm2(A-B)
    rcp2 = norm2(C-P)

    dPA = P-A
    dPB = P-B
    dPC = P-C

    Ax = A_array(l1,l2,dPA[0],dPB[0],dPC[0],gamma)
    Ay = A_array(m1,m2,dPA[1],dPB[1],dPC[1],gamma)
    Az = A_array(n1,n2,dPA[2],dPB[2],dPC[2],gamma)

    total = 0.
    for I in range(l1+l2+1):
        for J in range(m1+m2+1):
            for K in range(n1+n2+1):
                total += Ax[I]*Ay[J]*Az[K]*Fgamma(I+J+K,rcp2*gamma)
                
    val= -2*pi/gamma*exp(-alpha1*alpha2*rab2/gamma)*total
    return val

def A_term(i,r,u,l1,l2,PAx,PBx,CPx,gamma):
    """
    THO eq. 2.18

    >>> A_term(0,0,0,0,0,0,0,0,1)
    1.0
    >>> A_term(0,0,0,0,1,1,1,1,1)
    1.0
    >>> A_term(1,0,0,0,1,1,1,1,1)
    -1.0
    >>> A_term(0,0,0,1,1,1,1,1,1)
    1.0
    >>> A_term(1,0,0,1,1,1,1,1,1)
    -2.0
    >>> A_term(2,0,0,1,1,1,1,1,1)
    1.0
    >>> A_term(2,0,1,1,1,1,1,1,1)
    -0.5
    >>> A_term(2,1,0,1,1,1,1,1,1)    
    0.5
    """
    return pow(-1,i)*binomial_prefactor(i,l1,l2,PAx,PBx)*\
           pow(-1,u)*factorial(i)*pow(CPx,i-2*r-2*u)*\
           pow(0.25/gamma,r+u)/factorial(r)/factorial(u)/factorial(i-2*r-2*u)

def A_array(l1,l2,PA,PB,CP,g):
    """
    THO eq. 2.18 and 3.1

    >>> A_array(0,0,0,0,0,1)
    [1.0]
    >>> A_array(0,1,1,1,1,1)
    [1.0, -1.0]
    >>> A_array(1,1,1,1,1,1)
    [1.5, -2.5, 1.0]
    """
    Imax = l1+l2+1
    A = [0]*Imax
    for i in range(Imax):
        for r in range(int(floor(i/2)+1)):
            for u in range(int(floor((i-2*r)/2)+1)):
                I = i-2*r-u
                A[I] = A[I] + A_term(i,r,u,l1,l2,PA,PB,CP,g)
    return A

if __name__ == '__main__':
    import doctest; doctest.testmod()
