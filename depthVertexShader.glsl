#version 330 core

uniform mat4 modelMatrix;
uniform mat4 lightSpaceMatrix;

layout(location = 0) in vec3 a_pos;

void main() {
    vec4 worldPos = modelMatrix * vec4(a_pos, 1.0);
    gl_Position = lightSpaceMatrix * worldPos;
}
