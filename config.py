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

# Inimigo: mesma escala do jogador (usado em createSpriteMesh para a malha do inimigo)
ENEMY_OBJECT_SIZE_X = OBJECT_SIZE_X / 1.5 # Metade da largura (igual ao jogador)
ENEMY_OBJECT_SIZE_Y = OBJECT_SIZE_Y / 1.5 # Metade da altura (igual ao jogador)

# Posição inicial do jogador (x, y, z) em coordenadas de mundo
# y=0 representa o chão, o sprite é desenhado "de pé" a partir dessa posição
INITIAL_POSITION = (0.0, 0.0, 0.0)

# Vida do jogador (HUD na barra superior)
PLAYER_MAX_HP = 6


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

# Configurações de ataque (sistema formal)
ATTACK_DURATION = 0.4     # Duração fixa do ataque em segundos
ATTACK_COOLDOWN = 0.3     # Tempo de recarga em segundos (após o fim do ataque)
ATTACK_FRAMES = 8         # Número de frames da animação de ataque (deve bater com sprite)

# Hitbox de ataque (espada) — retângulo no plano XZ, direcional
ATTACK_HITBOX_LENGTH = 0.9   # Distância da espada na direção do ataque (tiles)
ATTACK_HITBOX_WIDTH = 0.5    # Largura perpendicular (tiles)
ATTACK_HITBOX_PLAYER_FRONT = 0.5  # Metade da largura do jogador; hitbox começa na “borda” do sprite


# ============================================================================
# CONFIGURAÇÕES DE ARQUIVOS
# ============================================================================

# Textura do sprite do jogador (arquivo PNG com transparência)
TEXTURE_FILE = "texture/player2/warrior_sprite_sheet.png"

# Textura do sprite idle do jogador (animação quando parado)
# Linhas 0-2: 12 colunas cada, linha 3: 4 colunas
IDLE_TEXTURE_FILE = "texture/player2/Swordsman_lvl3_Idle_with_shadow.png"

# Inimigos: animação idle (sequência Minotaur_03_Idle_000 a _011)
ENEMY_IDLE_ANIMATION_SPEED = 12.0   # “frames” por segundo (avance para próximo quadro)
ENEMY_IDLE_FRAMES = 12             # total de quadros (000 a 011)
ENEMY_IDLE_PREFIX = "texture/enemy/Minotaur_03_Idle"  # base do nome (sufixo _NNN.png)
# Animação de andar (texture/enemy-walking): Minotaur_03_Walking_000 a _017; esquerda = espelho
ENEMY_WALKING_PREFIX = "texture/enemy-walking/Minotaur_03_Walking"
ENEMY_WALKING_FRAMES = 18
ENEMY_WALKING_ANIMATION_SPEED = 12.0   # frames por segundo
# Animação de ataque (texture/enemy-attack): Minotaur_03_Attacking_000 a _011
ENEMY_ATTACK_PREFIX = "texture/enemy-attack/Minotaur_03_Attacking"
ENEMY_ATTACK_FRAMES = 12
ENEMY_ATTACK_ANIMATION_SPEED = 16.0   # frames por segundo
# Animação de morte (texture/enemy-dying): Minotaur_03_Dying_000 a _014
ENEMY_DYING_FRAMES = 15
ENEMY_DYING_ANIMATION_SPEED = 15.0   # frames por segundo (≈1 s para 15 quadros)
ENEMY_DYING_PREFIX = "texture/enemy-dying/Minotaur_03_Dying"

# Arqueiro (enemy-archer): separado dos inimigos; atira flechas; pode ser atacado como inimigo
ARCHER_MAX_HP = 2                       # vida do arqueiro (atingível pela espada)
ARCHER_IDLE_TEXTURE = "texture/enemy-archer/Idle.png"  # 1 linha, 7 colunas
ARCHER_IDLE_COLS = 7
ARCHER_IDLE_ANIMATION_SPEED = 16.0   # frames por segundo
# Animação de ataque (enemy-archer-attack): 1 linha, 15 colunas
ARCHER_ATTACK_TEXTURE = "texture/enemy-archer-attack/Shot_1.png"
ARCHER_ATTACK_COLS = 15
ARCHER_ATTACK_DURATION = 0.6         # duração da animação de ataque em segundos
ARCHER_ARROW_DELAY = 0.7             # delay (s) entre início do ataque e saída da flecha (sincroniza com a animação)
# Animação de morte (enemy-archer-dying): 1 linha, 5 colunas
ARCHER_DYING_TEXTURE = "texture/enemy-archer-dying/Dead.png"
ARCHER_DYING_COLS = 5
ARCHER_DYING_ANIMATION_SPEED = 4.0  # frames por segundo
# Tamanho do sprite (maior que o inimigo; mesma escala do jogador)
ARCHER_OBJECT_SIZE_X = OBJECT_SIZE_X   # Metade da largura
ARCHER_OBJECT_SIZE_Y = OBJECT_SIZE_Y   # Metade da altura
# Detecção = luz spot (ENEMY_DETECTION_HALF_EXTENT). Se player entra, arqueiro atira.
# Se player chega à metade da distância do spot, arqueiro foge.
ARCHER_FLEE_DISTANCE = 3.0             # Metade do spot (6/2); abaixo disso o arqueiro foge
ARCHER_SHOOT_COOLDOWN = 2.0            # Segundos entre um tiro e outro
ARCHER_FLEE_SPEED = 0.012              # Velocidade ao fugir (menor que o player)
ARCHER_ARROW_SPEED = 0.1               # Velocidade da flecha (tiles por frame)
ARCHER_ARROW_MAX_DIST = 15.0           # Flecha desaparece além desta distância do spawn
# Flecha: texture/errow/Arrow.png; dano = ENEMY_ATTACK_DAMAGE
ARROW_TEXTURE = "texture/errow/Arrow.png"
ARCHER_ARROW_SIZE_X = 0.55             # Metade da largura do sprite da flecha (maior para ser visível)
ARCHER_ARROW_SIZE_Y = 1.4              # Metade da altura (mais larga/espessa)
ARCHER_ARROW_HIT_RADIUS = 0.4          # Só acerta se distância < this (evita acerto quando já passou)

# Metade do lado da hitbox no plano XZ (inimigo ~1 tile de largura)
ENEMY_HITBOX_HALF_EXTENT = 0.5
# Vida inicial dos inimigos; ao chegar a 0 são removidos
ENEMY_MAX_HP = 3
# Dano do ataque do jogador por acerto
ATTACK_DAMAGE = 1
# Feedback visual ao acertar inimigo: duração (s) e distância do knockback (tiles)
HIT_FEEDBACK_DURATION = 0.12
HIT_KNOCKBACK_DISTANCE = 0.28

# Área de detecção: círculo de raio H ao redor do jogador (mesmo raio da luz spot)
# Quando o inimigo entra nessa área (luz chega nele), ele detecta e ataca
ENEMY_DETECTION_HALF_EXTENT = 6.0   # Raio do círculo de detecção e da luz spot (tiles)

# Luz spot ao redor do jogador: fora do spot o mapa fica mais escuro
SPOTLIGHT_DARK_FACTOR = 0.25       # Iluminação fora do spot (0.25 = 25%)
ENEMY_MOVEMENT_SPEED = 0.02         # Velocidade ao seguir o jogador (tiles por frame), um pouco mais lento que o player

# Ataque do inimigo ao jogador: ao encostar (alcance de hit), para e ataca; 2 s entre ataques
ENEMY_ATTACK_RANGE = 0.5            # Distância em XZ para considerar "ao alcance" (1 tile)
ENEMY_ATTACK_COOLDOWN = 2.0         # Segundos entre um ataque e o próximo
ENEMY_ATTACK_DAMAGE = 1             # Dano ao jogador por acerto

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
TEXTURE_WRAP_S = "GL_MIRRORED_REPEAT"  # Será definido como GL_CLAMP_TO_BORDER no código
TEXTURE_WRAP_T = "GL_MIRRORED_REPEAT"  # Será definido como GL_CLAMP_TO_BORDER no código


# ============================================================================
# CONFIGURAÇÕES DE ILUMINAÇÃO
# ============================================================================

# Cor da luz ambiente global (R, G, B) - valores de 0.0 a 1.0
# Multiplicada pela cor da textura/objeto para criar iluminação base
# Aumentado para 40% para reduzir visibilidade das bordas entre tiles de piso uniforme
AMBIENT_LIGHT = (0.4, 0.4, 0.4)  # Intensidade ambiente: 40% de iluminação base

# Luz direcional para iluminação difusa (modelo de Lambert)
# Direção da luz direcional (vetor normalizado apontando da superfície para a luz)
# Ajustado para ângulo isométrico agradável: luz vindo de cima e levemente de um lado
DIRECTIONAL_LIGHT_DIRECTION = (0.3, 0.9, 0.3)  # Direção da luz (será normalizada no shader)

# Cor/intensidade da luz direcional (R, G, B) - valores de 0.0 a 1.0
# Reduzido para 40% para diminuir variações de iluminação entre tiles adjacentes
# Isso ajuda a suavizar bordas quando o piso tem textura de cor uniforme
DIRECTIONAL_LIGHT_COLOR = (0.4, 0.4, 0.4)  # Intensidade da luz difusa: 40%

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
