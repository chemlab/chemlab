import os
import difflib

from .iohandler import make_ionotavailable
from .gro import GromacsIO
from .pdb import PdbIO
from .edr import EdrIO
from .xyz import XyzIO

try:
    from .xtctrr import XtcIO
except ImportError:
    XtcIO = make_ionotavailable('XtcIO',
                                'To enable XTC file reading install library pyxdr',
                                can_read = ['trajectory'])

# NOTE: We are adding the default handlers at the end of the file
_default_handlers = [
    [GromacsIO, 'gro', '.gro'],
    [XtcIO, 'xtc', '.xtc'],
    [PdbIO, 'pdb', '.pdb'],
    [EdrIO, 'edr', '.edr'],
    [XyzIO, 'xyz', '.xyz']
]

class DataFile(object):
    
    handlers = {}
    extensions = {}
    
    @classmethod
    def add_handler(cls, ioclass, format, extension=None):
        """Register a new data handler for a given format.
        
        Parameters
        ----------
        ioclass: IOHandler subclass
        format: str
          A string identifier representing the format
        extension: str, optional
          The file extension associated with the format.
        
        """
        
        
        if format in cls.handlers:
            print "Warning: format %s already present."%format

        cls.handlers[format] = ioclass
        
        if extension in cls.extensions:
            print "Warning: extension %s already handled by %s handler."%(extension, cls.extensions[extension])
            
        cls.extensions[extension] = format
        
    def __init__(self, filename, format=None):
        cls = type(self)
        # Add the default handlers
        
        
        if format is None:
            base, ext = os.path.splitext(filename)
            
            if ext in cls.extensions:
                self.format = format = cls.extensions[ext]
            else:
                raise ValueError("Unknown format for %s extension." % ext)    
        
        if format in cls.handlers:
            hc = cls.handlers[format]
            self.handler_class = hc
            self.handler = hc(filename)
        else:
            matches = difflib.get_close_matches(format, cls.handlers.keys())
            raise ValueError("Unknown Handler for format %s, close matches: %s"
                             % (format, str(matches)))

    def read(self, feature, *args, **kwargs):
        self._check_feature(feature, "read")
        return self.handler.read(feature, *args, **kwargs)
        
        
    def write(self, feature, value, *args, **kwargs):
        self._check_feature(feature, "write")
        return self.handler.write(feature, value, *args, **kwargs)
    
    
    def _check_feature(self, feature, what):
        if what == "read":
            features = self.handler_class.can_read
        if what == "write":
            features = self.handler_class.can_write
            
        if feature not in features:
            matches = difflib.get_close_matches(feature, features)
            raise ValueError("Feature %s not present in %s. Close matches: %s"
                             % (feature, str(self.handler_class), str(matches)))
        


# Registering the handlers
for h in _default_handlers:
    DataFile.add_handler(*h)
    