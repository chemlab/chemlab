import os
import difflib
try:
    from urllib.request import urlopen
    from urllib.parse import urlparse
except ImportError: # python 2
    from urllib2 import urlopen
    from urlparse import urlparse

from .handlers.base import make_ionotavailable
from .handlers import GromacsIO
from .handlers import PdbIO
from .handlers import EdrIO
from .handlers import XyzIO
from .handlers import XtcIO
from .handlers import MolIO
from .handlers import CmlIO
from .handlers import CifIO
from .handlers import HdfIO
from .handlers import Mol2IO

# NOTE: We are adding the default handlers at the end of the file
_default_handlers = [
    [GromacsIO, 'gro', '.gro'],
    [XtcIO, 'xtc', '.xtc'],
    [PdbIO, 'pdb', '.pdb'],
    [EdrIO, 'edr', '.edr'],
    [XyzIO, 'xyz', '.xyz'],
    [MolIO, 'mol', '.mol'],
    [CmlIO, 'cml', '.cml'],
    [CifIO, 'cif', '.cif'],
    [HdfIO, 'hdf', '.h5'],
    [Mol2IO, 'mol2', '.mol2']
]

_handler_map = {}
_extensions_map = {}

def add_default_handler(ioclass, format, extension=None):
    """Register a new data handler for a given format in
       the default handler list.

       This is a convenience function used internally to setup the
       default handlers. It can be used to add other handlers at
       runtime even if this isn't a suggested practice.

       **Parameters**

       ioclass: IOHandler subclass
       format: str
         A string identifier representing the format
       extension: str, optional
         The file extension associated with the format.

    """
    if format in _handler_map:
        print("Warning: format {} already present.".format(format))

    _handler_map[format] = ioclass

    if extension in _extensions_map:
        print("Warning: extension {} already handled by {} handler."
              .format(extension, _extensions_map[extension]))

    if extension is not None:
        _extensions_map[extension] = format

# Registering the default handlers
for h in _default_handlers:
    add_default_handler(*h)

# We add also the cclib handlers
load_cclib = False
try:
    import cclib
    load_cclib = True
except ImportError:
    print('cclib not found. Install cclib for more handlers.')

if load_cclib:
    from .handlers._cclib import _cclib_handlers
    for hclass, format in _cclib_handlers:
        add_default_handler(hclass, format)

def get_handler_class(ext):
    """Get the IOHandler that can handle the extension *ext*."""

    if ext in _extensions_map:
        format = _extensions_map[ext]
    else:
        raise ValueError("Unknown format for %s extension." % ext)

    if format in _handler_map:
        hc = _handler_map[format]
        return hc
    else:
        matches = difflib.get_close_matches(format, _handler_map.keys())
        raise ValueError("Unknown Handler for format %s, close matches: %s"
                         % (format, str(matches)))


def datafile(filename, mode="rb", format=None):
    """Initialize the appropriate
    :py:class:`~chemlab.io.iohandler.IOHandler` for a given file
    extension or file format.

    The *datafile* function can be conveniently used to quickly read
    or write data in a certain format::

        >>> handler = datafile("molecule.pdb")
        >>> mol = handler.read("molecule")
        # You can also use this shortcut
        >>> mol = datafile("molecule.pdb").read("molecule")

    **Parameters**

    filename: str
          Path of the file to open.
    format: str or None
          When different from *None*, can be used to specify a
          format identifier for that file. It should be used when
          the extension is ambiguous or when there isn't a specified
          filename. See below for a list of the formats supported by chemlab.

    """

    filename = os.path.expanduser(filename)
    base, ext = os.path.splitext(filename)

    if format is None:
        hc = get_handler_class(ext)
    else:
        hc = _handler_map.get(format)
        if hc is None:
            raise ValueError('Format {} not supported.'.format(format))

    fd = open(filename, mode)

    handler = hc(fd)
    return handler


def remotefile(url, format=None):
    """The usage of *remotefile* is equivalent to
    :func:`chemlab.io.datafile` except you can download a file from a
    remote url.

    **Example**

        mol = remotefile("https://github.com/chemlab/chemlab-testdata/blob/master/3ZJE.pdb").read("molecule")

    """

    if format is None:
        res = urlparse(url)
        filename, ext = os.path.splitext(res.path)

        hc = get_handler_class(ext)
    else:
        hc = _handler_map.get(format)
        if hc is None:
            raise ValueError('Format {} not supported.'.format(format))

    fd = urlopen(url)
    handler = hc(fd)
    return handler
