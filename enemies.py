"""
Módulo de inimigos: entidades básicas com posição, sprite e hitbox.
Servem como alvos de teste. Não se movem nem atacam.
Inclui detecção de acerto, dano, vida e feedback visual (flash + knockback).
"""
import os
import math
import glfw
from OpenGL.GL import *
import glm
import config
import resources
import map
import world_config
import player

# Direção do knockback por attack_direction do jogador: (dx, 0, dz) normalizado
_KNOCKBACK_DIR = {0: (0, 0, -1), 1: (1, 0, 0), 2: (-1, 0, 0), 3: (0, 0, 1)}

# Malha compartilhada (quad de sprite, igual ao jogador)
enemyMesh = 0
# Sequência de texturas idle: Minotaur_03_Idle_000.png a _011.png
enemyIdleTextures = []
# Sequência de texturas walking: Minotaur_03_Walking_000.png a _017.png (direita; esquerda = espelho)
enemyWalkingTextures = []
# Sequência de texturas ataque: Minotaur_03_Attacking_000.png a _011.png
enemyAttackTextures = []
# Sequência de texturas dying: Minotaur_03_Dying_000.png a _014.png
enemyDyingTextures = []
# Tempo de animação idle e último update (mesma lógica do player)
enemy_animation_time = 0.0
_last_update_time = 0.0
# Lista de inimigos: cada um é {"position": glm.vec3, "hp": int}
enemies = []
# IDs dos inimigos atingidos no ataque atual (máx. 1x por ataque); limpa quando o ataque termina.
# Usa id(enemy) porque dict não é hashable para set.
_hit_this_attack = set()


def _aabb_overlap_xz(a, b):
    """
    Verifica interseção de dois AABBs no plano XZ.
    a, b: (min_x, max_x, min_z, max_z)
    """
    (min_ax, max_ax, min_az, max_az) = a
    (min_bx, max_bx, min_bz, max_bz) = b
    if max_ax < min_bx or min_ax > max_bx:
        return False
    if max_az < min_bz or min_az > max_bz:
        return False
    return True


def _height_at(world_x, world_z):
    """Calcula a altura Y em (world_x, world_z) usando rampas e tiles."""
    ramp_height = map.getRampHeightAt(world_x, world_z)
    if ramp_height is not None:
        return world_config.GROUND_LEVEL + ramp_height
    tile_props = map.getTilePropertiesAt(world_x, world_z)
    if tile_props:
        h = tile_props.get("height", world_config.FLOOR_TILE_HEIGHT)
        return world_config.GROUND_LEVEL + h
    return world_config.GROUND_LEVEL


def _get_height_info(world_x, world_z):
    """Retorna (y, on_ramp). on_ramp=True se o ponto está em rampa (permite subir/descer)."""
    ramp_height = map.getRampHeightAt(world_x, world_z)
    if ramp_height is not None:
        return (world_config.GROUND_LEVEL + ramp_height, True)
    tile_props = map.getTilePropertiesAt(world_x, world_z)
    if tile_props:
        h = tile_props.get("height", world_config.FLOOR_TILE_HEIGHT)
        return (world_config.GROUND_LEVEL + h, False)
    return (world_config.GROUND_LEVEL, False)


def init(geometry_module):
    """
    Inicializa malha, sequência de texturas idle, dying e spawna inimigos.
    map.init() deve ter sido chamado antes (usa getRampHeightAt / getTilePropertiesAt).
    """
    global enemyMesh, enemyIdleTextures, enemyWalkingTextures, enemyAttackTextures, enemyDyingTextures, enemies
    here = os.path.dirname(os.path.abspath(__file__))
    enemyMesh = geometry_module.createSpriteMesh(
        config.ENEMY_OBJECT_SIZE_X, config.ENEMY_OBJECT_SIZE_Y
    )
    # Carregar Minotaur_03_Idle_000.png a Minotaur_03_Idle_011.png
    enemyIdleTextures = []
    for i in range(config.ENEMY_IDLE_FRAMES):
        path = os.path.join(here, f"{config.ENEMY_IDLE_PREFIX}_{i:03d}.png")
        enemyIdleTextures.append(resources.loadTexture(path))
    # Carregar Minotaur_03_Walking_000.png a Minotaur_03_Walking_017.png
    enemyWalkingTextures = []
    for i in range(config.ENEMY_WALKING_FRAMES):
        path = os.path.join(here, f"{config.ENEMY_WALKING_PREFIX}_{i:03d}.png")
        enemyWalkingTextures.append(resources.loadTexture(path))
    # Carregar Minotaur_03_Attacking_000.png a Minotaur_03_Attacking_011.png
    enemyAttackTextures = []
    for i in range(config.ENEMY_ATTACK_FRAMES):
        path = os.path.join(here, f"{config.ENEMY_ATTACK_PREFIX}_{i:03d}.png")
        enemyAttackTextures.append(resources.loadTexture(path))
    # Carregar Minotaur_03_Dying_000.png a Minotaur_03_Dying_014.png
    enemyDyingTextures = []
    for i in range(config.ENEMY_DYING_FRAMES):
        path = os.path.join(here, f"{config.ENEMY_DYING_PREFIX}_{i:03d}.png")
        enemyDyingTextures.append(resources.loadTexture(path))
    # Posições iniciais (x, z) no mundo; Y é calculada pelo terreno
    spawns = [
        (2.0, 2.0),
        (-5.0, 8.0),
        (10.0, -10.0),
        (-3.0, -15.0),
        (0.0, 5.0),
    ]
    enemies = []
    for x, z in spawns:
        y = _height_at(x, z)
        enemies.append({
            "position": glm.vec3(x, y, z),
            "hp": config.ENEMY_MAX_HP,
            "facing_right": True,  # direita=True; esquerda=espelho; cima/baixo usam a última direção
        })


def update(window):
    """
    Atualiza lógica dos inimigos.
    Área de detecção: quando o jogador entra no quadrado ao redor do inimigo, o inimigo segue o jogador.
    Animação idle: avança enemy_animation_time (mesma lógica do player).
    Durante o ataque: detecta acertos, aplica dano (ATTACK_DAMAGE) e remove mortos (hp <= 0).
    Cada inimigo é atingido no máximo uma vez por ataque.
    """
    global _hit_this_attack, _last_update_time, enemy_animation_time
    now = glfw.get_time()
    if _last_update_time == 0.0:
        _last_update_time = now
    delta = now - _last_update_time
    _last_update_time = now
    enemy_animation_time += delta * config.ENEMY_IDLE_ANIMATION_SPEED
    if not player.is_attacking:
        _hit_this_attack.clear()
    else:
        attack_box = player.get_attack_hitbox()
        if attack_box is not None:
            for e in enemies:
                if e.get("dying") or id(e) in _hit_this_attack:
                    continue
                if _aabb_overlap_xz(attack_box, get_hitbox(e)):
                    _hit_this_attack.add(id(e))
                    e["hp"] -= config.ATTACK_DAMAGE
                    # Feedback visual: knockback + flash
                    dx, _, dz = _KNOCKBACK_DIR.get(
                        player.attack_direction, (0, 0, 0)
                    )
                    d = config.HIT_KNOCKBACK_DISTANCE
                    e["knockback_initial"] = (dx * d, 0.0, dz * d)
                    e["hit_feedback_until"] = (
                        glfw.get_time() + config.HIT_FEEDBACK_DURATION
                    )
    # Atualizar knockback (decai até 0 no fim da duração) e limpar estado
    dur = config.HIT_FEEDBACK_DURATION
    for e in enemies:
        if "hit_feedback_until" not in e:
            continue
        if now >= e["hit_feedback_until"]:
            for k in ("hit_feedback_until", "knockback_initial", "knockback"):
                e.pop(k, None)
            continue
        t = (e["hit_feedback_until"] - now) / dur
        kbi = e["knockback_initial"]
        e["knockback"] = (kbi[0] * t, 0.0, kbi[2] * t)
    # Seguir o jogador quando ele está na área de detecção (quadrado ao redor do inimigo)
    player_pos = player.getPosition()
    H = config.ENEMY_DETECTION_HALF_EXTENT
    for e in enemies:
        e["is_moving"] = False
        e["attack_cooldown_remaining"] = max(0.0, e.get("attack_cooldown_remaining", 0.0) - delta)
        if e.get("dying"):
            continue
        if "hit_feedback_until" in e and now < e["hit_feedback_until"]:
            continue
        ex, ey, ez = e["position"].x, e["position"].y, e["position"].z
        px, pz = player_pos.x, player_pos.z
        dx = px - ex
        dz = pz - ez
        dist = math.sqrt(dx * dx + dz * dz)
        if dist <= H:  # dentro do círculo de raio H (mesma área da luz spot no jogador)
            if dist <= config.ENEMY_ATTACK_RANGE:
                # Ao alcance: para e ataca (cooldown 2 s); direção para o jogador
                if abs(dx) >= abs(dz):
                    e["facing_right"] = (dx > 0)
                if e.get("attack_cooldown_remaining", 0.0) <= 0.0:
                    player.take_damage(config.ENEMY_ATTACK_DAMAGE)
                    e["attack_cooldown_remaining"] = config.ENEMY_ATTACK_COOLDOWN
                    e["attacking"] = True
                    e["attacking_start"] = now
            elif dist > 0.001:
                dx /= dist
                dz /= dist
                if abs(dx) >= abs(dz):
                    e["facing_right"] = (dx > 0)
                speed = config.ENEMY_MOVEMENT_SPEED
                new_x = ex + dx * speed
                new_z = ez + dz * speed
                # Mesma lógica do player: não sobe em plataformas (só por rampas), não desce (só por rampas)
                current_y, current_on_ramp = _get_height_info(ex, ez)
                target_y, target_on_ramp = _get_height_info(new_x, new_z)
                height_diff = target_y - current_y
                max_height_jump = 0.15
                max_height_drop = 0.3
                if current_on_ramp or target_on_ramp:
                    allow = True
                elif height_diff > max_height_jump or height_diff < -max_height_drop:
                    allow = False
                else:
                    allow = True
                if allow:
                    e["position"] = glm.vec3(new_x, target_y, new_z)
                    e["is_moving"] = True
                    e["walking_time"] = e.get("walking_time", 0) + delta * config.ENEMY_WALKING_ANIMATION_SPEED
    # Encerrar estado "attacking" quando a animação de ataque termina
    attack_dur = config.ENEMY_ATTACK_FRAMES / config.ENEMY_ATTACK_ANIMATION_SPEED
    for e in enemies:
        if "attacking_start" in e and (now - e["attacking_start"]) >= attack_dur:
            e.pop("attacking", None)
            e.pop("attacking_start", None)
    # Inimigos com hp <= 0 entram em dying (animação de morte) antes de sumir
    for e in enemies:
        if e["hp"] <= 0 and "dying" not in e:
            e["dying"] = True
            e["dying_start"] = now
    dying_dur = config.ENEMY_DYING_FRAMES / config.ENEMY_DYING_ANIMATION_SPEED
    enemies[:] = [
        e for e in enemies
        if e["hp"] > 0 or (e.get("dying") and (now - e["dying_start"]) < dying_dur)
    ]


def render(modelMatrix_loc, cameraPos):
    """
    Renderiza todos os inimigos como sprites 2D com billboarding.
    Usa textura completa (0,0)-(1,1). Desenho antes do jogador para ordem de profundidade.
    """
    if not enemies:
        return
    glBindVertexArray(enemyMesh[0])
    shader_id = glGetInteger(GL_CURRENT_PROGRAM)
    sprite_offset_loc = glGetUniformLocation(shader_id, "spriteOffset")
    sprite_size_loc = glGetUniformLocation(shader_id, "spriteSize")
    is_sprite_loc = glGetUniformLocation(shader_id, "isSprite")
    if sprite_offset_loc != -1:
        glUniform2f(sprite_offset_loc, 0.0, 0.0)
    if sprite_size_loc != -1:
        glUniform2f(sprite_size_loc, 1.0, 1.0)
    if is_sprite_loc != -1:
        glUniform1i(is_sprite_loc, 1)
    sprite_hit_flash_loc = glGetUniformLocation(shader_id, "spriteHitFlash")
    now = glfw.get_time()
    dur = config.HIT_FEEDBACK_DURATION
    for e in enemies:
        if e.get("dying"):
            elapsed = now - e["dying_start"]
            frame = min(
                int(elapsed * config.ENEMY_DYING_ANIMATION_SPEED),
                config.ENEMY_DYING_FRAMES - 1,
            )
            glBindTexture(GL_TEXTURE_2D, enemyDyingTextures[frame])
        elif e.get("attacking"):
            elapsed = now - e.get("attacking_start", now)
            frame = min(
                int(elapsed * config.ENEMY_ATTACK_ANIMATION_SPEED),
                config.ENEMY_ATTACK_FRAMES - 1,
            )
            glBindTexture(GL_TEXTURE_2D, enemyAttackTextures[frame])
        elif e.get("is_moving"):
            frame = int(e.get("walking_time", 0)) % config.ENEMY_WALKING_FRAMES
            glBindTexture(GL_TEXTURE_2D, enemyWalkingTextures[frame])
        else:
            frame = int(enemy_animation_time) % config.ENEMY_IDLE_FRAMES
            glBindTexture(GL_TEXTURE_2D, enemyIdleTextures[frame])
        x, y, z = _display_position(e)
        modelMatrix = resources.calculateBillboardMatrix(
            glm.vec3(x, y, z), cameraPos
        )
        # Espelhar quando andando ou atacando para esquerda (cima/baixo usam última direção em facing_right)
        if (e.get("is_moving") or e.get("attacking")) and not e.get("facing_right", True):
            modelMatrix = glm.scale(modelMatrix, glm.vec3(-1.0, 1.0, 1.0))
        glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(modelMatrix))
        # Flash: 1 no início, 0 no fim da duração (não em dying)
        if "hit_feedback_until" in e and sprite_hit_flash_loc != -1:
            t = max(0.0, (e["hit_feedback_until"] - now) / dur)
            glUniform1f(sprite_hit_flash_loc, t)
        elif sprite_hit_flash_loc != -1:
            glUniform1f(sprite_hit_flash_loc, 0.0)
        glDrawArrays(GL_TRIANGLES, 0, enemyMesh[1])


def get_enemies():
    """Retorna a lista de inimigos (cada um com 'position', 'hp')."""
    return enemies


def _display_position(enemy):
    """Posição para render e hitbox: base + knockback (quando em feedback)."""
    p = enemy["position"]
    kb = enemy.get("knockback", (0.0, 0.0, 0.0))
    return (p.x + kb[0], p.y + kb[1], p.z + kb[2])


def get_hitbox(enemy):
    """
    Retorna a hitbox AABB no plano XZ do inimigo: (min_x, max_x, min_z, max_z).
    Usa posição de exibição (com knockback) para consistência visual.
    """
    x, _, z = _display_position(enemy)
    h = config.ENEMY_HITBOX_HALF_EXTENT
    return (x - h, x + h, z - h, z + h)


def get_enemies_hit_this_attack():
    """
    Retorna a lista de inimigos atingidos no ataque atual.
    Cada inimigo aparece no máximo uma vez por ataque.
    Lista é limpa quando o ataque termina (is_attacking = False).
    Útil para debug e, no futuro, aplicar dano.
    """
    return [e for e in enemies if id(e) in _hit_this_attack]


def was_hit_this_attack(enemy):
    """True se o inimigo foi atingido no ataque atual (máx. 1x por ataque)."""
    return id(enemy) in _hit_this_attack
