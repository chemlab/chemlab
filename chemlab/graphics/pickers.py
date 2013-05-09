"""Pick objects on screen
"""
import numpy as np
from .transformations import unit_vector

class SpherePicker(object):
    
    def __init__(self, widget, positions,  radii):
        
        self.positions = positions
        self.radii = radii
        self.widget = widget
        
    def pick(self, x, y):
        # X and Y are normalized coordinates
        
        # Origin of the ray, object space
        origin = self.widget.camera.unproject(x, y)
        
        # Another point to get the direction
        dest = self.widget.camera.unproject(x, y, 0.0) 
        
        # direction of the ray
        direction = unit_vector(dest - origin)
        
        intersections = []
        distances = []
        # Quadratic equation for the intersection
        for i, r in enumerate(self.positions):
            a = 1.0 # d . d
            b = 2*np.dot((origin - r), direction)
            c = np.dot((origin - r), (origin - r)) - self.radii[i]**2
            
            det =  b*b - 4*a*c
            
            if det >= 0.0:
                intersections.append(i)
                t = (b + np.sqrt(det))/(2*a)
                distances.append(t)
        if intersections:
            distances, intersections = zip(*sorted(zip(distances, intersections)))
            return tuple(reversed(intersections))
        else:
            return intersections