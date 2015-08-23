"""
Base classes
"""

import numpy as np
import collections

from itertools import islice
from contextlib import contextmanager
from collections import defaultdict
from .attributes import (InstanceField, InstanceArray, 
                         InstanceRelation, InstanceAttribute, 
                         Field, Attribute, Relation)
from .serialization import data_to_json, json_to_data

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
            attr = self.get_attribute(name)
            if isinstance(attr, InstanceArray):
                if self.dimensions[attr.dim] != len(value):
                    raise ValueError('Dimension {} needs {} elements.'.format(attr.dim, 
                                                                              self.dimensions[attr.dim]))            
            attr.value = value
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
    
    @classmethod
    def from_dict(cls, dict_):
        """Read a ChemicalEntity that was exported using to_dict
        
        """
        return cls.from_arrays(**dict_)
    
    def to_dict(self):
        """Return a dict representing the ChemicalEntity that can be read back
        using from_dict.
        
        """
        
        ret = merge_dicts(self.__attributes__, self.__relations__, self.__fields__)
        ret = {k : v.value for k,v in ret.items()}
        ret['maps'] = {k : v.value for k,v in self.maps.items()}
        return ret 

    @classmethod
    def from_json(cls, string):
        """Create a ChemicalEntity from a json string 
        """
        return cls.from_dict(json_to_data(string))
    
    def to_json(self):
        """Return a json string representing the ChemicalEntity. This is
        useful for serialization.

        """
        return data_to_json(self.to_dict())
    
    def copy(self):
        """Create a copy of this ChemicalEntity
        
        """
        inst = super(type(self), type(self)).empty(**self.dimensions)
        
        # Need to copy all attributes, fields, relations
        inst.__attributes__ = {k: v.copy() for k, v in self.__attributes__.items()}
        inst.__fields__ = {k: v.copy() for k, v in self.__fields__.items()}
        inst.__relations__ = {k: v.copy() for k, v in self.__relations__.items()}
        inst.maps = {k: m.copy() for k, m in self.maps.items()}
        inst.dimensions = self.dimensions.copy()
        
        return inst

    def copy_from(self, other):
        """Copy properties from another ChemicalEntity
        
        """
        # Need to copy all attributes, fields, relations
        self.__attributes__ = {k: v.copy() for k, v in other.__attributes__.items()}
        self.__fields__ = {k: v.copy() for k, v in other.__fields__.items()}
        self.__relations__ = {k: v.copy() for k, v in other.__relations__.items()}
        self.maps = {k: m.copy() for k, m in other.maps.items()}
        self.dimensions = other.dimensions.copy()
    
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
            
            # Copy only existing fields or attributes
            if attr.name not in tpl.__fields__.keys() + tpl.__attributes__.keys():
                continue
            
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
        maps = kwargs.pop('maps') if 'maps' in kwargs else {}
        # We need to infer dimensions
        # From attributes
        dimensions = {}
        for dim in cls._dimensions():
            for attr_name in cls._attr_by_dimension(dim):
                if attr_name in kwargs:
                    
                    val = kwargs[attr_name]
                    dimensions[dim] = len(val) if val is not None else 0

        # From maps
        map_pool = defaultdict(set)
        for a, b in maps:
            map_pool[b] |= set(maps[a, b])
        
        for dim in map_pool:
            dimensions[dim] = len(map_pool[dim])

        obj = cls._empty(**dimensions)
        
        # Set the map structures
        for a, b in maps:
            if len(maps[a, b]) != dimensions[a]:
                raise ValueError('Map for {}->{} has wrong dimension ({}) should be ({})'
                                 .format(a, b, len(maps[a, b]), dimensions[a]))
            
            obj.maps[a, b] = InstanceRelation('map', 
                                              map=b, 
                                              dim=a,
                                              index=range(obj.dimensions[b]))
            obj.maps[a, b].value = maps[a, b]
        
        # Initialize attributes
        for k in kwargs:
            attr = obj.get_attribute(k)
            if isinstance(attr, (InstanceAttribute, InstanceField)):
                attr.value = kwargs[k]
            elif isinstance(attr, InstanceRelation):
                attr.index = range(obj.dimensions[attr.map])
                attr.value = kwargs[k]
        
        return obj
    

    def add_entity(self, entity, Entity):
        # We need to extend various attributes with new entities
        newdim = Entity.__dimension__
        
        if self.dimensions[newdim] == 0:
            # This is not initialized
            self._from_entities([entity], newdim)
            return
        
        # Update the dimensions
        self.dimensions[newdim] += 1
            
        for dim in self.dimensions:
            self.dimensions[dim] += entity.dimensions.get(dim, 0)
            
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


    def _propagate_dim(self, index, dimension, propagate=True):
        index = normalize_index(index)
        
        # Initialize
        result = defaultdict(set)
        for dim in self.dimensions:
            result[dim] |= set(range(self.dimensions[dim]))
        
        result[dimension] &= set(index)

        # Propagate for relations
        for rel in self.__relations__.values():            
            if rel.map == dimension:
                result[rel.dim] &= set(rel.argfilter(index))
        
        # Propagate for the attribute maps
        for (a, b), rel in self.maps.items():
            # This is where the attribute propagation happens
            if not propagate: continue
            
            if a == dimension:
                result[b] &= set(np.unique(rel.sub(index).value))                
                # We need to propagate for the attributes that changed
                prop = self._propagate_dim(np.array(sorted(result[b]), 'int'), b)
                for r in result:
                    result[r] &= set(prop[r])
            
            if b == dimension:
                result[rel.dim] &= set(rel.argfilter(index))


        return {k: np.array(sorted(v), 'int') for k, v in result.items()}
        
    def sub_dimension(self, index, dimension, propagate=True, inplace=False):
        """Return a ChemicalEntity sliced through a dimension.
        
        If other dimensions depend on this one those are updated accordingly.
        """
        filter_ = self._propagate_dim(index, dimension, propagate)
        
        if not inplace:
            inst = self.copy()
        else:
            inst = self
        
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
    
    def shrink_dimension(self, newdim, dimension):
        return self.sub_dimension(range(newdim),
                                  dimension, 
                                  propagate=False,
                                  inplace=True)

    def expand_dimension(self, newdim, dimension, maps={}, relations={}):
        ''' When we expand we need to provide new maps and relations as those
        can't be inferred '''
        
        for name, attr in self.__attributes__.items():
            if attr.dim == dimension:
                newattr = attr.copy()
                newattr.empty(newdim - attr.size)
                self.__attributes__[name] = concatenate_attributes([attr, newattr])

        for name, rel in self.__relations__.items():
            if dimension == rel.dim:
                # We need the new relation from the user
                if not rel.name in relations:
                    raise ValueError('You need to provide the relation {} for this resize'.format(rel.name))
                else:
                    if len(relations[name]) != newdim:
                        raise ValueError('New relation {} should be of size {}'.format(rel.name, newdim))
                    else:
                        self.__relations__[name].value = relations[name]
            
            elif dimension == rel.map:
                # Extend the index
                rel.index = range(newdim)
                
        for (a, b), rel in self.maps.items():
            if dimension == rel.dim:
                # We need the new relation from the user
                if not (a, b) in maps:
                    raise ValueError('You need to provide the map {}->{} for this resize'.format(a,  b))
                else:
                    if len(maps[a, b]) != newdim:
                        raise ValueError('New map {} should be of size {}'.format(rel.name, newdim))
                    else:
                        rel.value = maps[a, b]
            
            elif dimension == rel.map:
                # Extend the index
                rel.index = range(newdim)
        
        # Update dimensions
        self.dimensions[dimension] = newdim
        
        return self
        
    def _propagate_reorder(self, order, dimension):
        if len(set(order)) != self.dimensions[dimension]:
            raise ValueError('order must contain all distinct elements in dimension %s' % dimension)
        order = np.asarray(order)
        # Initialize
        result = { k: range(v) for k, v in self.dimensions.items() }
        
        # The actual dimension gets reordered normally
        result[dimension] = order
        
        # Propagate for attribute maps
        for (a, b), rel in self.maps.items():
            if rel.map == dimension:
                rel_new = rel.remap(order, rel.index, inplace=False)
                result[a] = np.argsort(rel_new.value)
        
        return {k: np.array(v, dtype='int') for k,v in result.items()}

        
    def reorder_dimension(self, order, dimension):
        reorder = self._propagate_reorder(order, dimension)
        
        # Attributes get reordered normally
        for name, attr in self.__attributes__.items():
            attr.reorder(reorder[attr.dim])
        
        # Relations get reordered and remapped
        for name, rel in self.__relations__.items():
            rel.reorder(reorder[rel.dim])
            rel.remap(reorder[rel.map], rel.index)
        
        # Maps get reordered too
        for name, rel in self.maps.items():
            rel.remap(rel.index, reorder[rel.map])
            rel.reorder(reorder[rel.dim])
        
        
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
        lines.append('  Dimensions: ' + str(self.dimensions))
        lines.append('  Attributes:')
        [lines.append('    ' + str(attr)) for name, attr in sorted(self.__attributes__.items())]
        lines.append('  Relations:')
        [lines.append('    ' + str(attr)) for name, attr in sorted(self.__relations__.items())]
        lines.append('  Fields:')
        [lines.append('    ' + str(attr)) for name, attr in sorted(self.__fields__.items())]
        return '\n'.join(lines)

    _from_arrays = from_arrays
    _empty = empty

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


def normalize_index(index):
    """normalize numpy index"""
    index = np.asarray(index)
    if index.dtype == 'bool':
        index = index.nonzero()[0]
    elif index.dtype == 'int':
        pass
    else:
        raise ValueError('Index should be either integer or bool')
    return index
