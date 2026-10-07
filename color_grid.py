bl_info = {
    "name": "Color Grid",
    "author": "AI Assistant",
    "version": (1, 0, 0),
    "blender": (5, 1, 0),
    "location": "View3D > Sidebar > Color Grid tab",
    "description": "Create a grid of colored planes in the 3D viewport",
    "support": "TESTING",
    "category": "3D View"
}

import bpy
import json
import os
import math
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import StringProperty, IntProperty, FloatProperty, FloatVectorProperty
from bpy_extras.io_utils import ExportHelper


# ============================================================================
# PROPRIÉTÉS PERSONNALISÉES
# ============================================================================

class ColorGridProperties(PropertyGroup):
    """Propriétés pour l'add-on Color Grid"""
    
    cols: IntProperty(
        name="Colonnes",
        description="Nombre de colonnes dans la grille",
        min=1,
        max=50,
        default=5
    )
    
    rows: IntProperty(
        name="Lignes",
        description="Nombre de lignes dans la grille",
        min=1,
        max=50,
        default=5
    )
    
    spacing: FloatProperty(
        name="Espacement",
        description="Espacement entre les éléments",
        min=0.01,
        max=10.0,
        default=1.0,
        step=0.1
    )
    
    # 4 color pickers pour les 4 coins de la grille
    color_top_left: FloatVectorProperty(
        name="Haut Gauche",
        description="Couleur du coin haut gauche",
        subtype='COLOR',
        default=(1.0, 0.0, 0.0),
        min=0.0,
        max=1.0
    )
    
    color_top_right: FloatVectorProperty(
        name="Haut Droite",
        description="Couleur du coin haut droite",
        subtype='COLOR',
        default=(0.0, 1.0, 0.0),
        min=0.0,
        max=1.0
    )
    
    color_bottom_left: FloatVectorProperty(
        name="Bas Gauche",
        description="Couleur du coin bas gauche",
        subtype='COLOR',
        default=(0.0, 0.0, 1.0),
        min=0.0,
        max=1.0
    )
    
    color_bottom_right: FloatVectorProperty(
        name="Bas Droite",
        description="Couleur du coin bas droite",
        subtype='COLOR',
        default=(1.0, 1.0, 0.0),
        min=0.0,
        max=1.0
    )
    
    # Nom pour le fichier de sauvegarde
    grid_name: StringProperty(
        name="Nom",
        description="Nom de la grille",
        default="Ma Grille"
    )


# ============================================================================
# OPÉRATEUR: TEST BOUTON
# ============================================================================

class COLORGRID_OT_test_button(Operator):
    """Bouton de test"""
    bl_idname = "colorgrid.test_button"
    bl_label = "Bouton Test"
    bl_description = "Bouton de test qui ne fait rien"
    
    def execute(self, context):
        self.report({'INFO'}, "Bouton test cliqué!")
        print("✅ Bouton test cliqué!")
        return {'FINISHED'}


# ============================================================================
# OPÉRATEUR: SAUVER LA GRILLE
# ============================================================================

class COLORGRID_OT_save_grid(Operator):
    """Sauvegarder la configuration actuelle de la grille"""
    bl_idname = "colorgrid.save_grid"
    bl_label = "Sauver la Grille"
    bl_description = "Sauvegarder la configuration des couleurs"
    
    def execute(self, context):
        props = context.scene.color_grid_props
        
        # Créer le dictionnaire de configuration
        config = {
            'grid_name': props.grid_name,
            'cols': props.cols,
            'rows': props.rows,
            'spacing': props.spacing,
            'color_top_left': list(props.color_top_left),
            'color_top_right': list(props.color_top_right),
            'color_bottom_left': list(props.color_bottom_left),
            'color_bottom_right': list(props.color_bottom_right)
        }
        
        # Sauvegarder dans le dossier grids
        grids_dir = r"d:\_blend_colors\grids"
        os.makedirs(grids_dir, exist_ok=True)
        
        # Utiliser le nom de la grille comme nom de fichier
        filename = f"{props.grid_name.replace(' ', '_')}.json"
        file_path = os.path.join(grids_dir, filename)
        
        # Écrire dans le fichier
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        self.report({'INFO'}, f"Grille sauvegardée: {file_path}")
        print(f"✅ Grille sauvegardée: {file_path}")
        return {'FINISHED'}


# ============================================================================
# OPÉRATEUR: CHARGER UNE GRILLE
# ============================================================================

class COLORGRID_OT_load_grid(Operator):
    """Charger une configuration de grille depuis un fichier JSON"""
    bl_idname = "colorgrid.load_grid"
    bl_label = "Charger la Grille"
    bl_description = "Charger une configuration de grille depuis un fichier JSON"
    
    filepath: StringProperty(subtype='FILE_PATH')
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        # Lire le fichier JSON
        with open(self.filepath, 'r') as f:
            config = json.load(f)
        
        props = context.scene.color_grid_props
        
        # Appliquer la configuration
        props.grid_name = config.get('grid_name', 'Ma Grille')
        props.cols = config.get('cols', 5)
        props.rows = config.get('rows', 5)
        props.spacing = config.get('spacing', 1.0)
        
        if 'color_top_left' in config:
            props.color_top_left = tuple(config['color_top_left'])
        if 'color_top_right' in config:
            props.color_top_right = tuple(config['color_top_right'])
        if 'color_bottom_left' in config:
            props.color_bottom_left = tuple(config['color_bottom_left'])
        if 'color_bottom_right' in config:
            props.color_bottom_right = tuple(config['color_bottom_right'])
        
        self.report({'INFO'}, f"Grille chargée: {config.get('grid_name', 'Inconnue')}")
        return {'FINISHED'}


# ============================================================================
# OPÉRATEUR: LISTER LES GRILLES SAUVEGARDÉES
# ============================================================================

class COLORGRID_OT_load_saved_grid(Operator):
    """Charger une grille depuis le dossier des grilles sauvegardées"""
    bl_idname = "colorgrid.load_saved_grid"
    bl_label = "Charger Grille Sauvegardée"
    bl_description = "Charger une grille depuis le dossier des grilles sauvegardées"
    
    filename: StringProperty(description="Nom du fichier JSON à charger")
    
    def execute(self, context):
        # Dossier de sauvegarde
        grids_dir = r"d:\_blend_colors\grids"
        file_path = os.path.join(grids_dir, self.filename)
        
        if not os.path.exists(file_path):
            self.report({'ERROR'}, f"Fichier non trouvé: {file_path}")
            return {'CANCELLED'}
        
        # Lire le fichier JSON
        with open(file_path, 'r') as f:
            config = json.load(f)
        
        props = context.scene.color_grid_props
        
        # Appliquer la configuration
        props.grid_name = config.get('grid_name', 'Ma Grille')
        props.cols = config.get('cols', 5)
        props.rows = config.get('rows', 5)
        props.spacing = config.get('spacing', 1.0)
        
        if 'color_top_left' in config:
            props.color_top_left = tuple(config['color_top_left'])
        if 'color_top_right' in config:
            props.color_top_right = tuple(config['color_top_right'])
        if 'color_bottom_left' in config:
            props.color_bottom_left = tuple(config['color_bottom_left'])
        if 'color_bottom_right' in config:
            props.color_bottom_right = tuple(config['color_bottom_right'])
        
        self.report({'INFO'}, f"Grille chargée: {config.get('grid_name', 'Inconnue')}")
        print(f"✅ Grille chargée: {config.get('grid_name', 'Inconnue')}")
        return {'FINISHED'}


class COLORGRID_OT_list_grids(Operator):
    """Lister les grilles sauvegardées dans le dossier de l'add-on"""
    bl_idname = "colorgrid.list_grids"
    bl_label = "Grilles Sauvegardées"
    bl_description = "Lister les grilles sauvegardées"
    
    grids: bpy.props.CollectionProperty(type=bpy.props.StringProperty)
    
    def execute(self, context):
        # Dossier de sauvegarde
        addon_dir = os.path.dirname(os.path.dirname(__file__))
        grids_dir = os.path.join(addon_dir, "grids")
        
        if not os.path.exists(grids_dir):
            self.report({'INFO'}, "Aucune grille sauvegardée trouvée")
            return {'CANCELLED'}
        
        # Lister les fichiers JSON
        json_files = [f for f in os.listdir(grids_dir) if f.endswith('.json')]
        
        if not json_files:
            self.report({'INFO'}, "Aucune grille sauvegardée trouvée")
            return {'CANCELLED'}
        
        # Afficher les grilles dans le terminal
        print("=== Grilles sauvegardées ===")
        for i, filename in enumerate(json_files, 1):
            file_path = os.path.join(grids_dir, filename)
            with open(file_path, 'r') as f:
                config = json.load(f)
            print(f"{i}. {config.get('grid_name', filename)} ({filename})")
        
        self.report({'INFO'}, f"{len(json_files)} grille(s) trouvée(s)")
        return {'FINISHED'}


# ============================================================================
# OPÉRATEUR: GÉNÉRER LA GRILLE
# ============================================================================

class COLORGRID_OT_generate_grid(Operator):
    """Générer une grille de planes colorés dans la scène"""
    bl_idname = "colorgrid.generate_grid"
    bl_label = "Générer la Grille"
    bl_description = "Créer une grille de planes colorés dans une collection 'tiles'"
    
    def execute(self, context):
        props = context.scene.color_grid_props
        
        cols = props.cols
        rows = props.rows
        
        # Récupérer les 4 couleurs des coins
        color_tl = props.color_top_left    # Haut Gauche
        color_tr = props.color_top_right   # Haut Droite
        color_bl = props.color_bottom_left # Bas Gauche
        color_br = props.color_bottom_right # Bas Droite
        
        # Créer les couleurs pour chaque cellule par interpolation bilinéaire
        colors = []
        for row in range(rows):
            for col in range(cols):
                # Facteurs d'interpolation (0.0 à 1.0)
                x_factor = (col / (cols - 1)) if cols > 1 else 0.0
                y_factor = (1.0 - row / (rows - 1)) if rows > 1 else 0.0
                
                # Interpolation bilinéaire
                r = (color_bl[0] * (1 - x_factor) + color_br[0] * x_factor) * (1 - y_factor) + \
                    (color_tl[0] * (1 - x_factor) + color_tr[0] * x_factor) * y_factor
                g = (color_bl[1] * (1 - x_factor) + color_br[1] * x_factor) * (1 - y_factor) + \
                    (color_tl[1] * (1 - x_factor) + color_tr[1] * x_factor) * y_factor
                b = (color_bl[2] * (1 - x_factor) + color_br[2] * x_factor) * (1 - y_factor) + \
                    (color_tl[2] * (1 - x_factor) + color_tr[2] * x_factor) * y_factor
                
                colors.append((r, g, b))
        
        # Gérer la collection "tiles"
        collection_name = "tiles"
        collection = bpy.data.collections.get(collection_name)
        
        if collection:
            # Collection existe: supprimer tous les objets et la collection
            for obj in list(collection.objects):
                collection.objects.unlink(obj)
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(collection)
            print(f"✅ Collection '{collection_name}' supprimée")
        
        # Recréer la collection "tiles"
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)
        print(f"✅ Collection '{collection_name}' recréée")
        
        # Supprimer les anciens matériaux ColorTile_*
        for mat in list(bpy.data.materials):
            if mat.name.startswith("ColorTile_"):
                bpy.data.materials.remove(mat)
        print(f"✅ Anciens matériaux supprimés")
        
        # Calculer la position centrale
        total_width = (cols - 1) * props.spacing
        total_height = (rows - 1) * props.spacing
        start_x = -total_width / 2.0
        start_y = total_height / 2.0
        
        # OPTIMISATION: Créer un seul objet avec toutes les faces au lieu de 2500 objets
        print(f"🚀 Création d'une grille {cols}x{rows} avec optimisation...")
        
        # Préparer les vertices et faces
        vertices = []
        faces = []
        vertex_colors = []
        
        for row in range(rows):
            for col in range(cols):
                index = row * cols + col
                color = colors[index]
                
                # Position de la tuile
                x = start_x + col * props.spacing
                y = start_y - row * props.spacing
                
                # 4 coins de la tuile (vertices)
                half = props.spacing / 2.0
                v0 = (x - half, y - half, 0)  # bas gauche
                v1 = (x + half, y - half, 0)  # bas droite
                v2 = (x + half, y + half, 0)  # haut droite
                v3 = (x - half, y + half, 0)  # haut gauche
                
                base_idx = len(vertices)
                vertices.extend([v0, v1, v2, v3])
                faces.append((base_idx, base_idx + 1, base_idx + 2, base_idx + 3))
                
                # 4 couleurs pour la face (une par vertex)
                vertex_colors.extend([color] * 4)
        
        # Créer le mesh à partir des données
        mesh = bpy.data.meshes.new("ColorGridMesh")
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        
        # Créer l'objet
        obj = bpy.data.objects.new("ColorGrid", mesh)
        collection.objects.link(obj)
        
        # Ajouter les vertex colors (domain CORNER pour interpolation aux sommets)
        color_attribute = mesh.color_attributes.new(name="Color", type='BYTE_COLOR', domain='CORNER')
        
        # Assigner les couleurs à chaque vertex (coin de face) - Blender attend 4 canaux (RGBA)
        for i, color in enumerate(color_attribute.data):
            if i < len(color_attribute.data):
                # S'assurer que chaque couleur a 4 canaux (ajouter alpha si nécessaire)
                c = vertex_colors[i]
                if len(c) == 3:
                    c = c + (1.0,)  # Ajouter alpha = 1.0
                color.color = c
        
        # Créer un seul matériau pour toute la grille
        mat_name = "ColorGrid_Material"
        if mat_name in bpy.data.materials:
            mat = bpy.data.materials[mat_name]
        else:
            mat = bpy.data.materials.new(name=mat_name)
            mat.use_nodes = True
            
            # Supprimer le node Principled BSDF par défaut
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            mat.node_tree.nodes.remove(bsdf)
            
            # Créer le node Emission
            emission = mat.node_tree.nodes.new(type="ShaderNodeEmission")
            emission.inputs['Strength'].default_value = 1.0
            
            # Créer le node Vertex Color
            vertex_color = mat.node_tree.nodes.new(type="ShaderNodeVertexColor")
            vertex_color.layer_name = "Color"
            
            # Connecter Vertex Color -> Emission Color -> Material Output
            output = mat.node_tree.nodes["Material Output"]
            mat.node_tree.links.new(vertex_color.outputs['Color'], emission.inputs['Color'])
            mat.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
        
        # Appliquer le matériau
        obj.data.materials.append(mat)
        
        print(f"✅ Grille créée avec succès: {len(faces)} tuiles dans 1 objet")
        
        # Ajuster la caméra pour englober toute la grille
        _frame_selected_object(obj)
        
        # Forcer le rafraîchissement des vues 3D
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        self.report({'INFO'}, f"Grille générée : {cols}x{rows} ({cols * rows} éléments)")
        return {'FINISHED'}


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def _frame_selected_object(obj):
    """Placer la caméra au-dessus de l'objet et regarder vers le bas"""
    scene = bpy.context.scene
    
    # Obtenir le centre de l'objet
    center = obj.location
    
    # Calculer la taille de la grille avec le bounding box monde
    bpy.context.view_layer.update()
    world_bbox = obj.bound_box
    coords = [v[:] for v in world_bbox]  # Convertir en tuples
    
    x_min = min(c[0] for c in coords)
    x_max = max(c[0] for c in coords)
    y_min = min(c[1] for c in coords)
    y_max = max(c[1] for c in coords)
    
    x_size = x_max - x_min
    y_size = y_max - y_min
    max_size = max(x_size, y_size)
    
    # Créer ou récupérer la caméra
    camera = scene.camera
    if not camera:
        cam_data = bpy.data.cameras.new("ColorGridCamera")
        cam_obj = bpy.data.objects.new("ColorGridCamera", cam_data)
        scene.collection.objects.link(cam_obj)
        scene.camera = cam_obj
        camera = cam_obj
    
    # Calculer la distance optimale pour cadrer la grille
    # Utiliser le champ de vision vertical (le plus restrictif)
    sensor_height = camera.data.sensor_height
    focal_length = camera.data.lens
    
    # Champ de vision vertical
    fov_y = 2 * math.atan(sensor_height / (2 * focal_length))
    
    # Calculer la hauteur nécessaire pour cadrer le plus grand côté
    # Avec une marge de 15%
    half_size = max_size / 2
    margin = 1.15  # 15% de marge
    height = (half_size * margin) / math.tan(fov_y / 2)
    
    # Positionner la caméra directement au-dessus du centre
    camera.location = (center.x, center.y, center.z + height)
    
    # Rotation à 0,0,0 - la caméra pointe déjà vers le bas par défaut
    camera.rotation_euler = (0.0, 0.0, 0.0)
    
    # Forcer le recalcul des bornes
    obj.data.update()
    
    # Basculer le viewport en vue caméra
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    if space.region_3d.view_perspective != 'CAMERA':
                        space.region_3d.view_perspective = 'CAMERA'
            area.tag_redraw()
            break
    
    print(f"📷 Caméra top-down: pos={camera.location}, rot={camera.rotation_euler}")
    
    print(f"📷 Caméra placée au-dessus de la grille (hauteur: {height:.2f}m)")


# ============================================================================
# PANNEAU UI
# ============================================================================

class COLORGRID_PT_main_panel(Panel):
    """Panneau principal de l'add-on Color Grid"""
    bl_label = "Color Grid"
    bl_idname = "COLORGRID_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Color Grid"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.color_grid_props
        
        # Configuration de la grille
        layout.label(text="Configuration:")
        row = layout.row()
        row.prop(props, "cols", text="Colonnes")
        row.prop(props, "rows", text="Lignes")
        layout.prop(props, "spacing")
        
        layout.separator()
        
        # 4 color pickers pour les coins
        layout.label(text="Couleurs des coins:")
        
        row = layout.row()
        col1 = row.column()
        col1.prop(props, "color_top_left", text="Haut Gauche")
        col2 = row.column()
        col2.prop(props, "color_top_right", text="Haut Droite")
        
        row = layout.row()
        col1 = row.column()
        col1.prop(props, "color_bottom_left", text="Bas Gauche")
        col2 = row.column()
        col2.prop(props, "color_bottom_right", text="Bas Droite")
        
        layout.separator()
        
        # Bouton de génération
        layout.operator("colorgrid.generate_grid", icon='CHECKMARK')
        
        layout.separator()
        
        # Nom de la grille
        layout.prop(props, "grid_name", text="Nom")
        
        layout.separator()
        
        # Bouton de sauvegarde
        layout.operator("colorgrid.save_grid", icon='CHECKMARK')
        
        layout.separator()
        
        # Liste des grilles sauvegardées
        layout.label(text="Grilles sauvegardées:")
        
        # Dossier de sauvegarde
        grids_dir = r"d:\_blend_colors\grids"
        
        if os.path.exists(grids_dir):
            # Lister les fichiers JSON
            json_files = sorted([f for f in os.listdir(grids_dir) if f.endswith('.json')])
            
            if json_files:
                for filename in json_files:
                    file_path = os.path.join(grids_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            config = json.load(f)
                        grid_name = config.get('grid_name', filename.replace('.json', ''))
                    except:
                        grid_name = filename.replace('.json', '')
                    
                    # Bouton pour charger la grille
                    op = layout.operator("colorgrid.load_saved_grid", text=grid_name, icon='TRIA_RIGHT')
                    op.filename = filename
            else:
                layout.label(text="Aucune grille sauvegardée", icon='INFO')
        else:
            layout.label(text="Aucune grille sauvegardée", icon='INFO')


# ============================================================================
# ENREGISTREMENT / DÉSENFREGISTREMENT
# ============================================================================

classes = (
    ColorGridProperties,
    COLORGRID_OT_generate_grid,
    COLORGRID_OT_test_button,
    COLORGRID_OT_save_grid,
    COLORGRID_OT_load_grid,
    COLORGRID_OT_load_saved_grid,
    COLORGRID_OT_list_grids,
    COLORGRID_PT_main_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.color_grid_props = bpy.props.PointerProperty(type=ColorGridProperties)


def unregister():
    del bpy.types.Scene.color_grid_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
