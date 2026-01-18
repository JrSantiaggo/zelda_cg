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
    
    Formato esperado dos vértices:
    - Formato antigo (compatibilidade): [x, y, z, u, v] (5 floats)
    - Formato novo (com normais): [x, y, z, nx, ny, nz, u, v] (8 floats)
    
    Detecta automaticamente o formato pelo tamanho do array.
    """
    qtdVertices = len(vertices)
    vertices = np.array(vertices, dtype=np.float32)
    
    # Detectar formato: se o primeiro vértice tem 5 ou 8 elementos
    if len(vertices) > 0 and len(vertices[0]) == 8:
        # Formato novo com normais: [x, y, z, nx, ny, nz, u, v]
        stride = 8 * 4  # 8 floats * 4 bytes cada
        has_normals = True
    else:
        # Formato antigo: [x, y, z, u, v]
        stride = 5 * 4  # 5 floats * 4 bytes cada
        has_normals = False

    # Criando o espaço e enviando os dados para a memória gráfica
    vaoId = glGenVertexArrays(1)
    glBindVertexArray(vaoId)

    vboId = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vboId)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    # Atributo 0: posição (x, y, z)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    
    # Atributo 1: coordenada de textura (u, v)
    if has_normals:
        # Formato: [x, y, z, nx, ny, nz, u, v]
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6*4))  # u, v após normal
        
        # Atributo 2: normal (nx, ny, nz)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3*4))  # nx, ny, nz após posição
    else:
        # Formato antigo: [x, y, z, u, v]
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3*4))  # u, v após posição
        
        # Atributo 2: normal padrão (desabilitado para formato antigo - será ignorado pelo shader)
        # Mantém compatibilidade, mas norma será (0, 0, 1) por padrão
        pass

    glBindVertexArray(0)
    return vaoId, qtdVertices


def createCubeMesh():
    """
    Cria malha de cubo unitário (1x1x1) centrado na origem.
    Usado para plataformas - escala aplicada via modelMatrix.
    Formato: [x, y, z, nx, ny, nz, u, v]
    """
    s = 0.5
    
    vertices = [
        # Face frontal (z = +s) - normal: (0, 0, 1)
        [-s, -s,  s,   0.0, 0.0, 1.0,   0.0, 0.0],
        [ s, -s,  s,   0.0, 0.0, 1.0,   1.0, 0.0],
        [ s,  s,  s,   0.0, 0.0, 1.0,   1.0, 1.0],
        [-s, -s,  s,   0.0, 0.0, 1.0,   0.0, 0.0],
        [ s,  s,  s,   0.0, 0.0, 1.0,   1.0, 1.0],
        [-s,  s,  s,   0.0, 0.0, 1.0,   0.0, 1.0],
        
        # Face traseira (z = -s) - normal: (0, 0, -1)
        [ s, -s, -s,   0.0, 0.0, -1.0,   0.0, 0.0],
        [-s, -s, -s,   0.0, 0.0, -1.0,   1.0, 0.0],
        [-s,  s, -s,   0.0, 0.0, -1.0,   1.0, 1.0],
        [ s, -s, -s,   0.0, 0.0, -1.0,   0.0, 0.0],
        [-s,  s, -s,   0.0, 0.0, -1.0,   1.0, 1.0],
        [ s,  s, -s,   0.0, 0.0, -1.0,   0.0, 1.0],
        
        # Face superior (y = +s) - normal: (0, 1, 0)
        [-s,  s,  s,   0.0, 1.0, 0.0,   0.0, 0.0],
        [ s,  s,  s,   0.0, 1.0, 0.0,   1.0, 0.0],
        [ s,  s, -s,   0.0, 1.0, 0.0,   1.0, 1.0],
        [-s,  s,  s,   0.0, 1.0, 0.0,   0.0, 0.0],
        [ s,  s, -s,   0.0, 1.0, 0.0,   1.0, 1.0],
        [-s,  s, -s,   0.0, 1.0, 0.0,   0.0, 1.0],
        
        # Face inferior (y = -s) - normal: (0, -1, 0)
        [-s, -s, -s,   0.0, -1.0, 0.0,   0.0, 0.0],
        [ s, -s, -s,   0.0, -1.0, 0.0,   1.0, 0.0],
        [ s, -s,  s,   0.0, -1.0, 0.0,   1.0, 1.0],
        [-s, -s, -s,   0.0, -1.0, 0.0,   0.0, 0.0],
        [ s, -s,  s,   0.0, -1.0, 0.0,   1.0, 1.0],
        [-s, -s,  s,   0.0, -1.0, 0.0,   0.0, 1.0],
        
        # Face direita (x = +s) - normal: (1, 0, 0)
        [ s, -s,  s,   1.0, 0.0, 0.0,   0.0, 0.0],
        [ s, -s, -s,   1.0, 0.0, 0.0,   1.0, 0.0],
        [ s,  s, -s,   1.0, 0.0, 0.0,   1.0, 1.0],
        [ s, -s,  s,   1.0, 0.0, 0.0,   0.0, 0.0],
        [ s,  s, -s,   1.0, 0.0, 0.0,   1.0, 1.0],
        [ s,  s,  s,   1.0, 0.0, 0.0,   0.0, 1.0],
        
        # Face esquerda (x = -s) - normal: (-1, 0, 0)
        [-s, -s, -s,   -1.0, 0.0, 0.0,   0.0, 0.0],
        [-s, -s,  s,   -1.0, 0.0, 0.0,   1.0, 0.0],
        [-s,  s,  s,   -1.0, 0.0, 0.0,   1.0, 1.0],
        [-s, -s, -s,   -1.0, 0.0, 0.0,   0.0, 0.0],
        [-s,  s,  s,   -1.0, 0.0, 0.0,   1.0, 1.0],
        [-s,  s, -s,   -1.0, 0.0, 0.0,   0.0, 1.0],
    ]
    
    return createMeshFromVertices(vertices)


def createRampMesh():
    """
    Cria malha de rampa inclinada geometricamente.
    Rampa unitária: comprimento de 0 a 1 no eixo X, largura de -0.5 a 0.5 no eixo Z.
    Começa em y=0 (início) e sobe até y=1 (fim) no eixo X positivo.
    Geometria base que será escalada e rotacionada para direções N/S/E/W.
    Formato: [x, y, z, nx, ny, nz, u, v]
    
    Normal da face inclinada: perpendicular ao plano da rampa
    Vetor ao longo da rampa: (1, 1, 0) normalizado
    Vetor perpendicular (normal): calculado via produto vetorial
    """
    # Rampa unitária: vai de x=0 (y=0) até x=1 (y=1)
    # Largura: -0.5 a +0.5 (1 unidade total = 1 tile após escala)
    start_x = 0.0
    end_x = 1.0
    start_y = 0.0
    end_y = 1.0
    start_z = -0.5
    end_z = 0.5
    
    # Calcular normal da face inclinada superior
    # A rampa sobe de (0, 0, z) para (1, 1, z), então vetor de subida = (1, 1, 0)
    # Vetor de largura (ao longo do eixo Z) = (0, 0, 1)
    # Normal = normalize(cross(largura, subida)) = normalize(cross((0,0,1), (1,1,0)))
    # cross((0,0,1), (1,1,0)) = (0*0 - 1*1, 1*1 - 0*0, 0*1 - 0*1) = (-1, 1, 0)
    # Normalizada: (-1/sqrt(2), 1/sqrt(2), 0) ≈ (-0.707, 0.707, 0)
    ramp_normal_x = -0.70710678  # -1/sqrt(2)
    ramp_normal_y = 0.70710678   # 1/sqrt(2)
    ramp_normal_z = 0.0
    
    # Normal da face inferior (base plana): (0, -1, 0) - aponta para baixo
    base_normal = (0.0, -1.0, 0.0)
    
    # Normal das faces laterais (perpendiculares ao plano da rampa no eixo Z)
    # Face lateral esquerda (z negativo): normal = (-ramp_normal_x, -ramp_normal_y, 0) mas simplificando: (0, 0, -1) aproximadamente
    # Para simplificar, vamos usar normais perpendiculares ao plano XZ
    side_normal_left = (0.0, 0.0, -1.0)  # Aponta para Z negativo
    side_normal_right = (0.0, 0.0, 1.0)   # Aponta para Z positivo
    
    # Normal da face frontal (fim da rampa, x=1): perpendicular ao plano YZ, aponta para +X
    front_normal = (1.0, 0.0, 0.0)
    
    vertices = [
        # Face inclinada superior (plano inclinado - rampa)
        # UVs ajustados: U ao longo de Z (largura), V baseado em Y (altura da rampa, de 0 a 1)
        # Isso garante que a textura (grama no topo, terra embaixo) apareça correta independente da rotação
        # U: 0.0 = z=-0.5 (esquerda), 1.0 = z=0.5 (direita)
        # V: 0.0 = y=0 (baixo da rampa/terra), 1.0 = y=1 (topo da rampa/grama)
        # Triângulo 1
        [start_x, start_y, start_z,   ramp_normal_x, ramp_normal_y, ramp_normal_z,   0.0, 0.0],  # Início baixo esquerda: U=0 (z=-0.5), V=0 (y=0)
        [end_x, end_y, start_z,       ramp_normal_x, ramp_normal_y, ramp_normal_z,   0.0, 1.0],  # Fim alto esquerda: U=0 (z=-0.5), V=1 (y=1)
        [end_x, end_y, end_z,         ramp_normal_x, ramp_normal_y, ramp_normal_z,   1.0, 1.0],  # Fim alto direita: U=1 (z=0.5), V=1 (y=1)
        # Triângulo 2
        [start_x, start_y, start_z,   ramp_normal_x, ramp_normal_y, ramp_normal_z,   0.0, 0.0],  # Início baixo esquerda: U=0, V=0
        [end_x, end_y, end_z,         ramp_normal_x, ramp_normal_y, ramp_normal_z,   1.0, 1.0],  # Fim alto direita: U=1, V=1
        [start_x, start_y, end_z,     ramp_normal_x, ramp_normal_y, ramp_normal_z,   1.0, 0.0],  # Início baixo direita: U=1 (z=0.5), V=0 (y=0)
        
        # Face inferior (base plana) - normal: (0, -1, 0)
        [start_x, start_y, start_z,   base_normal[0], base_normal[1], base_normal[2],   0.0, 0.0],
        [start_x, start_y, end_z,     base_normal[0], base_normal[1], base_normal[2],   1.0, 0.0],
        [end_x, start_y, end_z,       base_normal[0], base_normal[1], base_normal[2],   1.0, 1.0],
        [start_x, start_y, start_z,   base_normal[0], base_normal[1], base_normal[2],   0.0, 0.0],
        [end_x, start_y, end_z,       base_normal[0], base_normal[1], base_normal[2],   1.0, 1.0],
        [end_x, start_y, start_z,     base_normal[0], base_normal[1], base_normal[2],   0.0, 1.0],
        
        # Face lateral esquerda (triângulo - lado Z negativo) - normal: (0, 0, -1)
        [start_x, start_y, start_z,   side_normal_left[0], side_normal_left[1], side_normal_left[2],   0.0, 0.0],
        [end_x, start_y, start_z,     side_normal_left[0], side_normal_left[1], side_normal_left[2],   1.0, 0.0],
        [end_x, end_y, start_z,       side_normal_left[0], side_normal_left[1], side_normal_left[2],   1.0, 1.0],
        
        # Face lateral direita (triângulo - lado Z positivo) - normal: (0, 0, 1)
        [start_x, start_y, end_z,     side_normal_right[0], side_normal_right[1], side_normal_right[2],   0.0, 0.0],
        [end_x, end_y, end_z,         side_normal_right[0], side_normal_right[1], side_normal_right[2],   1.0, 1.0],
        [end_x, start_y, end_z,       side_normal_right[0], side_normal_right[1], side_normal_right[2],   1.0, 0.0],
        
        # Face frontal (fim da rampa - retângulo vertical onde x=1, y vai de 0 a 1) - normal: (1, 0, 0)
        [end_x, start_y, start_z,     front_normal[0], front_normal[1], front_normal[2],   0.0, 0.0],
        [end_x, end_y, start_z,       front_normal[0], front_normal[1], front_normal[2],   0.0, 1.0],
        [end_x, end_y, end_z,         front_normal[0], front_normal[1], front_normal[2],   1.0, 1.0],
        [end_x, start_y, start_z,     front_normal[0], front_normal[1], front_normal[2],   0.0, 0.0],
        [end_x, end_y, end_z,         front_normal[0], front_normal[1], front_normal[2],   1.0, 1.0],
        [end_x, start_y, end_z,       front_normal[0], front_normal[1], front_normal[2],   1.0, 0.0],
    ]
    
    return createMeshFromVertices(vertices)


def createSpriteMesh(size_x=None, size_y=None):
    """
    Cria malha de quad para sprite (jogador ou inimigo).
    Formato: [x, y, z, nx, ny, nz, u, v]
    
    Para sprite 2D com billboarding, a normal fixa aponta para frente (0, 0, 1)
    para que o sprite sempre tenha iluminação correta quando a luz vier da frente.
    A normal será transformada pela modelMatrix durante o billboarding.
    
    Args:
        size_x: Metade da largura do quad (None = config.OBJECT_SIZE_X)
        size_y: Metade da altura do quad (None = config.OBJECT_SIZE_Y)
    """
    w = config.OBJECT_SIZE_X if size_x is None else size_x
    h = config.OBJECT_SIZE_Y if size_y is None else size_y
    
    # Normal fixa para sprite: aponta para frente no eixo Z positivo (0, 0, 1)
    # Isso garante que o sprite tenha iluminação consistente
    # A normal será transformada pela modelMatrix (via matriz normal) durante o billboarding
    sprite_normal = (0.0, 0.0, 1.0)
    
    vertices = [
        # Quad único (sprite) - posicionado "de pé" com base em y=0
        # Formato: [x, y, z, nx, ny, nz, u, v]
        [-w,  0.0, 0.0,   sprite_normal[0], sprite_normal[1], sprite_normal[2],   0.0, 0.0],
        [ w,  0.0, 0.0,   sprite_normal[0], sprite_normal[1], sprite_normal[2],   1.0, 0.0],
        [ w, h*2, 0.0,   sprite_normal[0], sprite_normal[1], sprite_normal[2],   1.0, 1.0],
        [-w,  0.0, 0.0,   sprite_normal[0], sprite_normal[1], sprite_normal[2],   0.0, 0.0],
        [ w, h*2, 0.0,   sprite_normal[0], sprite_normal[1], sprite_normal[2],   1.0, 1.0],
        [-w, h*2, 0.0,   sprite_normal[0], sprite_normal[1], sprite_normal[2],   0.0, 1.0],
    ]
    
    return createMeshFromVertices(vertices)


def createScreenQuad():
    """
    Cria um quad unitário (0,0)-(1,1) no plano XY, z=0.
    Usado para HUD (barra de vida etc.) em projeção ortográfica 2D.
    Formato: [x, y, z, nx, ny, nz, u, v]
    """
    n = (0.0, 0.0, 1.0)
    vertices = [
        [0.0, 0.0, 0.0,  n[0], n[1], n[2],  0.0, 0.0],
        [1.0, 0.0, 0.0,  n[0], n[1], n[2],  1.0, 0.0],
        [1.0, 1.0, 0.0,  n[0], n[1], n[2],  1.0, 1.0],
        [0.0, 0.0, 0.0,  n[0], n[1], n[2],  0.0, 0.0],
        [1.0, 1.0, 0.0,  n[0], n[1], n[2],  1.0, 1.0],
        [0.0, 1.0, 0.0,  n[0], n[1], n[2],  0.0, 1.0],
    ]
    return createMeshFromVertices(vertices)
