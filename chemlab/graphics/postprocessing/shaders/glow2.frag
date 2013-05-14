// Simple gaussian blur filter
uniform sampler2D s_color; // the texture with the scene you want to blur
uniform vec2 offset; 
uniform float radius;
uniform int horizontal;

void main(void)
{
   vec4 sum = vec4(0.0);
   vec2 blurSize=offset * radius;
   vec2 pos = offset * gl_FragCoord.xy;
   vec3 color;
   // take nine samples, with the distance blurSize between them

   if (horizontal == 0) {
     sum += texture2D(s_color, vec2(pos.x - 4.0*blurSize.x, pos.y)) * 0.05;
     sum += texture2D(s_color, vec2(pos.x - 3.0*blurSize.x, pos.y)) * 0.09;
     sum += texture2D(s_color, vec2(pos.x - 2.0*blurSize.x, pos.y)) * 0.12;
     sum += texture2D(s_color, vec2(pos.x - blurSize.x, pos.y)) * 0.15;
     sum += texture2D(s_color, vec2(pos.x, pos.y)) * 0.16;
     sum += texture2D(s_color, vec2(pos.x + blurSize.x, pos.y)) * 0.15;
     sum += texture2D(s_color, vec2(pos.x + 2.0*blurSize.x, pos.y)) * 0.12;
     sum += texture2D(s_color, vec2(pos.x + 3.0*blurSize.x, pos.y)) * 0.09;
     sum += texture2D(s_color, vec2(pos.x + 4.0*blurSize.x, pos.y)) * 0.05;
   }
   else if (horizontal == 1) {
     sum += texture2D(s_color, vec2(pos.x, pos.y - 4.0*blurSize.y)) * 0.05;
     sum += texture2D(s_color, vec2(pos.x, pos.y - 3.0*blurSize.y)) * 0.09;
     sum += texture2D(s_color, vec2(pos.x, pos.y - 2.0*blurSize.y)) * 0.12;
     sum += texture2D(s_color, vec2(pos.x, pos.y - blurSize.y)) * 0.15;
     sum += texture2D(s_color, vec2(pos.x, pos.y)) * 0.16;
     sum += texture2D(s_color, vec2(pos.x, pos.y + blurSize.y)) * 0.15;
     sum += texture2D(s_color, vec2(pos.x, pos.y + 2.0*blurSize.y)) * 0.12;
     sum += texture2D(s_color, vec2(pos.x, pos.y + 3.0*blurSize.y)) * 0.09;
     sum += texture2D(s_color, vec2(pos.x, pos.y + 4.0*blurSize.y)) * 0.05;
   }
     
   //gl_FragColor = sum;
   gl_FragColor = sum.rgba;
   
}
