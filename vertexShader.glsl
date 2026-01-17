#version 330 core

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec2 a_texCoord;

out vec2 texCoord;

void main(){
    texCoord = a_texCoord;
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(a_pos, 1.0);
}