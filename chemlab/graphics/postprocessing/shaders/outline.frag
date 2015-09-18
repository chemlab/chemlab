#version 120
uniform sampler2D s_depth;
uniform sampler2D s_norm;
uniform sampler2D s_color;
uniform vec2 texcoordOffset;
uniform mat4 inv_projection;
uniform int whichoutline; // 0 - depthnormal; 1 - depthonly; 0 - normalonly;
uniform vec3 outline_color;

vec2 offsets [8];

float linearize_depth(float depth, mat4 inv_proj_mat) {
  return (inv_proj_mat[2][2] * depth + inv_proj_mat[3][2]) / (inv_proj_mat[2][3]*depth + inv_proj_mat[3][3]);
}

void main() {
  vec2 pos = gl_FragCoord.st * texcoordOffset;
  vec4 depth = texture2D(s_depth, pos);
  vec3 norm = texture2D(s_norm, pos).xyz;

  offsets[0] = vec2(-texcoordOffset.x, -texcoordOffset.y);
  offsets[1] = vec2(-texcoordOffset.x, 0);
  offsets[2] = vec2(-texcoordOffset.x, texcoordOffset.y);

  offsets[3] = vec2(0, -texcoordOffset.y);
  offsets[4] = vec2(0,  texcoordOffset.y);


  offsets[5] = vec2(texcoordOffset.x, -texcoordOffset.y);
  offsets[6] = vec2(texcoordOffset.x, 0);
  offsets[7] = vec2(texcoordOffset.x, texcoordOffset.y);
  
  float darkness_depth = 0.0;
  float darkness_norm = 0.0;

  // We need to linearize this
  float base_depth = linearize_depth(depth.r * 2.0 - 1.0, inv_projection);
  vec3 base_norm = norm.xyz * 2.0 - 1.0;

  float zfar = linearize_depth(-1.0, inv_projection);
  float znear = linearize_depth(1.0, inv_projection);
  
  float threshold_depth = 0.1;
  float threshold_norm = 0.80;

  if (depth.r < 0.0){
    discard;
  }
  
  vec3 sample_norm;
  
  for (int i = 0; i < 8; i++) {
    depth = texture2D(s_depth, pos + offsets[i]);
    sample_norm = texture2D(s_norm, pos + offsets[i]).xyz * 2.0 - 1.0;
    
    float sample_depth = linearize_depth(depth.r * 2.0 - 1.0, inv_projection);
    
    
    if (abs(sample_depth - base_depth) > threshold_depth) 
      {
	darkness_depth += 1.0;
      }

    if (dot(sample_norm, base_norm) < threshold_norm) 
      {
	darkness_norm += 1.0;
      }
  }

  float illum;

  if (whichoutline == 0) {
    illum = 1.0 - (darkness_depth + darkness_norm);
  }
  else if (whichoutline == 1) {
    illum = 1.0 - darkness_depth;
  }
  else if (whichoutline == 2) {
    illum = 1.0 - darkness_norm;
  }
  
  gl_FragColor.rgb = mix(outline_color.rgb, texture2D(s_color, pos).rgb, illum);
  gl_FragColor.a = 1.0;
}
