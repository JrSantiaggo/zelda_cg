# ============================================================================
# CONFIGURAÇÕES DE JANELA
# ============================================================================

# Resolução inicial da janela (largura, altura) em pixels
WINDOW_WIDTH = 1800
WINDOW_HEIGHT = 1000

# Título da janela
WINDOW_TITLE = "OpenGL moderno"


# ============================================================================
# CONFIGURAÇÕES DE OPENGL
# ============================================================================

# Versão do OpenGL
OPENGL_VERSION_MAJOR = 3
OPENGL_VERSION_MINOR = 3

# Cor de fundo da janela (R, G, B, A) - valores de 0.0 a 1.0
BACKGROUND_COLOR = (0.9, 0.9, 0.9, 1.0)


# ============================================================================
# CONFIGURAÇÕES DO JOGADOR (SPRITE)
# ============================================================================

# Sistema de escala: 1 unidade = 1 tile lógico
# O jogador ocupa aproximadamente 2 tiles de altura (padrão Zelda)
# Tamanho do sprite do jogador (em unidades de mundo)
OBJECT_SIZE_X = 1.0  # Metade da largura do sprite (largura total = 1.0 tile)
OBJECT_SIZE_Y = 1.5   # Metade da altura do sprite (altura total = 2.0 tiles)

# Posição inicial do jogador (x, y, z) em coordenadas de mundo
# y=0 representa o chão, o sprite é desenhado "de pé" a partir dessa posição
INITIAL_POSITION = (0.0, 0.0, 0.0)


# ============================================================================
# CONFIGURAÇÕES DE MOVIMENTO/INPUT
# ============================================================================

# Velocidade de movimento do jogador (tiles por frame)
# ~0.05 tiles/frame = movimento suave, ~20 frames para atravessar 1 tile
MOVEMENT_SPEED = 0.05

# Configurações de animação do sprite sheet
SPRITE_SHEET_ROWS = 4      # Número de linhas (direções)
SPRITE_SHEET_COLS = 8      # Número de colunas (frames por direção)
ANIMATION_SPEED = 8.0      # Velocidade da animação (ciclos completos por segundo)
                          # 8.0 = completa um ciclo de 8 frames em ~1 segundo


# ============================================================================
# CONFIGURAÇÕES DE ARQUIVOS
# ============================================================================

# Textura do sprite do jogador (arquivo PNG com transparência)
TEXTURE_FILE = "texture/player2/warrior_sprite_sheet.png"

# Textura do sprite idle do jogador (animação quando parado)
# Linhas 0-2: 12 colunas cada, linha 3: 4 colunas
IDLE_TEXTURE_FILE = "texture/player2/Swordsman_lvl3_Idle_with_shadow.png"

# Textura das plataformas (blocos 3D do cenário)
PLATFORM_TEXTURE = "texture/wood/Wood084A_2K-JPG_Color.jpg"

# Nomes dos arquivos de shaders (devem estar na mesma pasta que main.py)
VERTEX_SHADER_FILE = "vertexShader.glsl"
FRAGMENT_SHADER_FILE = "fragmentShader.glsl"


# ============================================================================
# CONFIGURAÇÕES DE CÂMERA (VIEW MATRIX) - Estilo Zelda: Link to the Past
# ============================================================================

# Posição da câmera no mundo (x, y, z)
# Câmera posicionada acima e atrás do alvo para visão isométrica top-down
# Ajustada para mostrar ~8-12 tiles na tela mantendo proporção Zelda
CAMERA_POSITION = (0.0, 12.0, 8.0)

# Ponto para onde a câmera está olhando (x, y, z)
CAMERA_TARGET = (0.0, 0.0, 0.0)

# Vetor "up" da câmera
CAMERA_UP = (0.0, 1.0, 0.0)


# ============================================================================
# CONFIGURAÇÕES DE PROJEÇÃO (PROJECTION MATRIX)
# ============================================================================

# Campo de visão vertical em graus (Field of View)
# FOV ajustado para mostrar área adequada sem distorção excessiva
FOV = 45.0

# Plano de corte próximo (near plane)
NEAR_PLANE = 0.1

# Plano de corte distante (far plane)
FAR_PLANE = 100.0


# ============================================================================
# CONFIGURAÇÕES DE TEXTO
# ============================================================================

# Parâmetros de filtragem de textura (GL_LINEAR, GL_NEAREST, etc.)
# Esses valores são constantes do OpenGL, mas podem ser alterados se necessário
TEXTURE_MAG_FILTER = None  # Será definido como GL_LINEAR no código
TEXTURE_MIN_FILTER = None  # Será definido como GL_LINEAR no código

# Modo de wrapping da textura (GL_CLAMP_TO_BORDER, GL_REPEAT, etc.)
TEXTURE_WRAP_S = None  # Será definido como GL_CLAMP_TO_BORDER no código
TEXTURE_WRAP_T = None  # Será definido como GL_CLAMP_TO_BORDER no código


# ============================================================================
# CONFIGURAÇÕES DE ILUMINAÇÃO
# ============================================================================

# Cor da luz ambiente global (R, G, B) - valores de 0.0 a 1.0
# Multiplicada pela cor da textura/objeto para criar iluminação base
# Ajustado para 25% para permitir mais contraste e profundidade
AMBIENT_LIGHT = (0.25, 0.25, 0.25)  # Intensidade ambiente: 25% de iluminação base

# Luz direcional para iluminação difusa (modelo de Lambert)
# Direção da luz direcional (vetor normalizado apontando da superfície para a luz)
# Ajustado para ângulo isométrico agradável: luz vindo de cima e levemente de um lado
DIRECTIONAL_LIGHT_DIRECTION = (0.3, 0.9, 0.3)  # Direção da luz (será normalizada no shader)

# Cor/intensidade da luz direcional (R, G, B) - valores de 0.0 a 1.0
# Ajustado para 60% - moderado para não estourar superfícies claras
DIRECTIONAL_LIGHT_COLOR = (0.6, 0.6, 0.6)  # Intensidade da luz difusa: 60%

# Iluminação especular (modelo de Phong)
# Intensidade do brilho especular - valores de 0.0 a 1.0
# Ajustado para 30% - sutil e natural, não dominante
SPECULAR_STRENGTH = 0.3  # Força do brilho especular: 30%

# Shininess (expoente especular) - controla o tamanho do brilho
# Valor mais baixo (32) cria brilho mais suave e amplo, adequado para materiais naturais (madeira, pedra)
SPECULAR_SHININESS = 32  # Expoente especular: brilho suave e amplo

# Cor do brilho especular (R, G, B) - valores de 0.0 a 1.0
# Branco puro para brilho natural
SPECULAR_COLOR = (1.0, 1.0, 1.0)  # Cor do brilho: branco
