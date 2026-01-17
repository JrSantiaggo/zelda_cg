"""
Módulo do jogador: lógica e renderização do jogador
"""
import glfw
from OpenGL.GL import *
import glm
import math
import config
import resources
import map
import world_config

# Variáveis globais do jogador
playerMesh = 0
playerTexture = 0
playerIdleTexture = 0
playerAttackTexture = 0  # Ataque parado
playerRunAttackTexture = 0  # Ataque correndo
position = glm.vec3(*config.INITIAL_POSITION)

# Variáveis de animação
animation_time = 0.0
current_direction = 3  # Direção inicial: frente (linha 3)
last_direction = 3  # Direção anterior (para detectar mudanças de direção)
is_moving = False
is_attacking = False  # Estado de ataque
attack_animation_time = 0.0  # Tempo da animação de ataque
was_pressing_space = False  # Estado anterior da tecla espaço (para detectar apenas quando pressionada)
last_update_time = 0.0
was_moving = False  # Estado anterior de movimento (para detectar transições)


def init(geometry_module):
    """
    Inicializa recursos do jogador (malha e texturas).
    
    Args:
        geometry_module: Módulo geometry para criar malhas
    """
    global playerMesh, playerTexture, playerIdleTexture, playerAttackTexture, playerRunAttackTexture
    import os
    
    here = os.path.dirname(os.path.abspath(__file__))
    playerMesh = geometry_module.createSpriteMesh()
    playerTexture = resources.loadTexture(os.path.join(here, config.TEXTURE_FILE))
    playerIdleTexture = resources.loadTexture(os.path.join(here, config.IDLE_TEXTURE_FILE))
    playerAttackTexture = resources.loadTexture(os.path.join(here, "texture/player2/Swordsman_lvl3_attack_with_shadow.png"))
    playerRunAttackTexture = resources.loadTexture(os.path.join(here, "texture/player2/Swordsman_lvl3_Run_Attack_with_shadow.png"))


def update(window):
    """
    Atualiza a lógica do jogador (movimentação e input).
    Inclui verificação de colisão com tiles sólidos do mapa.
    """
    global position, animation_time, current_direction, is_moving, is_attacking, attack_animation_time
    
    moveX = 0.0
    moveZ = 0.0
    
    # Movimento horizontal (eixo X) - esquerda/direita na tela
    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS or glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        moveX = -1.0
    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS or glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        moveX = 1.0
    
    # Movimento em profundidade (eixo Z) - cima/baixo na tela (visão isométrica)
    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS or glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        moveZ = -1.0  # Z negativo = "para frente" (afasta da câmera)
    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS or glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        moveZ = 1.0   # Z positivo = "para trás" (aproxima da câmera)
    
    # Normaliza o vetor de movimento para que diagonais não sejam mais rápidas
    if moveX != 0.0 or moveZ != 0.0:
        length = math.sqrt(moveX * moveX + moveZ * moveZ)
        moveX /= length
        moveZ /= length
        
        # Determinar direção do movimento para animação
        # Linha 0 → jogador andando para trás (Z positivo) - DOWN/baixo
        # Linha 1 → jogador andando para esquerda (X negativo) - LEFT/esquerda
        # Linha 2 → jogador andando para direita (X positivo) - RIGHT/direita
        # Linha 3 → jogador andando para frente (Z negativo) - UP/cima
        
        # Priorizar movimento vertical (Z) sobre horizontal (X)
        if abs(moveZ) > abs(moveX):
            # INVERTIDO: sprite sheet tem cima na linha 0 e baixo na linha 3
            if moveZ > 0:
                current_direction = 3  # Trás (DOWN/baixo) - era 0, agora 3
            else:
                current_direction = 0  # Frente (UP/cima) - era 3, agora 0
        else:
            # INVERTIDO: sprite sheet tem direita na linha 1 e esquerda na linha 2
            if moveX < 0:
                current_direction = 2  # Esquerda (LEFT) - era 1, agora 2
            else:
                current_direction = 1  # Direita (RIGHT) - era 2, agora 1
        
        is_moving = True
        
        # Calcular posição alvo
        target_x = position.x + moveX * config.MOVEMENT_SPEED
        target_z = position.z + moveZ * config.MOVEMENT_SPEED
        
        # Verificar colisão com tiles sólidos
        # Usar raio do jogador baseado no tamanho do sprite (metade da largura)
        # OBJECT_SIZE_X é a metade da largura (0.5 tile), mas está definido como 1.0 incorretamente
        # Para colisão, usar 0.5 como raio (metade de 1.0 tile de largura)
        player_radius = 0.5
        
        # Calcular altura atual do jogador
        current_ramp_height = map.getRampHeightAt(position.x, position.z)
        if current_ramp_height is not None:
            current_y = world_config.GROUND_LEVEL + current_ramp_height
            current_on_ramp = True
        else:
            current_tile_props = map.getTilePropertiesAt(position.x, position.z)
            if current_tile_props:
                current_y = world_config.GROUND_LEVEL + current_tile_props.get('height', world_config.FLOOR_TILE_HEIGHT)
            else:
                current_y = world_config.GROUND_LEVEL
            current_on_ramp = False
        
        # Calcular altura esperada na posição alvo (para verificar colisão considerando altura)
        # Primeiro verificar se há rampa na posição alvo
        target_ramp_height = map.getRampHeightAt(target_x, target_z)
        if target_ramp_height is not None:
            target_y = world_config.GROUND_LEVEL + target_ramp_height
            target_on_ramp = True
        else:
            # Verificar altura do tile na posição alvo
            target_tile_props = map.getTilePropertiesAt(target_x, target_z)
            if target_tile_props:
                target_tile_height = target_tile_props.get('height', world_config.FLOOR_TILE_HEIGHT)
                target_y = world_config.GROUND_LEVEL + target_tile_height
            else:
                target_y = world_config.GROUND_LEVEL
            target_on_ramp = False
        
        # Verificar se a diferença de altura é muito grande (bloquear movimento se for)
        # MAS: permitir movimento se o jogador está em uma rampa ou está indo para uma rampa
        height_diff = target_y - current_y  # Diferença de altura (positiva = subindo, negativa = descendo)
        max_height_jump = 0.15  # Máxima diferença de altura permitida sem rampa (permite pequenos desníveis)
        max_height_drop = 0.3   # Máxima diferença de altura permitida para descida (mais permissivo)
        
        # Se o jogador está em uma rampa OU está indo para uma rampa, permitir movimento (rampas permitem subidas grandes)
        if current_on_ramp or target_on_ramp:
            # Permitir movimento - está em uma rampa ou indo para uma rampa
            pass  # Continuar com verificação de colisão normal
        # Se estiver tentando subir muito alto sem rampa, bloquear movimento
        elif height_diff > max_height_jump:
            # Não permitir movimento - diferença de altura muito grande (tentando subir sem rampa)
            pass  # Não mover
            return  # Sair da função sem mover
        # Se estiver descendo muito, também bloquear (para evitar quedas grandes)
        elif height_diff < -max_height_drop:
            # Não permitir movimento - queda muito grande
            pass  # Não mover
            return  # Sair da função sem mover
        
        # Se chegou aqui, pode tentar mover (está em rampa ou diferença de altura é aceitável)
        # Verificar colisão na posição alvo (passando altura do jogador)
        if not map.checkTileCollision(target_x, target_z, player_radius, target_y):
            # Sem colisão, atualizar posição
            position.x = target_x
            position.z = target_z
        else:
            # Tentar movimento apenas em X ou apenas em Z (slide ao longo das paredes)
                # Calcular altura para movimento apenas em X
                x_ramp_height = map.getRampHeightAt(target_x, position.z)
                if x_ramp_height is not None:
                    x_y = world_config.GROUND_LEVEL + x_ramp_height
                    x_on_ramp = True
                else:
                    x_tile_props = map.getTilePropertiesAt(target_x, position.z)
                    if x_tile_props:
                        x_y = world_config.GROUND_LEVEL + x_tile_props.get('height', world_config.FLOOR_TILE_HEIGHT)
                    else:
                        x_y = world_config.GROUND_LEVEL
                    x_on_ramp = False
                
                # Verificar diferença de altura para movimento em X
                x_height_diff = x_y - current_y
                # Permitir movimento em X se estiver em rampa ou diferença for aceitável
                if x_on_ramp or current_on_ramp or (x_height_diff <= max_height_jump and x_height_diff >= -max_height_drop):
                    # Tentar movimento apenas em X
                    if not map.checkTileCollision(target_x, position.z, player_radius, x_y):
                        position.x = target_x
                    else:
                        # Calcular altura para movimento apenas em Z
                        z_ramp_height = map.getRampHeightAt(position.x, target_z)
                        if z_ramp_height is not None:
                            z_y = world_config.GROUND_LEVEL + z_ramp_height
                            z_on_ramp = True
                        else:
                            z_tile_props = map.getTilePropertiesAt(position.x, target_z)
                            if z_tile_props:
                                z_y = world_config.GROUND_LEVEL + z_tile_props.get('height', world_config.FLOOR_TILE_HEIGHT)
                            else:
                                z_y = world_config.GROUND_LEVEL
                            z_on_ramp = False
                        
                        # Verificar diferença de altura para movimento em Z
                        z_height_diff = z_y - current_y
                        # Permitir movimento em Z se estiver em rampa ou diferença for aceitável
                        if z_on_ramp or current_on_ramp or (z_height_diff <= max_height_jump and z_height_diff >= -max_height_drop):
                            # Tentar movimento apenas em Z
                            if not map.checkTileCollision(position.x, target_z, player_radius, z_y):
                                position.z = target_z
                        # Se ambos causarem colisão, não mover (jogador bloqueado)
    else:
        # Jogador não está se movendo
        is_moving = False
    
    # ===== AJUSTAR ALTURA Y BASEADO EM RAMPAS E PLATAFORMAS =====
    # Verificar se o jogador está sobre uma rampa
    ramp_height = map.getRampHeightAt(position.x, position.z)
    
    if ramp_height is not None:
        # Jogador está sobre uma rampa - usar altura calculada gradualmente
        # Se estiver no topo da rampa (próximo de 1.0), garantir que está na altura correta
        if ramp_height >= 0.99:
            # No topo da rampa - usar altura da plataforma para garantir continuidade
            ramp_height = 1.0  # Garantir exatamente 1.0 no topo
        final_y = world_config.GROUND_LEVEL + ramp_height
        position.y = final_y
    else:
        # Jogador não está sobre uma rampa - verificar se está sobre uma plataforma
        tile_props = map.getTilePropertiesAt(position.x, position.z)
        if tile_props:
            tile_height = tile_props.get('height', world_config.FLOOR_TILE_HEIGHT)
            # Altura do topo do tile = GROUND_LEVEL + altura do tile
            final_y = world_config.GROUND_LEVEL + tile_height
            position.y = final_y
        else:
            # Tile não encontrado ou inválido - usar altura padrão do chão
            position.y = world_config.GROUND_LEVEL
    
    # ===== DETECTAR ATAQUE (TECLA ESPAÇO) =====
    # Detectar se espaço foi pressionado (apenas quando a tecla é pressionada, não mantida)
    global was_pressing_space
    space_pressed = glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS
    if space_pressed and not was_pressing_space and not is_attacking:
        # Iniciar animação de ataque apenas quando a tecla é pressionada pela primeira vez
        is_attacking = True
        attack_animation_time = 0.0
    was_pressing_space = space_pressed
    
    # ===== ATUALIZAR ANIMAÇÃO =====
    # Atualizar tempo de animação baseado no estado de movimento
    global last_update_time, was_moving, last_direction
    current_time = glfw.get_time()
    
    if last_update_time == 0.0:
        last_update_time = current_time
    
    delta_time = current_time - last_update_time
    last_update_time = current_time
    
    # Se está atacando, atualizar animação de ataque
    if is_attacking:
        # Animação de ataque é mais rápida que movimento normal (2x mais rápida)
        attack_animation_speed = config.ANIMATION_SPEED * 2.0
        attack_animation_time += delta_time * attack_animation_speed
        # Ataque tem 8 frames (0 a 7)
        if attack_animation_time >= config.SPRITE_SHEET_COLS:
            # Animação de ataque terminou
            is_attacking = False
            attack_animation_time = 0.0
            # Resetar animation_time para continuar animação normal
            animation_time = 0.0
    else:
        # Detectar transição de movimento para idle ou vice-versa
        if was_moving != is_moving:
            # Transição detectada - resetar animation_time para 0
            animation_time = 0.0
        
        # Detectar mudança de direção e resetar animation_time se necessário
        if last_direction != current_direction:
            animation_time = 0.0
        
        was_moving = is_moving
        last_direction = current_direction
        
        if is_moving:
            # Animação de movimento: 8 frames por direção
            animation_time += delta_time * config.ANIMATION_SPEED
            # Loop da animação (0 a 8 frames)
            animation_time = animation_time % config.SPRITE_SHEET_COLS
        else:
            # Animação idle: continuar animando quando parado
            # Velocidade de animação idle (um pouco mais lenta que movimento)
            idle_animation_speed = config.ANIMATION_SPEED * 0.6  # 60% da velocidade de movimento
            animation_time += delta_time * idle_animation_speed
            # Número de colunas varia por direção na textura idle:
            # Linha 0 (cima/W): 4 colunas
            # Linhas 1-3 (direita, esquerda, baixo): 12 colunas cada
            if current_direction == 0:
                idle_cols = 4   # Linha 0 (cima/W): 4 colunas
            else:
                idle_cols = 12  # Linhas 1-3 (direita, esquerda, baixo): 12 colunas
            # Loop da animação idle (garantir que está no range 0 a idle_cols)
            animation_time = animation_time % idle_cols


def render(modelMatrix_loc, cameraPos):
    """
    Renderiza o jogador na cena.
    """
    global animation_time, current_direction, is_moving, is_attacking, attack_animation_time
    
    glBindVertexArray(playerMesh[0])
    
    # Selecionar textura apropriada baseado no estado (ataque > movimento > idle)
    if is_attacking:
        # Usar textura de ataque
        if is_moving:
            # Ataque enquanto correndo
            glBindTexture(GL_TEXTURE_2D, playerRunAttackTexture)
        else:
            # Ataque enquanto parado
            glBindTexture(GL_TEXTURE_2D, playerAttackTexture)
        sprite_cols = config.SPRITE_SHEET_COLS  # 8 colunas para ataque
        animation_cols = sprite_cols  # Mesmo valor para ataque
        # Usar attack_animation_time para animação de ataque
        current_frame = int(attack_animation_time) % animation_cols
    elif is_moving:
        # Usar textura de movimento
        glBindTexture(GL_TEXTURE_2D, playerTexture)
        sprite_cols = config.SPRITE_SHEET_COLS  # 8 colunas para movimento
        animation_cols = sprite_cols  # Mesmo valor para movimento
        current_frame = int(animation_time) % animation_cols
    else:
        # Usar textura idle
        glBindTexture(GL_TEXTURE_2D, playerIdleTexture)
        # IMPORTANTE: A textura física tem 12 colunas em TODAS as linhas
        # Mas a linha 0 (cima/W) só usa as primeiras 4 colunas para animação
        # Linhas 1-3 (direita, esquerda, baixo) usam todas as 12 colunas
        sprite_cols = 12  # Número total de colunas na textura física (sempre 12)
        if current_direction == 0:
            animation_cols = 4   # Linha 0 (cima/W): 4 frames de animação
        else:
            animation_cols = 12  # Linhas 1-3: 12 frames de animação
        
        # Garantir que animation_time está normalizado para esta direção específica
        # Importante: normalizar ANTES de calcular o frame para evitar valores incorretos
        animation_time = animation_time % animation_cols
        current_frame = int(animation_time) % animation_cols
    
    # Calcular offset do sprite sheet
    # spriteOffset = (coluna * spriteWidth, linha * spriteHeight)
    sprite_width = 1.0 / sprite_cols
    sprite_height = 1.0 / config.SPRITE_SHEET_ROWS
    
    offset_x = current_frame * sprite_width
    offset_y = current_direction * sprite_height
    
    # Obter shader ID para definir uniforms
    shader_id = glGetInteger(GL_CURRENT_PROGRAM)
    sprite_offset_loc = glGetUniformLocation(shader_id, 'spriteOffset')
    sprite_size_loc = glGetUniformLocation(shader_id, 'spriteSize')
    is_sprite_loc = glGetUniformLocation(shader_id, 'isSprite')
    
    # Definir uniforms do sprite sheet
    if sprite_offset_loc != -1:
        glUniform2f(sprite_offset_loc, offset_x, offset_y)
    if sprite_size_loc != -1:
        glUniform2f(sprite_size_loc, sprite_width, sprite_height)
    
    # Marcar como sprite 2D (não recebe iluminação ambiente)
    if is_sprite_loc != -1:
        glUniform1i(is_sprite_loc, 1)  # true = sprite 2D (sem iluminação)
    
    # Matriz de modelo com billboarding cilíndrico
    # O sprite rotaciona apenas no eixo Y para sempre olhar para a câmera
    # no plano horizontal (XZ), mantendo-se sempre "em pé"
    # Não rotaciona nos eixos X ou Z (billboarding cilíndrico vs esférico)
    modelMatrix = resources.calculateBillboardMatrix(position, cameraPos)
    glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(modelMatrix))
    glDrawArrays(GL_TRIANGLES, 0, playerMesh[1])


def getPosition():
    """
    Retorna a posição atual do jogador.
    """
    return position
