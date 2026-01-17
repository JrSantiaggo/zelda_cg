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
position = glm.vec3(*config.INITIAL_POSITION)


def init(geometry_module):
    """
    Inicializa recursos do jogador (malha e textura).
    
    Args:
        geometry_module: Módulo geometry para criar malhas
    """
    global playerMesh, playerTexture
    import os
    
    here = os.path.dirname(os.path.abspath(__file__))
    playerMesh = geometry_module.createSpriteMesh()
    playerTexture = resources.loadTexture(os.path.join(here, config.TEXTURE_FILE))


def update(window):
    """
    Atualiza a lógica do jogador (movimentação e input).
    Inclui verificação de colisão com tiles sólidos do mapa.
    """
    global position
    
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
        
        # Calcular posição alvo
        target_x = position.x + moveX * config.MOVEMENT_SPEED
        target_z = position.z + moveZ * config.MOVEMENT_SPEED
        
        # Verificar colisão com tiles sólidos
        # Usar raio do jogador baseado no tamanho do sprite (metade da largura)
        player_radius = config.OBJECT_SIZE_X
        
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
        if True:  # Sempre executar o bloco de movimento
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


def render(modelMatrix_loc, cameraPos):
    """
    Renderiza o jogador na cena.
    """
    glBindVertexArray(playerMesh[0])
    glBindTexture(GL_TEXTURE_2D, playerTexture)
    
    # Matriz de modelo com billboarding (sprite olha para câmera)
    modelMatrix = resources.calculateBillboardMatrix(position, cameraPos)
    glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(modelMatrix))
    glDrawArrays(GL_TRIANGLES, 0, playerMesh[1])


def getPosition():
    """
    Retorna a posição atual do jogador.
    """
    return position
