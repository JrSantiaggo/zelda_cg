"""
Módulo do arqueiro: inimigo à distância, separado dos inimigos corpo a corpo.
Detecção = luz spot. Atira flecha ao detectar; se o player chega à metade do spot, foge.
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

archerMesh = 0
archerIdleTexture = 0
archerAttackTexture = 0
archerRunTexture = 0
archerDyingTexture = 0
arrowMesh = 0
arrowTexture = 0
archers = []
arrows = []  # {position, velocity: (dx, dz), spawn_pos}
archer_animation_time = 0.0
archer_run_animation_time = 0.0
_last_update_time = 0.0

H = config.ENEMY_DETECTION_HALF_EXTENT  # raio do spot = detecção
FLEE_D = config.ARCHER_FLEE_DISTANCE    # metade: abaixo disso foge

# Direção do knockback por attack_direction do jogador (igual aos inimigos)
_KNOCKBACK_DIR = {0: (0, 0, -1), 1: (1, 0, 0), 2: (-1, 0, 0), 3: (0, 0, 1)}
_hit_this_attack_archer = set()  # IDs dos arqueiros atingidos no ataque atual (máx. 1x)


def _aabb_overlap_xz(a, b):
    """Verifica interseção de dois AABBs no plano XZ. a, b: (min_x, max_x, min_z, max_z)."""
    (min_ax, max_ax, min_az, max_az) = a
    (min_bx, max_bx, min_bz, max_bz) = b
    if max_ax < min_bx or min_ax > max_bx:
        return False
    if max_az < min_bz or min_az > max_bz:
        return False
    return True


def _display_position(archer):
    """Posição para render e hitbox: base + knockback (quando em feedback)."""
    p = archer["position"]
    kb = archer.get("knockback", (0.0, 0.0, 0.0))
    return (p.x + kb[0], p.y + kb[1], p.z + kb[2])


def get_archer_hitbox(archer):
    """Retorna a hitbox AABB no plano XZ do arqueiro: (min_x, max_x, min_z, max_z)."""
    x, _, z = _display_position(archer)
    h = config.ENEMY_HITBOX_HALF_EXTENT
    return (x - h, x + h, z - h, z + h)


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
    Inicializa malhas (arqueiro e flecha), texturas e spawna arqueiros.
    map.init() deve ter sido chamado antes.
    """
    global archerMesh, archerIdleTexture, archerAttackTexture, archerRunTexture, archerDyingTexture, arrowMesh, arrowTexture, archers, arrows
    here = os.path.dirname(os.path.abspath(__file__))
    archerMesh = geometry_module.createSpriteMesh(
        config.ARCHER_OBJECT_SIZE_X, config.ARCHER_OBJECT_SIZE_Y
    )
    arrowMesh = geometry_module.createSpriteMesh(
        config.ARCHER_ARROW_SIZE_X, config.ARCHER_ARROW_SIZE_Y
    )
    archerIdleTexture = resources.loadTexture(
        os.path.join(here, config.ARCHER_IDLE_TEXTURE)
    )
    archerAttackTexture = resources.loadTexture(
        os.path.join(here, config.ARCHER_ATTACK_TEXTURE)
    )
    archerRunTexture = resources.loadTexture(
        os.path.join(here, config.ARCHER_RUN_TEXTURE)
    )
    archerDyingTexture = resources.loadTexture(
        os.path.join(here, config.ARCHER_DYING_TEXTURE)
    )

    arrowTexture = resources.loadTexture(os.path.join(here, config.ARROW_TEXTURE))
    cfg = map.get_enemy_spawn_config()
    archers = []
    arrows = []
    for x, z in cfg["archer"]:
        y = _height_at(x, z)
        archers.append({
            "position": glm.vec3(x, y, z),
            "hp": config.ARCHER_MAX_HP,
            "shoot_cooldown_remaining": 0.0,
            "facing_right": True,
            "attack_remaining": 0.0,  # > 0: em animação de ataque (atirar)
        })


def update(window):
    """
    Detecção = luz spot (raio H). Se dist <= FLEE_D (metade), foge.
    Se dist <= H e não em fuga: atira (cooldown). Flechas: movem, atingem player (dano = ENEMY_ATTACK_DAMAGE) e somem.
    Arqueiros podem ser atacados pela espada (como inimigos): dano, knockback, flash; hp <= 0 remove.
    """
    global _last_update_time, archer_animation_time, archer_run_animation_time, arrows, _hit_this_attack_archer
    now = glfw.get_time()
    if _last_update_time == 0.0:
        _last_update_time = now
    delta = now - _last_update_time
    _last_update_time = now
    archer_animation_time += delta * config.ARCHER_IDLE_ANIMATION_SPEED
    archer_run_animation_time += delta * config.ARCHER_RUN_ANIMATION_SPEED

    pp = player.getPosition()
    px, pz = pp.x, pp.z

    # Detecção de acerto da espada (igual aos inimigos): 1x por ataque
    if not player.is_attacking:
        _hit_this_attack_archer.clear()
    else:
        attack_box = player.get_attack_hitbox()
        if attack_box is not None:
            for a in archers:
                if a.get("hp", 2) <= 0 or id(a) in _hit_this_attack_archer:
                    continue
                if _aabb_overlap_xz(attack_box, get_archer_hitbox(a)):
                    _hit_this_attack_archer.add(id(a))
                    a["hp"] -= config.ATTACK_DAMAGE
                    dx, _, dz = _KNOCKBACK_DIR.get(player.attack_direction, (0, 0, 0))
                    d = config.HIT_KNOCKBACK_DISTANCE
                    a["knockback_initial"] = (dx * d, 0.0, dz * d)
                    a["hit_feedback_until"] = now + config.HIT_FEEDBACK_DURATION

    # hp <= 0: entra em dying (animação de morte) antes de sumir
    for a in archers:
        if a.get("hp", 2) <= 0 and "dying" not in a:
            a["dying"] = True
            a["dying_start"] = now

    # Decaimento do knockback (igual aos inimigos)
    dur = config.HIT_FEEDBACK_DURATION
    for a in archers:
        if "hit_feedback_until" not in a:
            continue
        if now >= a["hit_feedback_until"]:
            for k in ("hit_feedback_until", "knockback_initial", "knockback"):
                a.pop(k, None)
            continue
        t = (a["hit_feedback_until"] - now) / dur
        kbi = a["knockback_initial"]
        a["knockback"] = (kbi[0] * t, 0.0, kbi[2] * t)

    for a in archers:
        a["shoot_cooldown_remaining"] = max(0.0, a.get("shoot_cooldown_remaining", 0.0) - delta)
        a["attack_remaining"] = max(0.0, a.get("attack_remaining", 0.0) - delta)
        ax, ay, az = a["position"].x, a["position"].y, a["position"].z
        dx = px - ax
        dz = pz - az
        dist = math.sqrt(dx * dx + dz * dz)

        # Só fuge/atira se vivo, não morrendo e não em feedback de acerto
        if (a.get("hp", 2) > 0 and not a.get("dying")
                and not ("hit_feedback_until" in a and now < a["hit_feedback_until"])):
            if dist <= FLEE_D:
                a["fleeing"] = True
                # Fuga: correr na direção oposta (velocidade menor)
                if dist > 0.001:
                    dx /= dist
                    dz /= dist
                    flee_dx = -dx
                    flee_dz = -dz
                    spd = config.ARCHER_FLEE_SPEED
                    nx = ax + flee_dx * spd
                    nz = az + flee_dz * spd
                    # Mesma lógica do player: não sobe em plataformas (só por rampas), não desce (só por rampas)
                    current_y, current_on_ramp = _get_height_info(ax, az)
                    target_y, target_on_ramp = _get_height_info(nx, nz)
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
                        a["position"] = glm.vec3(nx, target_y, nz)
                        a["facing_right"] = (flee_dx > 0)
            elif dist <= H:
                a["fleeing"] = False
                # Dentro do spot: atira (com cooldown); encara o jogador
                a["facing_right"] = (dx > 0)
                if a.get("shoot_cooldown_remaining", 0.0) <= 0.0:
                    if dist > 0.001:
                        dx /= dist
                        dz /= dist
                        a["shoot_cooldown_remaining"] = config.ARCHER_SHOOT_COOLDOWN
                        a["attack_remaining"] = config.ARCHER_ATTACK_DURATION
                        a["pending_arrow"] = {
                            "delay": config.ARCHER_ARROW_DELAY,
                            "velocity": (dx, dz),
                            "spawn_pos": (ax, ay, az),
                        }
            else:
                a["fleeing"] = False  # dist > H
        else:
            a["fleeing"] = False  # morto, morrendo ou em hit_feedback

        # Flecha agendada: após o delay, spawna (sincroniza com o frame da animação)
        pa = a.get("pending_arrow")
        if pa:
            pa["delay"] -= delta
            if pa["delay"] <= 0.0:
                vx, vz = pa["velocity"]
                sx, sy, sz = pa["spawn_pos"]
                arrows.append({
                    "position": glm.vec3(sx, sy, sz),
                    "velocity": (vx, vz),
                    "spawn_pos": (sx, sz),
                })
                del a["pending_arrow"]

    # Mover flechas, colisão com jogador, remover se acertou ou longe
    spd = config.ARCHER_ARROW_SPEED
    hit_r = config.ARCHER_ARROW_HIT_RADIUS
    to_remove = []
    for i, arr in enumerate(arrows):
        vx, vz = arr["velocity"]
        p = arr["position"]
        arr["position"] = glm.vec3(p.x + vx * spd, p.y, p.z + vz * spd)
        ax, az = arr["position"].x, arr["position"].z
        # Acertou o jogador? Só se dist < hit_r E a flecha não passou (player ainda "à frente")
        d = math.sqrt((px - ax) ** 2 + (pz - az) ** 2)
        to_player_dot = (px - ax) * vx + (pz - az) * vz  # < 0 = já passou
        if d < hit_r and to_player_dot >= -0.05:
            player.take_damage(config.ENEMY_ATTACK_DAMAGE)
            to_remove.append(i)
            continue
        # Longe do spawn?
        sx, sz = arr["spawn_pos"]
        if math.sqrt((ax - sx) ** 2 + (az - sz) ** 2) > config.ARCHER_ARROW_MAX_DIST:
            to_remove.append(i)
    for i in reversed(to_remove):
        arrows.pop(i)

    # Remove arqueiros: mantém se hp>0 ou se em dying e animação não terminou
    dying_dur = config.ARCHER_DYING_COLS / config.ARCHER_DYING_ANIMATION_SPEED
    archers[:] = [
        a for a in archers
        if a.get("hp", 2) > 0 or (a.get("dying") and (now - a["dying_start"]) < dying_dur)
    ]


def render(modelMatrix_loc, cameraPos):
    """
    Renderiza arqueiros (idle 7 col; espelha ao fugir/atirar) e depois as flechas.
    """
    shader_id = glGetInteger(GL_CURRENT_PROGRAM)
    sprite_offset_loc = glGetUniformLocation(shader_id, "spriteOffset")
    sprite_size_loc = glGetUniformLocation(shader_id, "spriteSize")
    is_sprite_loc = glGetUniformLocation(shader_id, "isSprite")
    sprite_hit_flash_loc = glGetUniformLocation(shader_id, "spriteHitFlash")
    if is_sprite_loc != -1:
        glUniform1i(is_sprite_loc, 1)
    if sprite_hit_flash_loc != -1:
        glUniform1f(sprite_hit_flash_loc, 0.0)

    # Arqueiros (idle ou animação de ataque); posição com knockback, flash ao acertar
    if archers:
        glBindVertexArray(archerMesh[0])
        now = glfw.get_time()
        dur = config.HIT_FEEDBACK_DURATION
        for a in archers:
            if a.get("dying"):
                # Animação de morte: 5 colunas, 1 linha
                cols = config.ARCHER_DYING_COLS
                elapsed = now - a["dying_start"]
                frame = min(cols - 1, int(elapsed * config.ARCHER_DYING_ANIMATION_SPEED))
                sw, sh = 1.0 / cols, 1.0
                tex = archerDyingTexture
            elif a.get("attack_remaining", 0.0) > 0:
                # Animação de ataque: 15 colunas, 1 linha; frame baseado no tempo restante
                cols = config.ARCHER_ATTACK_COLS
                D = config.ARCHER_ATTACK_DURATION
                atk = a["attack_remaining"]
                progress = 1.0 - (atk / D)
                frame = min(cols - 1, int(progress * cols))
                sw, sh = 1.0 / cols, 1.0
                tex = archerAttackTexture
            elif a.get("fleeing"):
                # Animação de corrida/fuga: 6 colunas, 1 linha
                cols = config.ARCHER_RUN_COLS
                frame = int(archer_run_animation_time) % cols
                sw, sh = 1.0 / cols, 1.0
                tex = archerRunTexture
            else:
                cols = config.ARCHER_IDLE_COLS
                sw, sh = 1.0 / cols, 1.0
                frame = int(archer_animation_time) % cols
                tex = archerIdleTexture
            if sprite_offset_loc != -1:
                glUniform2f(sprite_offset_loc, frame * sw, 0.0)
            if sprite_size_loc != -1:
                glUniform2f(sprite_size_loc, sw, sh)
            glBindTexture(GL_TEXTURE_2D, tex)
            x, y, z = _display_position(a)
            M = resources.calculateBillboardMatrix(glm.vec3(x, y, z), cameraPos)
            if not a.get("facing_right", True):
                M = glm.scale(M, glm.vec3(-1.0, 1.0, 1.0))
            # Flash ao acertar (não em dying)
            if not a.get("dying") and "hit_feedback_until" in a and sprite_hit_flash_loc != -1:
                t = max(0.0, (a["hit_feedback_until"] - now) / dur)
                glUniform1f(sprite_hit_flash_loc, t)
            elif sprite_hit_flash_loc != -1:
                glUniform1f(sprite_hit_flash_loc, 0.0)
            glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(M))
            glDrawArrays(GL_TRIANGLES, 0, archerMesh[1])

    # Flechas (textura inteira; sem flash)
    if arrows:
        glBindVertexArray(arrowMesh[0])
        if sprite_offset_loc != -1:
            glUniform2f(sprite_offset_loc, 0.0, 0.0)
        if sprite_size_loc != -1:
            glUniform2f(sprite_size_loc, 1.0, 1.0)
        if sprite_hit_flash_loc != -1:
            glUniform1f(sprite_hit_flash_loc, 0.0)
        glBindTexture(GL_TEXTURE_2D, arrowTexture)
        for arr in arrows:
            pos = arr["position"]
            vx, vz = arr["velocity"]
            # Rotação no eixo Y: ponta da flecha (+X local) aponta na direção (vx, vz)
            angle = math.atan2(-vz, vx)
            M = glm.mat4(1.0)
            M = glm.translate(M, pos)
            M = glm.rotate(M, angle, glm.vec3(0.0, 1.0, 0.0))
            glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(M))
            glDrawArrays(GL_TRIANGLES, 0, arrowMesh[1])


def get_archers():
    return archers
