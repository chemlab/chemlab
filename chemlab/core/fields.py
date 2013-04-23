class FieldRequired(Exception):
    pass

class AtomicField(object):
    def __init__(self, name, default):
        self.name = name
        self.default = default
        
    def set(self, at, value):
        setattr(at, self.name, value)
    
    def get(self, at):
        return getattr(at, self.name)