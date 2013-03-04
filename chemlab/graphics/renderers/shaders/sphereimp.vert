//
// This is for projection and lighting
//

uniform mat4 mvproj;
uniform mat4 camera_mat;
uniform mat4 projection_mat;

// Camera in world coordinates
uniform vec3 camera; 
// light direction in world coordinates
uniform vec3 light_dir; 

// Scale factor
uniform float scalefac;

// Useful to compute sphere points
attribute vec2 at_mapping;
varying vec2 mapping;

attribute vec3 at_sphere_center;
varying vec3 sphere_center;

attribute float at_sphere_radius;
varying float sphere_radius;

void main()
{
    mapping = at_mapping;
    
    sphere_center = vec3(
        camera_mat*vec4(at_sphere_center, 1.0)).xyz;
    
    sphere_radius = at_sphere_radius;
    vec4 actual_vertex = gl_Vertex;

    // First rotate the points
    actual_vertex = camera_mat * actual_vertex;
    
    actual_vertex = vec4(
        actual_vertex.xy+mapping*sphere_radius*scalefac,
        actual_vertex.z,
        actual_vertex.w);
    
    gl_Position = projection_mat * actual_vertex;       
    gl_FrontColor = gl_Color;
}