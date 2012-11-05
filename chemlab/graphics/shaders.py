from .gletools import FragmentShader, VertexShader, ShaderProgram

default_program = ShaderProgram(
    VertexShader('''
                 varying vec3 normal;
                 varying vec3 halfvector;
                 uniform mat4 mvproj;
                 uniform vec3 camera;
                 uniform vec3 lightDir;
                 
                 void main()
                 {
                     normal = gl_Normal;
                     halfvector = normalize(-camera + lightDir);
                 
                     gl_Position = mvproj * gl_Vertex;                 
                     gl_FrontColor = gl_Color;
                 }'''),
    FragmentShader('''
                   uniform vec3 lightDir;
                   varying vec3 normal;
                   varying vec3 halfvector;
                   uniform vec3 camera;
                   
                   void main()
                   {
                       float NdotL, NdotHV;
                       vec4 color, diffuse;
                       float specular;
                   
                       NdotL = dot(normalize(lightDir), normalize(normal));
                       NdotHV = max(dot(normalize(normal), normalize(halfvector)), 0.0);
                       specular = 0.2*pow(NdotHV, 122.0); /* Shininess */
                       diffuse = gl_Color;
                       color =  diffuse * NdotL + specular;
                   
                       gl_FragColor = color;
                   }''')
)
