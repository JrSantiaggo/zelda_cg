"""
Configurações globais do mundo
Ponto único de definição para parâmetros do mundo do jogo.
"""

# ============================================================================
# CONFIGURAÇÕES DE TILE (UNIDADE BÁSICA DO MUNDO)
# ============================================================================

# Tamanho base de um tile (1 unidade = 1 tile lógico)
TILE_SIZE = 1.0

# Tamanho visual do tile com gap (para separação visual entre tiles)
TILE_SIZE_VISUAL = 0.92  # Gap de 0.08 entre tiles para leitura visual clara

# Gap entre tiles (para visualização)
TILE_GAP = TILE_SIZE - TILE_SIZE_VISUAL  # 0.08


# ============================================================================
# ALTURAS PADRÃO (em unidades/tiles)
# ============================================================================

# Altura padrão do chão/tile de piso
FLOOR_TILE_HEIGHT = 0.08

# Altura padrão do jogador (2 tiles)
PLAYER_HEIGHT = 2.0

# Alturas padrão para diferentes tipos de blocos/obstáculos
BLOCK_HEIGHT_HALF = 0.5    # Meio tile - obstáculo baixo (pulável)
BLOCK_HEIGHT_FULL = 1.0    # 1 tile - cintura do jogador (obstáculo padrão)
BLOCK_HEIGHT_PILLAR = 2.0  # 2 tiles - altura do jogador (pilar)
WALL_HEIGHT_LOW = 2.0      # 2 tiles - parede baixa
WALL_HEIGHT_HIGH = 3.0     # 3 tiles - parede alta

# Altura padrão do chão (onde as plataformas ficam)
GROUND_LEVEL = -0.15


# ============================================================================
# TIPOS DE TILE (nomes/constantes)
# ============================================================================

# Tipos básicos de tile/obstáculo
TILE_TYPE_FLOOR = "floor"              # Piso padrão (baixo)
TILE_TYPE_PLATFORM = "platform"        # Plataforma elevada (piso mais alto)
TILE_TYPE_RAMP = "ramp"                # Rampa inclinada


# ============================================================================
# DIREÇÕES DE RAMPA (cardinais)
# ============================================================================

# Direções cardinais para rampas
RAMP_DIRECTION_NORTH = "N"  # Norte (Z-)
RAMP_DIRECTION_SOUTH = "S"  # Sul (Z+)
RAMP_DIRECTION_EAST = "E"   # Leste (X+)
RAMP_DIRECTION_WEST = "W"   # Oeste (X-)


# ============================================================================
# MAPEAMENTO NUMÉRICO DE TILES (para visualização do mapa)
# ============================================================================

# Cada número representa um tipo de tile para facilitar visualização
# 0 = vazio (sem tile)
# 1 = FLOOR (chão/piso padrão)
# 5 = PLATFORM (plataforma/piso mais alto)
# 8 = RAMP N (rampa Norte)
# 9 = RAMP S (rampa Sul)
# 10 = RAMP E (rampa Leste)
# 11 = RAMP W (rampa Oeste)

TILE_ID_EMPTY = 0
TILE_ID_FLOOR = 1
TILE_ID_PLATFORM = 5
TILE_ID_RAMP_N = 8   # Rampa Norte
TILE_ID_RAMP_S = 9   # Rampa Sul
TILE_ID_RAMP_E = 10  # Rampa Leste
TILE_ID_RAMP_W = 11  # Rampa Oeste

# Dicionário de conversão: número -> tipo de tile (string)
TILE_ID_TO_TYPE = {
    TILE_ID_EMPTY: None,
    TILE_ID_FLOOR: TILE_TYPE_FLOOR,
    TILE_ID_PLATFORM: TILE_TYPE_PLATFORM,
    TILE_ID_RAMP_N: TILE_TYPE_RAMP,  # Rampa com direção Norte
    TILE_ID_RAMP_S: TILE_TYPE_RAMP,  # Rampa com direção Sul
    TILE_ID_RAMP_E: TILE_TYPE_RAMP,  # Rampa com direção Leste
    TILE_ID_RAMP_W: TILE_TYPE_RAMP,  # Rampa com direção Oeste
}

# Dicionário de conversão: ID numérico -> direção da rampa
# Usado quando uma rampa é definida diretamente na matriz (8, 9, 10, 11)
TILE_ID_TO_RAMP_DIRECTION = {
    TILE_ID_RAMP_N: RAMP_DIRECTION_NORTH,  # 8 -> "N"
    TILE_ID_RAMP_S: RAMP_DIRECTION_SOUTH,  # 9 -> "S"
    TILE_ID_RAMP_E: RAMP_DIRECTION_EAST,   # 10 -> "E"
    TILE_ID_RAMP_W: RAMP_DIRECTION_WEST,   # 11 -> "W"
}


def tileIdToType(tile_id):
    """
    Converte um ID numérico de tile para o tipo de tile (string).
    
    Args:
        tile_id: Número inteiro representando o tipo de tile
    
    Returns:
        String com o tipo de tile ou None se ID inválido ou vazio
    """
    return TILE_ID_TO_TYPE.get(tile_id, None)


# ============================================================================
# DEFINIÇÃO DE TIPOS DE TILE (propriedades)
# ============================================================================

# Estrutura de dados para definir tipos de tiles
# Cada tipo possui:
#   - height: altura base do tile (em unidades)
#   - texture: caminho relativo para a textura (None = usa textura padrão)
#   - is_solid: se o tile é sólido (para colisão futura)
#   - scale_x, scale_z: escala horizontal (largura/profundidade), padrão = TILE_SIZE
#
# O sistema permite adicionar novos tipos facilmente adicionando entradas ao dicionário.

TILE_DEFINITIONS = {
    TILE_TYPE_FLOOR: {
        'height': FLOOR_TILE_HEIGHT,  # 0.08
        'texture': None,  # Usa textura padrão das plataformas
        'is_solid': False,  # Chão não é sólido - permite movimento sobre ele
        'scale_x': TILE_SIZE,  # 1.0 (tiles encostados)
        'scale_z': TILE_SIZE,  # 1.0 (tiles encostados)
    },
    
    TILE_TYPE_PLATFORM: {
        'height': BLOCK_HEIGHT_FULL,  # 1.0 - piso mais alto
        'texture': None,  # Usa textura padrão das plataformas
        'is_solid': True,
        'scale_x': TILE_SIZE,  # 1.0
        'scale_z': TILE_SIZE,  # 1.0
    },
    
    TILE_TYPE_RAMP: {
        'height': BLOCK_HEIGHT_FULL,  # 1.0 (será ajustado depois com lógica de rampa)
        'texture': "texture/bricks/Bricks101_2K-JPG_Color.jpg",
        'is_solid': False,
        'scale_x': TILE_SIZE,  # 1.0
        'scale_z': TILE_SIZE,  # 1.0
        # Propriedades padrão para rampas (usadas automaticamente se setRampData() não for chamado)
        'default_start_height': 0.0,  # Altura inicial padrão (piso baixo)
        'default_end_height': BLOCK_HEIGHT_FULL,  # Altura final padrão (plataforma elevada)
        'default_direction': RAMP_DIRECTION_NORTH,  # Direção padrão (Norte)
    },
}


def getTileDefinition(tile_type):
    """
    Obtém a definição de um tipo de tile.
    
    Args:
        tile_type: String identificando o tipo de tile (ex: TILE_TYPE_FLOOR)
    
    Returns:
        Dicionário com as propriedades do tile ou None se tipo inválido
    """
    return TILE_DEFINITIONS.get(tile_type, None)


def getTileHeight(tile_type):
    """
    Obtém a altura base de um tipo de tile.
    
    Args:
        tile_type: String identificando o tipo de tile
    
    Returns:
        Altura em unidades (float) ou 0.0 se tipo inválido
    """
    definition = getTileDefinition(tile_type)
    return definition['height'] if definition else 0.0


def getTileTexture(tile_type):
    """
    Obtém o caminho da textura de um tipo de tile.
    
    Args:
        tile_type: String identificando o tipo de tile
    
    Returns:
        Caminho da textura (string) ou None se usar textura padrão
    """
    definition = getTileDefinition(tile_type)
    return definition['texture'] if definition else None


def isTileSolid(tile_type):
    """
    Verifica se um tipo de tile é sólido.
    
    Args:
        tile_type: String identificando o tipo de tile
    
    Returns:
        True se sólido, False caso contrário
    """
    definition = getTileDefinition(tile_type)
    return definition['is_solid'] if definition else False


# ============================================================================
# ESCALAS PADRÃO PARA DIFERENTES TIPOS
# ============================================================================

# Escalas padrão (largura/largura, altura, profundidade/largura)
SCALE_FLOOR_TILE = (TILE_SIZE_VISUAL, FLOOR_TILE_HEIGHT, TILE_SIZE_VISUAL)
SCALE_BLOCK_LOW = (1.0, BLOCK_HEIGHT_HALF, 1.0)
SCALE_BLOCK_STANDARD = (1.0, BLOCK_HEIGHT_FULL, 1.0)
SCALE_PILLAR = (0.8, BLOCK_HEIGHT_PILLAR, 0.8)
SCALE_WALL_LOW = (1.0, WALL_HEIGHT_LOW, 0.5)
SCALE_WALL_HIGH = (0.5, WALL_HEIGHT_HIGH, 1.0)


# ============================================================================
# CONFIGURAÇÕES DE POSICIONAMENTO
# ============================================================================

# Deslocamento Y padrão para diferentes elementos
Y_OFFSET_FLOOR = GROUND_LEVEL
Y_OFFSET_BLOCK_LOW = BLOCK_HEIGHT_HALF / 2.0  # Centro do bloco baixo
Y_OFFSET_BLOCK_STANDARD = BLOCK_HEIGHT_FULL / 2.0  # Centro do bloco padrão
Y_OFFSET_PILLAR = BLOCK_HEIGHT_PILLAR / 2.0  # Centro do pilar
Y_OFFSET_WALL_LOW = WALL_HEIGHT_LOW / 2.0  # Centro da parede baixa
Y_OFFSET_WALL_HIGH = WALL_HEIGHT_HIGH / 2.0  # Centro da parede alta


# ============================================================================
# SISTEMA DE PROPS (OBJETOS 3D NO MAPA)
# ============================================================================

# IDs numéricos para props (usar números negativos ou acima de 100 para evitar conflito com tiles)
# IDs negativos são mais seguros para não conflitar com tiles existentes
PROP_ID_EMPTY = 0
PROP_ID_TREE = -1      # Árvore
PROP_ID_ROCK = -2      # Pedra
PROP_ID_BUSH = -3      # Arbusto
# Adicione mais IDs conforme necessário

# Dicionário de conversão: ID numérico -> tipo de prop (string)
PROP_ID_TO_TYPE = {
    PROP_ID_EMPTY: None,
    PROP_ID_TREE: "tree",
    PROP_ID_ROCK: "rock",
    PROP_ID_BUSH: "bush",
}

# Definições de props (similar a TILE_DEFINITIONS)
# Cada prop possui:
#   - model: caminho relativo para o modelo 3D (.obj)
#   - texture: caminho relativo para textura (None = usar MTL do modelo)
#   - scale: tupla (x, y, z) - escala do modelo
#   - rotation: rotação padrão em graus (ao redor do eixo Y)
#   - y_offset: offset Y adicional (para ajustar altura base do modelo)
PROP_DEFINITIONS = {
    "tree": {
        'model': "models/tree/Lowpoly_tree_sample.obj",
        'texture': None,  # Usar MTL do modelo
        'scale': (0.1, 0.1, 0.1),
        'rotation': 0.0,  # Rotação padrão (pode ser sobrescrita)
        'y_offset': 0.7,  # Offset do modelo (compensa Y=-0.7 do modelo)
    },
    # Adicione mais definições conforme necessário:
    # "rock": {
    #     'model': "models/rock/rock.obj",
    #     'texture': None,
    #     'scale': (0.3, 0.3, 0.3),
    #     'rotation': 0.0,
    #     'y_offset': 0.0,
    # },
}


def propIdToType(prop_id):
    """
    Converte um ID numérico de prop para o tipo de prop (string).
    
    Args:
        prop_id: Número inteiro representando o tipo de prop
    
    Returns:
        String com o tipo de prop ou None se ID inválido ou vazio
    """
    return PROP_ID_TO_TYPE.get(prop_id, None)


def getPropDefinition(prop_type):
    """
    Obtém a definição de um tipo de prop.
    
    Args:
        prop_type: String identificando o tipo de prop (ex: "tree")
    
    Returns:
        Dicionário com as propriedades do prop ou None se tipo inválido
    """
    return PROP_DEFINITIONS.get(prop_type, None)
