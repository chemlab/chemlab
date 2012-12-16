import numpy as np

class CylinderRenderer(AbstractRenderer):
    def __init__(self, startlist, endlist, radiuslist, colorlist):
        '''Renders a set of cylinders. The starting and end point of
        each cylinder is stored in the startlist* and *endlist*.
        
        radius of cylinders are in *radiuslits*
        
        This renderer uses vertex array objects to deliver optimal
        performance.

        '''
        
        self.startlist = startlist
        self.endlist = endlist
        self.radiuslist = radiuslist
        self.colorlist = colorlist
        
        ncyl = len(startlist)
        
        dir = self.endlist - self.startlist
        
        
        for start, end, radius, color in zip(self.startlist,
                                             self.endlist,
                                             self.radiuslist,
                                             self.colorlist):
            cyl = OptCylinder(start, end, radius, color)
        
        # We expect to receive things in nanometers
        n_triangles = 0
        vertices = []
        normals = []
        colors_ = []
        
        
        for start, end, radius, color in zip(self.startlist,
                                             self.endlist,
                                             self.radiuslist,
                                             self.colorlist):
            cyl = OptCylinder(start, end, radius, color)
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

    def update_positions(self, startlist, endlist):
        offset = 0
        vertices = np.zeros(self._n_triangles*3, dtype=np.float32)
        
        for i in range(len(rarray)):
            color = self.colorlist[i]
            radius = self.radiuslist[i]
            start = startlist[i]
            end = endlist[i]
            s = OptCylinder(start, end, radius, color=color)
            
            n = len(s.tri_vertex)
            vertices[offset:offset+n] = s.tri_vertex
            offset += n
        
        self._vbo_v.bind()
        self._vbo_v.set_data(vertices.ctypes.data_as(POINTER(GLfloat)))
        self._vbo_v.unbind()
        
        self.startlist = startlist
        self.endlist = endlist
        
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
