from core.molecule import Molecule, Atom, Bond
from .viewer.viewer import Viewer
from .dataparsers import DataFile

def read_datafile(filename, format):
    """Read and parse the file *filename* that has the format
    *format*.  Returns a `DataFile` object. The available properties
    are stored in the attribute `DataFile.properties'. To retrieve a
    property, for example the property *geometry* simply do:

    >>> df = read_datafile("mol.out", "gamout")
    >>> mol = df["geometry"]
    
    To know the other properties refer to the documentation of the
    data parsers.

    Available formats are:

    - gamout, gamess output file.

    """

    return DataFile(filename, format)

def readgeom(filename, format):
    """Read and parse the file *filename* and retrieve the geometry
    present in it.

    Return a `Molecule` object

    Available formats are:

    - tinkerxyz
    """
    
    df = DataFile(filename, format)
    return df["geometry"]

