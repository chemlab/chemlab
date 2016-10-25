import numpy as np
import uuid

class Scene(object):
    
    def __init__(self):
        self._dict = {'representations': [], 'background': 0}
        self.camera = Camera()
    
    def add_representation(self, rep, args):
        self._dict["representations"].append({'rep_type' : rep,
                                              'rep_id': uuid.uuid1().hex,
                                              'options' : args})
        
    def to_dict(self):
        camera_dict = {'aspect': self.camera.aspectratio,
                       'vfov': self.camera.fov,
                       'quaternion': [0.0, 1.0, 0.0, 0.0],
                       'target': self.camera.pivot, 
                       'location': self.camera.position}
        self._dict['camera'] = camera_dict
        return self._dict
