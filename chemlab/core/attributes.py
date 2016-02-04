import numpy as np
import six.moves
from six import string_types

class EntityProperty(object):
    '''Main base class for ChemicalEntity property specification'''


class Attribute(EntityProperty):
    def __init__(self, shape=None, dtype=None, dim=None, alias=None):
        '''An array of values that belong to the current ChemicalEntity.'''
        
        if not isinstance(dim, string_types):
            raise ValueError('dim parameter is required and should be a string.')
        
        self.shape = shape
        self.dtype = dtype
        self.dim = dim
        self.alias = alias
    
    def create(self, name):
        return InstanceAttribute(name, self.shape, self.dtype, self.dim, self.alias)

class Relation(EntityProperty):
    def __init__(self, map=None, dim=None, alias=None, shape=None):
        '''An array of values that connects items belonging to the same dimension'''
        
        if not isinstance(dim, string_types):
            raise ValueError('dim parameter is required and should be a string.')
        if not isinstance(map, string_types):
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
        '''A single value that belongs to the current ChemicalEntity'''
        
        # A one-dimensional attribute
        self.dtype = dtype
        self.alias = alias
        self.shape = shape
    
    def create(self, name):
        return InstanceField(name, self.dtype, self.shape, self.alias)

class InstanceProperty(object):
    '''Instanced version of EntityProperty'''

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
            obj.value = value.copy()
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
        else:
            raise ValueError("Only array and lists are supported")

    def reorder(self, neworder, inplace=True):
        if self.value is None:
            return # No reordering
        else:
            if len(neworder) != self.size:
                raise ValueError("'%s': neworder doesn't have enough elements %d (value %d)" % (self.name, len(neworder), self.size))
            
            if set(neworder) != set(range(self.size)):
                raise ValueError("'%s': the new order is invalid as it doesn't contain all the indices." % self.name)
            
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
        
        if self.size < len(index):
            raise ValueError('Can\'t subset "{}": index ({}) is bigger than the number of elements ({})'.format(self.name, len(index), self.size))
        
        inst = self.copy()
        size = len(index)
        inst.empty(size)
        
        if len(index) > 0:
            inst.value = self.value.take(index, axis=0)
        
        return inst

class InstanceAttribute(InstanceArray):
    
    def __init__(self, name, shape=None, dtype=None, dim=None, alias=None):
        if not isinstance(dim, string_types):
            raise ValueError('dim parameter is required and should be a string.')
        self.name = name
        self.shape = shape
        self.dtype = dtype
        self.dim = dim
        self.alias = alias
        self.value = None
    
    def copy(self):
        obj = type(self)(self.name,
                         shape=self.shape,
                         dtype=self.dtype,
                         dim=self.dim,
                         alias=self.alias)
        obj.value = self.value.copy() if self.value is not None else None
        return obj
    
    def field(self, index):
        obj = InstanceField(name=self.name, dtype=self.dtype, shape=self.shape, alias=self.alias)
        
        if self.value is None:
            raise ValueError("Attribute '%s' is not initialized" % (self.name))
        
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
        if not isinstance(dim, string_types):
            raise ValueError('dim parameter is required and should be a string.')

        if not isinstance(map, string_types):
            raise ValueError('map parameter is required and should be a string.')
        
        if not isinstance(name, string_types):
            raise ValueError('name parameter should be a string')

        if not isinstance(index, (list, six.moves.range, np.ndarray)):
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
        obj.value = self.value.copy() if self.value is not None else None
        obj.index = self.index.copy() if self.index is not None else None
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
        if (not isinstance(from_map, (list, np.ndarray, six.moves.range)) or 
            not isinstance(to_map, (list, np.ndarray, six.moves.range))):
            raise ValueError('from_map and to_map should be either lists or arrays')
        
        if self.value is None:
            # Nothing to remap
            if inplace:
                return 
            else:
                return self.copy()
            
        # Remap columns -- pandas version
        # hashtable = Int64HashTable()
        # hashtable.map(np.asarray(from_map),
        #               np.asarray(to_map))
        # mapped = hashtable.lookup(self.value.flatten('F'))
        
        # This is quite a clever trick to efficiently remap column,
        # the idea is similar to an hashmap.
        stupidhash = np.empty(max(from_map) + 2)
        stupidhash.fill(-1)
        stupidhash[np.array(from_map)] = to_map
        mapped = stupidhash.take(self.value.flatten('F'), mode='clip')

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
        if self.size == 0:
            # No relations are defined here, we don't have to filter anything
            return index
        
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
        
        elif isinstance(value, (list, six.moves.range)):
            self._index = np.asarray(value, dtype='int')
        
        elif isinstance(value, np.ndarray):
            self._index = np.asarray(value, dtype='int')
        
        else:
            raise ValueError("Can't set index. Type not allowed {}".format(type(value)))
    
    @property
    def value(self):
        return super(InstanceRelation, self).value
    
    @value.setter
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
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        if self.shape is None:
            self._value = value
        else:
            if value is None:
                self.empty()
            else:
                value = np.asarray(value)
                if self.shape != value.shape:
                    raise ValueError('Field {}, shape mismatch: got {} instead of {}'.format(self.name, value.shape, self.shape))
                self._value = value
    
    def __repr__(self):
        return '<Field: {} = {}>'.format(self.name, str(self.value))
