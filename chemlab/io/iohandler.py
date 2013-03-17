class IOHandler(object):
    def __init__(self, filename):
        pass

    def read(self, feature, *args, **kwargs):
        pass
        
    def write(self, feature, value, *args, **kwargs):
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