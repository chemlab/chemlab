uniform vec3 lightDir;
varying vec3 normal;
varying vec3 halfvector;
uniform vec3 camera;
uniform mat4 viewmatrix;
                   
void main()
{
  float NdotL, NdotHV;
  vec4 color, diffuse;
  float specular;
  
  normal = normalize(normal);
  
  NdotL = dot(normalize(lightDir), normalize(normal));
  NdotHV = max(dot(normalize(normal), normalize(halfvector)), 0.0);
  specular = 0.2*pow(NdotHV, 122.0); /* Shininess */
  diffuse = gl_Color;
  color =  diffuse * NdotL + specular;

  gl_FragData[0] = color;
  
  // This is needed for ssao and other effects that require normals
  gl_FragData[1].xyz = (normal * mat3(viewmatrix)) * 0.5 + 0.5;
}
