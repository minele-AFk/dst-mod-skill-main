#ifdef SKINNED
uniform mat4 pv;
uniform mat4 fastanim_xform;
uniform vec4 fastanim_bones[64];
#else
uniform mat4 MatrixP;
uniform mat4 MatrixV;
uniform mat4 MatrixW;
#endif

uniform vec4 TIMEPARAMS;
uniform vec3 FLOAT_PARAMS;

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
    vec4 world_position = MatrixW * vec4(position, 1.0);
    if (FLOAT_PARAMS.z > 0.0)
    {
        float world_x = MatrixW[3][0];
        float world_z = MatrixW[3][2];
        world_position.y += sin(world_x + world_z + TIMEPARAMS.x * 3.0) * 0.025;
    }

    PS_TEXCOORD = vec3(
        POS2D_UV.z - 2.0 * sampler_index,
        POS2D_UV.w,
        sampler_index
    );
    gl_Position = MatrixP * MatrixV * world_position;
#endif
}
