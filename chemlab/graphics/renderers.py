"""Renderers are classes that encapsulate the representation of
various objects by using opengl.

"""
import numpy as np
import pyglet.gl

from pyglet.graphics.vertexbuffer import VertexBufferObject
from pyglet.gl import *

from . import colors
from ..data.vdw import vdw_dict
from .optshapes import OptSphere
from .gletools.shapes import Arrow


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
    
class SphereRenderer(AbstractRenderer):
    def __init__(self, poslist, radiuslist, colorlist):
        '''This renderer represents a list of *atoms* as simple
        spheres.

        '''
        
        self.poslist = poslist
        self.radiuslist = radiuslist
        self.colorlist = colorlist
        
        # We expect to receive things in nanometers
        n_triangles = 0
        vertices = []
        normals = []
        colors_ = []
        
        for coords, radius, color in zip(poslist, radiuslist, colorlist):
            s = OptSphere(radius, coords, color=color)
            n_triangles += s.tri_n
            
            vertices.append(s.tri_vertex)
            normals.append(s.tri_normals)
            colors_.append(s.tri_color)
        
        # Convert arrays to numpy arrays, float32 precision,
        # compatible with opengl, and cast to ctypes
        vertices = np.array(vertices, dtype=np.float32)
        normals = np.array(normals, dtype=np.float32)
        colors_ = np.array(colors_, dtype=np.uint8)

        # Store vertices, colors and normals in 3 different vertex
        # buffer objects
        self._vbo_v = VertexBufferObject(n_triangles*3*sizeof(GLfloat),
                                         GL_ARRAY_BUFFER,
                                         GL_DYNAMIC_DRAW)
        self._vbo_v.bind()
        self._vbo_v.set_data(vertices.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_v.unbind()
        
        self._vbo_n = VertexBufferObject(n_triangles*3*sizeof(GLfloat),
                                         GL_ARRAY_BUFFER,
                                         GL_DYNAMIC_DRAW)
        self._vbo_n.bind()
        self._vbo_n.set_data(normals.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_n.unbind()

        self._vbo_c= VertexBufferObject(n_triangles*4*sizeof(GLubyte),
                                        GL_ARRAY_BUFFER,
                                        GL_DYNAMIC_DRAW)
        self._vbo_c.bind()
        self._vbo_c.set_data(colors_.ctypes.data_as(POINTER(GLuint)))
        self._vbo_c.unbind()
        
        self._n_triangles = n_triangles
    
    def draw(self):
        # Draw all the vbo defined in set_atoms
        glEnableClientState(GL_VERTEX_ARRAY)
        self._vbo_v.bind()
        glVertexPointer(3, GL_FLOAT, 0, 0)
        
        glEnableClientState(GL_NORMAL_ARRAY)
        self._vbo_n.bind()
        glNormalPointer(GL_FLOAT, 0, 0)
        
        glEnableClientState(GL_COLOR_ARRAY)
        self._vbo_c.bind()
        glColorPointer(4, GL_UNSIGNED_BYTE, 0, 0)
        
        glDrawArrays(GL_TRIANGLES, 0, self._n_triangles)
        
        self._vbo_v.unbind()
        self._vbo_n.unbind()
        self._vbo_c.unbind()
        
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)

    def update_positions(self, rarray):
        offset = 0
        vertices = np.zeros(self._n_triangles*3, dtype=np.float32)
        
        for i in range(len(rarray)):
            color = self.colorlist[i]
            radius = self.radiuslist[i]
            s = OptSphere(radius, rarray[i], color=color)
            
            n = len(s.tri_vertex)
            vertices[offset:offset+n] = s.tri_vertex
            offset += n
        
        self._vbo_v.bind()
        self._vbo_v.set_data(vertices.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_v.unbind()
        
        self.poslist = rarray
        
    def update_colors(self, colorlist):
        self.colorlist = colorlist
        
        colors_ = []
        for coords, radius, color in zip(self.poslist, self.radiuslist, colorlist):
            s = OptSphere(radius, coords, color=color)
            colors_.append(s.tri_color)
        
        colors_ = np.array(colors_, dtype=np.uint8)
        
        self._vbo_c.bind()
        self._vbo_c.set_data(colors_.ctypes.data_as(POINTER(GLuint)))
        self._vbo_v.unbind()
        
class AtomRenderer(SphereRenderer):
    def __init__(self, atoms):
        radii = [vdw_dict[atom.type] for atom in atoms]
        colorlist = [colors.map.get(atom.type, colors.light_grey) for atom in atoms]
        poslist = [at.coords for at in atoms]
        
        super(AtomRenderer, self).__init__(poslist, radii, colorlist)

class ForcesRenderer(AbstractRenderer):
    def __init__(self, forces, atoms):
        self.set_forces(forces, atoms)
        
    def set_forces(self, forces, atoms):
        self.forces = forces
        self.atoms = atoms
        
    def draw(self):
        for f, a in zip(self.forces, self.atoms):
            arr = Arrow(f + a.coords, a.coords)
            arr.draw()

class CubeRenderer(AbstractRenderer):
    def __init__(self, dim):
        self.dim = dim
        
    def draw(self):
        l = self.dim
        x = l*0.5 
        pyglet.graphics.draw(8*3, pyglet.gl.GL_LINES,
                             # Front Square
                       ("v3f", (x, x, x,  -x, x, x,
                                -x, x, x, -x, -x, x,
                                -x, -x, x, x, -x, x,
                                x, -x, x,  x, x, x,
                                # Back Square
                                x, x, -x,  -x, x, -x,
                                -x, x, -x, -x, -x, -x,
                                -x, -x, -x, x, -x, -x,
                                x, -x, -x,  x, x, -x,
                                # Connecting the two squares
                                x,x,x, x,x,-x,
                                -x,x,x, -x,x,-x,
                                -x,-x,x, -x,-x,-x,
                                x,-x,x, x,-x, -x)),
                             ("n3f", (0.0,)*24*3))
    
    def update(self, boxsize):
        self.dim = boxsize


class PointRenderer(AbstractRenderer):
    
    def __init__(self, sys):
        self.sys = sys
        glPointSize(10.0)
        glEnable(GL_POINT_SMOOTH)        
        self.set_atoms(self.sys.atoms)
    
    def set_atoms(self, atoms):
        self.atoms = atoms
        
        positions = []
        radii = []
        colors_ = []
        
        for atom in atoms:
            color = colors.map.get(atom.type, colors.light_grey)
            positions.append(atom.coords)
            colors_.append(color)
            radii.append(0.27)
        
        # Convert arrays to numpy arrays, float32 precision,
        # compatible with opengl, and cast to ctypes
        positions = np.array(positions, dtype=np.float32)
        radii = np.array(radii, dtype=np.float32)
        colors_ = np.array(colors_, dtype=np.uint8)

        n_points = len(positions)
        # Store vertices, colors and normals in 3 different vertex
        # buffer objects
        self._vbo_v = VertexBufferObject(n_points*3*sizeof(GLfloat),
                                         GL_ARRAY_BUFFER,
                                         GL_DYNAMIC_DRAW)
        self._vbo_v.bind()
        self._vbo_v.set_data(positions.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_v.unbind()
        
        self._vbo_c= VertexBufferObject(n_points*4*sizeof(GLubyte),
                                        GL_ARRAY_BUFFER,
                                        GL_DYNAMIC_DRAW)
        self._vbo_c.bind()
        self._vbo_c.set_data(colors_.ctypes.data_as(POINTER(GLuint)))
        self._vbo_c.unbind()
        
        self._n_points = n_points
    
    def draw(self):
        # Draw all the vbo defined in set_atoms
        glEnableClientState(GL_VERTEX_ARRAY)
        self._vbo_v.bind()
        glVertexPointer(3, GL_FLOAT, 0, 0)
        
        glEnableClientState(GL_COLOR_ARRAY)
        self._vbo_c.bind()
        glColorPointer(4, GL_UNSIGNED_BYTE, 0, 0)
        
        glDrawArrays(GL_POINTS, 0, self._n_points)
        
        self._vbo_v.unbind()
        self._vbo_c.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)

    def update(self, rarray):
        positions = rarray
        
        self._vbo_v.bind()
        self._vbo_v.set_data(positions.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_v.unbind()

from .gletools import FragmentShader, VertexShader, ShaderProgram
billboard_program = ShaderProgram(
    VertexShader('''
                 //
                 // This is for projection and lighting
                 //
                 
                 uniform mat4 mvproj;
                 uniform mat4 camera_mat;
                 uniform mat4 projection_mat;
                 
                 // Camera in world coordinates
                 uniform vec3 camera; 
                 // light direction in world coordinates
                 uniform vec3 light_dir; 
                 
                 // Scale factor
                 uniform float scalefac;

                 // Useful to compute sphere points
                 attribute vec2 at_mapping;
                 varying vec2 mapping;
                 
                 attribute vec3 at_sphere_center;
                 varying vec3 sphere_center;
                 
                 attribute float at_sphere_radius;
                 varying float sphere_radius;
                 
                 void main()
                 {
                     mapping = at_mapping;
                     
                     sphere_center = vec3(
                         camera_mat*vec4(at_sphere_center, 1.0)).xyz;
                     
                     sphere_radius = at_sphere_radius;
                     vec4 actual_vertex = gl_Vertex;
                 
                     // First rotate the points
                     actual_vertex = camera_mat * actual_vertex;
                     
                     actual_vertex = vec4(
                         actual_vertex.xy+mapping*sphere_radius*scalefac,
                         actual_vertex.z,
                         actual_vertex.w);
                     
                     gl_Position = projection_mat * actual_vertex;                                   gl_FrontColor = gl_Color;
                 }'''),
    FragmentShader('''
                   uniform vec3 light_dir;
                   uniform vec3 camera;
                   uniform mat4 mvproj;
                   uniform float scalefac;
                   
                   // sphere-related
                   varying vec2 mapping;
                   varying vec3 sphere_center;
                   varying float sphere_radius;
                   
                   void impostor_point_normal(out vec3 point, out vec3 normal)
                   {
                   // 1. Calculation of the ray
                   //      Get point P on the square
                   //      Calculate the ray to be traced
                   vec3 P_map;
                   
                   vec3 ray_direction;
                   vec3 ray_origin;
                   vec3 sph_intersection;
                   vec3 sph_normal;
                   
                   float a, b, c, t, determinant;
                   
                   P_map.xy = sphere_radius*mapping.xy*scalefac + sphere_center.xy;
                   P_map.z = sphere_center.z;
                   
                   // Line to intersect
                   ray_origin = camera;
                   //ray_origin = vec3(0.0, 0.0, 5.0);
                   ray_direction = normalize(P_map - ray_origin); 
                   

                   
                   // 2. Calculation of the intersection: Got the point
                   
                   // Second-order equation solution
                   a = 1.0;
                   b = 2.0*dot(ray_direction, ray_origin - sphere_center);
                   c = dot(ray_origin - sphere_center,
                           ray_origin - sphere_center) -
                           sphere_radius*sphere_radius;

                   determinant = b*b - 4.0*a*c;
                   
                   if (determinant > 0.0)
                   {
                     // 3. Calculation of the normal
                     // We'll take the closest intersection value
                     float x1 = (- b - sqrt(determinant))/2.0;
                     float x2 = (- b + sqrt(determinant))/2.0;
                     vec3 inter_1 = ray_origin + x1*ray_direction;
                     vec3 inter_2 = ray_origin + x2*ray_direction;
                     
                     sph_intersection = inter_1;
                   
                     sph_normal = normalize(sph_intersection - sphere_center); 
                   
                     point = sph_intersection;
                     normal = sph_normal;
                   }
                   else if (determinant < 0.0)
                   {
                   // If no intersection, discard the point
                     discard;
                   }
                   
                   return;
                   }
                   
                   void main()
                   {
                       float NdotL, NdotHV;
                       vec4 color, diffuse;
                       vec3 point, normal;
                       float specular;
                       vec3 halfvector;
                       vec4 point_clipspace;
                   
                       halfvector = normalize(light_dir + camera);
                       
                       impostor_point_normal(point, normal);
                   
                       
                       // Fix the z-buffer thingy
                       point_clipspace = mvproj * vec4(point, 1.0);
                       float ndc_depth = point_clipspace.z / point_clipspace.w;
                       
                       gl_FragDepth = ((gl_DepthRange.far - gl_DepthRange.near) * ndc_depth +
                                        gl_DepthRange.near + gl_DepthRange.far)/2.0;
                   
                   
                       NdotL = dot(normalize(light_dir),
                                   normalize(normal));
                       NdotHV = max(dot(normalize(normal), normalize(halfvector)), 0.0);
                      
                       specular = 0.2*pow(NdotHV, 122.0); /* Shininess */
                       diffuse = gl_Color;
                       color =  diffuse * NdotL + specular;
                      
                       // gl_FragColor = diffuse * NdotL;
                       gl_FragColor = diffuse*NdotL + specular;
                   }''')
)

from renderers import AbstractRenderer

from pyglet.graphics import draw
from pyglet.graphics.vertexbuffer import VertexBufferObject
from pyglet import gl

import numpy as np

class SphereImpostorRenderer(AbstractRenderer):
    def __init__(self, poslist, radiuslist, colorlist):
        self.poslist = poslist
        self.radiuslist = radiuslist
        self.colorlist = colorlist

        
    def draw_sphere(self, sph_center, radius, color):
        scalefac = 1.5
        radius = radius
        
        mvproj = self.viewer.mvproj.copy()
        
        
        billboard_program.vars.camera_mat = self.viewer.camera.matrix
        billboard_program.vars.projection_mat = self.viewer._projection_matrix
        billboard_program.vars.mvproj = self.viewer._projection_matrix
        
        ldir = np.array([0.0, 10.0, 10.0, 1.0])
        #ldir = np.dot(self.viewer.camera.matrix, np.array([0.0, 100.0, 100.0,
        #                                                   1.0]))
        billboard_program.vars.light_dir = ldir[:3]
        billboard_program.vars.scalefac = scalefac

        cam = np.dot(self.viewer.camera.matrix[:3,:3], -self.viewer.camerapos)
        
        billboard_program.vars.camera = cam
        
        at_mapping = gl.glGetAttribLocation(billboard_program.id,
                                            "at_mapping")
        at_sphere_center = gl.glGetAttribLocation(billboard_program.id,
                                                  "at_sphere_center")
        at_sphere_radius = gl.glGetAttribLocation(billboard_program.id,
                                                  "at_sphere_radius")
        
        
        with billboard_program:
            draw(4, gl.GL_QUADS,
                 ("v3f", np.tile(sph_center, 4).tolist()),
                 ("c4B", color*4),
                 ("%ig2f"%at_mapping, [1.0, 1.0,
                                       -1.0, 1.0,
                                       -1.0,-1.0,
                                       1.0, -1.0,]),
                 ("%ig3f"%at_sphere_center, sph_center.tolist()*4),                 
                 ("%ig1f"%at_sphere_radius, [radius, radius, radius,
                                             radius]),                 
            )

        
    def draw(self):
        
        centers = [[0.0, 0.0, 0.0], [1.0, 0.0, -1.0], [-1.0, 0.0, 0.0]]
        radius = 1.0
        
        for c, radius, color in zip(self.poslist, self.radiuslist,
                                    self.colorlist):
            self.draw_sphere(np.array(c), radius, color)
        
    def update_positions(self, rarray):
        self.poslist = rarray

class AtomImpostorRenderer(SphereImpostorRenderer):
    def __init__(self, atoms):
        radii = [vdw_dict[atom.type] for atom in atoms]
        colorlist = [colors.map.get(atom.type, colors.light_grey) for atom in atoms]
        poslist = [at.coords for at in atoms]
        
        super(AtomImpostorRenderer, self).__init__(poslist, radii, colorlist)

