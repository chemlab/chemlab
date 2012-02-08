from .datafile import DataFile

def readdata(filename, format):
    """Read a chemistry file format datafile in order to retrieve all
    the possible information from it. Returns a DataFile object.
    
    This function is mostly an alias.

    """
    return DataFile(filename, format)
    
__all__ = ["readdata"]