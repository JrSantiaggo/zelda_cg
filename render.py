"""
Módulo de renderização: função principal de renderização da cena
"""
from OpenGL.GL import *
import glm
import config
import player
import map
import props


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
    
    # Matriz de visão (View Matrix) - compartilhada por todos os objetos
    viewMatrix = glm.lookAt(
        glm.vec3(*config.CAMERA_POSITION),
        glm.vec3(*config.CAMERA_TARGET),
        glm.vec3(*config.CAMERA_UP)
    )
    glUniformMatrix4fv(viewMatrix_loc, 1, GL_FALSE, glm.value_ptr(viewMatrix))
    
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
    cameraPos = glm.vec3(*config.CAMERA_POSITION)
    map.renderPlatforms(modelMatrix_loc)
    map.renderRamps(modelMatrix_loc)
    props.render(modelMatrix_loc)  # Renderizar props (objetos 3D decorativos)
    player.render(modelMatrix_loc, cameraPos)

    # Desativar recursos
    glBindTexture(GL_TEXTURE_2D, 0)
    glBindVertexArray(0)
    glUseProgram(0)
