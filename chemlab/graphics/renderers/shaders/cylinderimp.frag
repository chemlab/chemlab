#version 120

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
  surface_point += H * (local_coords.y * cylinder_lengthv);
  surface_point += V * (local_coords.z*2.0 - 1.0) * cylinder_radiusv;  

  // We need to raytrace the cylinder (!)
  // we can do the intersection in impostor space
  
  // Calculate the ray direction in viewspace
  vec3 ray_origin = vec3(0.0, 0.0, 0.0);
  vec3 ray_target = surface_point;
  vec3 ray_direction = normalize(ray_target - ray_origin);
  
  // basis = local coordinate system of cylinder
  mat3 basis = mat3(U, V, H);

  // Origin of the ray in cylinder space
  vec3 P = - cylinder_origin.xyz;
  P = basis * P;
  
  // Direction of the ray in cylinder space
  vec3 D = basis * ray_direction;
  
  // Now the intersection is between z-axis aligned cylinder and a ray
  float a0 = P.x*P.x + P.y*P.y - cylinder_radiusv*cylinder_radiusv; 
  float a1 = P.x*D.x + P.y*D.y;
  float a2 = D.x*D.x + D.y*D.y;
  float d = a1 * a1 - a0 * a2;
  
  //if (d < 0.0) 
  //  discard;
  gl_FragData[0] = vec4(surface_point, 0.0, 0.0, 1.0);
}
