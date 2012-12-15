class AbstractRenderer(object):
    '''An AbstractRenderer is an interface for Renderers. Each
    renderer have to implement an initialization function __init__, a
    draw method to do the actual drawing and an update function, that
    is used to update the data to be displayed.

    '''
    def __init__(self, *args, **kwargs):
        pass
    
    def draw(self):
        pass
    
    def update(self, *args, **kwargs):
        pass
    
    def set_viewer(self, v):
        self.viewer = v
