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
    
    # Test Copy
    iattr = InstanceAttribute('type_array', dim='atom', dtype='str')
    iattr.empty(3)
    iattr.value = ['O', 'H', 'H']

    
    iattr2 = iattr.copy()
    assert_npequal(iattr2.value, iattr.value)
    
    iattr2.value = ['A', 'B', 'C']
    assert_npequal(iattr.value, ['O', 'H', 'H'])
    assert_npequal(iattr2.value, ['A', 'B', 'C'])
    
    iattr = InstanceAttribute('type_array', dim='atom', dtype='str')
    iattr.empty(3)
    iattr.value = ['O', 'H', 'H']
    
    iattr1 = iattr.sub([0, 1]) 
    assert_npequal(iattr1.value, ['O', 'H'])
    iattr1 = iattr.sub([False, True, False]) 
    assert_npequal(iattr1.value, ['H'])

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
    
    a1 = InstanceField('type', dtype='str')
    a1.value = 'O'
    a2 = InstanceField('type', dtype='str')
    a2.value = 'H'
    attr = concatenate_fields([a1, a2], 'atom')
    assert_npequal(attr.value, ['O', 'H'])
    
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
    

class A(ChemicalEntity):
    __dimension__ = 'a'
    __attributes__ = {
        'type_array': Attribute(dim='x', dtype='str')
    }
    __relations__ = {
        'bonds': Relation(dim='y', map='x', shape=(2,))
    }

    __fields__ = {
        'export': Field(dtype=object)
    }

class B(ChemicalEntity):
    
    __dimension__ = 'b'
    __attributes__ = {
        'type_array': Attribute(dim='x', dtype='str'),
        'export': Attribute(dtype=object, dim='a')
    }
    __relations__ = {
        'bonds': Relation(dim='y', map='x', shape=(2,))
    }

class TestChemicalEntity(object):
    
    def test_empty(self):
        
        for b in [B(), B.empty()]:
            eq_(b.dimensions['a'], 0)
            eq_(b.dimensions['x'], 0)
            eq_(b.dimensions['y'], 0)
            eq_(b.type_array, None)
            eq_(b.bonds, None)
        
        a = A.empty(x=3, y=2)
        eq_(a.dimensions['x'], 3)
        eq_(a.dimensions['y'], 2)
        assert_npequal(a.type_array, ['', '', ''])
        assert_npequal(a.bonds, [[0, 0], [0, 0]])
        
        # Can we have relations between non-existent entities?
        # NO: we raise an exception
        assert_raises(ValueError, A.empty, x=0, y=2)
    
    def test_from_entities(self):
        a = A.empty(x=3, y=2)
        a.type_array = ['A', 'B', 'C']
        a.bonds = [[0, 1], [0, 2]]
        a.export = {}
        
        entities = [a for i in range(3)]
        
        b = B()
        b._from_entities(entities, 'a')
        assert_npequal(b.type_array, ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'])
        assert_npequal(b.bonds, [[0, 1], [0, 2], [3, 4], [3, 5], [6, 7], [6, 8]])
        assert_npequal(b.export, [{}, {}, {}])
        
        xa_map = b.maps['x', 'a']
        assert_npequal(xa_map.value, [0, 0, 0, 1, 1, 1, 2, 2, 2])
        
        ya_map = b.maps['y', 'a']
        assert_npequal(ya_map.value, [0, 0, 1, 1, 2, 2])        
    
    def test_from_arrays(self):
        b = B.from_arrays(type_array=['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
                          bonds=[[0, 1], [0, 2], [3, 4], [3, 5], [6, 7], [6, 8]],
                          maps={('x', 'a'): [0, 0, 0, 1, 1, 1, 2, 2, 2],
                                ('y', 'a'): [0, 0, 1, 1, 2, 2]})
        assert_npequal(b.type_array, ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'])
        assert_npequal(b.bonds, [[0, 1], [0, 2], [3, 4], [3, 5], [6, 7], [6, 8]])
        assert_npequal(b.maps['x', 'a'].value, [0, 0, 0, 1, 1, 1, 2, 2, 2])
        assert_npequal(b.maps['y', 'a'].value, [0, 0, 1, 1, 2, 2])        

    def test_subdimension(self):
        b = B.from_arrays(type_array=['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
                          bonds=[[0, 1], [0, 2], [3, 4], [3, 5], [6, 7], [6, 8]],
                          maps={('x', 'a'): [0, 0, 0, 1, 1, 1, 2, 2, 2],
                                ('y', 'a'): [0, 0, 1, 1, 2, 2]})
        
        result = b._propagate_dim([0, 1, 2, 3, 4], 'x')
        assert_npequal(result['x'], [0, 1, 2, 3, 4]) 
        assert_npequal(result['a'], [0, 1]) 
        assert_npequal(result['y'], [0, 1, 2]) 
        
        result = b._propagate_dim([0], 'x')
        assert_npequal(result['x'], [0]) 
        assert_npequal(result['a'], [0]) 
        assert_npequal(result['y'], []) 

        result = b._propagate_dim([2, 6], 'x')
        assert_npequal(result['x'], [2, 6]) 
        assert_npequal(result['a'], [0, 2]) 
        assert_npequal(result['y'], []) 

        result = b._propagate_dim([False, True, False], 'a')
        assert_npequal(result['x'], [3, 4, 5]) 
        assert_npequal(result['a'], [1]) 
        assert_npequal(result['y'], [2, 3]) 
        
        c = b.sub_dimension([False, True, False], 'a')
        eq_(c.dimensions['x'], 3)
        eq_(c.dimensions['y'], 2)
        eq_(c.dimensions['a'], 1)
        assert_npequal(c.bonds, [[0, 1], [0, 2]])
        assert_npequal(c.type_array, ['A', 'B', 'C'])
        assert_npequal(c.maps['x', 'a'].value, [0, 0, 0])
        assert_npequal(c.maps['y', 'a'].value, [0, 0])
        
        result = b._propagate_dim([True, True, False, False, False, False], 'y')
        assert_npequal(result['x'], [0, 1, 2])
        assert_npequal(result['y'], [0, 1])
        assert_npequal(result['a'], [0])
        
        # Now we do similar tests without cascading through the dependencies
        c = b.sub_dimension([True, True, False, False, False, False], 'y', propagate=False)
        assert_npequal(c.bonds, [[0, 1], [0, 2]])
        assert_npequal(c.type_array, ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'])
        assert_npequal(c.maps['x', 'a'].value, [0, 0, 0, 1, 1, 1, 2, 2, 2])
        assert_npequal(c.maps['y', 'a'].value, [0, 0])
    
        # Try without bonds
        b = B.from_arrays(type_array=['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
                          maps={('x', 'a'): [0, 1, 2, 3, 4, 5, 6, 6, 6]})
        
    
        c = b.sub_dimension([0, 1], 'x')
        assert_npequal(c.type_array, ['A', 'B'])
        
        
    # def test_query(self):
    #     b = B.from_arrays(type_array=['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
    #                       bonds=[[0, 1], [0, 2], [3, 4], [3, 5], [6, 7], [6, 8]],
    #                       maps={('x', 'a'): [0, 0, 0, 1, 1, 1, 2, 2, 2],
    #                             ('y', 'a'): [0, 0, 1, 1, 2, 2]})
    #     Query(b).select(type_array='A')
    #     
        
    def test_extend_dimension(self):
        b = B.from_arrays(type_array=['A', 'B', 'D', 'E', 'F', 'G', 'H', 'I'],
                          bonds=[[0, 1], [2, 3], [2, 4], [5, 6], [5, 7]],
                          maps={('x', 'a'): [0, 0, 1, 1, 1, 2, 2, 2],
                                ('y', 'a'): [0, 1, 1, 2, 2]})
        
        c = b.copy()
        c.shrink_dimension(4, 'x')
        eq_(c.dimensions['x'], 4)
        eq_(c.dimensions['y'], 2)
        eq_(c.dimensions['a'], 3)
        
        assert_npequal(c.type_array, ['A', 'B', 'D', 'E'])
        assert_npequal(c.bonds, [[0, 1], [2, 3]])
        assert_npequal(c.maps['x', 'a'].value, [0, 0, 1, 1])
        assert_npequal(c.maps['y', 'a'].value, [0, 1])
        
        # You won't be allowed to increase size because of the maps
        c = b.copy()
        
        c.expand_dimension(11, 'x', maps={('x', 'a'): [0, 0, 1, 1, 1, 2, 2, 2, 2, 2, 2]})
        eq_(c.dimensions['x'], 11)
        eq_(c.dimensions['y'], 5)
        eq_(c.dimensions['a'], 3)
        
        assert_npequal(c.type_array, ['A', 'B', 'D', 'E', 'F', 'G', 'H', 'I', '', '', ''])
        assert_npequal(c.bonds, [[0, 1], [2, 3], [2, 4], [5, 6], [5, 7]])
        assert_npequal(c.maps['x', 'a'].value, [0, 0, 1, 1, 1, 2, 2, 2, 2, 2, 2])
        assert_npequal(c.maps['y', 'a'].value, [0, 1, 1, 2, 2])

    
    def test_reorder_dimension(self):
        b = B.from_arrays(type_array=['A', 'B', 'D', 'E', 'F', 'G', 'H', 'I'],
                          bonds=[[0, 1], [2, 3], [2, 4], [5, 6], [5, 7]],
                          maps={('x', 'a'): [0, 0, 1, 1, 1, 2, 2, 2],
                                ('y', 'a'): [0, 1, 1, 2, 2]})

    
        b.reorder_dimension([1, 0, 2], 'a')
        # Atoms get reordered accordingly
        # this implies contingency
        assert_npequal(b.type_array, ['D', 'E', 'F', 'A', 'B', 'G', 'H', 'I'])
        assert_npequal(b.maps['x', 'a'].value, [0, 0, 0, 1, 1, 2, 2, 2])
        assert_npequal(b.maps['y', 'a'].value, [0, 0, 1, 2, 2])    
        assert_npequal(b.bonds, [[0, 1], [0, 2], [3, 4], [5, 6], [5, 7]])
        
        b = B.from_arrays(type_array=['A', 'B', 'D', 'E', 'F', 'G', 'H', 'I'],
                          bonds=[[0, 1], [2, 3], [2, 4], [5, 6], [5, 7]],
                          maps={('x', 'a'): [0, 0, 1, 1, 1, 2, 2, 2],
                                ('y', 'a'): [0, 1, 1, 2, 2]})
        
        # This doesn't imply contingency
        b.reorder_dimension([0, 3, 2, 1, 4, 5, 6, 7], 'x')
        assert_npequal(b.type_array, ['A', 'E', 'D', 'B', 'F', 'G', 'H', 'I'])
        assert_npequal(b.maps['x', 'a'].value, [0, 1, 1, 0, 1, 2, 2, 2]) # swapped
        assert_npequal(b.maps['y', 'a'].value, [0, 1, 1, 2, 2]) # untouched    
        assert_npequal(b.bonds, [[0, 3], [2, 1], [2, 4], [5, 6], [5, 7]]) # remapped 
    
    def test_copy(self):
        b = B.from_arrays(type_array=['A', 'B', 'D', 'E', 'F', 'G', 'H', 'I'],
                          bonds=[[0, 1], [2, 3], [2, 4], [5, 6], [5, 7]],
                          maps={('x', 'a'): [0, 0, 1, 1, 1, 2, 2, 2],
                                ('y', 'a'): [0, 1, 1, 2, 2]})
        c = b.copy()
        c.type_array[0] = 'D'
        eq_(b.type_array[0], 'A')
    
    def test_concat(self):
        b = B.from_arrays(type_array=['A', 'B', 'D', 'E', 'F'],
                          bonds=[[0, 1], [2, 3], [2, 4]],
                          maps={('x', 'a'): [0, 0, 1, 1, 1,],
                                ('y', 'a'): [0, 1, 1]})
        
        c = b.concat(b)
        eq_(c.dimensions['x'], 10)
        eq_(c.dimensions['a'], 4)
        eq_(c.dimensions['y'], 6)
        
        assert_npequal(c.type_array, ['A', 'B', 'D', 'E', 'F', 'A', 'B', 'D', 'E', 'F'])
        assert_npequal(c.bonds, [[0, 1], [2, 3], [2, 4], [5, 6], [7, 8], [7, 9]])

    def test_where(self):
        b = B.from_arrays(type_array=['A', 'B', 'D', 'E', 'F'],
                          bonds=[[0, 1], [2, 3], [2, 4]],
                          maps={('x', 'a'): [0, 0, 1, 1, 1],
                                ('y', 'a'): [0, 1, 1]})
        
        assert_npequal(b.sub(type_array='A').type_array, ['A'])
        assert_npequal(b.sub(type_array=['B', 'D']).type_array, ['B', 'D'])
        assert_npequal(b.sub(a_index=1).type_array, ['D', 'E', 'F'])
        
