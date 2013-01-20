from OpenGL.GL import shaders
import pkgutil

def set_uniform(prog, uni, typ, value):
    location = glGetUniformLocation(prog, uni)
    if typ == '1f':
        glUniform1f()
    if typ == '4fv':
        pass

class AbstractRenderer(object):
    '''An AbstractRenderer is an interface for Renderers. Each
    renderer have to implement an initialization function __init__, a
    draw method to do the actual drawing and an update function, that
    is used to update the data to be displayed.

    '''
    def __init_(self, *args, **kwargs):
        self.VERTEX_SHADER = pkgutil.get_data(".shaders", "default_persp.vert")
        self.FRAGMENT_SHADER = pkgutil.get_data(".shaders", "default_light.frag")
    
    def draw(self):
        pass
    
    def update(self, *args, **kwargs):
        pass
    
    def set_viewer(self, v):
        self.viewer = v
    
    def compile_shader(self):
        vertex = shaders.compileShader(self.VERTEX_SHADER,GL_VERTEX_SHADER)
        fragment = shaders.compileShader(self.FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        
        self.shader = shaders.compileProgram(self.VERTEX_SHADER, self.FRAGMENT_SHADER)

    def setup_shader(self):
        # Setup the uniforms
        set_uniform(self.shader, "mvproj", "4fv", self.viewer.mvproj)
        set_uniform(self.shader, "lightDir", "3f", self.viewer.ldir)
        set_uniform(self.shader, "camera", "3f", self.viewer.camera.position)
