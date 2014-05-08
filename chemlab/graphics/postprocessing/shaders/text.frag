#version 120

uniform sampler2D quad_texture;
uniform vec2 resolution;

varying vec2 vert_texCoord;

void main() {
   /* vec4 color =  texture2D(quad_texture,  */
   /* 			   vec2(gl_FragCoord.x/resolution.x, */
   /* 				gl_FragCoord.y/resolution.y)); */
   vec4 color =  texture2D(quad_texture, 
			   vec2(1.0, -1.0) * vert_texCoord.xy);
   gl_FragColor = vec4(color.xyz*vec3(1.0, 0.0, 0.0), color.a + 0.1);
}
