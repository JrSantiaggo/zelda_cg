"""
Módulo de recursos: carregamento de texturas, shaders e cálculos auxiliares
"""
from OpenGL.GL import *
import OpenGL.GL.shaders as gls
from PIL import Image
import glm
import math


def loadTexture(fileName):
    """
    Carrega arquivo de textura e envia para memória gráfica.
    Retorna o identificador da textura.
    """
    img = Image.open(fileName)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    imgData = img.convert('RGBA').tobytes()

    texId = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texId)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, imgData)
    
    glBindTexture(GL_TEXTURE_2D, 0)
    return texId


def loadShaders(vertexShaderFileName, fragmentShaderFileName):
    """
    Carrega e compila shaders a partir de arquivos.
    Retorna o identificador do shader program.
    """
    with open(vertexShaderFileName,'r') as file:           
        vsSource = file.read()
    with open(fragmentShaderFileName,'r') as file:
        fsSource = file.read()

    vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
    fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
    shaderId = gls.compileProgram(vsId, fsId)
    
    return shaderId


def calculateBillboardMatrix(objectPosition, cameraPosition):
    """
    Calcula a matriz de billboarding cilíndrico para sprite 2D.
    
    Billboarding cilíndrico:
    - Rotaciona o sprite apenas no eixo Y (vertical)
    - Mantém o sprite sempre "em pé" (não inclina nos eixos X ou Z)
    - Faz o sprite olhar para a câmera no plano horizontal (XZ)
    
    Args:
        objectPosition: Posição do objeto (glm.vec3) no mundo
        cameraPosition: Posição da câmera (glm.vec3) no mundo
    
    Returns:
        Matriz de modelo (glm.mat4) com transformações de billboarding
    """
    # Calcular direção da câmera para o objeto no plano horizontal (XZ)
    # Ignorar componente Y para billboarding cilíndrico (sprite sempre em pé)
    dirX = cameraPosition.x - objectPosition.x
    dirZ = cameraPosition.z - objectPosition.z
    
    # Calcular ângulo de rotação no eixo Y usando atan2
    # atan2(dirX, dirZ) retorna o ângulo em radianos
    # ângulo = 0 quando câmera está em +Z (em frente ao objeto)
    # ângulo = π/2 quando câmera está em +X (à direita do objeto)
    angle = math.atan2(dirX, dirZ)
    
    # Construir matriz de modelo com transformações na ordem correta:
    # 1. Transladar para a posição do objeto no mundo
    # 2. Rotacionar no eixo Y para que o sprite olhe para a câmera
    # A ordem importa: aplicar rotação DEPOIS da translação
    # Isso garante que o sprite rotacione em torno de sua própria posição
    
    modelMatrix = glm.mat4(1.0)
    modelMatrix = glm.translate(modelMatrix, objectPosition)
    modelMatrix = glm.rotate(modelMatrix, angle, glm.vec3(0.0, 1.0, 0.0))
    
    # Nota: Não aplicar escala aqui - a escala do sprite já está na geometria
    # (via OBJECT_SIZE_X e OBJECT_SIZE_Y na createSpriteMesh)
    
    return modelMatrix
