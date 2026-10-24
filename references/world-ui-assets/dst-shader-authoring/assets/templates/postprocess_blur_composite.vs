attribute vec3 POSITION;
attribute vec2 TEXCOORD0;

varying vec2 PS_TEXCOORD0;

void main()
{
    gl_Position = vec4(POSITION, 1.0);
    PS_TEXCOORD0 = TEXCOORD0;
}
