#version 120

uniform mat4 mvproj;
uniform mat4 camera_mat;
uniform mat4 projection_mat;

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

//attribute vec3 at_cylinder_vert;
//varying vec3 cylinder_vert;

//attribute float at_cylinder_radius;
//varying float cylinder_radius;

void main()
{
  //mapping = at_mapping;
    
    //sphere_center = vec3(
    //    camera_mat*vec4(at_sphere_center, 1.0)).xyz;
    
    //sphere_radius = at_sphere_radius;
    vec4 actual_vertex = gl_Vertex;
    
    // First rotate the points
    actual_vertex = camera_mat * actual_vertex;
    
    actual_vertex = vec4(
			 actual_vertex.x + (at_mapping.x*0.5 + 0.5),
			 actual_vertex.y,
			 actual_vertex.z,
			 actual_vertex.w);
    
    gl_Position = projection_mat * actual_vertex;       
    gl_FrontColor = vec4(at_mapping*0.5 + 0.5, 0.0, 1.0);
}
