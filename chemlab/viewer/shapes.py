"""Shapes to use in opengl renderers.

"""
from pyglet.gl import *
import numpy as np
from numpy.linalg import norm
from mathutils import normalized
import colors
GLfloat_4 = GLfloat * 4

def sphere(position, radius, color=colors.light_grey):
    x,y,z = position
    
    glPushMatrix()
    glTranslatef(x, y, z)
    _color(*color)
    sph = gluNewQuadric()
    gluSphere(sph, 0.3, 20, 20)

    glPopMatrix()


def cylinder(start, end, radius, color=colors.light_grey):
    axis_start = np.array([0,0,1])
    axis_end = end-start
    angle =np.degrees(np.arccos(np.dot(axis_end, axis_start)/
                                (norm(axis_end)*norm(axis_start))))

    glPushMatrix()
    axis_rot = np.cross(axis_start, axis_end)
    _color(*color)
    cyl = gluNewQuadric()

    glTranslatef(*start)
    glRotatef(angle, *axis_rot)
    gluCylinder(cyl, radius, radius, norm(axis_end), 10, 10)
    
    glPopMatrix()

def arc(r1, r2, r3, color=colors.pink):
    """Takes three cordinates and draws an arc between the 3
    
    """
    x, y, z = r2
    
    glPushMatrix()
    glTranslatef(x, y, z)
    axis_rot = np.cross(normalized(r1-r2),
                        normalized(r3-r2))
    _rotvec(np.array([0,0,1]), axis_rot)
    _rotvec(np.array([0,1,0]), normalized(r1-r2))
    _color(color[0], color[1], color[2], 0.5)
    arc = gluNewQuadric()
    gluPartialDisk(arc,
                   0.0, # Inner radius
                   1.0, # Outer radius
                   20,  # Slices
                   20,  # Loops
                   0,   # Starting angle
                   - _angle(normalized(r1-r2),
                            normalized(r3-r2)))  # disk angle 
    glPopMatrix()
    
def _rotvec(start, end):
    """rotate between vector start and end
    
    """
    angle =np.degrees(np.arccos(np.dot(end, start)/
                                (norm(end)*norm(start))))
    axis_rot = np.cross(start, end)
    glRotatef(angle, *axis_rot)

def _angle(start, end):
    angle = np.degrees(np.arccos(np.dot(end, start)/
                                (norm(end)*norm(start))))
    return angle
    
def _color(r,g,b, a=1.0):
    r, g, b = float(r)/255, float(g)/255, float(b)/255
    #glMaterialfv(GL_FRONT, GL_AMBIENT,
    #             GLfloat_4(r, g, b, 1.0))
    glMaterialfv(GL_FRONT, GL_DIFFUSE,
                 GLfloat_4(r, g, b, a))
