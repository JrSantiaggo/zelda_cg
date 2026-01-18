"""
Módulo do mapa: lógica e renderização do cenário (plataformas, rampas, tiles)
"""
import random
from OpenGL.GL import *
import glm
import config
import resources
import world_config

# Variáveis globais do mapa
platformMesh = 0
platformTexture = 0
rampMesh = 0
rampTexture = 0

# Texturas específicas por tipo de tile
tileTextures = {}  # {tile_type: texture_id}

# Matriz lógica do mapa (cada célula = 1 tile)
# mapa[z][x] onde z é a linha (profundidade) e x é a coluna (largura)
tileMap = []

# Dados de rampas: mapeia (map_x, map_z) para propriedades da rampa
# Cada rampa possui: altura_inicial, altura_final, direção (N/S/E/W)
rampData = {}  # {(map_x, map_z): {'start_height': float, 'end_height': float, 'direction': str}}

# Direções de rampas definidas diretamente na matriz (via IDs 8, 9, 10, 11)
# Armazenado temporariamente durante createTileMap() para uso em convertTileMapToGeometry()
_rampDirectionsFromMatrix = {}

# Cache de geometria renderizada (convertida da matriz)
platforms = []
ramps = []


def createPropsMap():
    """
    Cria a matriz lógica de props (objetos 3D) no mapa.
    Cada célula da matriz pode conter um ID de prop ou 0 (vazio).
    
    Legenda numérica:
        0 = vazio (sem prop)
        -1 = TREE (árvore)
        -2 = ROCK (pedra)
        -3 = BUSH (arbusto)
        -4 = MEDIEVAL_HOUSE (casa medieval; maior, colocar longe das árvores)
        -5 = TREE_LOW (árvore baixa, treeLow)
        # Adicione mais IDs conforme necessário
    
    Retorna:
        Lista 2D (matriz) com IDs de props (inteiros)
    """
    # Matriz numérica de props (40x40 - mesmo tamanho do mapa de tiles)
    # Mapa 40x40: de (-20, -20) a (19, 19) no mundo
    # Apenas 2 árvores no mapa (mantendo padrão original: uma no topo, uma embaixo)
    props_map = [
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, -5, 0, 0, 0, 0],
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
    """
    Cria a matriz lógica do mapa usando representação numérica visual.
    Cada célula da matriz representa exatamente 1 tile (1 unidade).
    
    Legenda numérica (apenas IDs em uso no mapa):
        0 = vazio (fallback → FLOOR)
        1 = FLOOR (chão)
        5 = PLATFORM (plataforma)
        6 = BUSH_BLOCK (arbusto; labirintos)
        7 = WATER (água; is_liquid, não atravessável)
        8 = RAMP N, 9 = RAMP S, 10 = RAMP E, 11 = RAMP W (rampas; direção na matriz)
    
    Retorna:
        Lista 2D (matriz) com tipos de tiles (strings)
    """
    # Mapa A→B: início (1,38) canto inf.esq. → meta (38,1) canto sup.dir. | 1=chão 5=plataforma 6=arbusto 7=água 8=N 9=S 10=E 11=W
    map_numeric = [
        # z=0-2: B (meta) — plataforma canto superior direito
[6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 0, 0, 0, 6],
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
[6, 2, 2, 2, 1, 1, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6],
[6, 2, 2, 1, 2, 1, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 1, 1, 1, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6],
[6, 2, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 7, 7, 7, 7, 7, 7, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6],
[6, 0, 0, 0, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],

    ]
    
    # Converter matriz numérica para matriz de tipos de tile
    # Também armazenar direções de rampas definidas na matriz (8, 9, 10, 11)
    global _rampDirectionsFromMatrix
    depth = len(map_numeric)
    width = len(map_numeric[0]) if depth > 0 else 0
    
    map_data = []
    ramp_directions_from_matrix = {}  # {(map_x, map_z): direction}
    
    for z in range(depth):
        row = []
        for x in range(width):
            tile_id = map_numeric[z][x]
            tile_type = world_config.tileIdToType(tile_id)
            
            # Se for uma rampa com direção definida na matriz (8-11)
            if tile_id in world_config.TILE_ID_TO_RAMP_DIRECTION:
                direction = world_config.TILE_ID_TO_RAMP_DIRECTION[tile_id]
                ramp_directions_from_matrix[(x, z)] = direction
            
            # Se tile_id é 0 (vazio) ou tipo inválido, usar FLOOR como padrão
            if tile_type is None:
                tile_type = world_config.TILE_TYPE_FLOOR
            row.append(tile_type)
        map_data.append(row)
    
    # Armazenar direções de rampas da matriz globalmente para uso em convertTileMapToGeometry
    _rampDirectionsFromMatrix = ramp_directions_from_matrix
    
    return map_data


def convertTileMapToGeometry(tileMap, startX=0, startZ=0):
    """
    Converte a matriz lógica do mapa em geometria para renderização.
    Tiles ficam exatamente encostados (sem gaps), usando TILE_SIZE diretamente.
    Rampas são tratadas como tiles especiais com propriedades (altura inicial/final, direção).
    
    Args:
        tileMap: Matriz 2D com tipos de tiles
        startX: Offset X inicial (default: 0, centro na origem)
        startZ: Offset Z inicial (default: 0, centro na origem)
    
    Returns:
        Tupla (platforms_list, ramps_list) com geometria convertida
    """
    global rampData
    platforms_list = []
    ramps_list = []
    
    depth = len(tileMap)
    if depth == 0:
        return platforms_list, ramps_list
    
    width = len(tileMap[0])
    
    # Converter cada célula da matriz em geometria
    # tileMap[z][x] onde z é a linha (profundidade) e x é a coluna (largura)
    for z in range(depth):
        for x in range(width):
            tile_type = tileMap[z][x]
            
            # Obter definição do tile
            tile_def = world_config.getTileDefinition(tile_type)
            if not tile_def:
                continue  # Tipo de tile inválido, pular
            
            # Posição no mundo: centro do tile
            # Cada célula da matriz representa exatamente 1 tile (1 unidade)
            # Tiles ficam encostados (sem gaps)
            world_x = startX + x
            world_z = startZ + z  # Z aumenta com a profundidade (linha) na matriz
            
            # Tratamento especial para rampas
            if tile_type == world_config.TILE_TYPE_RAMP:
                # Verificar se há dados de rampa específicos para esta posição
                ramp_info = rampData.get((x, z))
                if ramp_info:
                    # Rampa com propriedades definidas explicitamente via setRampData()
                    start_height = ramp_info['start_height']
                    end_height = ramp_info['end_height']
                    direction = ramp_info['direction']
                else:
                    # Rampa sem dados específicos - usar valores padrão de TILE_TYPE_RAMP
                    start_height = tile_def.get('default_start_height', 0.0)
                    end_height = tile_def.get('default_end_height', world_config.BLOCK_HEIGHT_FULL)
                    
                    # Verificar se a direção foi definida na matriz (via IDs 8, 9, 10, 11)
                    direction_from_matrix = _rampDirectionsFromMatrix.get((x, z))
                    if direction_from_matrix:
                        # Usar direção da matriz
                        direction = direction_from_matrix
                    else:
                        # Usar direção padrão de TILE_TYPE_RAMP
                        direction = tile_def.get('default_direction', world_config.RAMP_DIRECTION_NORTH)
                
                # Criar geometria de rampa (sempre cria rampa, não plataforma)
                ramps_list.append({
                    'pos': (world_x, world_config.GROUND_LEVEL, world_z),
                    'start_height': start_height,
                    'end_height': end_height,
                    'direction': direction,
                    'tile_type': tile_type,
                })
                continue
            
            # Altura e escala do tile
            tile_height = tile_def['height']
            scale_x = tile_def['scale_x']
            scale_z = tile_def['scale_z']
            
            # Posição Y: centro do tile baseado na altura
            # Para tiles de chão, usar GROUND_LEVEL como base e adicionar metade da altura
            if tile_type == world_config.TILE_TYPE_FLOOR:
                y_pos = world_config.GROUND_LEVEL + (tile_height / 2.0)
            else:
                # Para outros tiles, centro do tile baseado na altura (acima do chão)
                y_pos = world_config.GROUND_LEVEL + (tile_height / 2.0)
            
            # Criar geometria para renderização
            platforms_list.append({
                'pos': (world_x, y_pos, world_z),
                'scale': (scale_x, tile_height, scale_z),
                'tile_type': tile_type,  # Guardar tipo para possível uso futuro (texturas, etc)
            })
    
    return platforms_list, ramps_list


def getTileAt(world_x, world_z, map_offset_x=-20, map_offset_z=-20):
    """
    Obtém o tipo de tile na posição do mundo especificada.
    
    Args:
        world_x: Posição X no mundo
        world_z: Posição Z no mundo
        map_offset_x: Offset X do mapa (default: -20 para mapa 40x40 centrado)
        map_offset_z: Offset Z do mapa (default: -20 para mapa 40x40 centrado)
    
    Returns:
        Tipo do tile (string) ou None se posição fora do mapa
    """
    # Converter coordenada do mundo para índice da matriz
    map_x = int(world_x - map_offset_x)
    map_z = int(world_z - map_offset_z)
    
    # Verificar limites
    if map_z < 0 or map_z >= len(tileMap) or map_x < 0 or map_x >= len(tileMap[0]):
        return None
    
    return tileMap[map_z][map_x]


def getTilePropertiesAt(world_x, world_z, map_offset_x=-20, map_offset_z=-20):
    """
    Obtém as propriedades completas do tile na posição do mundo especificada.
    
    Args:
        world_x: Posição X no mundo
        world_z: Posição Z no mundo
        map_offset_x: Offset X do mapa (default: -20 para mapa 40x40 centrado)
        map_offset_z: Offset Z do mapa (default: -20 para mapa 40x40 centrado)
    
    Returns:
        Dicionário com propriedades do tile (height, texture, is_solid, etc) ou None
    """
    tile_type = getTileAt(world_x, world_z, map_offset_x, map_offset_z)
    if tile_type is None:
        return None
    
    return world_config.getTileDefinition(tile_type)


def is_valid_enemy_spawn(world_x, world_z, map_offset_x=-20, map_offset_z=-20):
    """
    Verifica se a posição (world_x, world_z) é válida para spawn de inimigo:
    apenas em plataformas ou tiles normais (floor, ground, platform, ramp).
    Nunca em água, bush_block ou fora do mapa.
    """
    tile_type = getTileAt(world_x, world_z, map_offset_x, map_offset_z)
    if tile_type is None:
        return False
    tile_def = world_config.getTileDefinition(tile_type)
    if not tile_def:
        return False
    if tile_def.get('is_liquid', False):
        return False  # água
    if tile_type == world_config.TILE_TYPE_BUSH_BLOCK:
        return False  # arbusto/bloco labirinto
    return True


def get_tree_world_positions(map_offset_x=-20, map_offset_z=-20):
    """
    Retorna lista de (world_x, world_z) onde há árvores (TREE ou TREE_LOW).
    Usado para spawn de inimigos principalmente ao redor de árvores.
    """
    pm = createPropsMap()
    out = []
    for z in range(len(pm)):
        row = pm[z]
        for x in range(len(row)):
            if row[x] in (-1, -5):  # PROP_ID_TREE, PROP_ID_TREE_LOW
                out.append((map_offset_x + x, map_offset_z + z))
    return out


def get_enemy_spawn_config(map_offset_x=-20, map_offset_z=-20):
    """
    Retorna posições de spawn para inimigos (melee e arqueiros).
    - Apenas em tiles válidos (plataforma, floor, ground, ramp); nunca em água.
    - Distribuídos por todo o mapa (distância mínima entre spawns para evitar aglomeração).
    - Não altera o mapa; apenas a lista de spawns.
    Retorno: {"melee": [(x,z), ...], "archer": [(x,z), ...]}
    """
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
    # Escolher spawns com distância mínima entre eles para distribuir por todo o mapa
    chosen = []
    min_dist_sq = 16   # dist mínima 4 tiles
    for (x, z) in candidates:
        if len(chosen) >= 36:
            break
        if any((x - cx) ** 2 + (z - cz) ** 2 < min_dist_sq for (cx, cz) in chosen):
            continue
        chosen.append((x, z))
    # Se faltar, relaxar para dist mínima 3
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
    # Variedade: ~2/3 melee, ~1/3 arqueiro; intercalados
    melee, archer = [], []
    for i, p in enumerate(chosen):
        if i % 3 == 2:
            archer.append(p)
        else:
            melee.append(p)
    return {"melee": melee, "archer": archer}


def setRampData(map_x, map_z, start_height, end_height, direction):
    """
    Define propriedades de uma rampa na posição (map_x, map_z) da matriz.
    
    Args:
        map_x: Posição X na matriz (coluna)
        map_z: Posição Z na matriz (linha)
        start_height: Altura inicial da rampa (em unidades)
        end_height: Altura final da rampa (em unidades)
        direction: Direção de subida ('N', 'S', 'E' ou 'W')
    """
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
        # rel_x positivo (direita/X+) = início baixo (0.0), rel_x negativo (esquerda/X-) = fim alto (1.0)
        t = 0.5 - rel_x  # Mapear de [-0.5, 0.5] para [1.0, 0.0] invertido
        t = max(0.0, min(1.0, t))  # Clamp entre 0.0 e 1.0
    
    elif direction == world_config.RAMP_DIRECTION_SOUTH:
        # Rampa Sul: visualmente sobe da esquerda (X-) para direita (X+)
        # Após rotação 0°, geometria x=0 local (baixo) fica no lado esquerdo mundo (X-), x=1 local (alto) fica no lado direito mundo (X+)
        # rel_x negativo (esquerda/X-) = início baixo (0.0), rel_x positivo (direita/X+) = fim alto (1.0)
        t = 0.5 + rel_x  # Mapear de [-0.5, 0.5] para [0.0, 1.0]
        t = max(0.0, min(1.0, t))  # Clamp entre 0.0 e 1.0
    
    elif direction == world_config.RAMP_DIRECTION_EAST:
        # Rampa Leste: visualmente sobe de trás (Z+) para frente (Z-)
        # Após rotação 90°, geometria x=0 local (baixo) fica em Z+ mundo, x=1 local (alto) fica em Z- mundo
        # rel_z positivo (trás/Z+) = início baixo (0.0), rel_z negativo (frente/Z-) = fim alto (1.0)
        t = 0.5 - rel_z  # Mapear de [-0.5, 0.5] para [1.0, 0.0] invertido
        t = max(0.0, min(1.0, t))  # Clamp entre 0.0 e 1.0
    
    elif direction == world_config.RAMP_DIRECTION_WEST:
        # Rampa Oeste: visualmente sobe da frente (Z-) para trás (Z+)
        # Após rotação -90°, geometria x=0 local (baixo) fica em Z- mundo, x=1 local (alto) fica em Z+ mundo
        # rel_z negativo (frente/Z-) = início baixo (0.0), rel_z positivo (trás/Z+) = fim alto (1.0)
        t = 0.5 + rel_z  # Mapear de [-0.5, 0.5] para [0.0, 1.0]
        t = max(0.0, min(1.0, t))  # Clamp entre 0.0 e 1.0
    
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
    """
    Verifica se a posição (world_x, world_z) colide com um tile sólido.
    Usa AABB (Axis-Aligned Bounding Box) simples baseado em tiles.
    Considera a altura do jogador para permitir movimento sobre plataformas quando na altura correta.
    
    Args:
        world_x: Posição X no mundo
        world_z: Posição Z no mundo
        player_radius: Raio do jogador para verificação (default: 0.5 = metade do tile)
        player_y: Altura Y do jogador (opcional, usado para verificar se pode caminhar sobre plataformas)
        map_offset_x: Offset X do mapa (default: -20 para mapa 40x40 centrado)
        map_offset_z: Offset Z do mapa (default: -20 para mapa 40x40 centrado)
    
    Returns:
        True se há colisão com tile sólido, False caso contrário
    """
    # Converter coordenada do mundo para índice da matriz
    map_x = int(world_x - map_offset_x)
    map_z = int(world_z - map_offset_z)
    
    # Verificar limites do mapa
    if map_z < 0 or map_z >= len(tileMap) or map_x < 0 or map_x >= len(tileMap[0]):
        return True  # Fora do mapa = colisão (bloquear)
    
    # Obter tipo de tile na posição
    tile_type = tileMap[map_z][map_x]
    
    # Verificar se o tile é líquido (água: sempre bloqueia)
    if tile_type:
        tile_def = world_config.getTileDefinition(tile_type)
        if tile_def and tile_def.get('is_liquid', False):
            return True
        if tile_def and tile_def.get('is_solid', False):
            # Se o jogador está na altura correta da plataforma, permitir movimento
            if player_y is not None:
                tile_height = tile_def.get('height', 0.0)
                tile_top = world_config.GROUND_LEVEL + tile_height
                # Se o jogador está no topo ou acima da plataforma, permitir movimento
                if player_y >= tile_top - 0.1:  # Tolerância de 0.1 para pequenas diferenças
                    return False  # Não há colisão - jogador está na altura correta
            return True  # Tile sólido e jogador não está na altura correta
    
    # Verificar também tiles adjacentes se o jogador se sobrepõe a múltiplos tiles
    # (para jogadores maiores que meio tile)
    if player_radius > 0.5:
        # Verificar tiles nas 4 direções adjacentes
        adjacent_tiles = [
            (map_x - 1, map_z),  # Oeste
            (map_x + 1, map_z),  # Leste
            (map_x, map_z - 1),  # Norte
            (map_x, map_z + 1),  # Sul
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
    # Dicionário que armazena propriedades de rampas por posição (map_x, map_z)
    rampData = {}
    
    # ===== CRIAR MATRIZ LÓGICA DO MAPA =====
    # Cada célula da matriz representa exatamente 1 tile (1 unidade)
    tileMap = createTileMap()
    
    # ===== DEFINIR PROPRIEDADES DE RAMPAS =====
    # Rampas nas linhas z=20-25 conectam piso baixo (altura 0.0) à plataforma elevada (altura 1.0)
    # As direções são definidas diretamente na matriz (IDs 8, 9, 10, 11)
    # Expandido do padrão original (linha z=5) para múltiplas linhas (z=20-25)
    for z in range(20, 26):  # Rampas nas linhas z=20 a z=25 (6 linhas)
        for x in range(2, 38):  # Rampas de x=2 até x=37 (36 colunas de rampas)
            # Verificar se há direção definida na matriz para esta posição
            direction_from_matrix = _rampDirectionsFromMatrix.get((x, z))
            if direction_from_matrix:
                # Usar direção da matriz
                direction = direction_from_matrix
            else:
                # Fallback: usar Leste (10) como padrão, baseado no padrão original
                # Rampas são do tipo 10 (Leste) no mapa expandido
                direction = world_config.RAMP_DIRECTION_EAST
            # Definir alturas e direção
            setRampData(x, z, 0.0, world_config.BLOCK_HEIGHT_FULL, direction)
    
    # ===== CONVERTER MATRIZ LÓGICA EM GEOMETRIA =====
    # Offset para centralizar o mapa na origem
    # Mapa 40x40: de (-20, -20) a (19, 19) no mundo
    # tileMap[0][0] deve mapear para mundo (-20, -20)
    map_offset_x = -20
    map_offset_z = -20  # Offset Z inicial (primeira linha da matriz = Z=-20 no mundo)
    
    platforms, ramps = convertTileMapToGeometry(tileMap, map_offset_x, map_offset_z)
    
    # ===== DEFINIR PROPS (OBJETOS 3D DECORATIVOS) =====
    # Props são objetos 3D externos posicionados sobre o mapa
    # Eles são independentes dos tiles e podem ser posicionados livremente
    # 
    # Árvores substituindo as pilastas (tiles 4) do mapa
    # Posições das pilastas originais convertidas para coordenadas do mundo:
    # - map_x=5, map_z=0 → mundo: x=0, z=-5
    # - map_x=5, map_z=1 → mundo: x=0, z=-4
    # - map_x=1, map_z=5 → mundo: x=-4, z=0
    # - map_x=9, map_z=5 → mundo: x=4, z=0
    # - map_x=5, map_z=9 → mundo: x=0, z=4
    import props
    
    # ===== ADICIONAR PROPS DO MAPA =====
    # Carregar props da matriz de props (sistema escalável)
    props_map = createPropsMap()
    map_offset_x = -20
    map_offset_z = -20
    
    # Função auxiliar para calcular altura do topo do tile
    def getTileTopHeight(world_x, world_z):
        """Retorna a altura Y do topo do tile na posição (world_x, world_z)"""
        tile_props = getTilePropertiesAt(world_x, world_z, map_offset_x, map_offset_z)
        if tile_props:
            tile_height = tile_props.get('height', world_config.FLOOR_TILE_HEIGHT)
            return world_config.GROUND_LEVEL + tile_height
        return world_config.GROUND_LEVEL + world_config.FLOOR_TILE_HEIGHT
    
    # Processar matriz de props e adicionar automaticamente
    for z in range(len(props_map)):
        for x in range(len(props_map[z]) if len(props_map) > 0 else 0):
            prop_id = props_map[z][x]
            
            # Se não houver prop nesta posição, pular
            if prop_id == 0 or prop_id == world_config.PROP_ID_EMPTY:
                continue
            
            # Converter ID para tipo de prop
            prop_type = world_config.propIdToType(prop_id)
            if prop_type is None:
                continue
            
            # Obter definição do prop
            prop_def = world_config.getPropDefinition(prop_type)
            if prop_def is None:
                print(f"AVISO: Definição não encontrada para prop '{prop_type}'")
                continue
            
            # Calcular posição no mundo
            world_x = map_offset_x + x
            world_z = map_offset_z + z
            
            # Calcular altura Y: topo do tile + offset do modelo
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
    """
    Renderiza todas as rampas do cenário.
    As rampas agora vêm da matriz de tiles com propriedades (start_height, end_height, direction).
    A geometria conecta visualmente dois níveis de piso com inclinação respeitando a direção.
    Usa textura específica de TILE_TYPE_RAMP se disponível, senão usa textura padrão.
    """
    glBindVertexArray(rampMesh[0])
    
    for ramp in ramps:
        pos = ramp['pos']
        start_height = ramp.get('start_height', 0.0)
        end_height = ramp.get('end_height', 1.0)
        direction = ramp.get('direction', world_config.RAMP_DIRECTION_NORTH)
        tile_type = ramp.get('tile_type', world_config.TILE_TYPE_RAMP)
        
        # Selecionar textura: específica do tile ou padrão
        texture = tileTextures.get(tile_type, rampTexture) if tile_type else rampTexture
        glBindTexture(GL_TEXTURE_2D, texture)
        
        # A geometria da rampa vai de x=0 (y=0) até x=1 (y=1)
        # Precisamos escalar e posicionar para conectar os níveis corretos
        height_diff = end_height - start_height
        
        # Calcular ângulo baseado na direção
        # Geometria base: x=0 (baixo) até x=1 (alto)
        # N: Z- (180°) - rampa sobe para Norte (Z-)
        # S: Z+ (0°) - rampa sobe para Sul (Z+)
        # E: X+ (90°) - rampa sobe para Leste (X+)
        # W: X- (-90°) - rampa sobe para Oeste (X-)
        angle = 0.0
        if direction == world_config.RAMP_DIRECTION_NORTH:
            angle = 180.0  # Rampa apontando para Z- (Norte)
        elif direction == world_config.RAMP_DIRECTION_SOUTH:
            angle = 0.0    # Rampa apontando para Z+ (Sul)
        elif direction == world_config.RAMP_DIRECTION_EAST:
            angle = 90.0   # Rampa apontando para X+ (Leste)
        elif direction == world_config.RAMP_DIRECTION_WEST:
            angle = -90.0  # Rampa apontando para X- (Oeste)
        
        # Debug removido - direções estão sendo lidas corretamente
        
        # Escala: comprimento = 1 tile, altura = diferença de altura, largura = 1 tile
        # A geometria base vai de y=0 a y=1. Após escalar por height_diff, vai de 0 a height_diff.
        # Depois transladamos por start_height para ter y de start_height a end_height.
        scale_length = world_config.TILE_SIZE   # Comprimento da rampa (1 tile)
        scale_height = abs(height_diff) if abs(height_diff) > 0.0 else 1.0  # Altura da inclinação
        scale_width = world_config.TILE_SIZE    # Largura da rampa (1 tile)
        
        # Posição: centro do tile no plano XZ, e base da rampa no eixo Y
        world_x = pos[0]
        world_z = pos[2]
        # A altura será ajustada após escalar (start_height + altura escalada)
        base_y = world_config.GROUND_LEVEL
        
        modelMatrix = glm.mat4(1.0)
        # Ordem de transformações (em GLM, aplicadas da direita para a esquerda):
        # Geometria base: x de 0 a 1 (baixo a alto), y de 0 a 1, z de -0.5 a 0.5
        # Queremos: comprimento 1 tile, altura de start_height a end_height, largura 1 tile, centralizado no tile
        
        # Ordem correta (em GLM, última transformação escrita é aplicada primeiro):
        # Queremos aplicar: scale → translate(-0.5, start_height, 0) → rotate → translate(world_x, base_y, world_z)
        # Então escrevemos na ordem inversa:
        
        # 1. Transladar para posição final no mundo (centro do tile XZ)
        modelMatrix = glm.translate(modelMatrix, glm.vec3(world_x, base_y, world_z))
        # 2. Rotacionar para a direção correta (ao redor do eixo Y)
        modelMatrix = glm.rotate(modelMatrix, glm.radians(angle), glm.vec3(0.0, 1.0, 0.0))
        # 3. Transladar para centralizar origem da geometria (geometria começa em x=0, mover -0.5 no eixo local X)
        # E ajustar altura base: transladar por start_height no eixo Y
        modelMatrix = glm.translate(modelMatrix, glm.vec3(-0.5, start_height, 0.0))
        # 4. Escalar (comprimento X, altura Y, largura Z)
        modelMatrix = glm.scale(modelMatrix, glm.vec3(scale_length, scale_height, scale_width))
        
        glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(modelMatrix))
        glDrawArrays(GL_TRIANGLES, 0, rampMesh[1])
