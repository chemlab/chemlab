

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
