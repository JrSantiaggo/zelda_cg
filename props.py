"""
Módulo de props: carregamento e renderização de objetos 3D externos (árvores, pedras, etc.)
Suporta formato OBJ (texto, sem dependências externas)
"""
from OpenGL.GL import *
import glm
import numpy as np
import ctypes
import os
import math
import resources
import world_config

# Lista global de props
props = []


def loadMTL(mtlFileName, modelDir):
    """
    Carrega arquivo MTL (Material Template Library) e extrai caminhos de texturas.
    
    Args:
        mtlFileName: Nome do arquivo .mtl (pode ser relativo ou absoluto)
        modelDir: Diretório base do modelo (para resolver caminhos relativos de texturas)
    
    Returns:
        Dicionário {material_name: texture_path} com texturas encontradas
    """
    materials = {}
    current_material = None
    
    try:
        # Se mtlFileName não é absoluto, tentar no mesmo diretório do modelo
        if not os.path.isabs(mtlFileName):
            mtl_path = os.path.join(modelDir, mtlFileName)
        else:
            mtl_path = mtlFileName
        
        if not os.path.exists(mtl_path):
            print(f"AVISO: Arquivo MTL não encontrado: {mtl_path}")
            return materials
        
        with open(mtl_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                
                # Novo material
                if parts[0] == 'newmtl':
                    if len(parts) > 1:
                        current_material = parts[1]
                        materials[current_material] = {'texture': None, 'color': None}
                
                # Cor difusa (Kd) - usar quando não houver textura
                elif parts[0] == 'Kd' and current_material:
                    if len(parts) >= 4:
                        # Kd r g b (valores de 0.0 a 1.0)
                        r = float(parts[1])
                        g = float(parts[2])
                        b = float(parts[3])
                        materials[current_material]['color'] = (r, g, b)
                
                # Textura difusa (map_Kd) - prioridade sobre cor
                elif parts[0] == 'map_Kd' and current_material:
                    if len(parts) > 1:
                        texture_path = parts[1]
                        # Resolver caminho relativo
                        if not os.path.isabs(texture_path):
                            full_texture_path = os.path.join(modelDir, texture_path)
                        else:
                            full_texture_path = texture_path
                        materials[current_material]['texture'] = full_texture_path
                
                # Textura ambiente (map_Ka) - usar como fallback
                elif parts[0] == 'map_Ka' and current_material:
                    if len(parts) > 1 and not materials[current_material].get('texture'):
                        texture_path = parts[1]
                        if not os.path.isabs(texture_path):
                            full_texture_path = os.path.join(modelDir, texture_path)
                        else:
                            full_texture_path = texture_path
                        materials[current_material]['texture'] = full_texture_path
                
                # Textura especular (map_Ks) - usar como fallback
                elif parts[0] == 'map_Ks' and current_material:
                    if len(parts) > 1 and not materials[current_material].get('texture'):
                        texture_path = parts[1]
                        if not os.path.isabs(texture_path):
                            full_texture_path = os.path.join(modelDir, texture_path)
                        else:
                            full_texture_path = texture_path
                        materials[current_material]['texture'] = full_texture_path
        
        return materials
    
    except Exception as e:
        print(f"ERRO ao ler arquivo MTL {mtlFileName}: {e}")
        return materials


def loadOBJ(fileName):
    """
    Carrega modelo 3D no formato OBJ com suporte a múltiplos materiais.
    Suporta vértices, coordenadas de textura e faces triangulares.
    Também detecta e carrega arquivo MTL associado.
    
    Separa a malha em sub-malhas por material, criando um VAO/VBO para cada material.
    
    Args:
        fileName: Caminho para o arquivo .obj
    
    Returns:
        Lista de sub-malhas: [{'vao': vaoId, 'count': vertexCount, 'material': material_name}, ...]
        Se não houver materiais, retorna uma única sub-malha com material None.
        Retorna None em caso de erro.
    """
    vertex_positions = []
    vertex_textures = []
    vertex_normals = []
    
    # Material library e materiais
    mtl_file = None
    materials = {}
    model_dir = os.path.dirname(os.path.abspath(fileName))
    
    # Rastrear material ativo e faces por material
    current_material = None
    faces_by_material = {}  # {material_name: [faces]}
    
    # Ler arquivo OBJ (formato texto)
    try:
    
        with open(fileName, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                
                # Material library (mtllib)
                if parts[0] == 'mtllib':
                    if len(parts) > 1:
                        mtl_file = parts[1]
                        materials = loadMTL(mtl_file, model_dir)
                
                # Usar material (usemtl)
                elif parts[0] == 'usemtl':
                    if len(parts) > 1:
                        current_material = parts[1]
                        if current_material not in faces_by_material:
                            faces_by_material[current_material] = []
                
                # Vértices (posição)
                elif parts[0] == 'v':
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    vertex_positions.append([x, y, z])
                
                # Coordenadas de textura
                elif parts[0] == 'vt':
                    u, v = float(parts[1]), float(parts[2])
                    vertex_textures.append([u, v])
                
                elif parts[0] == 'vn':
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    vertex_normals.append([x, y, z])
                
                elif parts[0] == 'f':
                    face_verts = []
                    for i in range(1, len(parts)):
                        vertex_data = parts[i].split('/')
                        v_idx = int(vertex_data[0]) - 1
                        
                        vt_idx = None
                        if len(vertex_data) > 1 and vertex_data[1]:
                            try:
                                vt_idx = int(vertex_data[1]) - 1
                            except (ValueError, IndexError):
                                vt_idx = None
                        
                        vn_idx = None
                        if len(vertex_data) > 2 and vertex_data[2]:
                            try:
                                vn_idx = int(vertex_data[2]) - 1
                            except (ValueError, IndexError):
                                vn_idx = None
                        
                        face_verts.append((v_idx, vt_idx, vn_idx))
                    
                    triangulated_faces = []
                    if len(face_verts) >= 3:
                        triangulated_faces.append([face_verts[0], face_verts[1], face_verts[2]])
                        for i in range(3, len(face_verts)):
                            triangulated_faces.append([face_verts[0], face_verts[i-1], face_verts[i]])
                    
                    material_key = current_material if current_material else None
                    if material_key not in faces_by_material:
                        faces_by_material[material_key] = []
                    faces_by_material[material_key].extend(triangulated_faces)
    
    except UnicodeDecodeError:
    
        return None
    except FileNotFoundError:
        return None
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None
    
    
    if not faces_by_material:
        return None
    
    
    sub_meshes = []
    
    for material_name, face_indices in faces_by_material.items():
        if not face_indices:
            continue
        
        final_vertices = []
        for face in face_indices:
            for v_idx, vt_idx, vn_idx in face:
                if v_idx >= 0 and v_idx < len(vertex_positions):
                    pos = vertex_positions[v_idx]
                    pos_list = [float(pos[0]), float(pos[1]), float(pos[2])]
                else:
                    pos_list = [0.0, 0.0, 0.0]
                
                if vn_idx is not None and vn_idx >= 0 and vn_idx < len(vertex_normals):
                    norm = vertex_normals[vn_idx]
                    norm_list = [float(norm[0]), float(norm[1]), float(norm[2])]
                else:
                    norm_list = [0.0, 1.0, 0.0]
                
                if vt_idx is not None and vt_idx >= 0 and vt_idx < len(vertex_textures):
                    uv = vertex_textures[vt_idx]
                    uv_list = [float(uv[0]), float(uv[1])]
                else:
                    uv_list = [0.0, 0.0]
                
                final_vertices.append([
                    pos_list[0], pos_list[1], pos_list[2],
                    norm_list[0], norm_list[1], norm_list[2],
                    uv_list[0], uv_list[1]
                ])
        
        if not final_vertices:
            continue
        
        vertices_array = np.array(final_vertices, dtype=np.float32)
        
        # Criar VAO e VBO para esta sub-malha
        vaoId = glGenVertexArrays(1)
        glBindVertexArray(vaoId)
        
        vboId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vboId)
        glBufferData(GL_ARRAY_BUFFER, vertices_array.nbytes, vertices_array, GL_STATIC_DRAW)
        
        # Atributos: posição (0), normal (2) e textura (1)
        # Formato: [x, y, z, nx, ny, nz, u, v] - 8 floats = 32 bytes
        stride = 8 * 4  # 8 floats * 4 bytes cada
        
        glEnableVertexAttribArray(0)  # Posição
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)  # Textura (coordenada UV)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6*4))  # u, v após normal
        
        glEnableVertexAttribArray(2)  # Normal
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3*4))  # nx, ny, nz após posição
        
        glBindVertexArray(0)
        
        vertex_count = len(final_vertices)
        print(f"DEBUG: Sub-malha criada para material '{material_name}': {vertex_count} vértices")
        
        # Armazenar informações do material
        material_info = None
        if material_name and material_name in materials:
            material_info = materials[material_name]
        
        sub_meshes.append({
            'vao': vaoId,
            'count': vertex_count,
            'material': material_name,
            'texture': material_info.get('texture') if material_info else None,
            'color': material_info.get('color') if material_info else None,
        })
    
    if not sub_meshes:
        print(f"AVISO: Nenhuma sub-malha válida criada para {fileName}")
        return None
    
    print(f"DEBUG: Total de {len(sub_meshes)} sub-malha(s) criada(s)")
    return sub_meshes


def addProp(model_path, texture_path, position, scale=(1.0, 1.0, 1.0), rotation=0.0):
    global props
    
    here = os.path.dirname(os.path.abspath(__file__))
    
    full_model_path = os.path.join(here, model_path)
    if not os.path.exists(full_model_path):
        return
    
    file_ext = os.path.splitext(model_path)[1].lower()
    if file_ext != '.obj':
        return
    
    sub_meshes = loadOBJ(full_model_path)
    if sub_meshes is None or len(sub_meshes) == 0:
        return
    
    override_texture_id = None
    if texture_path:
        full_texture_path = os.path.join(here, texture_path)
        if os.path.exists(full_texture_path):
            override_texture_id = resources.loadTexture(full_texture_path)
        else:
            return
    
    processed_sub_meshes = []
    for sub_mesh in sub_meshes:
        texture_id = None
        material_color = None
        
        if override_texture_id:
            texture_id = override_texture_id
        else:
            texture_path_mtl = sub_mesh.get('texture')
            if texture_path_mtl and os.path.exists(texture_path_mtl):
                texture_id = resources.loadTexture(texture_path_mtl)
            else:
                return
                material_color = sub_mesh.get('color')
                if material_color:
                    print(f"INFO: Usando cor do MTL (material '{sub_mesh['material']}'): {material_color}")
        
        processed_sub_meshes.append({
            'vao': sub_mesh['vao'],
            'count': sub_mesh['count'],
            'material': sub_mesh['material'],
            'texture': texture_id,
            'color': material_color,
        })
    
    # Adicionar prop à lista
    props.append({
        'sub_meshes': processed_sub_meshes,  # Lista de sub-malhas
        'pos': position,
        'scale': scale,
        'rotation': rotation,
    })
    print(f"INFO: Prop adicionado: {model_path} em {position} (escala: {scale}, rotação: {rotation}°)")


def init():
    """
    Inicializa o sistema de props.
    Limpa a lista de props.
    
    Props podem ser adicionados via addProp() em map.py::init() ou aqui.
    """
    global props
    props = []


def render(modelMatrix_loc):
    """
    Renderiza todos os props do mundo.
    
    Suporta modelos com múltiplos materiais, renderizando cada sub-malha
    com seu material correspondente (textura ou cor).
    
    Args:
        modelMatrix_loc: Localização do uniform modelMatrix no shader
    """
    global props
    
    if len(props) == 0:
        return  # Nenhum prop para renderizar
    
    shader_id = glGetInteger(GL_CURRENT_PROGRAM)
    use_color_loc = None
    object_color_loc = None
    if shader_id:
        use_color_loc = glGetUniformLocation(shader_id, 'useColor')
        object_color_loc = glGetUniformLocation(shader_id, 'objectColor')
    
    for prop in props:
        sub_meshes = prop.get('sub_meshes', [])
        pos = prop['pos']
        scale = prop['scale']
        rotation = prop['rotation']
        
        modelMatrix = glm.mat4(1.0)
        
        modelMatrix = glm.translate(modelMatrix, glm.vec3(pos[0], pos[1], pos[2]))
        
        if rotation != 0.0:
            modelMatrix = glm.rotate(modelMatrix, glm.radians(rotation), glm.vec3(0.0, 1.0, 0.0))
        
        # 3. Escalar
        modelMatrix = glm.scale(modelMatrix, glm.vec3(scale[0], scale[1], scale[2]))
        
        # Enviar matriz (uma vez por prop)
        glUniformMatrix4fv(modelMatrix_loc, 1, GL_FALSE, glm.value_ptr(modelMatrix))
        
        # Renderizar cada sub-malha com seu material
        for sub_mesh in sub_meshes:
            # Bind VAO desta sub-malha
            glBindVertexArray(sub_mesh['vao'])
            
            # Garantir que estamos no slot de textura correto
            glActiveTexture(GL_TEXTURE0)
            
            # Selecionar textura ou cor a usar para este material
            texture = sub_mesh.get('texture')
            color = sub_mesh.get('color')
            
            if texture:
                # Usar textura do material
                glBindTexture(GL_TEXTURE_2D, texture)
                if use_color_loc != -1:
                    glUniform1i(use_color_loc, 0)  # Usar textura
            elif color:
                # Usar cor do material quando não houver textura
                glBindTexture(GL_TEXTURE_2D, 0)
                if use_color_loc != -1 and object_color_loc != -1:
                    glUniform1i(use_color_loc, 1)  # Usar cor
                    glUniform3f(object_color_loc, color[0], color[1], color[2])  # Cor do MTL
            else:
                # Sem textura e sem cor - usar cor padrão
                glBindTexture(GL_TEXTURE_2D, 0)
                if use_color_loc != -1 and object_color_loc != -1:
                    glUniform1i(use_color_loc, 1)  # Usar cor
                    glUniform3f(object_color_loc, 0.5, 0.5, 0.5)  # Cor padrão cinza
            
            # Draw call para esta sub-malha
            glDrawArrays(GL_TRIANGLES, 0, sub_mesh['count'])
        
        # Restaurar uso de textura para outros objetos
        if use_color_loc != -1:
            glUniform1i(use_color_loc, 0)  # Voltar para textura
    
    # Limpar bindings
    glBindVertexArray(0)


def getProps():
    """
    Retorna a lista de todos os props no mundo.
    
    Returns:
        Lista de props (cada prop é um dicionário com 'pos', 'scale', 'rotation', etc)
    """
    return props


def checkPropCollision(world_x, world_z, player_radius=0.5, player_y=None):
    """
    Verifica se a posição (world_x, world_z) colide com algum prop 3D.
    Usa colisão cilíndrica no plano XZ e considera altura Y.
    
    Cada prop tem uma área de colisão simples baseada em sua posição e escala:
    - Cilindro no plano XZ (raio = max(scale_x, scale_z) * 0.5 * TILE_SIZE)
    - Altura do prop: base Y até base Y + scale_y * altura_modelo
    
    Args:
        world_x: Posição X do jogador no mundo
        world_z: Posição Z do jogador no mundo
        player_radius: Raio do jogador no plano XZ (default: 0.5 = metade do tile)
        player_y: Altura Y do jogador (opcional, usado para verificar se está na altura do prop)
    
    Returns:
        True se há colisão com algum prop, False caso contrário
    """
    global props
    import world_config
    
    if len(props) == 0:
        return False
    
    # Constante: assume que modelos de props têm altura padrão (~10 unidades sem escala)
    # Escalado pela escala Y do prop
    DEFAULT_MODEL_HEIGHT = 10.0  # Altura típica de um modelo de árvore sem escala
    
    for prop in props:
        prop_pos = prop['pos']
        prop_scale = prop['scale']
        # prop_rotation = prop.get('rotation', 0.0)  # Não usado para colisão cilíndrica
        
        # Calcular raio do prop no plano XZ (cilindro)
        # A escala já está em unidades do mundo
        # Assumindo que modelos de props têm dimensões base de ~10 unidades
        # Com escala (0.1, 0.1, 0.1), o modelo escalado tem ~1.0 unidade de largura
        # O raio seria metade disso: ~0.5 tiles
        # Para cálculo genérico: raio = max(scale_x, scale_z) * modelo_base_largura * 0.5
        # modelo_base_largura ~10 unidades, então: max(0.1, 0.1) * 10 * 0.5 = 0.5
        model_base_width = 10.0  # Largura base típica do modelo sem escala
        prop_radius_xz = max(prop_scale[0], prop_scale[2]) * model_base_width * 0.5
        
        # Posição do prop no plano XZ (centro do cilindro)
        prop_x = prop_pos[0]
        prop_z = prop_pos[2]
        
        # Calcular distância 2D do jogador ao centro do prop (no plano XZ)
        dist_x = world_x - prop_x
        dist_z = world_z - prop_z
        dist_2d = math.sqrt(dist_x * dist_x + dist_z * dist_z)
        
        # Verificar colisão no plano XZ (círculos sobrepostos)
        if dist_2d < (player_radius + prop_radius_xz):
            # Colisão no plano XZ detectada - agora verificar altura Y
            
            if player_y is not None:
                # Calcular altura do prop
                # Base do prop está em prop_pos[1] (já posicionado no topo do tile)
                # A altura do prop é scale_y * altura_modelo
                # Como os props são posicionados no topo do tile, a base do prop está em prop_pos[1]
                # e o topo está em prop_pos[1] + scale_y * altura_modelo
                prop_base_y = prop_pos[1]
                prop_height = prop_scale[1] * DEFAULT_MODEL_HEIGHT
                prop_top_y = prop_base_y + prop_height
                
                # Verificar se o jogador está dentro da altura do prop
                # Jogador tem ~2.0 de altura (PLAYER_HEIGHT), então verificar se base ou topo do jogador colidem
                player_base_y = player_y  # Posição Y do jogador é a base (pés)
                player_top_y = player_y + world_config.PLAYER_HEIGHT  # Topo do jogador (cabeça)
                
                # Colisão de altura: se o jogador (pés ou cabeça) está dentro da altura do prop
                if (player_base_y <= prop_top_y and player_top_y >= prop_base_y):
                    # Colisão completa: plano XZ e altura Y
                    return True
            else:
                # Se não fornecer player_y, assumir colisão apenas no plano XZ
                # (mais permissivo - permite colisão se estiver no mesmo plano horizontal)
                return True
    
    return False
