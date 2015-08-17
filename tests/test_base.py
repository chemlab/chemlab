from chemlab.core.base import (Attribute, InstanceAttribute, 
                               Field, InstanceField,
                               Relation, InstanceRelation,
                               ChemicalEntity,
                               concatenate_fields,
                               concatenate_relations,
                               concatenate_attributes) 
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
    irel = InstanceRelation('bonds', map='atoms', index=range(3), dim='bonds', shape=(2,))
    eq_(irel.size, 0)
    assert_npequal(irel.index, [0, 1, 2])
    
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
    eq_(ifield.value, 0.0)
    
    ifield = InstanceField('r_array', shape=(3,))
    assert_npequal(ifield.value, [0.0, 0.0, 0.0])
    
    ifield = InstanceField('symbol', dtype='str')
    eq_(ifield.value, '')
    
def test_concatenate_fields():
    # Uninitialized fields
    attr = concatenate_fields([InstanceField('mass'), 
                               InstanceField('mass'),
                               InstanceField('mass')], 'atom')
    eq_(attr.dim, 'atom')
    eq_(attr.size, 3)
    assert_npequal(attr.value, [0.0, 0.0, 0.0])
    
    # Non uniform fields
    assert_raises(ValueError, concatenate_fields, [InstanceField('mass'), 
                                                   InstanceField('impostor'),
                                                   InstanceField('mass')], 
                                                  'atom')
                               
    # Shape parameter
    r_array = InstanceField('r_array', shape=(3,), dtype='f')
    r_array.value = [0, 1, 2]
    
    attr = concatenate_fields([r_array, r_array, r_array], 'atom')
    assert_npequal(attr.value, [[0, 1, 2],[0, 1, 2],[0, 1, 2]])
    
    box = InstanceField('box', shape=(3, 3), dtype='f')
    box.value = np.eye(3)
    attr = concatenate_fields([box, box, box], 'atom')
    assert_npequal(attr.value, [np.eye(3),np.eye(3),np.eye(3)])

def test_concatenate_attributes():
    a1 = InstanceAttribute('type_array', dim='atom', dtype='str')
    newattr = concatenate_attributes([a1, a1, a1])
    eq_(newattr.size, 0)
    
    a2 = a1.empty(10, inplace=False)
    newattr = concatenate_attributes([a1, a2, a2])
    eq_(newattr.size, 20)
    
    # Shape parameter
    r_array = InstanceAttribute('r_array', shape=(3,), dtype='f', dim='atom')
    r_array.value = [[0, 1, 2]]
    newattr = concatenate_attributes([r_array, r_array, r_array])
    eq_(newattr.size, 3)
    assert_npequal(newattr.value, [[0, 1, 2], [0, 1, 2], [0, 1, 2]])
    

def test_concatenate_relations():
    a1 = InstanceRelation('bonds', map='atom', index=range(3), shape=(2,), dim='bond')
    newattr = concatenate_relations([a1, a1, a1])
    eq_(newattr.size, 0)
    
    a2 = a1.empty(2, inplace=False)
    a3 = a2.copy()
    
    newattr = concatenate_relations([a1, a2, a3])
    eq_(newattr.size, 4)
    assert_npequal(newattr.value, [[3, 3], [3, 3], 
                                   [6, 6], [6, 6]])
