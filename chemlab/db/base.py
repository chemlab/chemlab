class EntryNotFound(Exception):
    pass

class AbstractDB(object):
    """Interface for a generic database.

    A typical database can be used to retrieve
    molecules by calling the *get* method::
        
      water = db.get("molecule", "example.water")

    A database can also provide custom functionalities to store or
    search for entries. Those are implemented in custom methods.
    
    See the other implementations for more relevant examples.

    """

    def get(self, feature, key, *args, **kwargs):
        '''Get a data entry from the database.
        
        Subclasses are required to implement this method to provide
        access to the database.

        **Parameters**
        
        - feature: str
            An identifier that represents the kind of data
            that we want to extract. Examples of such identifier are
            "system", "molecule", "data" etc.
        - key: str
            The key associated with the database entry. By convention
            you can use dotted names to provide some kind of nested structure.
        
        - args, kwargs:
             Custom extra arguments.
        '''
        raise NotImplementedError()
