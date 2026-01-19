# ============================================================================
# JANELA
# ============================================================================
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_TITLE = "OpenGL moderno"

# ============================================================================
# OPENGL
# ============================================================================
OPENGL_VERSION_MAJOR = 3
OPENGL_VERSION_MINOR = 3
BACKGROUND_COLOR = (0.08, 0.08, 0.1, 1.0)

# ============================================================================
# JOGADOR (SPRITE)
# ============================================================================
OBJECT_SIZE_X = 1.0
OBJECT_SIZE_Y = 1.5
ENEMY_OBJECT_SIZE_X = OBJECT_SIZE_X / 1.5
ENEMY_OBJECT_SIZE_Y = OBJECT_SIZE_Y / 1.5
INITIAL_POSITION = (-18.0, 0.0, 18.0)
PLAYER_MAX_HP = 15

# ============================================================================
# MOVIMENTO / INPUT
# ============================================================================
MOVEMENT_SPEED = 5.0
SPRITE_SHEET_ROWS = 4
SPRITE_SHEET_COLS = 8
ANIMATION_SPEED = 8.0
ATTACK_DURATION = 0.4
ATTACK_COOLDOWN = 0.3
ATTACK_FRAMES = 8
ATTACK_HITBOX_LENGTH = 0.9
ATTACK_HITBOX_WIDTH = 0.5
ATTACK_HITBOX_PLAYER_FRONT = 0.5
BOOST_DURATION = 5.0
BOOST_COOLDOWN = 4.0
BOOST_SPEED_MULTIPLIER = 1.5

# ============================================================================
# ARQUIVOS
# ============================================================================
TEXTURE_FILE = "texture/player2/warrior_sprite_sheet.png"
IDLE_TEXTURE_FILE = "texture/player2/Swordsman_lvl3_Idle_with_shadow.png"
ENEMY_IDLE_ANIMATION_SPEED = 12.0
ENEMY_IDLE_FRAMES = 12
ENEMY_IDLE_PREFIX = "texture/enemy/Minotaur_03_Idle"
ENEMY_WALKING_PREFIX = "texture/enemy-walking/Minotaur_03_Walking"
ENEMY_WALKING_FRAMES = 18
ENEMY_WALKING_ANIMATION_SPEED = 12.0
ENEMY_ATTACK_PREFIX = "texture/enemy-attack/Minotaur_03_Attacking"
ENEMY_ATTACK_FRAMES = 12
ENEMY_ATTACK_ANIMATION_SPEED = 16.0
ENEMY_DYING_FRAMES = 15
ENEMY_DYING_ANIMATION_SPEED = 15.0
ENEMY_DYING_PREFIX = "texture/enemy-dying/Minotaur_03_Dying"
ARCHER_MAX_HP = 2
ARCHER_IDLE_TEXTURE = "texture/enemy-archer/Idle.png"
ARCHER_IDLE_COLS = 7
ARCHER_IDLE_ANIMATION_SPEED = 16.0
ARCHER_ATTACK_TEXTURE = "texture/enemy-archer-attack/Shot_1.png"
ARCHER_ATTACK_COLS = 15
ARCHER_ATTACK_DURATION = 0.6
ARCHER_ARROW_DELAY = 0.7
ARCHER_DYING_TEXTURE = "texture/enemy-archer-dying/Dead.png"
ARCHER_DYING_COLS = 5
ARCHER_DYING_ANIMATION_SPEED = 4.0
ARCHER_RUN_TEXTURE = "texture/enemy-archer-run/Evasion.png"
ARCHER_RUN_COLS = 6
ARCHER_RUN_ANIMATION_SPEED = 12.0
ARCHER_OBJECT_SIZE_X = OBJECT_SIZE_X
ARCHER_OBJECT_SIZE_Y = OBJECT_SIZE_Y
ARCHER_FLEE_DISTANCE = 3.0
ARCHER_SHOOT_COOLDOWN = 2.0
ARCHER_FLEE_SPEED = 3.0
ARCHER_ARROW_SPEED = 6.0
ARCHER_ARROW_MAX_DIST = 15.0
ARROW_TEXTURE = "texture/errow/Arrow.png"
ARCHER_ARROW_SIZE_X = 0.55
ARCHER_ARROW_SIZE_Y = 1.4
ARCHER_ARROW_HIT_RADIUS = 0.4
ENEMY_HITBOX_HALF_EXTENT = 0.5
ENEMY_MAX_HP = 3
ATTACK_DAMAGE = 1
HIT_FEEDBACK_DURATION = 0.12
HIT_KNOCKBACK_DISTANCE = 0.28
ENEMY_DETECTION_HALF_EXTENT = 6.0
SPOTLIGHT_DARK_FACTOR = 0.4
ENEMY_MOVEMENT_SPEED = 1.2
ENEMY_ATTACK_RANGE = 0.5
ENEMY_ATTACK_COOLDOWN = 2.0
ENEMY_ATTACK_DAMAGE = 1
PLATFORM_TEXTURE = "texture/wood/Wood084A_2K-JPG_Color.jpg"
VERTEX_SHADER_FILE = "vertexShader.glsl"
FRAGMENT_SHADER_FILE = "fragmentShader.glsl"
DEPTH_VERTEX_SHADER_FILE = "depthVertexShader.glsl"
DEPTH_FRAGMENT_SHADER_FILE = "depthFragmentShader.glsl"
SHADOW_MAPPING_ENABLED = False
SHADOW_MAP_SIZE = 1024
SHADOW_BIAS = 0.002
SHADOW_STRENGTH = 0.65
SHADOW_ORTHO_SIZE = 35.0
SHADOW_NEAR = 1.0
SHADOW_FAR = 80.0

# ============================================================================
# CÂMERA
# ============================================================================
CAMERA_POSITION = (0.0, 12.0, 8.0)
CAMERA_TARGET = (0.0, 0.0, 0.0)
CAMERA_UP = (0.0, 1.0, 0.0)

# ============================================================================
# PROJEÇÃO
# ============================================================================
FOV = 45.0
NEAR_PLANE = 0.1
FAR_PLANE = 100.0

# ============================================================================
# TEXTO / TEXTURA
# ============================================================================
TEXTURE_MAG_FILTER = None
TEXTURE_MIN_FILTER = None
TEXTURE_WRAP_S = "GL_MIRRORED_REPEAT"
TEXTURE_WRAP_T = "GL_MIRRORED_REPEAT"

# ============================================================================
# ILUMINAÇÃO
# ============================================================================
AMBIENT_LIGHT = (0.55, 0.55, 0.55)
DIRECTIONAL_LIGHT_DIRECTION = (0.3, 0.9, 0.3)
DIRECTIONAL_LIGHT_COLOR = (0.55, 0.55, 0.55)
SPECULAR_STRENGTH = 0.3
SPECULAR_SHININESS = 32
SPECULAR_COLOR = (1.0, 1.0, 1.0)
