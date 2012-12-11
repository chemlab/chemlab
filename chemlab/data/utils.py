# Utilities for data handling

class InsensitiveDict:
    """Dictionary, that has case-insensitive keys.

    Normally keys are retained in their original form when queried with
    .keys() or .items().  If initialized with preserveCase=0, keys are both
    looked up in lowercase and returned in lowercase by .keys() and .items().
    """
    """
    Modified recipe at
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66315 originally
    contributed by Sami Hangaslammi.
    """

    def __init__(self, dict=None, preserve=1):
        """Create an empty dictionary, or update from 'dict'."""
        self.data = {}
        self.preserve=preserve
        if dict:
            self.update(dict)

    def __delitem__(self, key):
        k=self._lowerOrReturn(key)
        del self.data[k]

    def _lowerOrReturn(self, key):
        if isinstance(key, str) or isinstance(key, unicode):
            return key.lower()
        else:
            return key

    def __getitem__(self, key):
        """Retrieve the value associated with 'key' (in any case)."""
        k = self._lowerOrReturn(key)
        return self.data[k][1]

    def __setitem__(self, key, value):
        """Associate 'value' with 'key'. If 'key' already exists, but
        in different case, it will be replaced."""
        k = self._lowerOrReturn(key)
        self.data[k] = (key, value)

    def has_key(self, key):
        """Case insensitive test whether 'key' exists."""
        k = self._lowerOrReturn(key)
        return k in self.data

    __contains__=has_key

    def _doPreserve(self, key):
        if not self.preserve and (isinstance(key, str)
                                  or isinstance(key, unicode)):
            return key.lower()
        else:
            return key

    def keys(self):
        """List of keys in their original case."""
        return list(self.iterkeys())

    def values(self):
        """List of values."""
        return list(self.itervalues())

    def items(self):
        """List of (key,value) pairs."""
        return list(self.iteritems())

    def get(self, key, default=None):
        """Retrieve value associated with 'key' or return default value
        if 'key' doesn't exist."""
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, key, default):
        """If 'key' doesn't exists, associate it with the 'default' value.
        Return value associated with 'key'."""
        if not self.has_key(key):
            self[key] = default
        return self[key]

    def update(self, dict):
        """Copy (key,value) pairs from 'dict'."""
        for k,v in dict.items():
            self[k] = v

    def __repr__(self):
        """String representation of the dictionary."""
        items = ", ".join([("%r: %r" % (k,v)) for k,v in self.items()])
        return "InsensitiveDict({%s})" % items

    def iterkeys(self):
        for v in self.data.itervalues():
            yield self._doPreserve(v[0])

    def itervalues(self):
        for v in self.data.itervalues():
            yield v[1]

    def iteritems(self):
        for (k, v) in self.data.itervalues():
            yield self._doPreserve(k), v

    def popitem(self):
        i=self.items()[0]
        del self[i[0]]
        return i

    def clear(self):
        for k in self.keys():
            del self[k]

    def copy(self):
        return InsensitiveDict(self, self.preserve)

    def __len__(self):
        return len(self.data)

    def __eq__(self, other):
        for k,v in self.items():
            if not (k in other) or not (other[k]==v):
                return 0
        return len(self)==len(other)
