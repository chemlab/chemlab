uniform vec3 lightDir;
varying vec3 normal;
varying vec3 halfvector;
uniform vec3 camera;
                   
void main()
{
  // Fog computation
  float density = 8.0;
  
/*  const float LOG2 = 1.442695;
  
  float z = (gl_FragCoord.z/gl_FragCoord.w)/40;
  float fog_factor = exp2(-density*density*z*z*LOG2);

  // Black fog color
  vec4 fog_color = vec4(1,1,1,0);
  
  
  gl_FragColor = mix(fog_color, gl_Color, fog_factor); */
  
  gl_FragColor = gl_Color;
}
