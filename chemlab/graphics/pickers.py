"""Pick objects on screen
"""
import numpy as np
from .transformations import unit_vector
import time

class SpherePicker(object):
    
    def __init__(self, widget, positions,  radii):
        
        self.positions = positions
        self.radii = np.array(radii)
        self.widget = widget
        
    def pick(self, x, y):
        # X and Y are normalized coordinates
        
        # Origin of the ray, object space
        origin = self.widget.camera.unproject(x, y)
        
        # Another point to get the direction
        dest = self.widget.camera.unproject(x, y, 0.0) 
        
        # direction of the ray
        direction = unit_vector(dest - origin)
        
        #intersections = []
        #distances = []
        # Quadratic equation for the intersection
        # for i, r in enumerate(self.positions):
        #     a = 1.0 # d . d
        #     b = 2*np.dot((origin - r), direction)
        #     c = np.dot((origin - r), (origin - r)) - self.radii[i]**2
            
        #     det =  b*b - 4*a*c
            
        #     if det >= 0.0:
        #         intersections.append(i)
        #         t = (b + np.sqrt(det))/(2*a)
        #         distances.append(t)
        
        # print time.time() - t

        # Vectorized intersections. This is just a numpy-vectorize
        # version of the above algorithm
        
        b_v = 2.0 * ((origin - self.positions) * direction).sum(axis=1)
        c_v = ((origin - self.positions)**2).sum(axis=1) - self.radii ** 2
        det_v = b_v * b_v - 4.0 * c_v
        
        inters_mask = det_v >= 0
        intersections = (inters_mask).nonzero()[0].tolist()
        distances = (b_v[inters_mask] + np.sqrt(det_v[inters_mask])) / 2.0

        
        if intersections:
            distances, intersections = zip(*sorted(zip(distances, intersections)))
            return list(reversed(intersections))
        else:
            return intersections