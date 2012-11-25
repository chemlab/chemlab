'''Test the minimization routines'''
#from chemlab.molsim.opt import minimize
from chemlab import MonatomicSystem
from chemlab.graphics import display_system
import pyglet
pyglet.options['vsync'] = False

import scipy.optimize as opt
import numpy as np
from chemlab.molsim import cenergy, cforces



def minimize(sys):
    '''Minimize the energy of the system'''
    
    def en_func(r0):
        r0 = r0.reshape(sys.n, 3).astype(np.float64)
        
        en = cenergy.lennard_jones(r0, sys.type)
        return en*1e80
        
    def fprime_func(r0):
        r0 = r0.reshape((sys.n, 3)).astype(np.float64)
        print r0*1e10
        return np.array([1.0]*sys.n*3)
        return -cforces.lennard_jones(r0, sys.type).reshape(sys.n*3)
        
        
    print opt.fmin_cg(en_func, sys.rarray.reshape(sys.n*3),
                fprime=fprime_func)
    
    
def test_minimize():
    sys = MonatomicSystem.random('Ar', 4, 0.7)
    #display_system(sys)
    sys = minimize(sys)
    #display_system(sys)
    


