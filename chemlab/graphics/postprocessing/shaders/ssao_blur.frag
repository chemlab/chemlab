#version 120

uniform sampler2D quad_texture;
uniform vec2 resolution;

const int blursize = 4; // This is the same as the random noise


void main() {

  vec2 texelSize =vec2(1.0/resolution.x,
		       1.0/resolution.y);
  
  vec2 uv = vec2(gl_FragCoord.x/resolution.x,
		gl_FragCoord.y/resolution.y);
  
  vec4 color =  texture2D(quad_texture, uv);
   
   
  vec4 fResult = vec4(0.0);
  vec2 hlim = vec2(float(-blursize) * 0.5 + 0.5);
   
  for (int x = 0; x < blursize; ++x) {
    for (int y = 0; y < blursize; ++y) {
      vec2 offset = vec2(float(x), float(y));
      offset += hlim;
      offset *= texelSize;
       
      fResult += texture2D(quad_texture, uv + offset);
    }
  }
   
  fResult = fResult / (blursize * blursize);
  
  gl_FragColor = vec4(color.xyz * fResult.w, 1.0);
}
