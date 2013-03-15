import numpy as np
from numpy.linalg import norm

def fequal(a, b, tol):
    return (abs(a-b) / max(abs(a), abs(b))) < tol

def normalized(x):
    '''Return the x vector normalized'''
    return x/norm(x)

def distance(x1, x2):
    '''Distance between two points in space
    '''
    return norm(x2 - x1)

def direction(x1, x2):
    '''Direction (normalized) between two point in space'''
    return normalized(x2 - x1)
