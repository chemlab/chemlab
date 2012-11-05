'''Module to provide a nice camera for 3d applications'''
from transformations import rotation_matrix, translation_matrix

import numpy as np
import numpy.linalg as LA

class Camera:
    def __init__(self):
        self.position = np.array([0.0, 0.0, 1.0])
        self.origin = np.array([0.0, 0.0, 0.0])
        
        self._pretrans = translation_matrix(np.array([0.0, 0.0, -1.0]))
        self._rotation = np.eye(4)
        
        self._haxis = np.array([0.0, 1.0, 0.0])
        self._vaxis = np.array([1.0, 0.0, 0.0])

    def _get_matrix(self):
        return np.dot(self._pretrans, self._rotation)
    
    matrix = property(_get_matrix)
    
    def moveto(self, point):
        r = point - self.position
        self._pretrans = self._pretrans.dot(translation_matrix(r))
        self.position = point
        
    def orbit(self, hor, ver):
        
        self._rotation = self._rotation.dot(rotation_matrix(hor, self._haxis))
        
        # Update rotation axis to keep him in place
        # this is like "undoing" the rotation on the axis
        self._vaxis = np.dot(
            LA.inv(rotation_matrix(hor, self._haxis)[:3,:3]),
            self._vaxis)
        
        self._rotation = self._rotation.dot(rotation_matrix(ver, self._vaxis))
        
        self._haxis = np.dot(
            LA.inv(rotation_matrix(ver, self._vaxis)[:3,:3]),
            self._haxis)
        
    def translate(self, r):
        self.position += r
        self._pretrans = self._pretrans.dot(translation_matrix(r))
        
    def zoom(self, dr):
        self.translate(np.array([0.0, 0.0, dr]))
