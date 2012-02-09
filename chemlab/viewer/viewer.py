"""The molecular viewer lets the user arrange and display the molecule
datatypes in chemlab in an easy and intuitive way.

"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import * # For cylinder primitive

from backends import GLUTBackend
from arcball import ArcBall
from . import colors

import numpy as np
from numpy.linalg import norm
from math import sqrt, sin, cos


class Viewer(GLUTBackend):
    def __init__(self):
        super(Viewer,self).__init__()

        self.molecules = []
        
        self.distance = 0.0
        
        self.camera_position = np.array([0.0, 0.0, -5.0])
        self.arcball = ArcBall()
        self.arcball.compute_optimal_radius(0, 0, self.camera_position)
        
        self.oldmat = np.eye(3)
        
        # Mouse position
        self.x = 30
        self.y = 30

        # Mouse status
        self.left_down = False
        
        # Rotation matrix, start with no-rotation
        self.mat = np.eye(4)
        
        self.init_materials()
        self.init_light()
        self.init_perspective()
        self.init_depth()

    def draw_molecule(self, mol):
        self.molecules.append(mol)

    def show(self):
        self.main()
    
    def init_perspective(self):
        glMatrixMode(GL_PROJECTION)
        # camera frustrum setup
        # IMPORTANT!!
        glFrustum(-0.5, 0.5, -0.5, 0.5, 1.0, 100.0)

    def init_materials(self):
        glMaterialfv(GL_FRONT, GL_AMBIENT,
                     GLfloat_4(0.2, 0.2, 0.2, 1.0))
        glMaterialfv(GL_FRONT, GL_DIFFUSE,
                     GLfloat_4(0.2, 0.2, 0.2, 1.0))
        glMaterialfv(GL_FRONT, GL_SPECULAR,
                     GLfloat_4(1.0, 1.0, 1.0, 1.0))
        glMaterialfv(GL_FRONT, GL_SHININESS,
                     GLfloat(50.0))



    def color(self, r, g, b):
        glMaterialfv(GL_FRONT, GL_AMBIENT,
                     GLfloat_4(r, g, b, 1.0))
        glMaterialfv(GL_FRONT, GL_DIFFUSE,
                     GLfloat_4(r, g, b, 1.0))

    def init_light(self):
        glLightfv(GL_LIGHT0, GL_AMBIENT, GLfloat_4(0.8, 0.8, 0.8, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, GLfloat_4(1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, GLfloat_4(1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_4(1.0, 1.0, 1.0, 0.0))   
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, GLfloat_4(0.2, 0.2, 0.2, 1.0))
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

    def init_depth(self):
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)

        
    def move(self, x, y):
        self.lastx, self.lasty = self.x, self.y
        self.x, self.y = x, y
        #print "next", x,y
        arcball = self.arcball
        arcball.compute_optimal_radius(0.0, 0.0, self.camera_position)
        arcball.set_bounds(500, 600)
        arcball.set_initial_coords(self.lastx, self.lasty)
        arcball.set_final_coords(self.x, self.y)

        from arcball import Matrix4fSetRotationFromMatrix3f
        mat = arcball.get_rot_matrix()
        mat = self.oldmat.dot(mat)
        self.oldmat = mat
        mat = Matrix4fSetRotationFromMatrix3f(np.eye(4), mat)
        print mat
        self.mat = mat
        self.refresh()

    def wheel(self, button, state, x, y):
        LEFT_MS = 0
        RIGHT_MS = 1
        WH_UP = 3
        WH_DOWN = 4

        DOWN, UP = range(2)
        
        if button == WH_UP:
            self.camera_position[2] += 0.5
            self.refresh()

        elif button == WH_DOWN:
            self.camera_position[2] += -0.5
            self.refresh()

        elif button == LEFT_MS:
            if state == DOWN:
                self.startx, self.starty = x, y
                
        
    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity() # Start fresh

        # Move the camera
        glTranslate(*self.camera_position)

        # Rotate according to the arcball
        glMultMatrixf(self.mat.reshape(16,))

        # Put atoms in their respective positions
        for mol in self.molecules:
            self.display_molecule(mol)
        
        self.swap_buffers()

    def display_atom(self, atom):
        x,y,z = atom.coord

        glPushMatrix()
        glTranslate(x, y, z)
        
        r, g, b = colors.elem_dict[atom.type]
        self.color(r, g, b)
        glutSolidSphere(0.3, 20, 20)
        self.color(0.2, 0.2, 0.2)
        glPopMatrix()

    def display_bond(self, bond):
        a = bond.start.coord
        b = bond.end.coord
        
        radius = 0.25
        axis_start = np.array([0,0,1])
        axis_end = b-a
        angle =np.degrees(np.arccos(np.dot(axis_end, axis_start)/
                                    (norm(axis_end)*norm(axis_start))))

        axis_rot = np.cross(axis_start, axis_end)
        
        glPushMatrix()
        cyl = gluNewQuadric()

        glTranslate(*a)
        
        glRotate(angle, *axis_rot)
        gluCylinder(cyl, radius, radius, norm(axis_end), 10, 10)
        
        glPopMatrix()

    def display_molecule(self, mol):
        """Handle the displaying of the molecule in terms of opengl."""
        for atom in mol.atoms:
            self.display_atom(atom)
            
        for bond in mol.bonds:
            self.display_bond(bond)

