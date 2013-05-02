#version 120

uniform sampler2D quad_texture;
uniform vec2 resolution;

void main() {
   vec4 color =  texture2D(quad_texture, 
			   vec2(gl_FragCoord.x/resolution.x,
				gl_FragCoord.y/resolution.y));
   gl_FragColor = vec4(color.xyz, 1.0);
}
