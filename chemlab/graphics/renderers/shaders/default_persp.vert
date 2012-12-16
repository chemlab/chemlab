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
}
