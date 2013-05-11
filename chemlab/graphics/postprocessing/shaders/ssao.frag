#version 120

uniform sampler2D quad_texture;
uniform sampler2D normal_texture;
uniform sampler2D depth_texture;
uniform sampler2D noise_texture;

uniform vec2 resolution;

const int MAX_KERNEL_SIZE = 128;

uniform vec3 random_kernel[MAX_KERNEL_SIZE];
uniform int kernel_size;
uniform float kernel_radius;
uniform float ssao_power;

uniform mat4 i_proj; // Inverse projection
uniform mat4 proj; // projection

void main() {
  
  float u = gl_FragCoord.x/resolution.x;
  float v = gl_FragCoord.y/resolution.y;
  vec2 uv = vec2(u, v);
  
  vec4 color = texture2D(quad_texture, uv);
  vec3 normal = texture2D(normal_texture, uv).xyz;
  vec4 depth = texture2D(depth_texture, uv); // This is gl_FragDepth
  
  normal.xyz = normal.xyz * 2.0 - 1.0;
  
  // Get the projected point

  // Those are the coordinates in normalized device coordinates
  float x = u * 2.0 - 1.0;
  float y = v * 2.0 - 1.0;
  float z = depth.x * 2.0 - 1.0;
  
  vec4 projected_pos = vec4(x, y, z, 1.0);
  
  // Unproject them
  vec4 pos = i_proj * projected_pos;
  pos /= pos.w; // This is our unprojected guy
  
  // Test if it's a background pixel
  if (z == 1.0)
    discard;
  
  // 4x4 noise texture, we have to tile this for the screen
  float rand_u, rand_v;
  rand_u = gl_FragCoord.x/4.0;
  rand_v = gl_FragCoord.y/4.0;
  
  vec4 noise_value = texture2D(noise_texture, vec2(rand_u, rand_v));
  vec3 rvec = noise_value.xyz * 2.0 - 1.0;

  // gram-schmidt
  vec3 tangent = normalize(rvec - normal.xyz
  			   * dot(rvec, normal.xyz));
  vec3 bitangent = cross(normal.xyz, tangent);
  mat3 tbn = mat3(tangent, bitangent, normal.xyz);

  vec4 offset;
  vec3 sample;
  float sample_depth;
  vec4 sample_depth_v;
  float occlusion = 0.0;
  
  for (int i=0; i < kernel_size; ++i){
    // Sample position
    sample = (tbn * random_kernel[i]) * kernel_radius;
    sample = sample + pos.xyz;
    
    // Project sample position
    offset = vec4(sample, 1.0);
    offset = proj * offset; // In the range -w, w
    offset /= offset.w; // in the range -1, 1
    offset.xyz = offset.xyz * 0.5 + 0.5;
    
    // Sample depth
    sample_depth_v = texture2D(depth_texture, offset.xy);
    sample_depth = sample_depth_v.x;
    
    // We have to linearize it.. again
    vec4 throwaway = vec4(offset.xy, sample_depth, 1.0); // range 0, 1
    throwaway.xyz = throwaway.xyz * 2.0 - 1.0;
    throwaway = i_proj * throwaway;
    throwaway /= throwaway.w;
    
    if (throwaway.z >= sample.z) {
      float rangeCheck= abs(pos.z - throwaway.z) < kernel_radius ? 1.0 : 0.0;
      occlusion += 1.0 * rangeCheck; 
    }
  }
  
  occlusion = 1.0 - (occlusion / float(kernel_size));
  occlusion = pow(occlusion, ssao_power);

  gl_FragColor = vec4(color.xyz, occlusion);
}
