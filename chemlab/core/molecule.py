import numpy as np
from collections import Counter
import numpy as np
from copy import copy

from ..libs.ckdtree import cKDTree
from ..db import ChemlabDB
cdb = ChemlabDB()

masses = cdb.get("data", "massdict")

from .attributes import MArrayAttr, MField
from .fields import AtomicField, FieldRequired
from .serialization import data_to_json, json_to_data

class Atom(object):
    '''
    Create an `Atom` instance. Atom is a generic container for
    particle data.
    
    .. seealso:: :doc:`/core`
        
    **Parameters**

      type: str
         Atomic symbol
      r: {np.ndarray [3], list [3]}
         Atomic coordinates in nm
      export: dict, optional
         Additional export information.
   
    
    **Example**

    >>> Atom('H', [0.0, 0.0, 0.0])
    
    In this example we're attaching additional data to the `Atom`
    instance. The `chemlab.io.GroIO` can use this information
    when exporting in the gro format.
    
    >>> Atom('H', [0.0, 0.0, 0.0], {'groname': 'HW1'})
  
    .. py:attribute:: type
       
       :Type: str
    
       The atomic symbol e.g. `Ar`, `H`, `O`.
    
    .. py:attribute:: r 
       
       :Type: np.ndarray(3) of floats
    
       Atomic position in *nm*.

    .. py:attribute:: mass
    
       :Type: float
    
       Mass in atomic mass units.
    
    .. py:attribute:: charge
    
       :Type: float
    
       Charge in electron charge units.

    .. py:attribute:: export
    
       :Type: dict
    
       Dictionary containing additional information when
       importing data from various formats.
    
       .. seealso:: :py:class:`chemlab.io.gro.GroIO`    
       
    .. py:attribute:: Atom.fields
    
       :Type: tuple
    
       This is a *class attribute*.
       The list of attributes that constitute the Atom. This is used
       to iterate over the `Atom` attributes at runtime. 
    
    '''

    fields = [AtomicField("type", default=False),
              AtomicField("r", default=lambda at: np.zeros(3,dtype=np.float)),
              AtomicField('export', default=lambda at: {}),
              AtomicField('mass', default=lambda at: masses[at.type]),
              AtomicField('charge', default=lambda at: 0.0)]
    
    def __init__(self, type, r, export=None):
        self.type = type
        self.r = np.array(r, dtype=np.float32)
        
        # Extra data for exporting reasons
        if export:
            self.export = export
        else:
            self.export = {}

        #self.atno = symbols.symbol_list.index(type.lower()) + 1
        self.mass = masses[type]
        self.charge = 0.0

    @classmethod
    def from_fields(cls, **kwargs):
        '''
        Create an `Atom` instance from a set of fields. This is a
        slightly faster way to initialize an Atom.
        
        **Example**

        >>> Atom.from_fields(type='Ar',
                             r_array=np.array([0.0, 0.0, 0.0]),
                             mass=39.948,
                             export={})
        '''
        self = cls.__new__(cls)
        
        for f in cls.fields:
            val = kwargs.get(f.name, None)
            if val == None:
                if f.default == False:
                    raise FieldRequired('{} field is required'.format(f.name))
                else:
                    f.set(self, f.default(self))
            else:
                f.set(self, val)
        
        return self

    def astype(self, cls):
        orig_cls = type(self)
        kwargs = dict((f.name, copy(f.get(self))) for f in orig_cls.fields)
        return cls.from_fields(**kwargs)
        
    def copy(self):
        '''Return a copy of the original Atom.
        '''

        cls = type(self)
        kwargs = dict((f.name, copy(f.get(self))) for f in cls.fields)
        return cls.from_fields(**kwargs)

    def __repr__(self):
        return "atom({})".format(self.type)




class Molecule(object):
    '''`Molecule` is a data container for a set of `N` *Atoms*.
    
    .. seealso:: :doc:`/core`

    **Parameters**
    
    atoms: list of :py:class:`Atom` instances
      Atoms that constitute the Molecule. Beware that the data
      **gets copied** and subsequend changes in the `Atom` instances
      will not reflect in the `Molecule`.
    
    export: dict, optional
      Export information for the Molecule 
    
    .. py:attribute:: r_array

       :type: np.ndarray((N,3), dtype=float)
       :derived from: Atom
    
       An array with the coordinates of each *Atom*.
    
    .. py:attribute:: type_array {numpy.array[N] of str}
    
       :type: np.ndarray(N, dtype=str)
       :derived from: Atom
    
       An array containing the chemical symbols of the
       constituent atoms.
    
    .. py:attribute::  m_array
    
       :type: np.ndarray(N, dtype=float)
       :derived from: Atom
    
       Array of masses.
    
    .. py:attribute:: charge_array

       :type: np.ndarray(N, dtype=float)
       :derived from: Atom
    
       Array of the charges present on the atoms.
    
    .. py:attribute:: atom_export_array
    
       :type: np.ndarray(N, dtype=object) *array of dicts*
       :derived from: Atom
    
       Array of `Atom.export` dicts.
    
       
    .. py:attribute:: n_atoms
    
       :type: int
    
       Number of atoms present in the molecule.
    
    .. py:attribute:: export

       :type: dict
    
       Export information for the whole Molecule.
    
    .. py:attribute:: bonds

       :type: np.ndarray((NBONDS,2), dtype=int)
    
       A list containing the indices of the atoms connected by a bond.
       Example: ``[[0 1] [0 2] [3 4]]``
    
    .. py:attribute:: mass
       
       :type: float
    
       Mass of the whole molecule in *amu*.
    
    .. py:attribute:: center_of_mass
    
       :type: float
    
    .. py:attribute:: geometric_center

       :type: float    
    
    .. py:attribute:: formula
    
       :type: str
    
       The brute formula of the Molecule. i.e. ``"H2O"``
       
    '''
    # Association between the Molecule array attribute and the atom one
    attributes = [MArrayAttr('type_array', 'type', object, default=False),
                  MArrayAttr('r_array', 'r', np.float, default=lambda mol: np.zeros((mol.n_atoms, 3), np.float)),
                  MArrayAttr('m_array', 'mass', np.float, default=lambda mol: np.array([masses[t] for t in mol.type_array])),
                  MArrayAttr('atom_export_array', 'export', object, default=lambda mol: np.array([{} for i in range(mol.n_atoms)])),
                  MArrayAttr('charge_array', 'charge', object, default=lambda mol: np.zeros(mol.n_atoms, np.float)),
                  ]
    
    fields = [MField('export', object, default=lambda mol: {}),
              MField('bonds', object, default=lambda mol: np.array([], dtype=object))]
    
    derived = ('formula',)
    
    def __init__(self, atoms, bonds=None, export=None):
        self.n_atoms = len(atoms)

        for attr in self.attributes:
            setattr(self, attr.name,
                    np.array([getattr(a, attr.fieldname)
                              for a in atoms], dtype=attr.dtype))
            # Example:
            # self.r_array = np.array([a.r for a in atoms], dtype=np.float64)

        # Extra data for exporting reasons
        if export:
            self.export = export
        else:
            self.export = {}

        if bonds is None:
            self.bonds = np.array([], dtype='int')
        else:
            self.bonds = np.array(bonds, dtype='int')

    def move_to(self, r):
        '''Translate the molecule to a new position *r*.
        '''
        dx = r - self.r_array[0]
        self.r_array += dx

            
        
    @classmethod
    def from_arrays(cls, **kwargs):
        '''Create a Molecule from a set of Atom-derived arrays. 
        Please refer to the Molecule *Atom Derived Attributes*.
        Only *r_array* and *type_array* are absolutely required,
        the others are optional.

        >>> Molecule.from_arrays(r_array=np.array([[0.0, 0.0, 0.0],
                                                   [1.0, 0.0, 0.0],
                                                   [0.0, 1.0, 0.0]]),
                                 type_array=np.array(['O', 'H', 'H']))
        molecule(H2O)

        Initializing a molecule in this way can be much faster than
        the default initialization method.        
        
        '''
        # Test for required fields:
        if 'type_array' not in kwargs:
            raise Exception('type_array is a required argument')
        
        inst = cls.__new__(cls)
        inst.n_atoms = len(kwargs['type_array'])
        
        for attr in cls.attributes:
            # Get the value from the passed arguments
            val = kwargs.get(attr.name, None)
            
            if val == None:
                # If the value is None set the attribute to its
                # default value
                attr.set(inst, attr.default(inst))
            else:
                # Set the attribute to the passed value
                attr.set(inst, val)
        
        for field in cls.fields:
            val = kwargs.get(field.name, None)
            if val == None:
                # If the value is None set the field to its
                # default value
                field.set(inst, field.default(inst))
            else:
                # Set the attribute to the passed value
                field.set(inst, val)
        
        return inst

    def astype(self, cls):
        orig_cls = type(self)
        kwargs = {}
        
        
        # Attributes
        for attr in orig_cls.attributes:
            kwargs[attr.name] = attr.get(self)
        
        # Fields
        for field in orig_cls.fields:
            kwargs[field.name] = field.get(self)

        return cls.from_arrays(**kwargs)
        
        
    @property
    def mass(self):
        return self.m_array.sum()
    
    @property
    def center_of_mass(self):
        return ((self.m_array * self.r_array)/self.m_array.sum()).sum(axis=0)

    @property
    def geometric_center(self):
        return self.r_array.sum(axis=0)/len(self.r_array)
        

    def tojson(self):
        """Return a json string representing the Molecule. This is
        useful for serialization.

        """
        return data_to_json(self.todict())

    @classmethod
    def from_json(cls, string):
        return cls.from_arrays(**json_to_data(string))
        
    def todict(self):
        cls = type(self)
        kwargs = {}
        # Attributes
        for attr in cls.attributes:
            kwargs[attr.name] = copy(attr.get(self))

        # Fields
        for field in cls.fields:
            kwargs[field.name] = copy(field.get(self))

        return kwargs
        
        
    def __repr__(self):
        return "molecule({})".format(self.formula)
    
    def copy(self):
        '''Return a copy of the molecule instance

        '''
        cls = type(self)
        
        kwargs = self.todict()
        
        for k, val in kwargs.items():
            kwargs[k] = copy(val)
            
        return cls.from_arrays(**kwargs)
        
    def guess_bonds(self):
        """Guess the molecular bonds by using covalent radii
        information.

        """
        self.bonds = guess_bonds(self.r_array, self.type_array)
        
    @property
    def n_bonds(self):
        return len(self.bonds)
        
    @property
    def formula(self):
        return make_formula(self.type_array)

# Those functions have a separate life
def guess_bonds(r_array, type_array):
    covalent_radii = cdb.get('data', 'covalentdict')
    MAXRADIUS = 0.3
    
    # Find all the pairs
    ck = cKDTree(r_array)
    pairs = ck.query_pairs(MAXRADIUS)
    
    bonds = []
    for i,j in pairs:
        threshold = 0.01
        a, b = covalent_radii[type_array[i]], covalent_radii[type_array[j]]
        rval = a + b
        

        thr_a = rval - threshold
        thr_b = rval + threshold 
        
        #thr_a2 = thr_a * thr_a
        thr_b2 = thr_b * thr_b
        dr2  = ((r_array[i] - r_array[j])**2).sum()
        
        if dr2 < thr_b2:
            bonds.append((i, j))
    return np.array(bonds)
    
def make_formula(elements):
    c = Counter(elements)
    formula = ''
    if c["C"] != 0:
        formula += "C{}".format(c["C"])
        del c["C"]

    if c["H"] != 0:
        formula += "H{}".format(c["H"])
        del c["H"]

    for item, count in sorted(c.items()):
        if count ==1:
            formula += item
        else:
            formula += "{}{}".format(item, count)

    return formula

    
