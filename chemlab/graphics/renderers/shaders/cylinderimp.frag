#version 120
varying vec4 vertex_viewspace;

varying vec3 U, V, H;

void main()
{
  // We need to raytrace the cylinder (!)
  // we can do the intersection in impostor space
  
  // Calculate the ray direction in viewspace
  vec3 ray_origin = vec3(0.0, 0.0, 0.0);
  vec3 ray_target = vertex_viewspace.xyz;
  vec3 ray_direction = normalize(ray_target - ray_origin);
  
  // basis = local coordinate system of cylinder
  mat3 basis = mat3(U, V, H);
  
  gl_FragData[0] = vec4(ray_direction.xyz, 1.0);
}
