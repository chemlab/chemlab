#version 120

attribute vec2 texCoord;
varying vec2 vert_texCoord;

void main() {
  vert_texCoord.xy = gl_MultiTexCoord0.xy;
  gl_Position = vec4(gl_Vertex.xy, 0.0, 1.0);
}
