// World AnimState bloom-pass template. This is not a main-pass replacement.
#ifdef SKINNED
uniform mat4 pv;
uniform mat4 fastanim_xform;
uniform vec4 fastanim_bones[64];
#else
uniform mat4 MatrixP;
uniform mat4 MatrixV;
uniform mat4 MatrixW;
#endif

attribute vec4 POS2D_UV;
varying vec3 PS_TEXCOORD;

void main()
{
    vec3 position = vec3(POS2D_UV.xy, 0.0);
    float sampler_index = floor(POS2D_UV.z / 2.0);

#ifdef SKINNED
    float bone_index = floor((POS2D_UV.w + 0.5) / 2.0);
    int matrix_index = int(bone_index);
    vec4 matrix_a = fastanim_bones[matrix_index * 2];
    vec4 matrix_b = fastanim_bones[matrix_index * 2 + 1];

    mat4 bone_world = mat4(
        matrix_a.x, matrix_a.y, 0.0, 0.0,
        matrix_a.z, matrix_a.w, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        matrix_b.x, matrix_b.y, 0.0, 1.0
    );

    PS_TEXCOORD = vec3(
        POS2D_UV.z - 2.0 * sampler_index,
        POS2D_UV.w - 2.0 * bone_index,
        sampler_index
    );
    gl_Position = pv * fastanim_xform * bone_world * vec4(position, 1.0);
#else
    PS_TEXCOORD = vec3(
        POS2D_UV.z - 2.0 * sampler_index,
        POS2D_UV.w,
        sampler_index
    );
    gl_Position = MatrixP * MatrixV * MatrixW * vec4(position, 1.0);
#endif
}
