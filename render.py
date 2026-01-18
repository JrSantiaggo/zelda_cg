"""
Módulo de renderização: função principal de renderização da cena
"""
from OpenGL.GL import *
import glm
import math
import config
import player
import map
import props
import enemies
import archer

# Quad 2D para HUD (barra de vida); criado em init(geometry)
_hud_quad = None


def init(geometry_module):
    """Inicializa recursos do render (ex.: quad da HUD)."""
    global _hud_quad
    _hud_quad = geometry_module.createScreenQuad()


def render(shaderId, resolution):
    """
    Renderiza toda a cena (cenário e jogador).
    
    Args:
        shaderId: Identificador do shader program
        resolution: Lista [width, height] da resolução da janela
    """
    # Procedimentos iniciais de limpeza da tela e do depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, resolution[0], resolution[1])

    # Ativar shader (compartilhado por todos os objetos)
    glUseProgram(shaderId)
    glActiveTexture(GL_TEXTURE0)
    
    # Obter localizações dos uniforms (uma vez por frame)
    myTexture_loc = glGetUniformLocation(shaderId, 'myTexture')
    modelMatrix_loc = glGetUniformLocation(shaderId, 'modelMatrix')
    viewMatrix_loc = glGetUniformLocation(shaderId, 'viewMatrix')
    projectionMatrix_loc = glGetUniformLocation(shaderId, 'projectionMatrix')
    
    glUniform1i(myTexture_loc, 0)
    
    # Inicializar uniforms de cor (para props sem textura)
    use_color_loc = glGetUniformLocation(shaderId, 'useColor')
    object_color_loc = glGetUniformLocation(shaderId, 'objectColor')
    if use_color_loc != -1:
        glUniform1i(use_color_loc, 0)  # Por padrão, usar textura
    if object_color_loc != -1:
        glUniform3f(object_color_loc, 1.0, 1.0, 1.0)  # Cor padrão branca
    
    # Definir luz ambiente global (aplicada a todos os objetos 3D)
    ambient_light_loc = glGetUniformLocation(shaderId, 'ambientLight')
    if ambient_light_loc != -1:
        glUniform3f(ambient_light_loc, *config.AMBIENT_LIGHT)  # Luz ambiente do config
    
    # Definir luz direcional para iluminação difusa (modelo de Lambert)
    directional_light_dir_loc = glGetUniformLocation(shaderId, 'directionalLightDir')
    directional_light_color_loc = glGetUniformLocation(shaderId, 'directionalLightColor')
    if directional_light_dir_loc != -1:
        # Normalizar direção da luz (será normalizada no shader também, mas normalizamos aqui também)
        dir = config.DIRECTIONAL_LIGHT_DIRECTION
        length = math.sqrt(dir[0]**2 + dir[1]**2 + dir[2]**2)
        if length > 0:
            normalized_dir = (dir[0]/length, dir[1]/length, dir[2]/length)
        else:
            normalized_dir = dir
        glUniform3f(directional_light_dir_loc, *normalized_dir)
    if directional_light_color_loc != -1:
        glUniform3f(directional_light_color_loc, *config.DIRECTIONAL_LIGHT_COLOR)

    
    # Definir parâmetros de iluminação especular (modelo de Phong)
    specular_strength_loc = glGetUniformLocation(shaderId, 'specularStrength')
    shininess_loc = glGetUniformLocation(shaderId, 'shininess')
    specular_color_loc = glGetUniformLocation(shaderId, 'specularColor')
    if specular_strength_loc != -1:
        glUniform1f(specular_strength_loc, config.SPECULAR_STRENGTH)
    if shininess_loc != -1:
        glUniform1f(shininess_loc, config.SPECULAR_SHININESS)
    if specular_color_loc != -1:
        glUniform3f(specular_color_loc, *config.SPECULAR_COLOR)
    
    # Definir flag isSprite (padrão: false para objetos 3D)
    is_sprite_loc = glGetUniformLocation(shaderId, 'isSprite')
    if is_sprite_loc != -1:
        glUniform1i(is_sprite_loc, 0)  # Por padrão, não é sprite (objetos 3D iluminados)
    
    # Inicializar uniforms do sprite sheet (para objetos que não usam sprite sheet, usar textura completa)
    sprite_offset_loc = glGetUniformLocation(shaderId, 'spriteOffset')
    sprite_size_loc = glGetUniformLocation(shaderId, 'spriteSize')
    sprite_hit_flash_loc = glGetUniformLocation(shaderId, 'spriteHitFlash')
    if sprite_offset_loc != -1:
        glUniform2f(sprite_offset_loc, 0.0, 0.0)  # Offset padrão: (0,0) = usar textura completa
    if sprite_size_loc != -1:
        glUniform2f(sprite_size_loc, 1.0, 1.0)  # Tamanho padrão: (1,1) = usar textura completa
    if sprite_hit_flash_loc != -1:
        glUniform1f(sprite_hit_flash_loc, 0.0)
    
    # ===== CALCULAR POSIÇÃO DA CÂMERA SEGUINDO O JOGADOR =====
    # Obter posição atual do jogador
    playerPos = player.getPosition()
    
    # Offset fixo da câmera relativo ao jogador
    # Mantém a mesma distância e ângulo que config.CAMERA_POSITION tinha em relação à origem
    # Offset atual: (0.0, 12.0, 8.0) em relação à origem, agora será em relação ao jogador
    camera_offset = glm.vec3(*config.CAMERA_POSITION)  # Offset fixo (0.0, 12.0, 8.0)
    
    # Calcular posição da câmera: posição do jogador + offset fixo
    # Como o offset original era (0, 12, 8) em relação à origem, usamos ele diretamente
    # mas aplicamos em relação ao jogador no plano XZ (mantendo Y fixo da câmera)
    cameraPos = glm.vec3(
        playerPos.x + camera_offset.x,  # X do jogador + offset X (0.0)
        camera_offset.y,                 # Y fixo da câmera (12.0) - altura da câmera
        playerPos.z + camera_offset.z   # Z do jogador + offset Z (8.0)
    )
    
    # Calcular target da câmera: câmera sempre olha para o jogador
    # O target é a posição do jogador (mantendo altura Y do jogador para olhar corretamente)
    cameraTarget = glm.vec3(
        playerPos.x,                     # X do jogador
        playerPos.y,                     # Y do jogador (para olhar na altura correta)
        playerPos.z                      # Z do jogador
    )
    
    # Matriz de visão (View Matrix) - compartilhada por todos os objetos
    # Câmera segue o jogador mantendo offset fixo
    viewMatrix = glm.lookAt(
        cameraPos,                       # Posição da câmera (seguindo jogador com offset)
        cameraTarget,                    # Target da câmera (jogador)
        glm.vec3(*config.CAMERA_UP)
    )
    glUniformMatrix4fv(viewMatrix_loc, 1, GL_FALSE, glm.value_ptr(viewMatrix))
    
    # Passar posição da câmera para o shader (necessária para cálculo especular)
    camera_pos_loc = glGetUniformLocation(shaderId, 'cameraPos')
    if camera_pos_loc != -1:
        glUniform3f(camera_pos_loc, cameraPos.x, cameraPos.y, cameraPos.z)

    # Luz spot ao redor do jogador (mesmo raio da detecção do inimigo)
    player_pos_loc = glGetUniformLocation(shaderId, 'playerPos')
    spotlight_radius_loc = glGetUniformLocation(shaderId, 'spotlightRadius')
    spotlight_dark_loc = glGetUniformLocation(shaderId, 'spotlightDarkFactor')
    if player_pos_loc != -1:
        glUniform3f(player_pos_loc, playerPos.x, playerPos.y, playerPos.z)
    if spotlight_radius_loc != -1:
        glUniform1f(spotlight_radius_loc, config.ENEMY_DETECTION_HALF_EXTENT)
    if spotlight_dark_loc != -1:
        glUniform1f(spotlight_dark_loc, config.SPOTLIGHT_DARK_FACTOR)
    
    # Matriz de projeção (Projection Matrix) - compartilhada por todos os objetos
    aspectRatio = resolution[0] / resolution[1]
    projectionMatrix = glm.perspective(
        glm.radians(config.FOV),
        aspectRatio,
        config.NEAR_PLANE,
        config.FAR_PLANE
    )
    glUniformMatrix4fv(projectionMatrix_loc, 1, GL_FALSE, glm.value_ptr(projectionMatrix))

    # Renderizar elementos do cenário
    # cameraPos já foi calculado acima
    
    # Garantir que os uniforms do sprite sheet estão resetados antes de renderizar tiles
    if sprite_offset_loc != -1:
        glUniform2f(sprite_offset_loc, 0.0, 0.0)  # Resetar offset
    if sprite_size_loc != -1:
        glUniform2f(sprite_size_loc, 1.0, 1.0)  # Resetar tamanho
    
    # Garantir que isSprite está definido como false para objetos 3D do cenário
    if is_sprite_loc != -1:
        glUniform1i(is_sprite_loc, 0)  # Objetos 3D recebem iluminação ambiente
    
    map.renderPlatforms(modelMatrix_loc)
    map.renderRamps(modelMatrix_loc)
    props.render(modelMatrix_loc)  # Renderizar props (objetos 3D decorativos)
    enemies.render(modelMatrix_loc, cameraPos)  # Inimigos (sprites, alvos de teste)
    archer.render(modelMatrix_loc, cameraPos)   # Arqueiros (separado; futuramente flechas)
    # Renderizar jogador (que usa sprite sheet - não recebe iluminação ambiente)
    player.render(modelMatrix_loc, cameraPos)
    
    # Resetar uniforms do sprite sheet após renderizar jogador (para não afetar próximos objetos)
    if sprite_offset_loc != -1:
        glUniform2f(sprite_offset_loc, 0.0, 0.0)  # Resetar offset
    if sprite_size_loc != -1:
        glUniform2f(sprite_size_loc, 1.0, 1.0)  # Resetar tamanho
    if sprite_hit_flash_loc != -1:
        glUniform1f(sprite_hit_flash_loc, 0.0)

    # ===== HUD: barra de vida do jogador no topo da tela =====
    if _hud_quad is not None:
        glDisable(GL_DEPTH_TEST)
        hp, max_hp = player.get_hp()
        w, h = resolution[0], resolution[1]
        ortho = glm.ortho(0.0, float(w), float(h), 0.0, -1.0, 1.0)
        view_hud = glm.mat4(1.0)
        glUniformMatrix4fv(projectionMatrix_loc, 1, GL_FALSE, glm.value_ptr(ortho))
        glUniformMatrix4fv(viewMatrix_loc, 1, GL_FALSE, glm.value_ptr(view_hud))
        if use_color_loc != -1:
            glUniform1i(use_color_loc, 1)
        if is_sprite_loc != -1:
            glUniform1i(is_sprite_loc, 1)
        glBindVertexArray(_hud_quad[0])
        # Fundo da barra (cinza escuro)
        if object_color_loc != -1:
            glUniform3f(object_color_loc, 0.25, 0.25, 0.25)
        model_hud = glm.translate(glm.mat4(1.0), glm.vec3(20.0, 20.0, 0.0))
        model_hud = glm.scale(model_hud, glm.vec3(204.0, 24.0, 1.0))
        glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(model_hud))
        glDrawArrays(GL_TRIANGLES, 0, _hud_quad[1])
        # Preenchimento (verde) = vida atual / máxima
        fill_w = 200.0 * (hp / max_hp) if max_hp > 0 else 0.0
        if object_color_loc != -1:
            glUniform3f(object_color_loc, 0.2, 0.8, 0.2)
        model_fill = glm.translate(glm.mat4(1.0), glm.vec3(22.0, 22.0, 0.0))
        model_fill = glm.scale(model_fill, glm.vec3(fill_w, 20.0, 1.0))
        glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(model_fill))
        glDrawArrays(GL_TRIANGLES, 0, _hud_quad[1])
        glEnable(GL_DEPTH_TEST)

    # Desativar recursos
    glBindTexture(GL_TEXTURE_2D, 0)
    glBindVertexArray(0)
    glUseProgram(0)
