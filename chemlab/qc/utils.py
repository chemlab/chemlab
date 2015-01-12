"""
utils.py - Simple utilility funtions used in pyquante2.
"""
import numpy as np
from math import factorial,lgamma
from itertools import combinations_with_replacement,combinations
from functools import reduce

def pairs(it): return combinations_with_replacement(it,2)
def upairs(it): return combinations(it,2)

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

def binomial(n,k):
    """
    Binomial coefficient
    >>> binomial(5,2)
    10
    >>> binomial(10,5)
    252
    """
    if n==k: return 1
    assert n>k, "Attempting to call binomial(%d,%d)" % (n,k)
    return factorial(n)//(factorial(k)*factorial(n-k))

def Fgamma(m,x):
    """
    Incomplete gamma function
    >>> np.isclose(Fgamma(0,0),1.0)
    True
    """
    SMALL=1e-12
    x = max(x,SMALL)
    return 0.5*pow(x,-m-0.5)*gamm_inc(m+0.5,x)

# def gamm_inc_scipy(a,x):
#     """
#     Demonstration on how to replace the gamma calls with scipy.special functions.
#     By default, pyquante only requires numpy, but this may change as scipy
#     builds become more stable.
#     >>> np.isclose(gamm_inc_scipy(0.5,1),1.49365)
#     True
#     >>> np.isclose(gamm_inc_scipy(1.5,2),0.6545103)
#     True
#     >>> np.isclose(gamm_inc_scipy(2.5,1e-12),0)
#     True
#     """
#     from scipy.special import gamma,gammainc
#     return gamma(a)*gammainc(a,x)
    
def gamm_inc(a,x):
    """
    Incomple gamma function \gamma; computed from NumRec routine gammp.
    >>> np.isclose(gamm_inc(0.5,1),1.49365)
    True
    >>> np.isclose(gamm_inc(1.5,2),0.6545103)
    True
    >>> np.isclose(gamm_inc(2.5,1e-12),0)
    True
    """
    assert (x > 0 and a >= 0), "Invalid arguments in routine gamm_inc: %s,%s" % (x,a)

    if x < (a+1.0): #Use the series representation
        gam,gln = _gser(a,x)
    else: #Use continued fractions
        gamc,gln = _gcf(a,x)
        gam = 1-gamc
    return np.exp(gln)*gam

def _gser(a,x):
    "Series representation of Gamma. NumRec sect 6.1."
    ITMAX=100
    EPS=3.e-7

    gln=lgamma(a)
    assert(x>=0),'x < 0 in gser'
    if x == 0 : return 0,gln

    ap = a
    delt = sum = 1./a
    for i in range(ITMAX):
        ap=ap+1.
        delt=delt*x/ap
        sum=sum+delt
        if abs(delt) < abs(sum)*EPS: break
    else:
        print('a too large, ITMAX too small in gser')
    gamser=sum*np.exp(-x+a*np.log(x)-gln)
    return gamser,gln

def _gcf(a,x):
    "Continued fraction representation of Gamma. NumRec sect 6.1"
    ITMAX=100
    EPS=3.e-7
    FPMIN=1.e-30

    gln=lgamma(a)
    b=x+1.-a
    c=1./FPMIN
    d=1./b
    h=d
    for i in range(1,ITMAX+1):
        an=-i*(i-a)
        b=b+2.
        d=an*d+b
        if abs(d) < FPMIN: d=FPMIN
        c=b+an/c
        if abs(c) < FPMIN: c=FPMIN
        d=1./d
        delt=d*c
        h=h*delt
        if abs(delt-1.) < EPS: break
    else:
        print('a too large, ITMAX too small in gcf')
    gammcf=np.exp(-x+a*np.log(x)-gln)*h
    return gammcf,gln

def trace2(A,B):
    "Return trace(AB) of matrices A and B"
    return np.sum(A*B)

def dmat(c,nocc):
    "Form the density matrix from the first nocc orbitals of c"
    return np.dot(c[:,:nocc],c[:,:nocc].T)

def symorth(S):
    "Symmetric orthogonalization"
    E,U = np.linalg.eigh(S)
    n = len(E)
    Shalf = np.identity(n,'d')
    for i in range(n):
        Shalf[i,i] /= np.sqrt(E[i])
    return simx(Shalf,U,True)

def canorth(S):
    "Canonical orthogonalization U/sqrt(lambda)"
    E,U = np.linalg.eigh(S)
    for i in range(len(E)):
        U[:,i] = U[:,i] / np.sqrt(E[i])
    return U

def cholorth(S):
    "Cholesky orthogonalization"
    return np.linalg.inv(np.linalg.cholesky(S)).T

def simx(A,B,transpose=False):
    "Similarity transform B^T(AB) or B(AB^T) (if transpose)"
    if transpose:
        return np.dot(B,np.dot(A,B.T))
    return np.dot(B.T,np.dot(A,B))

def geigh(H,S):
    "Solve the generalized eigensystem Hc = ESc"
    A = cholorth(S)
    E,U = np.linalg.eigh(simx(H,A))
    return E,np.dot(A,U)
    
def parseline(line,format):
    """\
    Given a line (a string actually) and a short string telling
    how to format it, return a list of python objects that result.

    The format string maps words (as split by line.split()) into
    python code:
    x   ->    Nothing; skip this word
    s   ->    Return this word as a string
    i   ->    Return this word as an int
    d   ->    Return this word as an int
    f   ->    Return this word as a float

    Basic parsing of strings:
    >>> parseline('Hello, World','ss')
    ['Hello,', 'World']

    You can use 'x' to skip a record; you also don't have to parse
    every record:
    >>> parseline('1 2 3 4','xdd')
    [2, 3]

    >>> parseline('C1   0.0  0.0 0.0','sfff')
    ['C1', 0.0, 0.0, 0.0]

    Should this return an empty list?
    >>> parseline('This line wont be parsed','xx')
    """
    xlat = {'x':None,'s':str,'f':float,'d':int,'i':int}
    result = []
    words = line.split()
    for i in range(len(format)):
        f = format[i]
        trans = xlat.get(f,None)
        if trans: result.append(trans(words[i]))
    if len(result) == 0: return None
    if len(result) == 1: return result[0]
    return result

def colorscale(mag, cmin, cmax):
    """
    Return a tuple of floats between 0 and 1 for R, G, and B.
    From Python Cookbook (9.11?)
    """
    # Normalize to 0-1
    try:
        x = float(mag-cmin)/(cmax-cmin)
    except ZeroDivisionError:
        x = 0.5  # cmax == cmin
    blue = min((max((4*(0.75-x), 0.)), 1.))
    red = min((max((4*(x-0.25), 0.)), 1.))
    green = min((max((4*abs(x-0.5)-1., 0.)), 1.))
    return red, green, blue

#Todo: replace with np.isclose
#def isnear(a,b,tol=1e-6): return abs(a-b) < tol

if __name__ == '__main__':
    import doctest
    doctest.testmod()

