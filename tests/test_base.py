from chemlab.core.base import (Attribute, InstanceAttribute, 
                               Field, InstanceField,
                               Relation, InstanceRelation,
                               ChemicalEntity) 
from nose.tools import eq_, ok_, assert_raises
import numpy as np
from .testtools import assert_npequal

def test_attribute():
    # Initalize
    attr = Attribute(dim='atom')
    eq_(attr.shape, None)
    assert isinstance(attr.dim, str)
    
    iattr = attr.create('r_array')
    eq_(iattr.name, 'r_array')
    
    # Initialize error
    assert_raises(ValueError, Attribute)

def test_instance_attribute():
    iattr = InstanceAttribute('type_array', dim='atom', dtype='str')
    eq_(iattr.size, 0)
    
    # Now we initialize as empty
    iattr.empty(10)
    eq_(iattr.size, 10) 
    
    # We get another one
    iattr = InstanceAttribute('type_array', dim='atom', dtype='str')
    iattr.value = ['A', 'B', 'C', 'D']
    
    # Automatic casting
    ok_(isinstance(iattr.value, np.ndarray))
    assert_npequal(iattr.value, ['A', 'B', 'C', 'D'])
    
    # Reordering
    iattr2 = iattr.reorder([1, 0, 3, 2], inplace=False)
    assert_npequal(iattr2.value, ['B', 'A', 'D', 'C'])
    
    iattr.reorder([1, 0, 3, 2])
    assert_npequal(iattr.value, ['B', 'A', 'D', 'C'])
    
    # Reordering with wrong input raises ValueError
    assert_raises(ValueError, iattr.reorder, [1, 2])
    assert_raises(ValueError, iattr.reorder, [0, 1, 2, 100])


def test_instance_relation():
    irel = InstanceRelation('bonds', map='atoms', dim='bonds', shape=(2,))
    eq_(irel.size, 0)
    
    # initialize as empty
    irel.empty(2)
    assert_npequal(irel.value, [[0, 0], [0, 0]])
    
    # reorder
    irel.value = [[0, 1], [0, 2]]
    irel.reorder([1, 0])
    assert_npequal(irel.value, [[0, 2], [0, 1]])
    
    # remap
    irel2 = irel.remap([0, 1, 2], [2, 0, 1], inplace=False)
    assert_npequal(irel2.value, [[2, 1], [2, 0]])
    
    irel.remap([0, 1, 2], [2, 0, 1])
    assert_npequal(irel.value, [[2, 1], [2, 0]])
    
def test_instance_field():
    ifield = InstanceField('mass')
    ifield.empty()
    eq_(ifield.value, 0.0)
    
    ifield = InstanceField('r_array', shape=(3,))
    ifield.empty()
    assert_npequal(ifield.value, [0.0, 0.0, 0.0])
    
    ifield = InstanceField('symbol', dtype='str')
    ifield.empty()
    eq_(ifield.value, '')
