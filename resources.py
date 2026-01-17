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
    Calcula a matriz de billboarding (sprite sempre voltado para a câmera).
    Utiliza billboarding cilíndrico: rotaciona apenas no eixo Y (sprite fica em pé).
    """
    dirX = cameraPosition.x - objectPosition.x
    dirZ = cameraPosition.z - objectPosition.z
    
    angle = math.atan2(dirX, dirZ)
    
    modelMatrix = glm.mat4(1.0)
    modelMatrix = glm.translate(modelMatrix, objectPosition)
    modelMatrix = glm.rotate(modelMatrix, angle, glm.vec3(0, 1, 0))
    
    return modelMatrix
