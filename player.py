import glfw
from OpenGL.GL import *
import glm
import math
import config
import resources
import map
import world_config
import props

playerMesh = 0
playerTexture = 0
playerIdleTexture = 0
playerAttackTexture = 0
playerRunAttackTexture = 0
position = glm.vec3(*config.INITIAL_POSITION)
hp = 0

animation_time = 0.0
current_direction = 3
last_direction = 3
is_moving = False
is_attacking = False
attack_animation_time = 0.0
attack_direction = 3
attack_cooldown_remaining = 0.0

was_pressing_space = False
boost_remaining = 0.0
boost_cooldown_remaining = 0.0
was_moving = False

hit_feedback_until = 0.0
knockback_initial = (0.0, 0.0, 0.0)
knockback = (0.0, 0.0, 0.0)


def init(geometry_module):
    global playerMesh, playerTexture, playerIdleTexture, playerAttackTexture, playerRunAttackTexture, hp
    global boost_remaining, boost_cooldown_remaining, playerIdleTexture, playerAttackTexture, playerRunAttackTexture, hp
    global boost_remaining, boost_cooldown_remaining
    import os

    hp = config.PLAYER_MAX_HP
    boost_remaining = config.BOOST_DURATION
    boost_cooldown_remaining = 0.0
    here = os.path.dirname(os.path.abspath(__file__))
    playerMesh = geometry_module.createSpriteMesh()
    playerTexture = resources.loadTexture(os.path.join(here, config.TEXTURE_FILE))
    playerIdleTexture = resources.loadTexture(os.path.join(here, config.IDLE_TEXTURE_FILE))
    playerAttackTexture = resources.loadTexture(os.path.join(here, "texture/player2/Swordsman_lvl3_attack_with_shadow.png"))
    playerRunAttackTexture = resources.loadTexture(os.path.join(here, "texture/player2/Swordsman_lvl3_Run_Attack_with_shadow.png"))


def update(window, dt):
    global position, animation_time, current_direction, is_moving, is_attacking, attack_animation_time
    global attack_direction, attack_cooldown_remaining
    global boost_remaining, boost_cooldown_remaining
    global hit_feedback_until, knockback_initial, knockback

    now = glfw.get_time()
    dur = config.HIT_FEEDBACK_DURATION
    if hit_feedback_until > 0.0:
        if now >= hit_feedback_until:
            hit_feedback_until = 0.0
            knockback_initial = (0.0, 0.0, 0.0)
            knockback = (0.0, 0.0, 0.0)
        else:
            t = (hit_feedback_until - now) / dur
            knockback = (knockback_initial[0] * t, 0.0, knockback_initial[2] * t)

    ctrl_pressed = (
        glfw.get_key(window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS
        or glfw.get_key(window, glfw.KEY_RIGHT_CONTROL) == glfw.PRESS
    )

    moveX = 0.0
    moveZ = 0.0

    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS or glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        moveX = -1.0
    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS or glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        moveX = 1.0
    
    # Movimento em profundidade (eixo Z) - cima/baixo na tela (visão isométrica)
    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS or glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        moveZ = -1.0
    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS or glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        moveZ = 1.0

    if moveX != 0.0 or moveZ != 0.0:
        length = math.sqrt(moveX * moveX + moveZ * moveZ)
        moveX /= length
        moveZ /= length

        if abs(moveZ) > abs(moveX):
            if moveZ > 0:
                current_direction = 3
            else:
                current_direction = 0
        else:
            if moveX < 0:
                current_direction = 2
            else:
                current_direction = 1

        is_moving = True
        effective_speed = config.MOVEMENT_SPEED * (
            config.BOOST_SPEED_MULTIPLIER if (ctrl_pressed and boost_remaining > 0.0) else 1.0
        )

        target_x = position.x + moveX * effective_speed * dt
        target_z = position.z + moveZ * effective_speed * dt
        player_radius = 0.5

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

        target_ramp_height = map.getRampHeightAt(target_x, target_z)
        if target_ramp_height is not None:
            target_y = world_config.GROUND_LEVEL + target_ramp_height
            target_on_ramp = True
        else:
            target_tile_props = map.getTilePropertiesAt(target_x, target_z)
            if target_tile_props:
                target_tile_height = target_tile_props.get('height', world_config.FLOOR_TILE_HEIGHT)
                target_y = world_config.GROUND_LEVEL + target_tile_height
            else:
                target_y = world_config.GROUND_LEVEL
            target_on_ramp = False

        height_diff = target_y - current_y
        max_height_jump = 0.15
        max_height_drop = 0.3

        if current_on_ramp or target_on_ramp:
            pass
        elif height_diff > max_height_jump:
            return
        elif height_diff < -max_height_drop:
            return

        tile_collision = map.checkTileCollision(target_x, target_z, player_radius, target_y)
        prop_collision = props.checkPropCollision(target_x, target_z, player_radius, target_y)
        
        if not tile_collision and not prop_collision:
            position.x = target_x
            position.z = target_z
        else:
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

                x_height_diff = x_y - current_y
                if x_on_ramp or current_on_ramp or (x_height_diff <= max_height_jump and x_height_diff >= -max_height_drop):
                    x_tile_collision = map.checkTileCollision(target_x, position.z, player_radius, x_y)
                    x_prop_collision = props.checkPropCollision(target_x, position.z, player_radius, x_y)
                    if not x_tile_collision and not x_prop_collision:
                        position.x = target_x
                    else:
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

                        z_height_diff = z_y - current_y
                        if z_on_ramp or current_on_ramp or (z_height_diff <= max_height_jump and z_height_diff >= -max_height_drop):
                            z_tile_collision = map.checkTileCollision(position.x, target_z, player_radius, z_y)
                            z_prop_collision = props.checkPropCollision(position.x, target_z, player_radius, z_y)
                            if not z_tile_collision and not z_prop_collision:
                                position.z = target_z
    else:
        is_moving = False

    # ===== ALTURA Y (rampas e plataformas) =====
    ramp_height = map.getRampHeightAt(position.x, position.z)

    if ramp_height is not None:
        if ramp_height >= 0.99:
            ramp_height = 1.0
        final_y = world_config.GROUND_LEVEL + ramp_height
        position.y = final_y
    else:
        tile_props = map.getTilePropertiesAt(position.x, position.z)
        if tile_props:
            tile_height = tile_props.get('height', world_config.FLOOR_TILE_HEIGHT)
            final_y = world_config.GROUND_LEVEL + tile_height
            position.y = final_y
        else:
            position.y = world_config.GROUND_LEVEL

    # ===== ATAQUE (ESPAÇO) =====
    global was_pressing_space
    space_pressed = glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS
    can_start_attack = not is_attacking and attack_cooldown_remaining <= 0.0
    if space_pressed and not was_pressing_space and can_start_attack:
        is_attacking = True
        attack_animation_time = 0.0
        attack_direction = current_direction
    was_pressing_space = space_pressed

    # ===== ANIMAÇÃO =====
    global was_moving, last_direction

    if is_attacking:
        attack_animation_time += dt
        if attack_animation_time >= config.ATTACK_DURATION:
            is_attacking = False
            attack_animation_time = 0.0
            attack_cooldown_remaining = config.ATTACK_COOLDOWN
            animation_time = 0.0
    elif attack_cooldown_remaining > 0.0:
        attack_cooldown_remaining = max(0.0, attack_cooldown_remaining - dt)

    # Boost (Ctrl): só drena enquanto a tecla está pressionada; ao esgotar, cooldown 4 s e recarrega
    if ctrl_pressed and boost_remaining > 0.0:
        boost_remaining = max(0.0, boost_remaining - dt)
        if boost_remaining <= 0.0:
            boost_cooldown_remaining = config.BOOST_COOLDOWN
    elif boost_cooldown_remaining > 0.0:
        boost_cooldown_remaining = max(0.0, boost_cooldown_remaining - dt)
        if boost_cooldown_remaining <= 0.0:
            boost_remaining = config.BOOST_DURATION

    if not is_attacking:
        if was_moving != is_moving:
            animation_time = 0.0

        if last_direction != current_direction:
            animation_time = 0.0

        was_moving = is_moving
        last_direction = current_direction

        if is_moving:
            animation_time += dt * config.ANIMATION_SPEED
            animation_time = animation_time % config.SPRITE_SHEET_COLS
        else:
            idle_animation_speed = config.ANIMATION_SPEED * 0.6
            animation_time += dt * idle_animation_speed
            if current_direction == 0:
                idle_cols = 4
            else:
                idle_cols = 12
            animation_time = animation_time % idle_cols


def _display_position():
    kb = knockback if hit_feedback_until > 0.0 else (0.0, 0.0, 0.0)
    return glm.vec3(position.x + kb[0], position.y + kb[1], position.z + kb[2])


def render(modelMatrix_loc, cameraPos):
    global animation_time, current_direction, is_moving, is_attacking, attack_animation_time

    glBindVertexArray(playerMesh[0])

    if is_attacking:
        if is_moving:
            glBindTexture(GL_TEXTURE_2D, playerRunAttackTexture)
        else:
            glBindTexture(GL_TEXTURE_2D, playerAttackTexture)
        sprite_cols = config.SPRITE_SHEET_COLS
        progress = min(1.0, attack_animation_time / config.ATTACK_DURATION)
        current_frame = min(config.ATTACK_FRAMES - 1, int(progress * config.ATTACK_FRAMES))
    elif is_moving:
        glBindTexture(GL_TEXTURE_2D, playerTexture)
        sprite_cols = config.SPRITE_SHEET_COLS
        animation_cols = sprite_cols
        current_frame = int(animation_time) % animation_cols
    else:
        glBindTexture(GL_TEXTURE_2D, playerIdleTexture)
        sprite_cols = 12
        if current_direction == 0:
            animation_cols = 4
        else:
            animation_cols = 12
        animation_time = animation_time % animation_cols
        current_frame = int(animation_time) % animation_cols

    sprite_width = 1.0 / sprite_cols
    sprite_height = 1.0 / config.SPRITE_SHEET_ROWS
    
    offset_x = current_frame * sprite_width
    direction_row = attack_direction if is_attacking else current_direction
    offset_y = direction_row * sprite_height

    shader_id = glGetInteger(GL_CURRENT_PROGRAM)
    sprite_offset_loc = glGetUniformLocation(shader_id, 'spriteOffset')
    sprite_size_loc = glGetUniformLocation(shader_id, 'spriteSize')
    is_sprite_loc = glGetUniformLocation(shader_id, 'isSprite')
    
    # Definir uniforms do sprite sheet
    if sprite_offset_loc != -1:
        glUniform2f(sprite_offset_loc, offset_x, offset_y)
    if sprite_size_loc != -1:
        glUniform2f(sprite_size_loc, sprite_width, sprite_height)

    if is_sprite_loc != -1:
        glUniform1i(is_sprite_loc, 1)
    sprite_hit_flash_loc = glGetUniformLocation(shader_id, 'spriteHitFlash')
    now = glfw.get_time()
    dur = config.HIT_FEEDBACK_DURATION
    if sprite_hit_flash_loc != -1:
        if hit_feedback_until > 0.0:
            t = max(0.0, (hit_feedback_until - now) / dur)
            glUniform1f(sprite_hit_flash_loc, t)
        else:
            glUniform1f(sprite_hit_flash_loc, 0.0)

    modelMatrix = resources.calculateBillboardMatrix(_display_position(), cameraPos)
    glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(modelMatrix))
    glDrawArrays(GL_TRIANGLES, 0, playerMesh[1])


def getPosition():
    return position


def get_hp():
    return (hp, config.PLAYER_MAX_HP)


def get_stamina_fill():
    if boost_remaining > 0.0:
        return boost_remaining / config.BOOST_DURATION
    if boost_cooldown_remaining > 0.0:
        return 1.0 - (boost_cooldown_remaining / config.BOOST_COOLDOWN)
    return 1.0


def take_damage(amount, knockback_direction=None):
    global hp, hit_feedback_until, knockback_initial, knockback
    hp = max(0, hp - amount)
    hit_feedback_until = glfw.get_time() + config.HIT_FEEDBACK_DURATION
    if knockback_direction is not None and (knockback_direction[0] != 0.0 or knockback_direction[1] != 0.0):
        dx, dz = knockback_direction[0], knockback_direction[1]
        L = math.sqrt(dx * dx + dz * dz)
        if L > 1e-6:
            dx /= L
            dz /= L
        d = config.HIT_KNOCKBACK_DISTANCE
        knockback_initial = (dx * d, 0.0, dz * d)
        knockback = (dx * d, 0.0, dz * d)
    else:
        knockback_initial = (0.0, 0.0, 0.0)
        knockback = (0.0, 0.0, 0.0)


def reset():
    global position, hp, animation_time, current_direction, last_direction
    global is_moving, is_attacking, attack_animation_time, attack_direction, attack_cooldown_remaining
    global was_pressing_space, was_moving, boost_remaining, boost_cooldown_remaining
    global hit_feedback_until, knockback_initial, knockback
    position = glm.vec3(*config.INITIAL_POSITION)
    hp = config.PLAYER_MAX_HP
    animation_time = 0.0
    current_direction = 3
    last_direction = 3
    is_moving = False
    is_attacking = False
    attack_animation_time = 0.0
    attack_cooldown_remaining = 0.0
    was_pressing_space = False
    was_moving = False
    boost_remaining = config.BOOST_DURATION
    boost_cooldown_remaining = 0.0
    hit_feedback_until = 0.0
    knockback_initial = (0.0, 0.0, 0.0)
    knockback = (0.0, 0.0, 0.0)


def get_attack_hitbox():
    if not is_attacking:
        return None
    px, pz = position.x, position.z
    L = config.ATTACK_HITBOX_LENGTH
    W = config.ATTACK_HITBOX_WIDTH
    front = config.ATTACK_HITBOX_PLAYER_FRONT
    hw = W / 2
    if attack_direction == 0:   # cima (-Z)
        return (px - hw, px + hw, pz - front - L, pz - front)
    if attack_direction == 3:   # baixo (+Z)
        return (px - hw, px + hw, pz + front, pz + front + L)
    if attack_direction == 1:   # direita (+X)
        return (px + front, px + front + L, pz - hw, pz + hw)
    if attack_direction == 2:   # esquerda (-X)
        return (px - front - L, px - front, pz - hw, pz + hw)
    return None


def is_point_in_attack_hitbox(x, z):
    """
    Verifica se o ponto (x, z) no plano XZ está dentro da hitbox de ataque.

    Útil para detecção de alvos quando for implementar dano.

    Returns:
        bool: True se is_attacking e o ponto está no retângulo da hitbox.
    """
    box = get_attack_hitbox()
    if box is None:
        return False
    min_x, max_x, min_z, max_z = box
    return min_x <= x <= max_x and min_z <= z <= max_z
