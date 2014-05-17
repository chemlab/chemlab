"""Pick objects on screen
"""

import numpy as np
from .transformations import unit_vector, angle_between_vectors, rotation_matrix


def ray_spheres_intersection(origin, direction, centers, radii):
    """Calculate the intersection points between a ray and multiple
    spheres.

    **Returns**

    intersections
    
    distances
    
    Ordered by closest to farther
    """
    b_v = 2.0 * ((origin - centers) * direction).sum(axis=1)
    c_v = ((origin - centers)**2).sum(axis=1) - radii ** 2
    det_v = b_v * b_v - 4.0 * c_v

    inters_mask = det_v >= 0
    intersections = (inters_mask).nonzero()[0]
    distances = (-b_v[inters_mask] - np.sqrt(det_v[inters_mask])) / 2.0

    # We need only the thing in front of us, that corresponts to
    # positive distances.
    dist_mask = distances > 0.0

    # We correct this aspect to get an absolute distance
    distances = distances[dist_mask]
    intersections = intersections[dist_mask].tolist()

    if intersections:
        distances, intersections = zip(*sorted(zip(distances, intersections)))
        return list(intersections), list(distances)
    else:
        return [], []


class SpherePicker(object):

    def __init__(self, widget, positions, radii):

        self.o_positions = positions
        self.o_radii = np.array(radii)

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
        return ray_spheres_intersection(origin, direction, self.positions, self.radii)
        
class CylinderPicker(object):

    def __init__(self, widget, bounds, radii):
        # Special case, empty array
        self.widget = widget
        self.bounds = bounds
        self.radii = radii
        self.is_empty = (bounds.size == 0)
        
        if self.is_empty:
            return
        
        self.directions = bounds[:, 1, :] - bounds[:, 0, :]
        self.origins = bounds[:, 0, :]
        
        # The center of the bounding sphere
        centers = 0.5 * (bounds[:, 1, :] + bounds[:, 0, :])
        # The radii of the bounding spheres
        sph_radii = 0.5 * np.sqrt((self.directions**2).sum(axis=1)) + radii
        
        self.lengths = np.sqrt((self.directions**2).sum(axis=1))
        # Normalize the directions        
        self.directions /= self.lengths[:, np.newaxis]
        
        self._bounding_sphere = SpherePicker(widget, centers, sph_radii)

    def _origin_ray(self, x, y):
        # X and Y are normalized coordinates
        # Origin of the ray, object space
        origin = self.widget.camera.unproject(x, y)
        
        # Another point to get the direction
        dest = self.widget.camera.unproject(x, y, 0.0) 
        
        # direction of the ray
        direction = unit_vector(dest - origin)
        
        return origin, direction

    def pick(self, x, y):
        
        if self.is_empty:
            return [], []
        
        origin, direction = self._origin_ray(x, y)

        # First, take only the things intersection with the bounding spheres
        sph_intersections, sph_distances = self._bounding_sphere.pick(x, y)
        
        # Now, do the proper intersection with the cylinders
        z_axis = np.array([0.0, 0.0, 1.0])

        intersections = []
        distances = []
        for i in sph_intersections:
            # 1) Change frame of reference of the origin and direction
            # Rotation matrix
            cyl_direction = self.directions[i]
            cyl_length = self.lengths[i]
            
            angle = angle_between_vectors(cyl_direction, z_axis)
            normal = np.cross(cyl_direction, z_axis)
            M = rotation_matrix(angle, normal)[:3, :3].T
            
            cyl_origin = self.origins[i]
            origin_p = M.dot(origin - cyl_origin)
            direction_p = M.dot(direction)

            # 2) Intersection between ray and z-aligned cylinder
            cyl_radius = self.radii[i]

            a = direction_p[:2].dot(direction_p[:2])
            b = 2.0 * origin_p[:2].dot(direction_p[:2])
            c = origin_p[:2].dot(origin_p[:2]) - cyl_radius*cyl_radius
            det = b**2 - 4*a*c

            if det >= 0.0:
                # Hit
                t = (-b - np.sqrt(det))/(2.0*a)

                new_point = origin + t * direction
                # Now, need to check if the intersection point is
                # outside of the caps
                end_cyl = cyl_origin + cyl_direction * cyl_length

                outside_top = np.dot(new_point - end_cyl, cyl_direction)
                if outside_top > 0.0:
                    # Discard
                    continue
                
                outside_bottom = np.dot(new_point - cyl_origin, cyl_direction)
                if outside_bottom < 0.0:
                    # Discard
                    continue
                
                intersections.append(i)
                distances.append(t)
                
        if intersections:
            distances, intersections = zip(*sorted(zip(distances, intersections)))
            return list(intersections), list(distances)
        else:
            return [], []
