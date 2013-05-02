#version 120

uniform sampler2D quad_texture;
uniform float time;

void main() {
   vec4 color =  texture2D(quad_texture, vec2(gl_FragCoord.x/600, gl_FragCoord.y/600));
   gl_FragColor = vec4(color.xyz + vec3(0.5, 0.5, 0.5)*sin(time), 1.0);
}
