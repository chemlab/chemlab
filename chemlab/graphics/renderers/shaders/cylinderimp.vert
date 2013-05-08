#version 120

uniform mat4 model_view_mat;
uniform mat4 model_view_projection_mat;
uniform mat4 model_view_rotation_mat;
uniform mat4 projection_mat;

attribute vec3 cylinder_axis;
attribute float cylinder_radius;


attribute vec3 vert_local_coordinate; // Those coordinates are between
				      // 0,1

varying vec4 vertex_viewspace;
varying float cylinder_radiusv;
varying float cylinder_lengthv;
varying vec3 U, V, H;
varying vec4 cylinder_origin;
varying vec3 local_coords;


void main()
{
  
  float cylinder_length = length(cylinder_axis);
  
  cylinder_lengthv = cylinder_length;
  cylinder_radiusv = cylinder_radius;
  
  // We compute the bounding box
  
  // We receive 8 points, and we should place this 8 points
  // at their bounding box position
  vec4 cylinder_base = vec4(gl_Vertex.xyz, 1.0);
  cylinder_origin = model_view_mat * cylinder_base;
  cylinder_origin /= cylinder_origin.w;
  
  // We receive from the program the origin that is the cylinder start
  // point. To this guy we have to add the local coordinates.
  
  // Local vectors, u, v, h
  vec3 u, h, v;
  
  h = normalize(cylinder_axis);
  u = cross(h, vec3(1.0, 0.0, 0.0));
  if (length(u) < 0.001){
    u = cross(h, vec3(0.0, 0.0, 1.0));
  }
  u = normalize(u);
  v = normalize(cross(u, h));
  
  // We do the addition in object space
  vec4 vertex = cylinder_base;
  vertex.xyz += u * (vert_local_coordinate.x*2.0 - 1.0) * cylinder_radius; 
  vertex.xyz += v * (vert_local_coordinate.y*2.0 - 1.0) * cylinder_radius;  
  vertex.xyz += h * vert_local_coordinate.z * cylinder_length;
  
  // Vertex in view space
  vertex_viewspace = vertex * model_view_mat;
  //vertex_viewspace /= vertex_viewspace.w;
  
  // Base vectors of cylinder in view space
  U = normalize(mat3(model_view_rotation_mat) * u);
  V = normalize(mat3(model_view_rotation_mat) * v);
  H = normalize(mat3(model_view_rotation_mat) * h);
  
  // Projecting
  vertex = model_view_projection_mat * vertex;
  
  // To reconstruct the current fragment position, I pass the local
  // coordinates
  local_coords = vert_local_coordinate;
  
  gl_Position = vertex;
  gl_FrontColor = gl_Color;
}
