#version 120

uniform vec3 lightDir;
varying vec3 normal;
varying vec3 halfvector;

uniform vec3 camera;
uniform mat4 viewmatrix;
uniform int shading_type;                   



vec3 phong_shading(vec3 light_dir, vec3 camera_position,vec3 normal, vec3 color) 
{
  
  vec3 halfvector = normalize(light_dir + camera_position);
  
  float NdotL = dot(normalize(light_dir), normal);
  float NdotHV = max(dot(normal, halfvector), 0.0);
   
  float specular = 0.3*pow(NdotHV, 110.0); /* Shininess */
  return color * NdotL + specular;
}

vec3 toon_shading(vec3 light_dir, vec3 normal, vec3 color)
{
  float NdotL = dot(normalize(light_dir), normal);
  vec3 ret;
  
  // Adjust the color a bit
  //color = mix(color, vec3(1.0, 1.0, 1.0), 0.25);
  
  if (NdotL <= 0.4)
    ret = vec3(0.0, 0.0, 0.0); 

  else if (NdotL <= 0.6)
    ret = 0.75 * color;
  
  else
    ret = color;
  
  return ret;
}

void main()
{
  float NdotL, NdotHV;
  vec3 color;
  float specular;
  vec3 normal_interp;
 
  normal_interp = normalize(normal);
  
  if (shading_type == 0) 
    {
      color = phong_shading(lightDir, camera, normal, gl_Color.xyz);
    }
  else if (shading_type == 1)
    {
      color = toon_shading(lightDir, normal, gl_Color.xyz);
    }

 
  
 
  gl_FragData[0] = vec4(color, gl_Color.a);
  
  // This is needed for ssao and other effects that require normals
  gl_FragData[1].xyz = (normal * mat3(viewmatrix)) * 0.5 + 0.5;
}
