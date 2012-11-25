from core.molecule import Molecule, Atom, Bond
from .graphics.viewer import Viewer
from .dataparsers import DataFile
from .core.system import System, MonatomicSystem


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

def display(molecule):
    """Display a *molecule* (that have to be an instance of the
    Molecule class) using the chemlab viewer.

    """
    vw = Viewer()
    vw.molecule = molecule
    vw.show()

def animate(molecule_list, timestep=1.0/60):
    """Display a list of Molecule instances *molecule_list* in an
    animation, the *timestep* attribute sets the timestep in
    seconds.

    """
    vw = Viewer()
    vw.animate(molecule_list, timestep)
    vw.show()
