#version 330 core

uniform sampler2D myTexture;
uniform vec3 objectColor;  // Cor do objeto (para debug quando não há textura)
uniform bool useColor;    // Se true, usa cor ao invés de textura

in vec2 texCoord;

out vec4 finalColor;

void main(){
    if (useColor) {
        // Usar cor sólida para debug
        finalColor = vec4(objectColor, 1.0);
    } else {
        // Usar textura normalmente
        vec4 texColor = texture(myTexture, texCoord);
        finalColor = texColor;
    }
}