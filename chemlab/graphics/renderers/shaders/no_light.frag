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

  gl_FragColor = gl_Color;
}
