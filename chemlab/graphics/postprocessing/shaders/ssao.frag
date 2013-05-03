#version 120
precision mediump float;

uniform sampler2D quad_texture;
uniform sampler2D normal_texture;
uniform sampler2D depth_texture;
uniform sampler2D noise_texture;

uniform vec2 resolution;

const int MAX_KERNEL_SIZE = 128;
const float kernel_radius = 10.0; // TODO, transfer as an uniform

uniform vec3 random_kernel[MAX_KERNEL_SIZE];
uniform int kernel_size;


uniform mat4 i_proj; // Inverse projection
uniform mat4 proj; // projection

float linearizeDepth(in float depth, in mat4 projMatrix) {
	return projMatrix[3][2] / (depth - projMatrix[2][2]);
}

void main() {
  
  float u = gl_FragCoord.x/resolution.x;
  float v = gl_FragCoord.y/resolution.y;
  vec2 uv = vec2(u, v);
  
  vec4 color = texture2D(quad_texture, uv);
  vec4 normal = texture2D(normal_texture, uv);
  vec4 depth = texture2D(depth_texture, uv); // This is gl_FragDepth
  
   
  // Get the projected point

  // Those are the coordinates in normalized device coordinates
  float x = u * 2.0 - 1.0;
  float y = v * 2.0 - 1.0;
  float z = depth.x * 2.0 - 1.0;
  
  vec4 projected_pos = vec4(x, y, z, 1.0);
  
  // Unproject them
  vec4 pos = i_proj * projected_pos;
  
  // 4x4 noise texture, we have to tile this for the screen
  float rand_u, rand_v;
  rand_u = gl_FragCoord.x/4.0;
  rand_v = gl_FragCoord.y/4.0;
  
  vec4 noise_value = texture2D(noise_texture, vec2(rand_u, rand_v));
  vec3 random_axis = noise_value.xyz * 2.0 - 1.0;

  // gram-schmidt
  vec3 tangent = normalize(random_axis - normal.xyz
  			   * dot(random_axis, normal.xyz));
  vec3 bitangent = cross(normal.xyz, tangent);
  mat3 tbn = mat3(tangent, bitangent, normal.xyz);

  
  float occlusion = 0.0;
  
  for (int i=0; i < kernel_size; ++i){
    // Sample position
    vec3 sample = tbn * random_kernel[i];
    sample = sample * kernel_radius + pos.xyz;
    
    // Project sample position
    vec4 offset = vec4(sample, 1.0);
    offset = proj * offset;
    // offset.xy /= offset.w;
    offset.xy = offset.xy * 0.5 + 0.5;
    
    // Sample depth
    vec4 sample_depth_v = texture2D(depth_texture, offset.xy);
    float sample_depth = sample_depth_v.x;
    offset.z = sample_depth;
    offset.w = 1.0;
    
    sample_depth = (i_proj * offset).z;
  
    
    if (sample_depth >= sample.z) {
      occlusion += 1.0;
    }
  }
  
  occlusion = 1.0 - (occlusion / float(kernel_size));
  
  gl_FragColor = vec4(occlusion, occlusion, occlusion,  1.0);
}
