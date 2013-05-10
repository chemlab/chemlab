uniform vec3 light_dir;
//uniform vec3 camera;
uniform mat4 mvproj;
uniform float scalefac;
uniform int shading_type;

// sphere-related
varying vec2 mapping;
varying vec3 sphere_center;
varying float sphere_radius;


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

void impostor_point_normal(out vec3 point, out vec3 normal)
{
  // 1. Calculation of the ray
  //      Get point P on the square
  //      Calculate the ray to be traced
  vec3 P_map;

  vec3 ray_direction;
  vec3 ray_origin;
  vec3 sph_intersection;
  vec3 sph_normal;

  float a, b, c, t, determinant;

  P_map.xy = sphere_radius*mapping.xy*scalefac + sphere_center.xy;
  P_map.z = sphere_center.z;

  // Line to intersect
  ray_origin = vec3(0.0, 0.0, 0.0);
  //ray_origin = vec3(0.0, 0.0, 5.0);
  ray_direction = normalize(P_map - ray_origin); 



  // 2. Calculation of the intersection: Got the point

  // Second-order equation solution
  a = 1.0;
  b = 2.0*dot(ray_direction, ray_origin - sphere_center);
  c = dot(ray_origin - sphere_center,
	  ray_origin - sphere_center) -
    sphere_radius*sphere_radius;

  determinant = b*b - 4.0*a*c;

  if (determinant >= 0.0)
    {
      // 3. Calculation of the normal
      // We'll take the closest intersection value
      float x1 = (- b - sqrt(determinant))/2.0;
      vec3 inter_1 = ray_origin + x1*ray_direction;
  
      sph_intersection = inter_1;

      sph_normal = normalize(sph_intersection - sphere_center); 

      point = sph_intersection;
      normal = sph_normal;
    }
  else if (determinant < 0.0)
    {
      // If no intersection, discard the point
      discard;
    }

  return;
}

void main()
{
  float NdotL, NdotHV;
  vec3 color;
  vec3 diffuse;
  vec3 point, normal;
  float specular;
  vec3 halfvector;
  vec4 point_clipspace;

  vec3 camera = vec3(0.0, 0.0, 0.0); // FIXME
  halfvector = normalize(light_dir + camera);
    
  impostor_point_normal(point, normal);
  
  // Fix the z-buffer thingy
  point_clipspace = mvproj * vec4(point, 1.0);
  float ndc_depth = point_clipspace.z / point_clipspace.w;
    
  gl_FragDepth = ((gl_DepthRange.far - gl_DepthRange.near) * ndc_depth +
		  gl_DepthRange.near + gl_DepthRange.far)/2.0;

  
  if (shading_type == 0) 
    {
      color = phong_shading(light_dir, camera, normal, gl_Color.xyz);
    }
  else if (shading_type == 1)
    {
      color = toon_shading(light_dir, normal, gl_Color.xyz);
    }

  gl_FragData[0] = vec4(color, gl_Color.a);
  
  // This is needed for ssao and other effects that require normals
  gl_FragData[1].xyz = normal * 0.5 + 0.5;
  
}
