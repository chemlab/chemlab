"""
Base classes
"""
import numpy as np
from pandas.hashtable import Int64HashTable
import collections
from contextlib import contextmanager
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
    
    def create(self, name, index):
        return InstanceRelation(name, map=self.map, index=index, dim=self.dim, shape=self.shape, alias=self.alias)


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
    
    def sub(self, index):
        """Return a sub-attribute"""
        inst = self.copy()
        size = np.count_nonzero(index)
        inst.empty(size)
        
        index = np.asarray(index)
        if index.dtype == 'bool':
            index = index.nonzero()[0]
        
        inst.value = self.value.take(index, axis=0)
        return inst

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
    
    def field(self, index):
        obj = InstanceField(name=self.name, dtype=self.dtype, shape=self.shape, alias=self.alias)
        obj.value = self.value[index]
        return obj
    
    def append(self, attr_or_field):        
        if isinstance(attr_or_field, InstanceAttribute):
            self.value = np.append(self.value, attr_or_field.value, axis=0)
        elif isinstance(attr_or_field, InstanceField):
            self.value = np.append(self.value, [attr_or_field.value], axis=0)
        else:
            raise ValueError('Can append only InstanceAttribute or InstanceField')
    def __repr__(self):
        return '<Attribute: {} = {}>'.format(self.name, str(self.value))


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

    def append(self, rel):
        newix = rel.index + len(self.index)
        newrel = rel.remap(rel.index, newix, inplace=False)
        # Extend index
        self.index = np.append(self.index, newix, axis=0)
        # Extend value
        self.value = np.append(self.value, newrel.value, axis=0)
    
    def remap(self, from_map, to_map, inplace=True):
        if not isinstance(from_map, (list, np.ndarray)) or not isinstance(to_map, (list, np.ndarray)):
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

    @property
    def index(self):
        return self._index
    
    @index.setter
    def index(self, value):
        if value is None:
            self._index = None
        
        elif isinstance(value, list):
            self._index = np.asarray(value, dtype='int')
        
        elif isinstance(value, np.ndarray):
            self._index = np.asarray(value, dtype='int')
    
    @InstanceArray.value.setter
    def value(self, value):
        if value is None:
            pass
        else:
            # We have to check that all the values in the map are in the index
            # as well
            ix_value = set(np.asarray(value).flatten())
            ix_max = set(self.index)
            
            if ix_value > ix_max:
                raise ValueError('Error setting relation "{}". Values {} not present in index'
                                 .format(self.name, list(ix_value - ix_max)))
        
        InstanceArray.value.__set__(self, value)

    def __repr__(self):
        return '<Relation: {} = {}>'.format(self.name, str(self.value))

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
    
    def copy(self):
        inst = InstanceField(self.name, self.dtype, self.shape, self.alias)
        inst.value = self.value
        return inst
    
    def __repr__(self):
        return '<Field: {} = {}>'.format(self.name, str(self.value))

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
        instance.__relations__ = {name : attr.create(name, index=range(1)) 
                                   for name, attr in cls.__relations__.items()}
        instance.__fields__ = {name: attr.create(name) 
                                   for name, attr in cls.__fields__.items()}
        
        instance.dimensions = {}
        
        for val in merge_dicts(cls.__attributes__, cls.__relations__).values():
            instance.dimensions[val.dim] = 0
            
        return instance
    
    def __getattribute__(self, name):
        try:
            return super(ChemicalEntity, self).__getattribute__(name)
        except AttributeError as exc:
            try:
                return self.get_attribute(name).value
            except KeyError:
                pass
            raise exc
    
    def __setattr__(self, name, value):
        try:
            self.get_attribute(name).value = value
        except KeyError:
            super(ChemicalEntity, self).__setattr__(name, value)
    
    def get_attribute(self, name):
        return merge_dicts(self.__attributes__ , self.__fields__, self.__relations__)[name]
    
    @classmethod
    def empty(cls, **kwargs):
        instance = cls.__new__(cls)
        # We need to add the extra kwarg
        cls.initialize_empty(instance, **kwargs)
        return instance
    
    def copy(self):
        inst = type(self).empty(**self.dimensions)
        
        # Need to copy all attributes, fields, relations
        inst.__attributes__ = {k: v.copy() for k, v in self.__attributes__.items()}
        inst.__fields__ = {k: v.copy() for k, v in self.__fields__.items()}
        inst.__relations__ = {k: v.copy() for k, v in self.__relations__.items()}
        return inst
    
    def initialize_empty(self, **kwargs):
        self.maps = {}
        
        for attr in self.__attributes__.values():
            dim = kwargs.get(attr.dim, 0)
            attr.empty(dim)
            self.dimensions[attr.dim] = dim
            
        for rel in self.__relations__.values():
            dim = kwargs.get(attr.dim, 0)
            ixdim = self.dimensions.get(rel.map, 0)
            rel.index = range(ixdim)
            rel.empty(dim)
            
        for field in self.__fields__.values():
            field.empty()

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
        self.dimensions = {}
        self.maps = {}
        
        self.dimensions[newdim] = len(entities)
        
        for name, attr in self.__attributes__.items():
            child_attr = [e.get_attribute(attr.name) for e in entities]
            if attr.dim == newdim:
                self.__attributes__[name] = concatenate_fields(child_attr, newdim)
            else:
                child_attr = [e.get_attribute(attr.name) for e in entities]
                self.__attributes__[name] = concatenate_attributes(child_attr)
                self.dimensions[attr.dim] = self.__attributes__[name].size
                
                # Creating a value to retrieve old dimension values
                # from the new dimension values
                map_ = InstanceRelation('map', map=newdim, dim=attr.dim, index=range(self.dimensions[newdim]))
                map_.value = np.concatenate([np.repeat(i, c.size) for i,c in enumerate(child_attr)])
                self.maps[attr.dim, newdim] = map_
        
        for name, attr in self.__relations__.items():
            if newdim in attr.map:
                self.__relations__[name].index = range(self.dimensions[newdim])
            else:
                child_rel = [e.get_attribute(attr.name) for e in entities]
                self.__relations__[name] = concatenate_relations(child_rel)
                self.dimensions[attr.dim] = self.__relations__[name].size

                # Create the maps applies also to relations
                map_ = InstanceRelation('map', map=newdim, dim=attr.dim, index=range(self.dimensions[newdim]))
                map_.value = np.concatenate([np.repeat(i, c.size) for i, c in enumerate(child_rel)])
                self.maps[attr.dim, newdim] = map_
    
    def add_entity(self, entity, Entity):
        # We need to extend various attributes with new entities
        newdim = Entity.__dimension__
        
        for name, attr in self.__attributes__.items():
            attr.append(entity.get_attribute(name))
        
        for name, rel in self.__relations__.items():
            rel.append(entity.get_attribute(name))
        
        # We need to extend the maps
        for a, b in self.maps:
            # If destination is the dimension of the entity we are adding
            # we extend the map relation
            if newdim == b:
                # Create a new relation 
                # index = [0]
                # value = [0, 0, 0]
                additional_map = InstanceRelation('map', map=b, dim=a, index=[0])
                additional_map.value = [0] * entity.dimensions[a]
                # That get appended and transformed
                self.maps[a, b].append(additional_map)
        
    def subentity(self, Entity, index):
        """Return child entity"""
        dim = Entity.__dimension__
        entity = Entity.empty()
        
        if index >= self.dimensions[dim]:
            raise ValueError('index {} out of bounds for dimension {} (size {})'
                             .format(index, dim, self.dimensions[dim]))
        
        
        for name, attr in self.__attributes__.items():
            if attr.dim == dim:
                # If the dimension of the attributes is the same of the
                # dimension of the entity, we generate a field
                entity.__fields__[name] = attr.field(index)
            elif attr.dim in entity.dimensions:
                # Else, we generate an subattribute
                mapped_index = self.maps[attr.dim, dim].value == index
                entity.__attributes__[name] = attr.sub(mapped_index)
                entity.dimensions[attr.dim] = np.count_nonzero(mapped_index)

        for name, rel in self.__relations__.items():
            if rel.map == dim:
                # The relation is between entities we need to return
                # which means the entity doesn't know about that
                pass
            if rel.map in entity.dimensions:
                mapped_index = self.maps[rel.dim, dim].value == index
                entity.__relations__[name] = rel.sub(mapped_index)
                entity.dimensions[rel.dim] = np.count_nonzero(mapped_index)
                
                # We need to remap values
                convert_index = self.maps[rel.map, dim].value == index
                entity.__relations__[name].remap(convert_index.nonzero()[0],
                                                 range(entity.dimensions[rel.map]))
        
        return entity
    
    @contextmanager
    def batch(self):
        """Batch initialization"""
        _batch = []
        yield _batch
        if _batch:
            self._from_entities(_batch, _batch[0].__dimension__)
        
    def __repr__(self):
        lines = []
        lines.append('<Entity ' + type(self).__name__ + '>')
        lines.append('  Attributes:')
        [lines.append('    ' + str(attr)) for name, attr in sorted(self.__attributes__.items())]
        lines.append('  Relations:')
        [lines.append('    ' + str(attr)) for name, attr in sorted(self.__relations__.items())]
        lines.append('  Fields:')
        [lines.append('    ' + str(attr)) for name, attr in sorted(self.__fields__.items())]
        return '\n'.join(lines)

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
