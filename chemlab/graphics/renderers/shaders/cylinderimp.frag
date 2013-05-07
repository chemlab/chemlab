//uniform vec3 light_dir;
//uniform vec3 camera;
//uniform mat4 mvproj;
//uniform float scalefac;
uniform mat4 projection_mat;


varying vec2 mapping;
varying vec3 nx, ny, nz;
varying vec3 view_pos;
varying float cyl_radius;
varying float cyl_length;
varying vec3 origin; // Origin of the cylinder, 0, 0
varying float dz;


void main()
{
  
  // Point intersection
  // Now it starts to get pretty hard, first we need to find the point
  vec3 point_impostorspace = vec3(mapping.x, mapping.y * 0.5 + 0.5,
				  sqrt(1.0 - mapping.x * mapping.x));
  
  //view_pos = origin + cyl_radius * point_impostorspace.x * nx 
  //  + cyl_length * point_impostorspace.y * ny + 
  //  cyl_radius * point_impostorspace.z * nz;
  
  // Now we need to convert from impostor space to view space for
  // light computations
  vec3 point_viewspace = view_pos + 
    vec3(0.0, 0.0, abs(dz)*point_impostorspace.z);
  
  // Now correct the depth value, we first project and then extract the z
  vec4 projected_point = projection_mat * vec4(point_viewspace, 1.0);
  projected_point /= projected_point.w;
  
  float ndc_depth = projected_point.z;
  
  gl_FragDepth = ((gl_DepthRange.far - gl_DepthRange.near) * ndc_depth +
  		  gl_DepthRange.near + gl_DepthRange.far)/2.0;


  // We need the normal
  vec3 normal_impostorspace = vec3(mapping.x, 0.0,  sqrt(1.0 - mapping.x*mapping.x));
  normal_impostorspace = normalize(normal_impostorspace);
  
  // Convert the normal in real_space
  vec3 normal_viewspace = normalize(mat3(nx, ny, nz) * normal_impostorspace);
  
  //gl_FragColor = color;
  float light_factor = dot(normal_viewspace, vec3(0.0, 0.0, 1.0));
  gl_FragData[0] = vec4(gl_Color.xyz, 1.0);
  //gl_FragData[0] = vec4( gl_Color.xyz, 1.0);
  //gl_FragData[0] = vec4(dz, dz, dz, 1.0);
  // This is needed for ssao and other effects that require normals
  // gl_FragData[1].xyz = normal * 0.5 + 0.5;
  
}
