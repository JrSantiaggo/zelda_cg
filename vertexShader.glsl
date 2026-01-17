#version 330 core

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform vec2 spriteOffset;  // Offset do sprite sheet (coluna, linha)
uniform vec2 spriteSize;     // Tamanho de cada sprite (1/cols, 1/rows)

layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec2 a_texCoord;
layout(location = 2) in vec3 a_normal;  // Normal do vértice (para iluminação futura)

out vec2 texCoord;
out vec3 normal;           // Normal no espaço do mundo (para iluminação futura)
out vec3 fragPos;          // Posição do fragmento no espaço do mundo (para iluminação futura)

void main(){
    // Calcular coordenadas UV do sprite sheet
    // a_texCoord vai de (0,0) a (1,1) para o sprite completo
    // Multiplicamos pelo tamanho do sprite e adicionamos o offset
    texCoord = a_texCoord * spriteSize + spriteOffset;
    
    // Calcular posição do vértice no espaço do mundo
    vec4 worldPos = modelMatrix * vec4(a_pos, 1.0);
    fragPos = vec3(worldPos);
    
    // Transformar normal para espaço do mundo
    // Usar matriz normal (inversa transposta da modelMatrix) para normais
    // Por simplicidade, usando apenas mat3(modelMatrix) - funciona bem se não houver escala não-uniforme
    normal = mat3(transpose(inverse(modelMatrix))) * a_normal;
    // Normalizar para garantir comprimento 1
    normal = normalize(normal);
    
    gl_Position = projectionMatrix * viewMatrix * worldPos;
}