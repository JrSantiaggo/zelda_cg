import random
from OpenGL.GL import *
import glm
import config
import resources
import world_config

platformMesh = 0
platformTexture = 0
rampMesh = 0
rampTexture = 0
tileTextures = {}
tileMap = []
rampData = {}
_rampDirectionsFromMatrix = {}
platforms = []
ramps = []


def createPropsMap():
    props_map = [
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, -5, 0, -5, 0, 0, -1, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -4, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, -5, -1, 0, 0, 0, 0, 0, -5, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, -5, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, -1, 0, 0, -1, 0, -5, 0, 0, 0, -5, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, -1, 0, 0, -5, 0, -5, 0, 0, -5, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -5, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, -5, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, -4, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, -4, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, -5, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, -5, 0, -5, 0, -5, 0, 0, 0, -5, -1, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

    ]
    
    return props_map


def createTileMap():
    map_numeric = [
[6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 1, 0, 0, 0, 6],
[6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 6],
[6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 6],
[6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 2, 2, 6, 6, 6, 6, 2, 2, 6, 6, 6, 6, 6, 2, 6, 6, 6, 6, 6, 2, 2, 2, 6, 6, 6, 6, 2, 2, 2, 2, 1, 1, 2, 2, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 6],
[6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 2, 2, 6, 2, 2, 6, 2, 2, 6, 2, 2, 2, 6, 2, 6, 2, 2, 2, 2, 2, 6, 6, 6, 2, 2, 2, 2, 1, 1, 1, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 6],
[6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 2, 2, 2, 2, 2, 6, 2, 2, 6, 2, 2, 2, 6, 2, 6, 2, 2, 2, 2, 6, 6, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 6, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 2, 1, 2, 2, 6],
[6, 2, 2, 2, 6, 6, 6, 6, 6, 6, 2, 2, 6, 6, 6, 6, 6, 6, 6, 2, 2, 6, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 2, 2, 6, 6, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 6],
[6, 2, 2, 2, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 2, 2, 2, 2, 2, 2, 1, 2, 1, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 6],
[6, 2, 2, 2, 6, 2, 2, 6, 6, 6, 6, 6, 2, 2, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 2, 2, 2, 2, 2, 1, 2, 2, 6, 2, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 6],
[6, 2, 2, 2, 6, 2, 2, 2, 2, 2, 2, 6, 2, 2, 6, 2, 2, 2, 2, 2, 6, 6, 6, 6, 6, 6, 2, 2, 2, 2, 2, 6, 6, 2, 2, 6, 2, 2, 2, 1, 1, 2, 9, 5, 5, 5, 5, 5, 5, 5, 5, 5, 8, 1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6],
[6, 2, 2, 2, 6, 6, 6, 6, 6, 2, 2, 6, 2, 2, 6, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 2, 2, 2, 6, 2, 2, 1, 1, 1, 2, 9, 5, 5, 5, 5, 5, 5, 5, 5, 5, 8, 2, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 2, 2, 6, 6, 2, 2, 2, 2, 2, 1, 2, 2, 2, 6],
[6, 2, 2, 2, 2, 2, 2, 2, 6, 2, 2, 6, 2, 2, 2, 6, 6, 2, 2, 6, 6, 2, 2, 1, 2, 1, 1, 1, 6, 2, 2, 2, 2, 2, 2, 6, 6, 2, 2, 2, 2, 2, 9, 5, 5, 5, 5, 5, 5, 5, 5, 5, 8, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 6],
[6, 2, 2, 2, 2, 2, 2, 2, 6, 2, 2, 6, 2, 2, 2, 2, 6, 2, 2, 6, 2, 1, 1, 2, 2, 6, 6, 6, 6, 2, 2, 1, 1, 1, 2, 2, 6, 2, 2, 2, 2, 2, 2, 7, 7, 7, 5, 5, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 1, 1, 2, 1, 2, 1, 1, 1, 2, 2, 2, 2, 1, 2, 1, 2, 6],
[6, 6, 6, 6, 6, 2, 2, 6, 6, 2, 2, 6, 2, 2, 6, 2, 6, 2, 2, 6, 2, 2, 2, 2, 6, 2, 2, 2, 1, 1, 2, 2, 6, 6, 6, 2, 1, 1, 2, 2, 2, 2, 7, 7, 7, 7, 5, 5, 7, 7, 7, 7, 7, 2, 2, 6, 6, 6, 6, 6, 2, 2, 2, 6, 2, 2, 1, 2, 1, 2, 1, 2, 2, 2, 2, 2, 2, 1, 2, 6],
[6, 2, 2, 2, 2, 2, 2, 6, 2, 2, 2, 6, 2, 2, 6, 2, 6, 2, 2, 2, 1, 2, 2, 2, 6, 6, 2, 2, 1, 1, 2, 6, 6, 2, 2, 2, 2, 1, 2, 2, 2, 7, 7, 7, 7, 7, 5, 5, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 1, 1, 1, 1, 2, 2, 1, 2, 2, 2, 2, 1, 2, 6],
[6, 2, 2, 2, 2, 2, 2, 6, 2, 2, 2, 6, 2, 2, 2, 2, 6, 2, 2, 2, 2, 1, 2, 1, 2, 6, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 11, 11, 11, 2, 7, 7, 7, 7, 7, 7, 5, 5, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1, 1, 2, 6],
[6, 2, 2, 2, 2, 2, 2, 6, 2, 2, 6, 6, 2, 2, 2, 2, 2, 2, 2, 6, 6, 1, 1, 1, 2, 2, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 5, 5, 2, 7, 7, 7, 5, 5, 5, 5, 5, 5, 5, 5, 5, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 2, 1, 2, 2, 2, 1, 1, 1, 2, 2, 6],
[6, 2, 2, 2, 2, 6, 6, 6, 2, 2, 6, 2, 2, 6, 2, 1, 1, 2, 6, 6, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 5, 5, 5, 7, 7, 7, 7, 5, 5, 5, 5, 5, 5, 5, 5, 5, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 2, 2, 1, 1, 1, 1, 2, 2, 2, 6],
[6, 1, 2, 2, 2, 6, 2, 2, 2, 2, 6, 2, 2, 6, 1, 2, 2, 6, 6, 1, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 5, 5, 5, 7, 7, 7, 7, 5, 5, 5, 5, 5, 5, 5, 5, 5, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 2, 2, 2, 2, 2, 6],
[6, 2, 2, 1, 2, 6, 2, 2, 6, 6, 6, 2, 2, 6, 2, 6, 6, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 2, 2, 6],
[6, 2, 1, 1, 2, 6, 2, 2, 6, 2, 2, 2, 2, 2, 2, 6, 6, 2, 1, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 6, 2, 6],
[6, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 6, 1, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 5, 5, 5, 7, 7, 7, 7, 5, 5, 5, 5, 5, 5, 5, 5, 5, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 6, 6, 6],
[6, 2, 2, 1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1, 2, 1, 1, 2, 2, 1, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 5, 5, 5, 7, 7, 7, 7, 5, 5, 5, 5, 5, 5, 5, 5, 5, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 11, 11, 11, 2, 2, 6, 6],
[6, 2, 2, 1, 1, 2, 2, 2, 2, 2, 1, 1, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 5, 5, 5, 7, 7, 7, 7, 5, 5, 5, 5, 5, 5, 5, 5, 5, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 5, 5, 5, 7, 7, 7, 7],
[6, 2, 2, 2, 1, 2, 1, 2, 2, 1, 2, 1, 1, 1, 2, 2, 1, 1, 1, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 5, 5, 5, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 5, 5, 5, 7, 7, 7, 7],
[6, 2, 2, 2, 1, 1, 2, 2, 1, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 5, 5, 5, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 5, 5, 5, 7, 7, 7, 7],
[6, 2, 1, 2, 2, 1, 2, 2, 1, 2, 1, 1, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 10, 10, 10, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 5, 5, 5, 7, 7, 7, 7],
[6, 2, 2, 1, 2, 1, 1, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 5, 5, 5, 7, 7, 7, 7],
[6, 2, 2, 1, 2, 2, 1, 2, 1, 1, 2, 2, 1, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 5, 5, 5, 7, 7, 7, 7],
[6, 2, 2, 1, 1, 2, 1, 1, 1, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 5, 5, 2, 7, 7, 7],
[6, 2, 2, 2, 2, 2, 1, 1, 2, 2, 1, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 10, 10, 10, 2, 2, 2, 6],
[6, 2, 1, 2, 1, 2, 1, 1, 2, 2, 1, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 6],
[6, 1, 2, 2, 2, 1, 1, 1, 2, 2, 1, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 1, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 6],
[6, 2, 2, 1, 2, 1, 1, 2, 2, 1, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 9, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 8, 2, 1, 2, 1, 1, 1, 2, 1, 2, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 2, 1, 2, 2, 2, 6],
[6, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 9, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 8, 1, 1, 2, 2, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 2, 2, 2, 6],
[6, 2, 2, 1, 1, 1, 2, 2, 1, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 9, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 8, 1, 2, 2, 1, 2, 2, 1, 1, 2, 2, 1, 2, 1, 2, 2, 1, 2, 2, 1, 2, 2, 2, 2, 2, 6],
[6, 2, 2, 2, 1, 1, 2, 2, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6],
[6, 2, 2, 1, 2, 1, 2, 2, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 1, 1, 1, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6],
[6, 2, 2, 2, 2, 2, 2, 2, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6],
[6, 0, 0, 0, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],

    ]

    global _rampDirectionsFromMatrix
    depth = len(map_numeric)
    width = len(map_numeric[0]) if depth > 0 else 0
    
    map_data = []
    ramp_directions_from_matrix = {}

    for z in range(depth):
        row = []
        for x in range(width):
            tile_id = map_numeric[z][x]
            tile_type = world_config.tileIdToType(tile_id)
            if tile_id in world_config.TILE_ID_TO_RAMP_DIRECTION:
                direction = world_config.TILE_ID_TO_RAMP_DIRECTION[tile_id]
                ramp_directions_from_matrix[(x, z)] = direction
            if tile_type is None:
                tile_type = world_config.TILE_TYPE_FLOOR
            row.append(tile_type)
        map_data.append(row)

    _rampDirectionsFromMatrix = ramp_directions_from_matrix
    return map_data


def convertTileMapToGeometry(tileMap, startX=0, startZ=0):
    global rampData
    platforms_list = []
    ramps_list = []
    
    depth = len(tileMap)
    if depth == 0:
        return platforms_list, ramps_list
    
    width = len(tileMap[0])

    for z in range(depth):
        for x in range(width):
            tile_type = tileMap[z][x]
            tile_def = world_config.getTileDefinition(tile_type)
            if not tile_def:
                continue

            world_x = startX + x
            world_z = startZ + z

            if tile_type == world_config.TILE_TYPE_RAMP:
                ramp_info = rampData.get((x, z))
                if ramp_info:
                    start_height = ramp_info['start_height']
                    end_height = ramp_info['end_height']
                    direction = ramp_info['direction']
                else:
                    start_height = tile_def.get('default_start_height', 0.0)
                    end_height = tile_def.get('default_end_height', world_config.BLOCK_HEIGHT_FULL)
                    direction_from_matrix = _rampDirectionsFromMatrix.get((x, z))
                    if direction_from_matrix:
                        direction = direction_from_matrix
                    else:
                        direction = tile_def.get('default_direction', world_config.RAMP_DIRECTION_NORTH)
                ramps_list.append({
                    'pos': (world_x, world_config.GROUND_LEVEL, world_z),
                    'start_height': start_height,
                    'end_height': end_height,
                    'direction': direction,
                    'tile_type': tile_type,
                })
                continue

            tile_height = tile_def['height']
            scale_x = tile_def['scale_x']
            scale_z = tile_def['scale_z']
            if tile_type == world_config.TILE_TYPE_FLOOR:
                y_pos = world_config.GROUND_LEVEL + (tile_height / 2.0)
            else:
                y_pos = world_config.GROUND_LEVEL + (tile_height / 2.0)
            platforms_list.append({
                'pos': (world_x, y_pos, world_z),
                'scale': (scale_x, tile_height, scale_z),
                'tile_type': tile_type,
            })
    
    return platforms_list, ramps_list


def getTileAt(world_x, world_z, map_offset_x=-20, map_offset_z=-20):
    map_x = int(world_x - map_offset_x)
    map_z = int(world_z - map_offset_z)
    if map_z < 0 or map_z >= len(tileMap) or map_x < 0 or map_x >= len(tileMap[0]):
        return None
    
    return tileMap[map_z][map_x]


def getTilePropertiesAt(world_x, world_z, map_offset_x=-20, map_offset_z=-20):
    tile_type = getTileAt(world_x, world_z, map_offset_x, map_offset_z)
    if tile_type is None:
        return None
    
    return world_config.getTileDefinition(tile_type)


def is_valid_enemy_spawn(world_x, world_z, map_offset_x=-20, map_offset_z=-20):
    tile_type = getTileAt(world_x, world_z, map_offset_x, map_offset_z)
    if tile_type is None:
        return False
    tile_def = world_config.getTileDefinition(tile_type)
    if not tile_def:
        return False
    if tile_def.get('is_liquid', False):
        return False
    if tile_type == world_config.TILE_TYPE_BUSH_BLOCK:
        return False
    return True


def get_tree_world_positions(map_offset_x=-20, map_offset_z=-20):
    pm = createPropsMap()
    out = []
    for z in range(len(pm)):
        row = pm[z]
        for x in range(len(row)):
            if row[x] in (-1, -5):
                out.append((map_offset_x + x, map_offset_z + z))
    return out


def get_enemy_spawn_config(map_offset_x=-20, map_offset_z=-20):
    tree_set = set(get_tree_world_positions(map_offset_x, map_offset_z))
    start, goal = (-18.0, 18.0), (18.0, -19.0)
    candidates = []
    for x in range(-20, 60):
        for z in range(-20, 20):
            if (x, z) in tree_set:
                continue
            if not is_valid_enemy_spawn(x, z, map_offset_x, map_offset_z):
                continue
            if (x - start[0]) ** 2 + (z - start[1]) ** 2 < 9:
                continue  # dist < 3 do início
            if (x - goal[0]) ** 2 + (z - goal[1]) ** 2 < 4:
                continue  # dist < 2 da meta
            candidates.append((x, z))
    random.shuffle(candidates)
    chosen = []
    min_dist_sq = 16
    for (x, z) in candidates:
        if len(chosen) >= 36:
            break
        if any((x - cx) ** 2 + (z - cz) ** 2 < min_dist_sq for (cx, cz) in chosen):
            continue
        chosen.append((x, z))
    if len(chosen) < 36:
        min_dist_sq = 9
        for (x, z) in candidates:
            if len(chosen) >= 36:
                break
            if (x, z) in chosen:
                continue
            if any((x - cx) ** 2 + (z - cz) ** 2 < min_dist_sq for (cx, cz) in chosen):
                continue
            chosen.append((x, z))
    melee, archer = [], []
    for i, p in enumerate(chosen):
        if i % 3 == 2:
            archer.append(p)
        else:
            melee.append(p)
    return {"melee": melee, "archer": archer}


def setRampData(map_x, map_z, start_height, end_height, direction):
    global rampData
    rampData[(map_x, map_z)] = {
        'start_height': start_height,
        'end_height': end_height,
        'direction': direction,
    }


def getRampData(world_x, world_z, map_offset_x=-20, map_offset_z=-20):
    """
    Obtém propriedades de uma rampa na posição do mundo especificada.
    
    Args:
        world_x: Posição X no mundo
        world_z: Posição Z no mundo
        map_offset_x: Offset X do mapa (default: -20 para mapa 40x40 centrado)
        map_offset_z: Offset Z do mapa (default: -20 para mapa 40x40 centrado)
    
    Returns:
        Dicionário com propriedades da rampa (start_height, end_height, direction) ou None
    """
    # Converter coordenada do mundo para índice da matriz
    map_x = int(world_x - map_offset_x)
    map_z = int(world_z - map_offset_z)
    
    return rampData.get((map_x, map_z), None)


def getRampHeightAt(world_x, world_z, map_offset_x=-20, map_offset_z=-20):
    """
    Calcula a altura Y baseada na posição do jogador sobre uma rampa.
    A altura varia gradualmente de start_height para end_height baseado na posição dentro do tile.
    
    Args:
        world_x: Posição X no mundo
        world_z: Posição Z no mundo
        map_offset_x: Offset X do mapa (default: -20 para mapa 40x40 centrado)
        map_offset_z: Offset Z do mapa (default: -20 para mapa 40x40 centrado)
    
    Returns:
        Altura Y calculada (float) ou None se não estiver sobre uma rampa
    """
    # Converter coordenada do mundo para índice da matriz
    map_x = int(world_x - map_offset_x)
    map_z = int(world_z - map_offset_z)
    
    # Verificar limites do mapa
    if map_z < 0 or map_z >= len(tileMap) or map_x < 0 or map_x >= len(tileMap[0]):
        return None
    
    # Verificar se há uma rampa nesta posição
    tile_type = tileMap[map_z][map_x]
    if tile_type != world_config.TILE_TYPE_RAMP:
        return None
    
    # Obter dados da rampa (específicos ou padrão)
    ramp_info = rampData.get((map_x, map_z))
    if ramp_info:
        # Rampa com propriedades definidas explicitamente via setRampData()
        start_height = ramp_info['start_height']
        end_height = ramp_info['end_height']
        direction = ramp_info['direction']
    else:
        # Rampa sem dados específicos - usar valores padrão de TILE_TYPE_RAMP
        tile_def = world_config.getTileDefinition(world_config.TILE_TYPE_RAMP)
        if not tile_def:
            return None
        
        start_height = tile_def.get('default_start_height', 0.0)
        end_height = tile_def.get('default_end_height', world_config.BLOCK_HEIGHT_FULL)
        
        # Verificar se a direção foi definida na matriz (via IDs 8, 9, 10, 11)
        direction_from_matrix = _rampDirectionsFromMatrix.get((map_x, map_z))
        if direction_from_matrix:
            direction = direction_from_matrix
        else:
            direction = tile_def.get('default_direction', world_config.RAMP_DIRECTION_NORTH)
    
    # Calcular posição relativa dentro do tile (0.0 a 1.0)
    # Centro do tile em coordenadas do mundo
    tile_center_x = map_x + map_offset_x
    tile_center_z = map_z + map_offset_z
    
    # Posição relativa do jogador dentro do tile (-0.5 a 0.5)
    rel_x = world_x - tile_center_x
    rel_z = world_z - tile_center_z
    
    # Normalizar para 0.0 a 1.0 baseado na direção da rampa
    # A rampa interpola ao longo da direção de subida
    t = 0.0  # Parâmetro de interpolação (0.0 = início, 1.0 = fim)
    
    if direction == world_config.RAMP_DIRECTION_NORTH:
        # Rampa Norte: visualmente sobe da direita (X+) para esquerda (X-)
        # Após rotação 180°, geometria x=0 local (baixo) fica no lado direito mundo (X+), x=1 local (alto) fica no lado esquerdo mundo (X-)
        
        t = 0.5 - rel_x 
        t = max(0.0, min(1.0, t))  
    
    elif direction == world_config.RAMP_DIRECTION_SOUTH:
      
        t = 0.5 + rel_x  
        t = max(0.0, min(1.0, t))  
    
    elif direction == world_config.RAMP_DIRECTION_EAST:
   
        t = 0.5 - rel_z  
        t = max(0.0, min(1.0, t)) 
    
    elif direction == world_config.RAMP_DIRECTION_WEST:

        t = 0.5 + rel_z 
        t = max(0.0, min(1.0, t))  
    
    # Interpolar linearmente entre start_height e end_height
    height = start_height + (end_height - start_height) * t
    
    return height


def getMapSize():
    """
    Retorna o tamanho da matriz do mapa.
    
    Returns:
        Tupla (width, depth) - largura e profundidade do mapa em tiles
    """
    if len(tileMap) == 0:
        return (0, 0)
    return (len(tileMap[0]), len(tileMap))


def checkTileCollision(world_x, world_z, player_radius=0.5, player_y=None, map_offset_x=-20, map_offset_z=-20):
    map_x = int(world_x - map_offset_x)
    map_z = int(world_z - map_offset_z)
    
    if map_z < 0 or map_z >= len(tileMap) or map_x < 0 or map_x >= len(tileMap[0]):
        return True
    
    tile_type = tileMap[map_z][map_x]
    
    if tile_type:
        tile_def = world_config.getTileDefinition(tile_type)
        if tile_def and tile_def.get('is_liquid', False):
            return True
        if tile_def and tile_def.get('is_solid', False):
            if player_y is not None:
                tile_height = tile_def.get('height', 0.0)
                tile_top = world_config.GROUND_LEVEL + tile_height
                if player_y >= tile_top - 0.1:
                    return False
            return True
    
    if player_radius > 0.5:
        adjacent_tiles = [
            (map_x - 1, map_z),
            (map_x + 1, map_z),
            (map_x, map_z - 1),
            (map_x, map_z + 1),
        ]
        
        for adj_x, adj_z in adjacent_tiles:
            if 0 <= adj_z < len(tileMap) and 0 <= adj_x < len(tileMap[0]):
                adj_tile_type = tileMap[adj_z][adj_x]
                if adj_tile_type:
                    adj_tile_def = world_config.getTileDefinition(adj_tile_type)
                    adj_world_x = adj_x + map_offset_x
                    adj_world_z = adj_z + map_offset_z
                    dist_x = abs(world_x - adj_world_x)
                    dist_z = abs(world_z - adj_world_z)
                    overlaps = dist_x < (player_radius + 0.5) and dist_z < (player_radius + 0.5)
                    if overlaps and adj_tile_def and adj_tile_def.get('is_liquid', False):
                        return True
                    if adj_tile_def and adj_tile_def.get('is_solid', False) and overlaps:
                        return True
    
    return False


def init(geometry_module):
    """
    Inicializa recursos do mapa (malhas e texturas).
    Cria a matriz lógica do mapa e converte para geometria.
    
    Args:
        geometry_module: Módulo geometry para criar malhas
    """
    global platformMesh, platformTexture, rampMesh, rampTexture, platforms, ramps, tileMap, tileTextures, rampData
    import os
    
    here = os.path.dirname(os.path.abspath(__file__))
    
    # Criar malhas
    platformMesh = geometry_module.createCubeMesh()
    rampMesh = geometry_module.createRampMesh()
    
    # Carregar texturas padrão
    platformTexture = resources.loadTexture(os.path.join(here, config.PLATFORM_TEXTURE))
    rampTexture = resources.loadTexture(os.path.join(here, config.PLATFORM_TEXTURE))
    
    # Carregar texturas específicas por tipo de tile
    tileTextures = {}
    # Percorrer todos os tipos de tile e carregar texturas quando especificadas
    for tile_type, tile_def in world_config.TILE_DEFINITIONS.items():
        texture_path = tile_def.get('texture')
        if texture_path:
            full_path = os.path.join(here, texture_path)
            if os.path.exists(full_path):
                tileTextures[tile_type] = resources.loadTexture(full_path)
    
    # ===== INICIALIZAR DADOS DE RAMPAS =====

    rampData = {}
    
    # ===== CRIAR MATRIZ LÓGICA DO MAPA =====

    tileMap = createTileMap()
    

    for z in range(20, 26):
        for x in range(2, 38):
            direction_from_matrix = _rampDirectionsFromMatrix.get((x, z))
            if direction_from_matrix:
                direction = direction_from_matrix
            else:
                direction = world_config.RAMP_DIRECTION_EAST
            setRampData(x, z, 0.0, world_config.BLOCK_HEIGHT_FULL, direction)
    
    map_offset_x = -20
    map_offset_z = -20
    
    platforms, ramps = convertTileMapToGeometry(tileMap, map_offset_x, map_offset_z)
    
    import props
    
    props_map = createPropsMap()
    map_offset_x = -20
    map_offset_z = -20
    
    def getTileTopHeight(world_x, world_z):
        tile_props = getTilePropertiesAt(world_x, world_z, map_offset_x, map_offset_z)
        if tile_props:
            tile_height = tile_props.get('height', world_config.FLOOR_TILE_HEIGHT)
            return world_config.GROUND_LEVEL + tile_height
        return world_config.GROUND_LEVEL + world_config.FLOOR_TILE_HEIGHT
    
    for z in range(len(props_map)):
        for x in range(len(props_map[z]) if len(props_map) > 0 else 0):
            prop_id = props_map[z][x]
            
            if prop_id == 0 or prop_id == world_config.PROP_ID_EMPTY:
                continue
            
            prop_type = world_config.propIdToType(prop_id)
            if prop_type is None:
                continue
            
            prop_def = world_config.getPropDefinition(prop_type)
            if prop_def is None:
                print(f"AVISO: Definição não encontrada para prop '{prop_type}'")
                continue
            
            # Calcular posição no mundo
            world_x = map_offset_x + x
            world_z = map_offset_z + z
            
            tile_top = getTileTopHeight(world_x, world_z)
            y_offset = prop_def.get('y_offset', 0.0)
            scale = prop_def.get('scale', (1.0, 1.0, 1.0))
            # Ajustar offset pela escala
            adjusted_y_offset = y_offset * scale[1] if y_offset != 0 else 0.0
            prop_y = tile_top + adjusted_y_offset
            
            # Obter propriedades do prop
            model_path = prop_def.get('model')
            texture_path = prop_def.get('texture')
            rotation = prop_def.get('rotation', 0.0)
            
            # Adicionar prop
            props.addProp(
                model_path,
                texture_path,
                (world_x, prop_y, world_z),
                scale,
                rotation
            )


def renderPlatforms(modelMatrix_loc):
    """
    Renderiza todas as plataformas do cenário.
    Usa textura específica de cada tile se disponível, senão usa textura padrão.
    """
    glBindVertexArray(platformMesh[0])
    
    for platform in platforms:
        pos = platform['pos']
        scale = platform['scale']
        tile_type = platform.get('tile_type')
        
        # Selecionar textura: específica do tile ou padrão
        texture = tileTextures.get(tile_type, platformTexture) if tile_type else platformTexture
        glBindTexture(GL_TEXTURE_2D, texture)
        
        modelMatrix = glm.mat4(1.0)
        modelMatrix = glm.translate(modelMatrix, glm.vec3(pos[0], pos[1], pos[2]))
        modelMatrix = glm.scale(modelMatrix, glm.vec3(scale[0], scale[1], scale[2]))
        
        glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(modelMatrix))
        glDrawArrays(GL_TRIANGLES, 0, platformMesh[1])


def renderRamps(modelMatrix_loc):
    glBindVertexArray(rampMesh[0])
    
    for ramp in ramps:
        pos = ramp['pos']
        start_height = ramp.get('start_height', 0.0)
        end_height = ramp.get('end_height', 1.0)
        direction = ramp.get('direction', world_config.RAMP_DIRECTION_NORTH)
        tile_type = ramp.get('tile_type', world_config.TILE_TYPE_RAMP)
        
        texture = tileTextures.get(tile_type, rampTexture) if tile_type else rampTexture
        glBindTexture(GL_TEXTURE_2D, texture)
        
        height_diff = end_height - start_height
        
        angle = 0.0
        if direction == world_config.RAMP_DIRECTION_NORTH:
            angle = 180.0
        elif direction == world_config.RAMP_DIRECTION_SOUTH:
            angle = 0.0
        elif direction == world_config.RAMP_DIRECTION_EAST:
            angle = 90.0
        elif direction == world_config.RAMP_DIRECTION_WEST:
            angle = -90.0
        scale_length = world_config.TILE_SIZE   # Comprimento da rampa (1 tile)
        scale_height = abs(height_diff) if abs(height_diff) > 0.0 else 1.0  # Altura da inclinação
        scale_width = world_config.TILE_SIZE
        
        world_x = pos[0]
        world_z = pos[2]
        base_y = world_config.GROUND_LEVEL
        
        modelMatrix = glm.mat4(1.0)
        modelMatrix = glm.translate(modelMatrix, glm.vec3(world_x, base_y, world_z))
        modelMatrix = glm.rotate(modelMatrix, glm.radians(angle), glm.vec3(0.0, 1.0, 0.0))
        modelMatrix = glm.translate(modelMatrix, glm.vec3(-0.5, start_height, 0.0))
        modelMatrix = glm.scale(modelMatrix, glm.vec3(scale_length, scale_height, scale_width))
        
        glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(modelMatrix))
        glDrawArrays(GL_TRIANGLES, 0, rampMesh[1])
