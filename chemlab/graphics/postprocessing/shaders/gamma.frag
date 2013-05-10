uniform sampler2D rendered_texture;
uniform vec2 resolution;
uniform float gamma;


void main(void)
{
  vec2 uv = gl_FragCoord.xy/resolution;
  vec3 color = texture2D(rendered_texture, uv).rgb;
  
  gl_FragColor.rgb = pow(color, vec3(1.0 / gamma));
  
  gl_FragColor.a = 1.0;
}
