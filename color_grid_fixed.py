import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import IntProperty, FloatProperty, FloatVectorProperty


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
        
        # Créer ou vider la collection "tiles"
        collection_name = "tiles"
        collection = bpy.data.collections.get(collection_name)
        
        if collection:
            # Vider la collection existante
            for obj in list(collection.objects):
                collection.objects.unlink(obj)
            bpy.data.collections.remove(collection)
            collection = None
        
        # Créer la collection
        if not collection:
            collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(collection)
        
        # Calculer la position centrale
        total_width = (cols - 1) * props.spacing
        total_height = (rows - 1) * props.spacing
        start_x = -total_width / 2.0
        start_y = total_height / 2.0
        
        # Créer les planes
        mesh_name = "ColorGrid_Mesh"
        if mesh_name in bpy.data.meshes:
            mesh = bpy.data.meshes[mesh_name]
        else:
            mesh = bpy.data.meshes.new(mesh_name)
            mesh.from_pydata([], [], [])
        
        for row in range(rows):
            for col in range(cols):
                index = row * cols + col
                color = colors[index]
                
                # Créer l'objet plane
                obj = bpy.data.objects.new(f"Tile_{row}_{col}", mesh)
                
                # Positionner
                x = start_x + col * props.spacing
                y = start_y - row * props.spacing
                obj.location = (x, y, 0)
                
                # Rotation vue de dessus
                obj.rotation_euler = (0, 0, 0)
                
                # Créer le matériau avec la couleur
                mat_name = f"ColorTile_{index}"
                if mat_name in bpy.data.materials:
                    mat = bpy.data.materials[mat_name]
                else:
                    mat = bpy.data.materials.new(name=mat_name)
                    mat.use_nodes = True
                    # Trouver le node Principled BSDF
                    bsdf = None
                    for node in mat.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            bsdf = node
                            break
                    if bsdf:
                        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
                
                if obj.data.materials:
                    obj.data.materials[0] = mat
                else:
                    obj.data.materials.append(mat)
                
                # Lier à la collection
                collection.objects.link(obj)
        
        self.report({'INFO'}, f"Grille générée : {cols}x{rows} ({cols * rows} éléments)")
        return {'FINISHED'}


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


# ============================================================================
# ENREGISTREMENT / DÉSENFREGISTREMENT
# ============================================================================

classes = (
    ColorGridProperties,
    COLORGRID_OT_generate_grid,
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
