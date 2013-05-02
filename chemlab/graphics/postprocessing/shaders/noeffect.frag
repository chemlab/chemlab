#version 120

uniform sampler2D quad_texture;

void main() {
   vec4 color =  texture2D(quad_texture, vec2(gl_FragCoord.x/600, gl_FragCoord.y/600));
   gl_FragColor = vec4(color.xyz + vec3(0.1, 0.1, 0.1), 1.0);
}
