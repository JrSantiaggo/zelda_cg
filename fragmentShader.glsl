#version 330 core

uniform sampler2D myTexture;
uniform vec3 objectColor;  // Cor do objeto (para debug quando não há textura)
uniform bool useColor;    // Se true, usa cor ao invés de textura
uniform vec3 ambientLight; // Cor/intensidade da luz ambiente global (R, G, B)
uniform bool isSprite;    // Se true, é sprite 2D (não recebe iluminação)
uniform float spriteHitFlash;  // 0–1: mistura com branco (flash ao ser atingido)
uniform vec3 directionalLightDir; // Direção da luz direcional (normalizada)
uniform vec3 directionalLightColor; // Cor/intensidade da luz direcional (R, G, B)
uniform vec3 cameraPos;   // Posição da câmera no espaço do mundo (para cálculo especular)
uniform float specularStrength; // Intensidade do brilho especular (0.0 a 1.0)
uniform float shininess;  // Expoente especular (shininess)
uniform vec3 specularColor; // Cor do brilho especular (R, G, B)
uniform vec3 playerPos;   // Posição do jogador (centro da luz spot)
uniform float spotlightRadius;   // Raio do spot (= ENEMY_DETECTION_HALF_EXTENT)
uniform float spotlightDarkFactor; // Escurecimento fora do spot (0.25 = 25%)

in vec2 texCoord;
in vec3 normal;           // Normal no espaço do mundo (já transformada e normalizada)
in vec3 fragPos;          // Posição do fragmento no espaço do mundo (para iluminação futura)

out vec4 finalColor;

void main(){
    vec3 baseColor;
    float alpha = 1.0;  // Alpha padrão
    
    // Obter cor base do objeto (textura ou cor sólida)
    if (useColor) {
        // Usar cor sólida para debug
        baseColor = objectColor;
    } else {
        // Usar textura normalmente
        vec4 texColor = texture(myTexture, texCoord);
        baseColor = texColor.rgb;
        alpha = texColor.a;  // Preservar alpha da textura (importante para sprites com transparência)
    }
    
    // Descartar fragmentos transparentes: evitam que áreas transparentes do PNG
    // escrevam no depth buffer e “cubram” o jogador atrás (o depth ficaria ocupado
    // pelo retângulo inteiro do sprite, inclusive as bordas transparentes).
    if (alpha < 0.01) discard;
    
    // Normalizar a direção da luz (garantir que está normalizada)
    vec3 lightDir = normalize(directionalLightDir);
    
    // Normalizar a normal (garantir comprimento 1)
    vec3 norm = normalize(normal);
    
    // Calcular iluminação difusa usando modelo de Lambert
    // diffuse = max(dot(normal, lightDir), 0.0) * lightColor
    // O produto escalar entre normal e direção da luz determina o ângulo
    // Se > 0, a superfície está voltada para a luz; se < 0, está de costas
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * directionalLightColor;
    
    // Flash ao ser atingido (sprites): pisca para branco
    if (isSprite && spriteHitFlash > 0.0) {
        baseColor = mix(baseColor, vec3(1.0, 1.0, 1.0), spriteHitFlash);
    }
    // Aplicar iluminação baseado no tipo de objeto
    vec3 finalColorRGB;
    if (isSprite) {
        // Sprites 2D não recebem iluminação - usam cor/textura direta
        // Isso mantém o visual original e legível do sprite
        finalColorRGB = baseColor;
    } else {
        // Objetos 3D recebem iluminação Phong completa: ambiente + difusa + especular
        
        // Calcular iluminação especular (modelo de Phong)
        // viewDir: direção da câmera para o fragmento
        vec3 viewDir = normalize(cameraPos - fragPos);
        
        // reflectDir: direção do reflexo da luz (vetor refletido)
        // reflect(-lightDir, norm) calcula o reflexo da luz na superfície
        vec3 reflectDir = reflect(-lightDir, norm);
        
        // Cálculo do brilho especular usando modelo de Phong
        // spec = (dot(viewDir, reflectDir))^shininess * specularStrength
        // O produto escalar entre viewDir e reflectDir determina quão alinhado está o reflexo
        // Se viewDir está próximo de reflectDir, há brilho (specular highlight)
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
        vec3 specular = spec * specularStrength * specularColor;
        
        // Iluminação Phong completa:
        // - Ambiente: iluminação base uniforme
        // - Difusa: variação com o ângulo da luz (modelo de Lambert)
        // - Especular: brilho que varia com o ângulo de visão (modelo de Phong)
        finalColorRGB = baseColor * (ambientLight + diffuse) + specular;

        // Luz spot ao redor do jogador: fora do raio o mapa fica mais escuro (mesmo raio da detecção do inimigo)
        float dist_xz = length(fragPos.xz - playerPos.xz);
        float in_spot = 1.0 - smoothstep(spotlightRadius * 0.85, spotlightRadius, dist_xz);
        float spot_factor = in_spot + (1.0 - in_spot) * spotlightDarkFactor;
        finalColorRGB *= spot_factor;
    }
    
    finalColor = vec4(finalColorRGB, alpha);
}