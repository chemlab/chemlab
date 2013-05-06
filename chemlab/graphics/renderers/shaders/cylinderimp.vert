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
  //mapping = at_mapping;

    //sphere_center = vec3(
    //    camera_mat*vec4(at_sphere_center, 1.0)).xyz;
    
    //sphere_radius = at_sphere_radius;
    vec4 actual_vertex = gl_Vertex;
    
    // Project the points on the plane (now this is in clip space)
    actual_vertex = mvproj * actual_vertex;

    // calculate the cylinder axis in camera space.  we want the
    // axis of our billboard, so we need to project this guy on the z
    // plane
    vec3 axis = normalize(mat3(camera_rotation) * at_cylinder_direction);
    
    // Side development of our cylinder billboard
    vec3 disp = normalize(cross(actual_vertex.xyz, axis));
    
    actual_vertex = vec4(actual_vertex.x + 0.5*at_mapping.x,
			 actual_vertex.y,
			 actual_vertex.z,
			 actual_vertex.w);
    
    gl_Position = actual_vertex;       
    gl_FrontColor = vec4(actual_vertex.x, actual_vertex.y, abs(actual_vertex.z), 1.0);
}
