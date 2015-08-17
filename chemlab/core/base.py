"""
Base classes
"""
import numpy as np
from pandas.hashtable import Int64HashTable
import collections
from itertools import islice

# BASE CLASS
class EntityProperty(object):
    pass


class Attribute(EntityProperty):
    def __init__(self, shape=None, dtype=None, dim=None, alias=None):
        if not isinstance(dim, str):
            raise ValueError('dim parameter is required and should be a string.')
        
        self.shape = shape
        self.dtype = dtype
        self.dim = dim
        self.alias = alias
    
    def create(self, name):
        return InstanceAttribute(name, self.shape, self.dtype, self.dim, self.alias)

class Relation(EntityProperty):
    def __init__(self, map=None, dim=None, alias=None, shape=None):
        if not isinstance(dim, str):
            raise ValueError('dim parameter is required and should be a string.')
        if not isinstance(map, str):
            raise ValueError('map parameter is required and should be a string.')
        
        self.map=map
        self.dtype = 'int'
        self.dim = dim
        self.alias = alias
        self.shape = shape
    
    def create(self, name):
        return InstanceRelation(name, map=self.map, dim=self.dim, shape=self.shape, alias=self.alias)

class Field(EntityProperty):
    
    def __init__(self, dtype=None, shape=None, alias=None):
        # A one-dimensional attribute
        self.dtype = dtype
        self.alias = alias
        self.shape = shape
    
    def create(self, name):
        return InstanceField(name, self.dtype, self.shape, self.alias)

class InstanceProperty(object):
    pass

class InstanceArray(InstanceProperty):

    def empty(self, size, inplace=True):
        # If it is its own dimension, we need shape 1
        if size == 0:
            value = None
        else:
            shape = (size,) + self.shape if self.shape else (size,)
            value = np.zeros(shape, dtype=self.dtype)
        
        if inplace:
            self.value = value
        else:
            obj = self.copy()
            obj.value = value
            return obj
    
    def copy(self):
        raise NotImplementedError()
    
    @property
    def size(self):
        if self.value is None:
            return 0
        else:
            return len(self.value)
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        if value is None:
            self._value = None
        
        elif isinstance(value, list):
            self._value = np.asarray(value, dtype=self.dtype)
        
        elif isinstance(value, np.ndarray):
            self._value = np.asarray(value, dtype=self.dtype)
    

    def reorder(self, neworder, inplace=True):
        if self.value is None:
            return # No reordering
        else:
            if len(neworder) != self.size:
                raise ValueError("neworder doesn't have enough elements %d (value %d)" % (len(neworder), self.size))
            
            if set(neworder) != set(range(self.size)):
                raise ValueError("The new order is invalid as it doesn't contain all the indices.")
            
            if inplace:
                self.value = self.value.take(neworder, axis=0)
            else:
                obj = self.copy()
                obj.value = self.value.take(neworder, axis=0)
                return obj
                

class InstanceAttribute(InstanceArray):
    
    def __init__(self, name, shape=None, dtype=None, dim=None, alias=None):
        if not isinstance(dim, str):
            raise ValueError('dim parameter is required and should be a string.')
        self.name = name
        self.shape = shape
        self.dtype = dtype
        self.dim = dim
        self.alias = alias
        self.value = None
    
    def copy(self):
        obj = type(self)(self.name, self.shape, self.dtype, self.dim, self.alias)
        obj.value = self.value
        return obj
    


class InstanceRelation(InstanceArray):
    
    def __init__(self, name, map=None, index=None, dim=None, shape=None, alias=None):
        if not isinstance(dim, str):
            raise ValueError('dim parameter is required and should be a string.')

        if not isinstance(map, str):
            raise ValueError('map parameter is required and should be a string.')
        
        if not isinstance(name, str):
            raise ValueError('name parameter should be a string')

        if not isinstance(index, (list, np.ndarray)):
            raise ValueError('index parameter should be an array-like object')

        if shape is not None and not isinstance(shape, tuple):
            raise ValueError('shape parameter should be a tuple')
        
        self.name = name
        self.map = map
        self.index = index
        self.dtype = 'int'
        self.dim = dim
        self.alias = alias
        self.shape = shape
        self.value = None

    def copy(self):
        obj = type(self)(self.name, self.map, self.index, self.dim, self.shape, self.alias)
        obj.value = self.value
        return obj
    
    def remap(self, from_map, to_map, inplace=True):
        if not isinstance(from_map, (list, np.ndarray)) or not isinstance(to_map, list):
            raise ValueError('from_map and to_map should be either lists or arrays')
        
        if self.value is None:
            # Nothing to remap
            if inplace:
                return 
            else:
                return self.copy()
            
        # Remap columns
        hashtable = Int64HashTable()
        hashtable.map(np.asarray(from_map),
                      np.asarray(to_map))
        
        mapped = hashtable.lookup(self.value.flatten('F'))
        
        if inplace:
            # Flatten and back
            self.value = mapped.reshape(self.value.shape, order='F')
        else:
            obj = self.copy()
            obj.value = mapped.reshape(self.value.shape, order='F')
            return obj


class InstanceField(InstanceProperty):
    def __init__(self, name, dtype=None, shape=None, alias=None):
        self.name = name
        self.dtype = dtype
        self.alias = alias
        self.shape = shape
        self.value = None
        self.empty()
    
    def empty(self):
        if self.shape is None:
            self.value = np.zeros(1, self.dtype)[0]
        else:
            self.value = np.zeros(self.shape, dtype=self.dtype)

class ChemicalEntity(object):
    
    __dimension__ = 'chemical_entity'
    __attributes__ = {}
    __relations__ = {}
    __fields__ = {}
    
    def __new__(cls, *args, **kwargs):
        instance = super(ChemicalEntity, cls).__new__(cls)
        # We create the actual attributes, relations and fields.
        instance.__attributes__ = {name : attr.create(name) 
                                   for name, attr in cls.__attributes__.items()}
        instance.__relations__ = {name : attr.create(name) 
                                   for name, attr in cls.__relations__.items()}
        instance.__fields__ = {name: attr.create(name) 
                                   for name, attr in cls.__fields__.items()}
        return instance
    
    def __getattr__(self, name):
        try:
            return super(ChemicalEntity, self).__getattr__(name)
        except AttributeError:
            return self.get_attribute(name).value
    
    def __setattr__(self, name, value):
        try:
            super(ChemicalEntity, self).__setattr__(name, value)
        except AttributeError:
            self.get_attribute(name).value = value
    
    def get_attribute(self, name):
        return merge_dicts(self.__attributes__ , self.__fields__, self.__relations__)[name]
    
    @classmethod
    def empty(cls, **kwargs):
        instance = cls.__new__(cls)
        # We need to add the extra kwarg
        cls.initialize_empty(instance, **kwargs)
        return instance
    
    def initialize_empty(self, **kwargs):
        self.dimensions = {}
        for attr in merge_dicts(self.__attributes__, self.__relations__).values():
            self.dimensions[attr.dim] = kwargs.get(attr.dim, 0)
            attr.empty(**kwargs)
        
        for attr in self.__fields__.values():
            attr.empty()
        
        # We need indexes
        self.index = {k: np.asarray(range(v)) for k,v in kwargs.items()}

    def reorder(self, **kwargs):
        for attr in self.__attributes__.values():
            order = kwargs.get(attr.dim, None)
            if order is not None:
                attr.reorder(order, inplace=True)
        
        for attr in self.__relations__.values():
            from_map = {column: kwargs.get(column, None) for column in attr.columns}
            to_map = {column: range(self.dimensions[column]) for column in attr.columns}
            attr.remap(from_map, to_map, inplace=True)

    def _from_entities(self, entities, newdim):
        for name, attr in self.__attributes__.items():
            child_attr = [e.get_attribute(attr.name) for e in entities]
            if attr.dim == newdim:
                self.__attributes__[name] = concatenate_fields(child_attr)
            else:
                child_attr = [e.get_attribute(attr.name) for e in entities]
                self.__attributes__[name] = concatenate_attributes(child_attr)
        
        for name, attr in self.__relations__.items():
            if newdim in attr.columns:
                pass
            else:
                self.__relations__[name] = concatenate_relations([e.get_attribute(attr.name) for e in entities], 
                                                                  entity_dimensions=[e.dimensions for e in entities],
                                                                  final_dimensions=self.dimensions)



def concatenate_relations(relations):
    tpl = relations[0]
    
    rel = tpl.copy()
    rel.index = range(sum(len(r.index) for r in relations)) 
    
    arrays = []
    iterindex = iter(rel.index)
    for r in relations:
        # For a molecule e.index['atom'] = [0, 1, 2]
        from_map = r.index
        # we remap this to [3, 4, 5]
        to_map = consume(iterindex, len(r.index))
        if r.size == 0:
            continue            
        arrays.append(r.remap(from_map, to_map, inplace=False).value)
    
    if len(arrays) == 0:
        rel.value = None
    else:
        rel.value = np.concatenate(arrays, axis=0)
    
    return rel

def concatenate_attributes(attributes):
    '''Concatenate InstanceAttribute to return a bigger one.'''
    # We get a template
    tpl = attributes[0]
    attr = InstanceAttribute(tpl.name, tpl.shape, 
                             tpl.dtype, tpl.dim, tpl.alias)
    # Special case, not a single array has size bigger than 0
    if all(a.size == 0 for a in attributes):
        return attr
    else: 
        attr.value = np.concatenate([a.value for a in attributes if a.size > 0], axis=0)
        return attr

def concatenate_fields(fields, dim):
    'Create an INstanceAttribute from a list of InstnaceFields'
    if len(fields) == 0:
        raise ValueError('fields cannot be an empty list')
    
    if len(set((f.name, f.shape, f.dtype) for f in fields)) != 1:
        raise ValueError('fields should have homogeneous name, shape and dtype')
    tpl = fields[0]
    attr = InstanceAttribute(tpl.name, shape=tpl.shape, dtype=tpl.dtype, 
                             dim=dim, alias=tpl.alias)
    
    attr.value = np.array([f.value for f in fields], dtype=tpl.dtype)
    return attr


#TODO: move the utilities
def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def consume(iterator, n):
    "Advance the iterator n-steps ahead. If n is none, consume entirely."
    return list(islice(iterator, 0, n))
