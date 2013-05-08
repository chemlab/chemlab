#version 120
uniform mat4 projection_mat;

varying vec4 vertex_viewspace; // this guy should be the surface point.

varying vec3 U, V, H;
varying float cylinder_radiusv;
varying float cylinder_lengthv;

varying vec4 cylinder_origin;
varying vec3 local_coords;

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
   
   
   float light_fact = dot(normal, vec3(0.0, 0.0, 1.0));
   

   gl_FragData[0] = vec4(light_fact * gl_Color.xyz , 1.0);
   gl_FragData[1] = vec4(normal, 1.0);
}
