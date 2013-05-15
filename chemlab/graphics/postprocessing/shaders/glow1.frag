// The first step in the glow shader is to create a mask

uniform sampler2D s_color; 
uniform vec2 offset; 

void main(void) {

vec4 color = texture2D(s_color, offset * gl_FragCoord.xy);
color.rgb = vec3(1.0, 1.0, 1.0);
gl_FragColor = vec4(color.rgb * (1.0 - color.a), 1.0 - color.a);

}
