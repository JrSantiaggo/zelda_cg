import os
os.environ['PYOPENGL_PLATFORM'] = 'x11'

import glfw
from OpenGL.GL import *
import config
import geometry
import resources
import player
import map
import props
import enemies
import archer
import render

# ============================================================================
# VARIÁVEIS GLOBAIS
# ============================================================================
resolution = [config.WINDOW_WIDTH, config.WINDOW_HEIGHT]
myShaderId = 0
_last_frame_time = 0.0

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

def init():
    global myShaderId

    glClearColor(*config.BACKGROUND_COLOR)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glDisable(GL_CULL_FACE)

    here = os.path.dirname(os.path.abspath(__file__))
    myShaderId = resources.loadShaders(
        os.path.join(here, config.VERTEX_SHADER_FILE),
        os.path.join(here, config.FRAGMENT_SHADER_FILE),
    )
    depthShaderId = resources.loadShaders(
        os.path.join(here, config.DEPTH_VERTEX_SHADER_FILE),
        os.path.join(here, config.DEPTH_FRAGMENT_SHADER_FILE),
    )

    props.init()
    player.init(geometry)
    map.init(geometry)
    enemies.init(geometry)
    archer.init(geometry)
    render.init(geometry, depthShaderId)

# ============================================================================
# UPDATE E CALLBACKS
# ============================================================================

def update(window):
    global _last_frame_time
    now = glfw.get_time()
    if _last_frame_time > 0.0:
        delta_time = now - _last_frame_time
        delta_time = max(0.0001, min(0.1, delta_time))
    else:
        delta_time = 0.0
    _last_frame_time = now

    player.update(window, delta_time)
    enemies.update(delta_time)
    archer.update(delta_time)

    if player.get_hp()[0] <= 0:
        player.reset()
        enemies.respawn()
        archer.respawn()

def updateWindowSize(window, width, height):
    global resolution
    resolution = [width, height]

def keyboard(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

# ============================================================================
# MAIN
# ============================================================================

def main():
    if not glfw.init():
        print('GLFW falhou ao inicializar')
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, config.OPENGL_VERSION_MAJOR)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, config.OPENGL_VERSION_MINOR)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_COMPAT_PROFILE)
    glfw.window_hint(glfw.VISIBLE, glfw.TRUE)

    window = glfw.create_window(resolution[0], resolution[1], config.WINDOW_TITLE, None, None)
    if window is None:
        print('GLFW falhou ao criar uma janela')
        glfw.terminate()
        return

    glfw.make_context_current(window)
    if not glfw.get_current_context():
        print('Falha ao criar contexto OpenGL')
        glfw.terminate()
        return

    init()
    glfw.set_framebuffer_size_callback(window, updateWindowSize)
    glfw.set_key_callback(window, keyboard)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        update(window)
        render.render(myShaderId, resolution)
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == '__main__':
    main()
