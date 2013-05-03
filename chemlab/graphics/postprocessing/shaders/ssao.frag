#version 120

uniform sampler2D quad_texture;
uniform sampler2D normal_texture;
uniform sampler2D depth_texture;

uniform vec2 resolution;

void main() {
   vec4 color = texture2D(quad_texture, 
			   vec2(gl_FragCoord.x/resolution.x,
				gl_FragCoord.y/resolution.y));
   vec4 normal = texture2D(normal_texture, 
			    vec2(gl_FragCoord.x/resolution.x,
				 gl_FragCoord.y/resolution.y));
   
   float depth =  texture2D(depth_texture, 
			    vec2(gl_FragCoord.x/resolution.x,
				 gl_FragCoord.y/resolution.y));
   
   
   gl_FragColor = vec4(depth, depth, depth, 1.0);
}
