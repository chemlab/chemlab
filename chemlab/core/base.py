"""
Base classes
"""
import numpy as np
from pandas.hashtable import Int64HashTable
import collections
from collections import defaultdict
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
        index = np.asarray(index)
        if index.dtype == 'bool':
            index = index.nonzero()[0]
        
        inst = self.copy()
        size = len(index)
        inst.empty(size)
        
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
        if attr_or_field.value is None:
            return
        
        # We deal also when the values are None
        if isinstance(attr_or_field, InstanceAttribute):
            if self.value is None:
                self.value = attr_or_field.value
            else:
                self.value = np.append(self.value, attr_or_field.value, axis=0)
        elif isinstance(attr_or_field, InstanceField):
            if self.value is None:
                self.value = [attr_or_field.value]
            else:
                self.value = np.append(self.value, [attr_or_field.value], axis=0)
        else:
            raise ValueError('Can append only InstanceAttribute or InstanceField')
    def __repr__(self):
        value_str = str(self.value).replace('\n', ' ')
        if len(value_str) > 52:
            value_str = value_str[:52] + ' ...'
        return '<Attribute[{}={}] {} = {}>'.format(self.dim, self.size, self.name, value_str)


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
        if rel.value is None:
            return
        if self.value is None:
            self.value = rel.value
        else:
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

    def reindex(self, inplace=True):
        if inplace:
            obj = self
        else:
            obj = self.copy()
        
        newindex = range(len(obj.index))
        obj.remap(obj.index, newindex)
        obj.index = newindex
        return obj

    def argfilter(self, index):
        newindex = self.index[index]
        newrel = self.remap(newindex, newindex, inplace=False)
        
        # We select only the values that are in the map
        mask = newrel.value != -1
        if len(mask.shape) == 2:
            mask = np.all(mask, axis=1)
        elif len(mask.shape) == 1:
            pass
        else:
            raise ValueError('filter only works for shapes for lenth 1 or 2')
        
        return mask.nonzero()[0]
    
    def filter(self, index):
        mask = self.argfilter(index)
        newrel = self.sub(mask)
        newrel.index = newrel.index[index]
        return newrel
        
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
        value_str = str(self.value).replace('\n', '')
        if len(value_str) > 52:
            value_str = value_str[:52] + ' ...'
                
        return '<Relation[{}={}] {} = {} {{Ix[{}={}]: {}}}>'.format(self.dim, self.size, 
                                           self.name, value_str, self.map, len(self.index), str(self.index))

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
        
        # Dimensions get initialized at 0
        instance.dimensions = { attr.dim: 0 for attr in merge_dicts(instance.__attributes__, 
                                                                    instance.__relations__).values()}
        # No subentity information at the beginning
        instance.maps = {}
        
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
        inst = super(type(self), type(self)).empty(**self.dimensions)
        
        # Need to copy all attributes, fields, relations
        inst.__attributes__ = {k: v.copy() for k, v in self.__attributes__.items()}
        inst.__fields__ = {k: v.copy() for k, v in self.__fields__.items()}
        inst.__relations__ = {k: v.copy() for k, v in self.__relations__.items()}
        inst.maps = {k: m.copy() for k, m in self.maps.items()}
        inst.dimensions = self.dimensions.copy()
        
        return inst
    
    def initialize_empty(self, **kwargs):
        self.dimensions.update(kwargs)
        
        for attr in self.__attributes__.values():
            attr.empty(self.dimensions[attr.dim])
            
        for rel in self.__relations__.values():
            ixdim = self.dimensions[rel.map]
            rel.index = range(ixdim)
            rel.empty(self.dimensions[rel.dim])
            
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
        if len(entities) == 0:
            return # Nothing to be done here
        
        # Pick one object as template, we assume they're all of the same kind
        tpl = entities[0]
        
        # Populate dimensions
        self.dimensions[newdim] = len(entities)
        for dim in self.dimensions:
            if dim in tpl.dimensions:
                # Make the sub-attribute structure
                subattr_map = InstanceRelation('map', map=newdim, 
                                                dim=dim, 
                                                index=range(self.dimensions[newdim]))
                subattr_map.value = np.concatenate([[i] * e.dimensions[dim] for i, e in enumerate(entities)])
                
                # TODO: redundant
                self.maps[dim, newdim] = subattr_map
                
                self.dimensions[dim] = sum(e.dimensions[dim] for e in entities)
        
        for name, attr in self.__attributes__.items():
            # Concatenate fields in new, independent, attributes
            child_attr = [e.get_attribute(attr.name) for e in entities]
            if attr.dim == newdim:
                self.__attributes__[name] = concatenate_fields(child_attr, newdim)
            else:
                # Concatenate sub-attributes
                child_attr = [e.get_attribute(attr.name) for e in entities]
                self.__attributes__[name] = concatenate_attributes(child_attr)

        # Concatenate relations as well
        for name, attr in self.__relations__.items():
            if newdim in attr.map:
                self.__relations__[name].index = range(self.dimensions[newdim])
            else:
                child_rel = [e.get_attribute(attr.name) for e in entities]
                self.__relations__[name] = concatenate_relations(child_rel)

    @classmethod
    def _attr_by_dimension(cls, dim):
        return [name for name, attr in merge_dicts(cls.__attributes__, cls.__relations__).items() if attr.dim == dim]
    
    @classmethod
    def _dimensions(cls):
        return set(attr.dim for attr in merge_dicts(cls.__attributes__, cls.__relations__).values())

    @classmethod
    def from_arrays(cls, **kwargs):
        maps = kwargs.pop('maps')
        # We need to infer dimensions
        # From attributes
        dimensions = {}
        for dim in cls._dimensions():
            for attr_name in cls._attr_by_dimension(dim):
                if attr_name in kwargs:
                    dimensions[dim] = len(kwargs[attr_name])
        
        # From maps
        map_pool = defaultdict(set)
        for a, b in maps:
            map_pool[b] |= set(maps[a, b])
        
        for dim in map_pool:
            dimensions[dim] = len(map_pool[dim])

        obj = cls.empty(**dimensions)
        
        # Set the map structures
        for a, b in maps:
            obj.maps[a, b] = InstanceRelation('map', 
                                              map=b, 
                                              dim=a,
                                              index=range(obj.dimensions[b]))
            obj.maps[a, b].value = maps[a, b]
        
        # Initialize attributes
        for k in kwargs:
            attr = obj.get_attribute(k)
            if isinstance(attr, InstanceAttribute):
                attr.value = kwargs[k]
            elif isinstance(attr, InstanceRelation):
                attr.index = range(obj.dimensions[attr.map])
                attr.value = kwargs[k]
        
        
        return obj
    
    def add_entity(self, entity, Entity):
        # We need to extend various attributes with new entities
        newdim = Entity.__dimension__
        
        # Update the dimensions
        self.dimensions[newdim] += 1
        
        for dim in self.dimensions:
            if dim in entity.dimensions:
                # Update the sub-attribute structure to accomodate for
                # extra attributes
                additional_map = InstanceRelation('map', map=newdim, dim=dim, index=[0])
                additional_map.value = [0] * entity.dimensions[dim]
                # That get appended and transformed
                self.maps[dim, newdim].append(additional_map)
                
        for name, attr in self.__attributes__.items():
            # This takes care of attributes and fields
            attr.append(entity.get_attribute(name))
        
        for name, rel in self.__relations__.items():
            rel.append(entity.get_attribute(name))
    
        
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

    def _propagate_dim(self, index, dimension):
        #TODO Propagate filter?
        index = np.asarray(index)
        if index.dtype == 'bool':
            index = index.nonzero()[0]
        elif index.dtype == 'int':
            pass
        else:
            raise ValueError('sub_dimension only supports integer or bool arrays')
        
        result = defaultdict(set)
        
        for dim in self.dimensions:
            result[dim] |= set(range(self.dimensions[dim]))
        
        result[dimension] &= set(index)
        
        # Propagate for the attribute maps
        for (a, b), rel in self.maps.items():
            if a == dimension:
                result[b] &= set(np.unique(rel.sub(index).value))

        # Propagate for relations
        for rel in self.__relations__.values():
            if rel.map == dimension:
                result[rel.dim] &= set(rel.argfilter(index))

        return {k: np.array(sorted(v), 'int') for k, v in result.items()}
        
    def sub_dimension(self, index, dimension):
        """Return a ChemicalEntity sliced through a dimension.
        
        If other dimensions depend on this one those are updated accordingly.
        """
        index = np.asarray(index)
        if index.dtype == 'bool':
            index = index.nonzero()[0]
        elif index.dtype == 'int':
            pass
        else:
            raise ValueError('sub_dimension only supports integer or bool arrays')
        
        filter_ = self._propagate_dim(index, dimension)
        
        inst = self.copy()
        inst.dimensions = {k: len(f) for k, f in filter_.items()}
        
        for name, attr in self.__attributes__.items():
            inst.__attributes__[name] = attr.sub(filter_[attr.dim])

        for name, rel in self.__relations__.items():
            inst.__relations__[name] = rel.sub(filter_[rel.dim])
            inst.__relations__[name].index = rel.index[filter_[rel.map]]
            inst.__relations__[name].reindex()
            
        for (a, b), rel in self.maps.items():
            inst.maps[a, b] = rel.sub(filter_[a])
            inst.maps[a, b].index = rel.index[filter_[b]]
            inst.maps[a, b].reindex()
        
        return inst

    def concat(self, other, inplace=False):
        '''Concatenate two ChemicalEntity of the same kind'''
        
        # Create new entity
        if inplace:
            obj = self
        else:
            obj = self.copy()
        
        # Stitch every attribute
        for name, attr in obj.__attributes__.items():
            attr.append(other.__attributes__[name])
            
        # Stitch every relation
        for name, rel in obj.__relations__.items():
            rel.append(other.__relations__[name])
        
        # Update maps
        # Update dimensions
        
        if obj.is_empty():
            obj.maps = {k: m.copy() for k, m in other.maps.items()}
            obj.dimensions = other.dimensions.copy()
        else:
            for (a, b), rel in obj.maps.items():
                rel.append(other.maps[a, b])
            for d in obj.dimensions:
                obj.dimensions[d] += other.dimensions[d]
        
        return obj
    
    def is_empty(self):
        return sum(self.dimensions.values()) == 0
    
    @contextmanager
    def batch(self):
        """Batch initialization"""
        _batch = []
        yield _batch
        if _batch:
            new_part = super(type(self), type(self)).empty()
            new_part._from_entities(_batch, _batch[0].__dimension__)
            self.concat(new_part, inplace=True)
        
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
