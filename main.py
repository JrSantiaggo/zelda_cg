"""
Módulo principal: inicialização e loop principal da aplicação
"""
import os
# Configurar plataforma PyOpenGL para usar GLX (compatível com GLFW no Linux/WSL)
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
# VARIÁVEIS GLOBAIS DO SISTEMA
# ============================================================================
resolution = [config.WINDOW_WIDTH, config.WINDOW_HEIGHT]
myShaderId = 0
_last_frame_time = 0.0  # Para delta time (frame-rate independent)

# ============================================================================
# FUNÇÕES DE INICIALIZAÇÃO
# ============================================================================

def init():
    """
    Inicializa OpenGL e carrega recursos (malhas, texturas, shaders).
    """
    global myShaderId

    # Configurações OpenGL
    glClearColor(*config.BACKGROUND_COLOR)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    # Desabilitar face culling temporariamente para debug
    glDisable(GL_CULL_FACE)

    here = os.path.dirname(os.path.abspath(__file__))
    
    # Carregar shaders (principal e depth para shadow mapping)
    myShaderId = resources.loadShaders(
        os.path.join(here, config.VERTEX_SHADER_FILE),
        os.path.join(here, config.FRAGMENT_SHADER_FILE),
    )
    depthShaderId = resources.loadShaders(
        os.path.join(here, config.DEPTH_VERTEX_SHADER_FILE),
        os.path.join(here, config.DEPTH_FRAGMENT_SHADER_FILE),
    )
    
    # Inicializar recursos dos módulos
    # IMPORTANTE: props.init() deve ser chamado ANTES de map.init()
    # porque map.init() adiciona props à lista
    props.init()
    player.init(geometry)
    map.init(geometry)
    enemies.init(geometry)  # após map.init (usa getRampHeightAt / getTilePropertiesAt)
    archer.init(geometry)   # arqueiros (separado; futuramente flechas)
    render.init(geometry, depthShaderId)  # HUD e FBO/textura de shadow map

# ============================================================================
# FUNÇÕES DO SISTEMA (UPDATE E CALLBACKS)
# ============================================================================

def update(window):
    """
    Atualiza a lógica do jogo (chama updates de cada sistema).
    Usa delta time para ser independente da taxa de quadros.
    Se a vida do jogador chegar a zero, reinicia: player na posição inicial e inimigos respawnam.
    """
    global _last_frame_time
    now = glfw.get_time()
    if _last_frame_time > 0.0:
        delta_time = now - _last_frame_time
        delta_time = max(0.0001, min(0.1, delta_time))  # Limitar para evitar saltos (ex.: ao voltar do debug)
    else:
        delta_time = 0.0
    _last_frame_time = now

    player.update(window, delta_time)
    enemies.update(delta_time)
    archer.update(delta_time)

    # Vida zerada: reinicia o jogo (player no começo, inimigos nascem de novo)
    if player.get_hp()[0] <= 0:
        player.reset()
        enemies.respawn()
        archer.respawn()

# Função de tratamento de evento (Callback Function) de alteração do tamanho da janela
def updateWindowSize(window, width, height):
    """
    Atualiza resolução da janela quando redimensionada.
    """
    global resolution
    resolution = [width, height]

# Função de tratamento de evento (Callback Function) de teclado
def keyboard(window, key, scancode, action, mods):
    """
    Trata eventos de teclado (ESC para fechar).
    """
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """
    Função principal e inicial da aplicação.
    """
    # Inicializa a GLFW
    if not glfw.init():
        print('GLFW falhou ao inicializar')
        return
    
    # Configurando hints de janela para especificar a versão do OpenGL
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, config.OPENGL_VERSION_MAJOR)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, config.OPENGL_VERSION_MINOR)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_COMPAT_PROFILE)
    glfw.window_hint(glfw.VISIBLE, glfw.TRUE)
    
    # Cria uma janela definida através da resolução e mensagem de título
    window = glfw.create_window(resolution[0], resolution[1], config.WINDOW_TITLE, None, None)
    if window is None:
        print('GLFW falhou ao criar uma janela')
        glfw.terminate()
        return
    
    # Ativa o contexto GLFW e OpenGL na janela
    glfw.make_context_current(window)
    
    # Verificação se o contexto foi criado corretamente
    if not glfw.get_current_context():
        print('Falha ao criar contexto OpenGL')
        glfw.terminate()
        return
    
    # Chama funções de configurações iniciais
    init()
    
    # Define as callback functions para a API GLFW
    glfw.set_framebuffer_size_callback(window, updateWindowSize)
    glfw.set_key_callback(window, keyboard)
    
    # Laço principal da aplicação
    while not glfw.window_should_close(window):
        glfw.poll_events()
        update(window)
        render.render(myShaderId, resolution)
        glfw.swap_buffers(window)

    # Quando o laço finalizar, desative a GLFW
    glfw.terminate()

# Chamando a função principal
if __name__ == '__main__':
    main()
