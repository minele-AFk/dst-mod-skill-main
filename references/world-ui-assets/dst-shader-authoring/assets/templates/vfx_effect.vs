uniform mat4 MatrixPVW;

attribute vec3 POSITION;
attribute vec3 TEXCOORD0_LIFE;
attribute vec4 DIFFUSE;

varying vec3 PS_TEXCOORD_LIFE;
varying vec4 PS_COLOUR;

void main()
{
    gl_Position = MatrixPVW * vec4(POSITION, 1.0);
    PS_TEXCOORD_LIFE = TEXCOORD0_LIFE;
    PS_COLOUR = DIFFUSE;
    PS_COLOUR.rgb *= PS_COLOUR.a;
}
