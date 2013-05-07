#version 120

uniform mat4 mvproj;
uniform mat4 camera_mat;
uniform mat4 projection_mat;
uniform mat4 camera_rotation;

// Camera in world coordinates
uniform vec3 camera; 

// light direction in world coordinates
uniform vec3 light_dir; 

// Scale factor
//uniform float scalefac;

// The cylinder radius
attribute float cylinder_radius;

// Useful to compute sphere points
attribute vec2 at_mapping;
//varying vec2 mapping;

attribute vec3 at_cylinder_direction;
//attribute vec3 at_cylinder_vert;
//varying vec3 cylinder_vert;

//attribute float at_cylinder_radius;
//varying float cylinder_radius;

void main()
{
  // Cylinder start point
  vec3 cylinder_start = gl_Vertex.xyz;
  vec3 cylinder_end = cylinder_start + at_cylinder_direction;  
  
  // In view space
  vec4 view_cylinder_start = camera_mat * vec4(cylinder_start, 1.0);
  vec4 view_cylinder_end = camera_mat * vec4(cylinder_end, 1.0);

  view_cylinder_start /= view_cylinder_start.w;
  view_cylinder_end /= view_cylinder_end.w;
  
  vec3 view_direction = view_cylinder_end.xyz - view_cylinder_start.xyz;
  vec3 normal_direction;
  vec4 displacement;
  vec4 view_vertex;
  
  normal_direction = normalize(cross(vec3(view_direction.xy, 0.0), view_cylinder_start.xyz));
  displacement = vec4(normalize(normal_direction.xy) * at_mapping.x * 0.5 + 
		      view_direction.xy * (at_mapping.y * 0.5 + 0.5), 
		      0.0, 0.0);
  view_vertex = view_cylinder_start + displacement;
  view_vertex.z = max(view_cylinder_start.z, view_cylinder_end.z); 
  gl_Position = projection_mat * view_vertex;       
  gl_FrontColor = vec4(view_vertex.x, view_vertex.y, abs(view_vertex.z), 1.0);
}
