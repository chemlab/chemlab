# Some classes for custom events without using QObject
class Event(object):
    def __get__(self, inst, type_):
        return BoundEvent(inst, self.name)

class BoundEvent(object):
    def __init__(self, inst, name):
        self.inst = inst
        self.name = name
        
        # I can create the _callbacks attribute for the first time
        # here
        if not hasattr(inst, '_callbacks'):
            self.inst._callbacks = {}

    def connect(self, callback):
        self.inst._callbacks[self.name] = callback
    
    def emit(self, *args, **kwargs):
        callback = self.inst._callbacks.get(self.name, None)
        if callback is not None:
            callback(*args, **kwargs)
        
class EventMeta(type):
    def __init__(cls, name, bases, dct):
        for k,v in dct.items():
            if isinstance(v, Event):
                # Give the event a name
                v.name = k
        
        super(EventMeta, cls).__init__(name, bases, dct)

class Model(object):
    __metaclass__ = EventMeta
    
    def __init__(self):
        self._callbacks = {}

# Applying metaclass in a python2/python3 compatible fashion
Model = EventMeta('Model', (Model,), {})