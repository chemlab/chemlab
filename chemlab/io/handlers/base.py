import difflib

class FeatureNotAvailable(Exception):
    pass

class IOHandler(object):
    """Generic base class for file readers and writers.

    The initialization function takes a file-like object *fd*, as an
    argument.
    
    Subclasses can extend the methods *__init__*, *read* and *write*
    to implement their reading and writing routines.
    
    **Attributes**
    
    .. py:attribute:: fd
    
    .. py:attribute:: IOHandler.can_read
        
        :type: list of str
    
        A list of *features* that the handler can read.
    
    .. py:attribute:: IOHandler.can_write
    
        :type: list of str
        
        A list of *features* that IOHandler can write.

    """

    can_read = []
    can_write = []
    
    def __init__(self, fd):
        # TODO: This is a deprecation warning
        if isinstance(fd, str):
            raise Exception("IOHandler takes a file-like object as its first argument")
        
        self.fd = fd

    def read(self, feature, *args, **kwargs):
        """Read and return the feature *feature*. It should raise an
        ValueError if the feature is not present in the handler
        *can_read* attribute, use the method
        :py:meth:`IOHandler.check_feature` to provide this behaviour.
        
        Certain features may require additional arguments, and it is
        possible to pass those as well.
        
        **Example**
        
        Subclasses can reimplement this method to add functionality::
        
            class XyzIO(IOHandler):
                can_read = ['molecule']
        
                def read(self, feature, *args, **kwargs):
                    self.check_feature(feature, "read")
                    if feature == 'molecule':
                       # Do stuff
                       return geom
        
        """

        self.check_feature(feature, "read")
        
    def write(self, feature, value, *args, **kwargs):
        """Same as  :py:meth:`~chemlab.io.iohandler.IOHandler.read`. You have to pass
        also a *value* to write and you may pass any additional 
        arguments.
        
        **Example**
        
        ::
        
            class XyzIO(IOHandler):
                can_write = ['molecule']
        
                def write(self, feature, value, *args, **kwargs):
                    self.check_feature(feature, "write")
                    if feature == 'molecule':
                       # Do stuff
                       return geom
        
        """
        if 'w' not in self.fd.mode and 'x' not in self.fd.mode:
            raise Exception("The file is not opened in writing mode. If you're using datafile, add the 'w' option.\ndatafile(filename, 'w')")
        
        self.check_feature(feature, "write")
        
    def check_feature(self, feature, readwrite):
        """Check if the *feature* is supported in the handler and
        raise an exception otherwise.

        **Parameters**
        
        feature: str
            Identifier for a certain feature.
        readwrite: "read" or "write"
            Check if the feature is available for reading or writing.
        
        """

        if readwrite == "read":
            features = self.can_read
        if readwrite == "write":
            features = self.can_write
            
        if feature not in features:
            matches = difflib.get_close_matches(feature, features)
            raise FeatureNotAvailable("Feature %s not present in %s. Close matches: %s"
                                      % (feature, str(type(self).__name__),
                                         str(matches)))

class FormatNotSupported(ValueError):
    pass

def make_ionotavailable(name, msg, can_read = [], can_write = []):
    def read(self, feature):
        raise Exception(msg)
    def write(self, feature):
        raise Exception(msg)
        
    new_class = type(name, (IOHandler,), {
        'can_read' : can_read,
        'can_write': can_write,
        'read' : read,
        'write': write
    })
    
    return new_class