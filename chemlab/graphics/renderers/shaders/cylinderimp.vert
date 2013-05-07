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

varying vec2 mapping;
varying vec3 nx, ny, nz;
varying vec3 view_pos;
varying float cyl_radius;

attribute vec3 at_cylinder_direction;
//attribute vec3 at_cylinder_vert;
//varying vec3 cylinder_vert;

//attribute float at_cylinder_radius;
//varying float cylinder_radius;

void main()
{
  
  // Pass the mapping
  mapping = at_mapping;
  cyl_radius = cylinder_radius;
  
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
  
  normal_direction = -normalize(cross(view_direction.xyz, view_cylinder_start.xyz));
  
  
  nx = normal_direction;// perpendicular to cylinder axis, it's our 'x'
  ny = normalize(view_direction);  // cylinder axis
  nz = cross(nx, ny); // The direction of cylinder that points in front of us
  
  displacement = vec4(normal_direction * at_mapping.x * cylinder_radius + 
		      view_direction.xyz * (at_mapping.y * 0.5 + 0.5),  0.0);
  
  view_vertex = view_cylinder_start + displacement;
  // We need also an extra displacement at end caps
  
  
  
  view_pos = view_vertex.xyz/view_vertex.w;
  
  gl_Position = projection_mat * view_vertex;       

  
  gl_FrontColor = gl_Color;
}
