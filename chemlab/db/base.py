class EntryNotFound(Exception):
    pass

class AbstractDB(object):
    """Abstract class for a general database
    """

    def get(self, feature, key, *args, **kwargs):
        pass
