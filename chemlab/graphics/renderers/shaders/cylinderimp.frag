#version 120
uniform mat4 projection_mat;
uniform vec3 light_dir;
uniform vec3 camera_position;
uniform int shading_type;

varying vec4 vertex_viewspace; // this guy should be the surface point.

varying vec3 U, V, H;
varying float cylinder_radiusv;
varying float cylinder_lengthv;

varying vec4 cylinder_origin;
varying vec3 local_coords;

vec3 phong_shading(vec3 light_dir, vec3 camera_position,vec3 normal, vec3 color) {
  
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
  // First of all, I need the correct point that we're pointing at
  
  vec3 surface_point = cylinder_origin.xyz;
  surface_point += U * (local_coords.x*2.0 - 1.0) * cylinder_radiusv; 
  surface_point += V * (local_coords.y*2.0 - 1.0) * cylinder_radiusv;  
  surface_point += H * (local_coords.z * cylinder_lengthv);

  // We need to raytrace the cylinder (!)
  // we can do the intersection in impostor space
  
  // Calculate the ray direction in viewspace
  vec3 ray_origin = vec3(0.0, 0.0, 0.0);
  vec3 ray_target = surface_point;
  vec3 ray_direction = normalize(ray_target - ray_origin);
  
  // basis = local coordinate system of cylinder
  mat3 basis = transpose(mat3(U, V, H));

  vec3 base = cylinder_origin.xyz;
  vec3 end_cyl = cylinder_origin.xyz + H * cylinder_lengthv;
  
  // Origin of the ray in cylinder space
  vec3 P = - cylinder_origin.xyz;
  P = basis * P;
  
  // Direction of the ray in cylinder space
  vec3 D = basis * ray_direction;
  
  // Now the intersection is between z-axis aligned cylinder and a ray
  float c = P.x*P.x + P.y*P.y - cylinder_radiusv*cylinder_radiusv; 
  float b = 2.0*(P.x*D.x + P.y*D.y);
  float a = D.x*D.x + D.y*D.y;
  
  float d = b*b - 4*a*c;
  
   if (d < 0.0) 
     discard;
   
   float t = (-b - sqrt(d))/(2*a);
   vec3 new_point = ray_origin + t * ray_direction;
   // Discarding points outside cylinder
   float outside_top = dot(new_point - end_cyl, -H);
   if (outside_top < 0.0) {
     discard;
   }
   float outside_bottom = dot(new_point - base, H);
   if (outside_bottom < 0.0) {
     discard;
   }


   vec3 tmp_point = new_point - cylinder_origin.xyz;
   vec3 normal = normalize(tmp_point - H * dot(tmp_point, H));
   

   
   // Extracting the z component
   vec4 projected_point = projection_mat * vec4(new_point, 1.0);
   projected_point /= projected_point.w;
   
   gl_FragDepth = projected_point.z * 0.5 + 0.5;
   
   vec3 color;
   if (shading_type == 0) 
     {
       color = phong_shading(light_dir, camera_position, normal, gl_Color.xyz);
     }
   else if (shading_type == 1)
     {
       color = toon_shading(light_dir, normal, gl_Color.xyz);
     }

   gl_FragData[0] = vec4(color, gl_Color.a);
   gl_FragData[1].xyz = normal * 0.5 + 0.5;
}



