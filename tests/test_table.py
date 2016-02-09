from chemlab.table import *
from nose.tools import eq_
from .testtools import feq_, npeq_

def test_atomic_no():
    eq_(atomic_no('H'), 1)
    npeq_(atomic_no(['O', 'H', 'H']), [8, 1, 1])
    
def test_atomic_weight():
    feq_(atomic_weight('H'), 1.00794)
    npeq_(atomic_weight(['O', 'H', 'H']), [15.9994, 1.00794, 1.00794])

def test_vdw_radius():
    feq_(vdw_radius('H'), 0.11)
    npeq_(vdw_radius(['O', 'H', 'H']), [0.152, 0.11, 0.11])


    
