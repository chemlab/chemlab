uniform sampler2D s_depth;
uniform sampler2D s_norm;
uniform sampler2D s_color;
uniform vec2 texcoordOffset;
uniform mat4 inv_projection;

vec2 offsets [8];

float linearize_depth(float depth, mat4 proj_mat) {
  return proj_mat[3][2] / (depth - proj_mat[2][2]);
}

void main() {
  vec2 pos = gl_FragCoord.st * texcoordOffset;
  vec4 depth = texture2D(s_depth, pos);
  vec4 norm = texture2D(s_norm, pos);

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

  float base_depth = depth.r;
  vec3 base_norm = normalize(norm.xyz * 2.0 - 1.0);

  float threshold_depth = 0.05 * (1.0 - depth.r);
  float threshold_norm = 0.95;

  if (depth.r < 0.0){
    discard;
  }
  
  for (int i = 0; i < 8; i++) {
    depth = texture2D(s_depth, pos + offsets[i]);
    norm.xyz = normalize(texture2D(s_norm, pos + offsets[i]).xyz * 2.0 - 1.0);
    
    if (abs(depth.z - base_depth) > threshold_depth) 
      {
	darkness_depth += 1.0;
	break;
      }

    if (dot(norm.xyz, base_norm) < threshold_norm) 
      {
	darkness_norm += 1.0;
	break;
      }
  }

  float illum = 1.0 - (darkness_depth + darkness_norm);

  gl_FragColor.rgb = texture2D(s_color, pos).rgb * illum;
  gl_FragColor.a = 1.0;
}
