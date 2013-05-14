// In this step we will perform alpha blending
#version 120

uniform sampler2D s_color1;
uniform sampler2D s_color2;
uniform vec2 offset;

void main() {
  vec2 pos = offset * gl_FragCoord.xy;
  vec4 color1 =  texture2D(s_color1, pos);
  vec4 color2 = texture2D(s_color2, pos);
  color2.rgb += 0.2;
  
  gl_FragColor = vec4(color1.rgb + color2.rgb*color2.a, 1.0);
}
