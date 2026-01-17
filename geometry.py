"""
Módulo de geometria: criação de malhas 3D
"""
import numpy as np
from OpenGL.GL import *
import ctypes
import config


def createMeshFromVertices(vertices):
    """
    Função auxiliar que envia vértices para a GPU e retorna (vaoId, vertexCount).
    """
    qtdVertices = len(vertices)
    vertices = np.array(vertices, dtype=np.float32)

    # Criando o espaço e enviando os dados para a memória gráfica
    vaoId = glGenVertexArrays(1)
    glBindVertexArray(vaoId)

    vboId = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vboId)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5*4, ctypes.c_void_p(0))
    
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5*4, ctypes.c_void_p(3*4))

    glBindVertexArray(0)
    return vaoId, qtdVertices


def createCubeMesh():
    """
    Cria malha de cubo unitário (1x1x1) centrado na origem.
    Usado para plataformas - escala aplicada via modelMatrix.
    """
    s = 0.5
    
    vertices = [
        # Face frontal (z = +s)
        [-s, -s,  s,   0.0, 0.0],
        [ s, -s,  s,   1.0, 0.0],
        [ s,  s,  s,   1.0, 1.0],
        [-s, -s,  s,   0.0, 0.0],
        [ s,  s,  s,   1.0, 1.0],
        [-s,  s,  s,   0.0, 1.0],
        
        # Face traseira (z = -s)
        [ s, -s, -s,   0.0, 0.0],
        [-s, -s, -s,   1.0, 0.0],
        [-s,  s, -s,   1.0, 1.0],
        [ s, -s, -s,   0.0, 0.0],
        [-s,  s, -s,   1.0, 1.0],
        [ s,  s, -s,   0.0, 1.0],
        
        # Face superior (y = +s)
        [-s,  s,  s,   0.0, 0.0],
        [ s,  s,  s,   1.0, 0.0],
        [ s,  s, -s,   1.0, 1.0],
        [-s,  s,  s,   0.0, 0.0],
        [ s,  s, -s,   1.0, 1.0],
        [-s,  s, -s,   0.0, 1.0],
        
        # Face inferior (y = -s)
        [-s, -s, -s,   0.0, 0.0],
        [ s, -s, -s,   1.0, 0.0],
        [ s, -s,  s,   1.0, 1.0],
        [-s, -s, -s,   0.0, 0.0],
        [ s, -s,  s,   1.0, 1.0],
        [-s, -s,  s,   0.0, 1.0],
        
        # Face direita (x = +s)
        [ s, -s,  s,   0.0, 0.0],
        [ s, -s, -s,   1.0, 0.0],
        [ s,  s, -s,   1.0, 1.0],
        [ s, -s,  s,   0.0, 0.0],
        [ s,  s, -s,   1.0, 1.0],
        [ s,  s,  s,   0.0, 1.0],
        
        # Face esquerda (x = -s)
        [-s, -s, -s,   0.0, 0.0],
        [-s, -s,  s,   1.0, 0.0],
        [-s,  s,  s,   1.0, 1.0],
        [-s, -s, -s,   0.0, 0.0],
        [-s,  s,  s,   1.0, 1.0],
        [-s,  s, -s,   0.0, 1.0],
    ]
    
    return createMeshFromVertices(vertices)


def createRampMesh():
    """
    Cria malha de rampa inclinada geometricamente.
    Rampa unitária: comprimento de 0 a 1 no eixo X, largura de -0.5 a 0.5 no eixo Z.
    Começa em y=0 (início) e sobe até y=1 (fim) no eixo X positivo.
    Geometria base que será escalada e rotacionada para direções N/S/E/W.
    """
    # Rampa unitária: vai de x=0 (y=0) até x=1 (y=1)
    # Largura: -0.5 a +0.5 (1 unidade total = 1 tile após escala)
    start_x = 0.0
    end_x = 1.0
    start_y = 0.0
    end_y = 1.0
    start_z = -0.5
    end_z = 0.5
    
    vertices = [
        # Face inclinada superior (plano inclinado - rampa)
        # Triângulo 1
        [start_x, start_y, start_z,   0.0, 0.0],  # Início baixo, esquerda
        [end_x, end_y, start_z,       1.0, 0.0],  # Fim alto, esquerda
        [end_x, end_y, end_z,         1.0, 1.0],  # Fim alto, direita
        # Triângulo 2
        [start_x, start_y, start_z,   0.0, 0.0],  # Início baixo, esquerda
        [end_x, end_y, end_z,         1.0, 1.0],  # Fim alto, direita
        [start_x, start_y, end_z,     0.0, 1.0],  # Início baixo, direita
        
        # Face inferior (base plana)
        [start_x, start_y, start_z,   0.0, 0.0],
        [start_x, start_y, end_z,     1.0, 0.0],
        [end_x, start_y, end_z,       1.0, 1.0],
        [start_x, start_y, start_z,   0.0, 0.0],
        [end_x, start_y, end_z,       1.0, 1.0],
        [end_x, start_y, start_z,     0.0, 1.0],
        
        # Face lateral esquerda (triângulo - lado Z negativo)
        [start_x, start_y, start_z,   0.0, 0.0],
        [end_x, start_y, start_z,     1.0, 0.0],
        [end_x, end_y, start_z,       1.0, 1.0],
        
        # Face lateral direita (triângulo - lado Z positivo)
        [start_x, start_y, end_z,     0.0, 0.0],
        [end_x, end_y, end_z,         1.0, 1.0],
        [end_x, start_y, end_z,       1.0, 0.0],
        
        # Face frontal (fim da rampa - retângulo vertical onde x=1, y vai de 0 a 1)
        [end_x, start_y, start_z,     0.0, 0.0],
        [end_x, end_y, start_z,       0.0, 1.0],
        [end_x, end_y, end_z,         1.0, 1.0],
        [end_x, start_y, start_z,     0.0, 0.0],
        [end_x, end_y, end_z,         1.0, 1.0],
        [end_x, start_y, end_z,       1.0, 0.0],
        
        # Face traseira (início da rampa - não é necessária pois é apenas uma linha onde x=0, y=0)
        # Não adicionamos vértices aqui pois a base já cobre essa área
    ]
    
    return createMeshFromVertices(vertices)


def createSpriteMesh():
    """
    Cria malha de quad para sprite do jogador.
    """
    w = config.OBJECT_SIZE_X
    h = config.OBJECT_SIZE_Y
    
    vertices = [
        # Quad único (sprite) - posicionado "de pé" com base em y=0
        [-w,  0.0, 0.0,   0.0, 0.0],
        [ w,  0.0, 0.0,   1.0, 0.0],
        [ w, h*2, 0.0,   1.0, 1.0],
        [-w,  0.0, 0.0,   0.0, 0.0],
        [ w, h*2, 0.0,   1.0, 1.0],
        [-w, h*2, 0.0,   0.0, 1.0],
    ]
    
    return createMeshFromVertices(vertices)
