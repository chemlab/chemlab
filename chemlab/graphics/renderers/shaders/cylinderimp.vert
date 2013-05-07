#version 120

uniform mat4 model_view_mat;
uniform mat4 model_view_projection_mat;
uniform mat4 model_view_rotation_mat;

attribute vec3 cylinder_axis;
attribute float cylinder_radius;

attribute vec3 vert_local_coordinate; // Those coordinates are between
				      // 0,1

varying vec4 vertex_viewspace;
varying vec3 U, V, H;

void main()
{
  
  float cylinder_length = length(cylinder_axis);
  // We compute the bounding box
  
  // We receive 8 points, and we should place this 8 points
  // at their bounding box position
  vec3 cylinder_base = gl_Vertex.xyz;
  
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
  vec4 vertex = vec4(cylinder_base, 1.0);
  vertex.xyz += u * (vert_local_coordinate.x*2.0 - 1.0) * cylinder_radius; 
  vertex.xyz += h * vert_local_coordinate.y * cylinder_length;
  vertex.xyz += v * (vert_local_coordinate.z*2.0 - 1.0) * cylinder_radius;  
  
  vertex = model_view_projection_mat * vertex;
  
  // Vertex in view space
  vertex_viewspace = model_view_mat * vertex;
  vertex_viewspace /= vertex_viewspace.w; // Not sure if the vertex
					  // interpolation will yield
					  // good results
  
  // Base vectors of cylinder in view space
  U = mat3(model_view_rotation_mat) * u;
  V = mat3(model_view_rotation_mat) * v;
  H = mat3(model_view_rotation_mat) * h;
  
  gl_Position = vertex;
  //gl_Position = vec4(vert_local_coordinate.xy * 2.0 - 1.0, 0.0, 1.0);
  gl_FrontColor = vec4(vert_local_coordinate.xyz, 1.0);
}
