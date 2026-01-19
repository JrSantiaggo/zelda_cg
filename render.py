"""
Módulo de renderização: função principal de renderização da cena
Inclui shadow mapping (pass de profundidade + amostragem no fragment).
"""
import os
from OpenGL.GL import *
import glm
import math
import config
import player
import map
import props
import enemies
import archer
import resources

# Quad 2D para HUD (barra de vida); criado em init(geometry)
_hud_quad = None
# Shadow mapping: FBO, textura de profundidade e shader do depth pass
_shadow_fbo = None
_shadow_depth_tex = None
_depth_shader_id = None
# Lua (easter egg Zelda / Majora's Mask) — canto sup. direito do mapa (meta), fora dos tiles
_moon_texture = None
_moon_mesh = None
# Posição no mundo: à direita da meta (mapa 80x40, offset -20,-20; tiles até ~x=59, z=-20)
# Colocada no "céu" (y alto), fora da área de tiles
MOON_WORLD_POS = (56.0, 00.0, -20.0)


def init(geometry_module, depth_shader_id):
    """Inicializa recursos do render (HUD, FBO e textura de shadow map)."""
    global _hud_quad, _shadow_fbo, _shadow_depth_tex, _depth_shader_id, _moon_texture, _moon_mesh
    _hud_quad = geometry_module.createScreenQuad()
    _depth_shader_id = depth_shader_id

    # Carregar textura e malha da lua (easter egg estilo Zelda / Majora's Mask)
    here = os.path.dirname(os.path.abspath(__file__))
    moon_path = os.path.join(here, "moon.png")
    if os.path.exists(moon_path):
        try:
            _moon_texture = resources.loadTexture(moon_path)
            _moon_mesh = geometry_module.createSpriteMesh(2.0, 2.0)  # 4x4 unidades
        except Exception:
            _moon_texture = None
            _moon_mesh = None
    else:
        _moon_texture = None
        _moon_mesh = None

    # FBO e textura de profundidade para shadow mapping
    sz = config.SHADOW_MAP_SIZE
    _shadow_fbo = glGenFramebuffers(1)
    _shadow_depth_tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, _shadow_depth_tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, sz, sz, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
    border = [1.0, 1.0, 1.0, 1.0]
    glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, border)
    glBindFramebuffer(GL_FRAMEBUFFER, _shadow_fbo)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, _shadow_depth_tex, 0)
    glDrawBuffer(GL_NONE)
    glReadBuffer(GL_NONE)
    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        raise RuntimeError("Shadow FBO incompleto")
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glBindTexture(GL_TEXTURE_2D, 0)


def render(shaderId, resolution):
    """
    Renderiza toda a cena: depth pass (shadow map) e main pass com sombras.
    """
    # ---- Dados comuns: jogador, câmera e matriz da luz ----
    playerPos = player.getPosition()
    camera_offset = glm.vec3(*config.CAMERA_POSITION)
    cameraPos = glm.vec3(
        playerPos.x + camera_offset.x, camera_offset.y, playerPos.z + camera_offset.z
    )
    cameraTarget = glm.vec3(playerPos.x, playerPos.y, playerPos.z)

    if config.SHADOW_MAPPING_ENABLED:
        dd = config.DIRECTIONAL_LIGHT_DIRECTION
        ln = math.sqrt(dd[0] ** 2 + dd[1] ** 2 + dd[2] ** 2) or 1.0
        light_dir = (dd[0] / ln, dd[1] / ln, dd[2] / ln)
        center = glm.vec3(0.0, 5.0, 0.0)
        light_eye = center + glm.vec3(light_dir[0], light_dir[1], light_dir[2]) * 50.0
        light_view = glm.lookAt(light_eye, center, glm.vec3(0, 1, 0))
        osz = config.SHADOW_ORTHO_SIZE
        light_proj = glm.ortho(-osz, osz, -osz, osz, config.SHADOW_NEAR, config.SHADOW_FAR)
        light_space = light_proj * light_view
        # Depth pass: renderizar cena do ponto de vista da luz
        glViewport(0, 0, config.SHADOW_MAP_SIZE, config.SHADOW_MAP_SIZE)
        glBindFramebuffer(GL_FRAMEBUFFER, _shadow_fbo)
        glClear(GL_DEPTH_BUFFER_BIT)
        glUseProgram(_depth_shader_id)
        d_model = glGetUniformLocation(_depth_shader_id, "modelMatrix")
        d_light = glGetUniformLocation(_depth_shader_id, "lightSpaceMatrix")
        glUniformMatrix4fv(d_light, 1, GL_FALSE, glm.value_ptr(light_space))
        map.renderPlatforms(d_model)
        map.renderRamps(d_model)
        props.render(d_model)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, resolution[0], resolution[1])
    else:
        light_space = glm.mat4(1.0)

    # ---- Main pass ----
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glUseProgram(shaderId)
    glActiveTexture(GL_TEXTURE0)

    myTexture_loc = glGetUniformLocation(shaderId, "myTexture")
    modelMatrix_loc = glGetUniformLocation(shaderId, "modelMatrix")
    viewMatrix_loc = glGetUniformLocation(shaderId, "viewMatrix")
    projectionMatrix_loc = glGetUniformLocation(shaderId, "projectionMatrix")
    light_space_loc = glGetUniformLocation(shaderId, "lightSpaceMatrix")
    shadow_map_loc = glGetUniformLocation(shaderId, "shadowMap")
    use_shadow_loc = glGetUniformLocation(shaderId, "useShadowMapping")
    shadow_bias_loc = glGetUniformLocation(shaderId, "shadowBias")
    shadow_strength_loc = glGetUniformLocation(shaderId, "shadowStrength")

    glUniform1i(myTexture_loc, 0)
    if light_space_loc != -1:
        glUniformMatrix4fv(light_space_loc, 1, GL_FALSE, glm.value_ptr(light_space))
    if use_shadow_loc != -1:
        glUniform1i(use_shadow_loc, 1 if config.SHADOW_MAPPING_ENABLED else 0)
    if shadow_map_loc != -1 and config.SHADOW_MAPPING_ENABLED:
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, _shadow_depth_tex)
        glUniform1i(shadow_map_loc, 1)
        glActiveTexture(GL_TEXTURE0)
    if shadow_bias_loc != -1:
        glUniform1f(shadow_bias_loc, config.SHADOW_BIAS)
    if shadow_strength_loc != -1:
        glUniform1f(shadow_strength_loc, config.SHADOW_STRENGTH)
    
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
    
    # Matriz de visão (View Matrix) - compartilhada por todos os objetos (cameraPos/cameraTarget já calculados no início)
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
    # Lua (easter egg Zelda) — canto sup. direito do mapa (meta), fora dos tiles, no céu
    if _moon_texture is not None and _moon_mesh is not None:
        if use_color_loc != -1:
            glUniform1i(use_color_loc, 0)
        if is_sprite_loc != -1:
            glUniform1i(is_sprite_loc, 1)
        glBindTexture(GL_TEXTURE_2D, _moon_texture)
        moon_pos = glm.vec3(*MOON_WORLD_POS)
        model_moon = resources.calculateBillboardMatrix(moon_pos, cameraPos)
        glBindVertexArray(_moon_mesh[0])
        glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(model_moon))
        glDrawArrays(GL_TRIANGLES, 0, _moon_mesh[1])
        if is_sprite_loc != -1:
            glUniform1i(is_sprite_loc, 0)
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
        # Barra de estamina (boost): amarela, ao lado da vida; drena no boost, recarrega no cooldown
        stamina_fill = player.get_stamina_fill()
        if object_color_loc != -1:
            glUniform3f(object_color_loc, 0.28, 0.26, 0.12)
        model_stam_bg = glm.translate(glm.mat4(1.0), glm.vec3(244.0, 20.0, 0.0))
        model_stam_bg = glm.scale(model_stam_bg, glm.vec3(204.0, 24.0, 1.0))
        glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(model_stam_bg))
        glDrawArrays(GL_TRIANGLES, 0, _hud_quad[1])
        stam_fill_w = 200.0 * max(0.0, min(1.0, stamina_fill))
        if object_color_loc != -1:
            glUniform3f(object_color_loc, 0.95, 0.88, 0.2)
        model_stam_fill = glm.translate(glm.mat4(1.0), glm.vec3(246.0, 22.0, 0.0))
        model_stam_fill = glm.scale(model_stam_fill, glm.vec3(stam_fill_w, 20.0, 1.0))
        glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(model_stam_fill))
        glDrawArrays(GL_TRIANGLES, 0, _hud_quad[1])
        glEnable(GL_DEPTH_TEST)

    # Desativar recursos
    glBindTexture(GL_TEXTURE_2D, 0)
    glBindVertexArray(0)
    glUseProgram(0)
