from ..gletools import FragmentShader, VertexShader, ShaderProgram

default_program = ShaderProgram(
    VertexShader('''
                 varying vec3 normal;
                 uniform mat4 mvproj;
                 
                 void main()
                 {
                     normal = gl_Normal;
                     gl_Position = mvproj * gl_Vertex;
                     gl_FrontColor = gl_Color;
                 }'''),
    FragmentShader('''
                   uniform vec3 lightDir;
                   varying vec3 normal;
                   
                   void main()
                   {
                       float NdotL;
                       vec4 color, diffuse;
                       
                       NdotL = dot(lightDir, normalize(normal));
                       
                       
                       diffuse = gl_Color;
                       color =  diffuse * NdotL;
                       gl_FragColor = color;
                   }''')
)
