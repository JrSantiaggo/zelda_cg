import numpy as np
from OpenGL.GL import *
import ctypes
import config


def createMeshFromVertices(vertices):
    qtdVertices = len(vertices)
    vertices = np.array(vertices, dtype=np.float32)

    if len(vertices) > 0 and len(vertices[0]) == 8:
        stride = 8 * 4
        has_normals = True
    else:
        stride = 5 * 4
        has_normals = False

    vaoId = glGenVertexArrays(1)
    glBindVertexArray(vaoId)

    vboId = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vboId)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

    if has_normals:
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6*4))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3*4))
    else:
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3*4))

    glBindVertexArray(0)
    return vaoId, qtdVertices


def createCubeMesh():
    s = 0.5
    vertices = [
        [-s, -s,  s,   0.0, 0.0, 1.0,   0.0, 0.0],
        [ s, -s,  s,   0.0, 0.0, 1.0,   1.0, 0.0],
        [ s,  s,  s,   0.0, 0.0, 1.0,   1.0, 1.0],
        [-s, -s,  s,   0.0, 0.0, 1.0,   0.0, 0.0],
        [ s,  s,  s,   0.0, 0.0, 1.0,   1.0, 1.0],
        [-s,  s,  s,   0.0, 0.0, 1.0,   0.0, 1.0],
        [ s, -s, -s,   0.0, 0.0, -1.0,   0.0, 0.0],
        [-s, -s, -s,   0.0, 0.0, -1.0,   1.0, 0.0],
        [-s,  s, -s,   0.0, 0.0, -1.0,   1.0, 1.0],
        [ s, -s, -s,   0.0, 0.0, -1.0,   0.0, 0.0],
        [-s,  s, -s,   0.0, 0.0, -1.0,   1.0, 1.0],
        [ s,  s, -s,   0.0, 0.0, -1.0,   0.0, 1.0],
        [-s,  s,  s,   0.0, 1.0, 0.0,   0.0, 0.0],
        [ s,  s,  s,   0.0, 1.0, 0.0,   1.0, 0.0],
        [ s,  s, -s,   0.0, 1.0, 0.0,   1.0, 1.0],
        [-s,  s,  s,   0.0, 1.0, 0.0,   0.0, 0.0],
        [ s,  s, -s,   0.0, 1.0, 0.0,   1.0, 1.0],
        [-s,  s, -s,   0.0, 1.0, 0.0,   0.0, 1.0],
        [-s, -s, -s,   0.0, -1.0, 0.0,   0.0, 0.0],
        [ s, -s, -s,   0.0, -1.0, 0.0,   1.0, 0.0],
        [ s, -s,  s,   0.0, -1.0, 0.0,   1.0, 1.0],
        [-s, -s, -s,   0.0, -1.0, 0.0,   0.0, 0.0],
        [ s, -s,  s,   0.0, -1.0, 0.0,   1.0, 1.0],
        [-s, -s,  s,   0.0, -1.0, 0.0,   0.0, 1.0],
        [ s, -s,  s,   1.0, 0.0, 0.0,   0.0, 0.0],
        [ s, -s, -s,   1.0, 0.0, 0.0,   1.0, 0.0],
        [ s,  s, -s,   1.0, 0.0, 0.0,   1.0, 1.0],
        [ s, -s,  s,   1.0, 0.0, 0.0,   0.0, 0.0],
        [ s,  s, -s,   1.0, 0.0, 0.0,   1.0, 1.0],
        [ s,  s,  s,   1.0, 0.0, 0.0,   0.0, 1.0],
        [-s, -s, -s,   -1.0, 0.0, 0.0,   0.0, 0.0],
        [-s, -s,  s,   -1.0, 0.0, 0.0,   1.0, 0.0],
        [-s,  s,  s,   -1.0, 0.0, 0.0,   1.0, 1.0],
        [-s, -s, -s,   -1.0, 0.0, 0.0,   0.0, 0.0],
        [-s,  s,  s,   -1.0, 0.0, 0.0,   1.0, 1.0],
        [-s,  s, -s,   -1.0, 0.0, 0.0,   0.0, 1.0],
    ]
    return createMeshFromVertices(vertices)


def createRampMesh():
    start_x, end_x = 0.0, 1.0
    start_y, end_y = 0.0, 1.0
    start_z, end_z = -0.5, 0.5
    ramp_normal_x = -0.70710678
    ramp_normal_y = 0.70710678
    ramp_normal_z = 0.0
    base_normal = (0.0, -1.0, 0.0)
    side_normal_left = (0.0, 0.0, -1.0)
    side_normal_right = (0.0, 0.0, 1.0)
    front_normal = (1.0, 0.0, 0.0)

    vertices = [
        [start_x, start_y, start_z,   ramp_normal_x, ramp_normal_y, ramp_normal_z,   0.0, 0.0],
        [end_x, end_y, start_z,       ramp_normal_x, ramp_normal_y, ramp_normal_z,   0.0, 1.0],
        [end_x, end_y, end_z,         ramp_normal_x, ramp_normal_y, ramp_normal_z,   1.0, 1.0],
        [start_x, start_y, start_z,   ramp_normal_x, ramp_normal_y, ramp_normal_z,   0.0, 0.0],
        [end_x, end_y, end_z,         ramp_normal_x, ramp_normal_y, ramp_normal_z,   1.0, 1.0],
        [start_x, start_y, end_z,     ramp_normal_x, ramp_normal_y, ramp_normal_z,   1.0, 0.0],
        [start_x, start_y, start_z,   base_normal[0], base_normal[1], base_normal[2],   0.0, 0.0],
        [start_x, start_y, end_z,     base_normal[0], base_normal[1], base_normal[2],   1.0, 0.0],
        [end_x, start_y, end_z,       base_normal[0], base_normal[1], base_normal[2],   1.0, 1.0],
        [start_x, start_y, start_z,   base_normal[0], base_normal[1], base_normal[2],   0.0, 0.0],
        [end_x, start_y, end_z,       base_normal[0], base_normal[1], base_normal[2],   1.0, 1.0],
        [end_x, start_y, start_z,     base_normal[0], base_normal[1], base_normal[2],   0.0, 1.0],
        [start_x, start_y, start_z,   side_normal_left[0], side_normal_left[1], side_normal_left[2],   0.0, 0.0],
        [end_x, start_y, start_z,     side_normal_left[0], side_normal_left[1], side_normal_left[2],   1.0, 0.0],
        [end_x, end_y, start_z,       side_normal_left[0], side_normal_left[1], side_normal_left[2],   1.0, 1.0],
        [start_x, start_y, end_z,     side_normal_right[0], side_normal_right[1], side_normal_right[2],   0.0, 0.0],
        [end_x, end_y, end_z,         side_normal_right[0], side_normal_right[1], side_normal_right[2],   1.0, 1.0],
        [end_x, start_y, end_z,       side_normal_right[0], side_normal_right[1], side_normal_right[2],   1.0, 0.0],
        [end_x, start_y, start_z,     front_normal[0], front_normal[1], front_normal[2],   0.0, 0.0],
        [end_x, end_y, start_z,       front_normal[0], front_normal[1], front_normal[2],   0.0, 1.0],
        [end_x, end_y, end_z,         front_normal[0], front_normal[1], front_normal[2],   1.0, 1.0],
        [end_x, start_y, start_z,     front_normal[0], front_normal[1], front_normal[2],   0.0, 0.0],
        [end_x, end_y, end_z,         front_normal[0], front_normal[1], front_normal[2],   1.0, 1.0],
        [end_x, start_y, end_z,       front_normal[0], front_normal[1], front_normal[2],   1.0, 0.0],
    ]
    return createMeshFromVertices(vertices)


def createSpriteMesh(size_x=None, size_y=None):
    w = config.OBJECT_SIZE_X if size_x is None else size_x
    h = config.OBJECT_SIZE_Y if size_y is None else size_y
    sprite_normal = (0.0, 0.0, 1.0)
    vertices = [
        [-w,  0.0, 0.0,   sprite_normal[0], sprite_normal[1], sprite_normal[2],   0.0, 0.0],
        [ w,  0.0, 0.0,   sprite_normal[0], sprite_normal[1], sprite_normal[2],   1.0, 0.0],
        [ w, h*2, 0.0,   sprite_normal[0], sprite_normal[1], sprite_normal[2],   1.0, 1.0],
        [-w,  0.0, 0.0,   sprite_normal[0], sprite_normal[1], sprite_normal[2],   0.0, 0.0],
        [ w, h*2, 0.0,   sprite_normal[0], sprite_normal[1], sprite_normal[2],   1.0, 1.0],
        [-w, h*2, 0.0,   sprite_normal[0], sprite_normal[1], sprite_normal[2],   0.0, 1.0],
    ]
    return createMeshFromVertices(vertices)


def createScreenQuad():
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
