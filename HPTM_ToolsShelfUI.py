bl_info = {
    "name": "HPTM Tools Shelfs",
    "author": "HPTM",
    "version": (0, 0, 1),
    "blender": (4, 0, 2),
    "location": "View3D > UI > Tools Shelfs",
    "description": "Add a Tools Shelf UI for HPTM",
    "support": "COMMUNITY",
    "category": "3D View",
}

import bpy
from bpy.types import Operator, Panel, Menu
import webbrowser

# GitHub repository information
GITHUB_REPO_OWNER = "HippotamusZz"
GITHUB_REPO_NAME = "BlenderToolsShelftUI"
GITHUB_RELEASE_TAG = ".".join(map(str, bl_info["version"]))
GITHUB_REPO_URL = f"https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}"


# Main Class
class HPTMPanel(Panel):
    bl_label = "HPTM - Tools Shelfs UI"
    bl_idname = "VIEW_3D_PT_HPTM_UI"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tools Shelfs UI"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)

        row.label(text=f"Tools Shelfs UI {GITHUB_RELEASE_TAG}", icon='BLENDER')
        row.operator("wm.open_github_page", text="GitHub Page", icon='URL')
        layout.separator(factor=1)
        row = layout.row(align=True)
        row.operator("outliner.orphans_purge", text="Purge", icon="ERROR")
        layout.separator(factor=1)

        # Import & Export
        box = layout.box()
        box.label(text="Import & Export", icon='DOWNARROW_HLT')
        box.popover("VIEW_3D_PT_Import", text="IMPORT", icon='IMPORT')
        box.popover("VIEW_3D_PT_Export", text="EXPORT", icon='EXPORT')
        layout.separator(factor=1)

        # Delete Object by Name
        if context.selected_objects:
            obj = context.selected_objects[0]

            # Rename Object
            row = layout.box()
            row.label(text="Rename", icon='OUTLINER_DATA_GP_LAYER')
            row.prop(obj, "name", text="")
            # Duplicate Object
            row.operator("object.repeat_object", text="Duplicate", icon="DUPLICATE")

            # Delete Object Section
            row.operator("object.delete", text="Delete Select", icon="CANCEL")
            layout.separator(factor=1)

            # Object Transform
            row = layout.row(align=True)
            box = layout.box()
            box.label(text="Transforms", icon='TRANSFORM_ORIGINS')
            split = box.split(factor=0.33)
            coll = [split.column() for _ in range(3)]

            # Define transform properties
            transform_point = [
                ("location", "Location"),
                ("rotation_euler", "Rotation"),
                ("scale", "Scale"),
            ]

            for i, (prop_name, prop_label) in enumerate(transform_point):
                split = box.split(factor=0.33)
                coll[i].prop(obj, prop_name, text=prop_label)

        layout.separator(factor=1)
        row = layout.box()
        row.prop(context.scene.delete_objects_props, "target_string", text="")
        row.operator("object.set_target_string", text="Get Object Name", icon="LINKED")
        row.operator("object.delete_objects", text="Delete By Name", icon="CANCEL")
        layout.separator(factor=1)

        # Create Objects
        box = layout.box()
        box.label(text="Object", icon='OUTLINER_OB_MESH')
        box.menu("OBJECT_MT_create_mesh_menu", text="Add Mesh", icon='MESH_CUBE')
        box.menu("OBJECT_MT_create_curve_menu", text="Add Curve", icon='OUTLINER_OB_CURVE')
        layout.separator(factor=1)

        box = layout.box()
        box.label(text="Text", icon='FILE_FONT')
        split_text = box.split(factor=0.50)
        coll = [split_text.column() for _ in range(2)]

        show_prop_dict = {
            "show_custom_text": ("custom_text", "Custom Text"),
            "show_custom_font": ("custom_font_path", "Custom Font"),
        }

        for i, (key, (properties, value)) in enumerate(show_prop_dict.items()):
            coll[i].prop(context.scene, key, text=value)

            if getattr(context.scene, key):
                box.prop(context.scene, properties, text=value)

        # Create Text
        box.operator("object.add_text_operator", text="Add Text")
        layout.separator(factor=1)

        # Create Camera
        box = layout.box()
        box.label(text="Camera", icon='CAMERA_DATA')
        box.operator("object.camera_add", text="Camera", icon="VIEW_CAMERA")


# Sub Class
# Import Panel Class
class HPTMPanel_IMPORT(Panel):
    bl_label = "Import & Export"
    bl_idname = "VIEW_3D_PT_Import"
    bl_options = {'INSTANCED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="IMPORT", icon='IMPORT')
        row = layout.row()
        formats = [
            ("FBX", "import_scene.fbx"),
            ("STL", "import_mesh.stl"),
            ("ABC", "wm.alembic_export")
        ]
        for label, operator in formats:
            row.operator(operator, text=label)
        layout.separator(factor=1)


# Export Panel Class
class HPTMPanel_EXPORT(Panel):
    bl_label = "Import & Export"
    bl_idname = "VIEW_3D_PT_Export"
    bl_options = {'INSTANCED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="EXPORT", icon='EXPORT')
        row = layout.row()
        formats = [
            ("FBX", "export_scene.fbx"),
            ("STL", "export_mesh.stl"),
            ("ABC", "wm.alembic_export")
        ]
        for label, operator in formats:
            row.operator(operator, text=label)
        layout.separator(factor=1)


class HPTM_CreateMeshMenu(Menu):
    bl_idname = "OBJECT_MT_create_mesh_menu"
    bl_label = "Create Objects"

    def draw(self, context):
        layout = self.layout
        primitives_mesh = [
            ("cube", "Cube", "MESH_CUBE"),
            ("cylinder", "Cylinder", "MESH_CYLINDER"),
            ("ico_sphere", "IcoSphere", "MESH_UVSPHERE"),
            ("uv_sphere", "UvSphere", "MESH_UVSPHERE"),
            ("plane", "Plane", "MESH_PLANE"),
            ("circle", "Circle", "MESH_CIRCLE"),
            ("cone", "Cone", "MESH_CONE"),
            ("torus", "Torus", "MESH_TORUS"),
        ]

        for mesh_name, label, icon in primitives_mesh:
            operator_name = "mesh.primitive_" + mesh_name + "_add"
            layout.operator(operator_name, text=label, icon=icon)


class HPTM_CreateCurveMenu(Menu):
    bl_idname = "OBJECT_MT_create_curve_menu"
    bl_label = "Create Curves"

    def draw(self, context):
        layout = self.layout

        primitives_curve = [
            ("bezier_curve", "Bezier", "CURVE_BEZCURVE"),
            ("bezier_circle", "Circle", "CURVE_BEZCIRCLE"),
            ("nurbs_curve", "Nurbs Curve", "CURVE_NCURVE"),
            ("circle_curve", "Nurbs Circle", "CURVE_NCIRCLE"),
            ("nurbs_path", "Path", "CURVE_BEZCIRCLE"),
        ]

        for curve_name, label, icon in primitives_curve:
            operator_name = "curve.primitive_" + curve_name + "_add"
            layout.operator(operator_name, text=label, icon=icon)


class HPTM_SetTargetStringOperator(Operator):
    bl_idname = "object.set_target_string"
    bl_label = "Set Target String"

    def execute(self, context):
        selected_objects = context.selected_objects
        if selected_objects:
            context.scene.delete_objects_props.target_string = selected_objects[0].name

        return {'FINISHED'}


class HPTM_DeleteObjectsOperator(Operator):
    bl_idname = "object.delete_objects"
    bl_label = "Delete Objects"
    bl_description = "Deletes all objects with the specified name"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        target_string = context.scene.delete_objects_props.target_string
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.context.scene.objects:
            if target_string in obj.name:
                obj.select_set(True)
        bpy.ops.object.delete()
        return {'FINISHED'}


class HPTM_DeleteObjectsProps(bpy.types.PropertyGroup):
    target_string: bpy.props.StringProperty(
        name="Object Name",
        default="object name",
        description="Objects containing this string in their name will be deleted"
    )


class HPTM_AddTextOperator(Operator):
    bl_label = "Add Text"
    bl_idname = "object.add_text_operator"

    def execute(self, context):
        custom_text = context.scene.custom_text
        show_custom_text = context.scene.show_custom_text
        custom_font_path = context.scene.custom_font_path
        show_custom_font = context.scene.show_custom_font

        def add_text_to_scene(text_body):
            bpy.ops.object.text_add()
            text_obj = bpy.context.active_object
            text_obj.data.body = text_body
            return text_obj

        text_body = custom_text if show_custom_text and custom_text else "HPTM"
        text_obj = add_text_to_scene(text_body)

        if show_custom_font and custom_font_path:
            text_obj.data.font = bpy.data.fonts.load(custom_font_path)

        return {'FINISHED'}


class HPTM_RepeatObjectOperator(Operator):
    bl_idname = "object.repeat_object"
    bl_label = "Repeat Object"
    bl_description = "Duplicates the selected object"

    def execute(self, context):
        bpy.ops.object.duplicate(linked=False)
        return {'FINISHED'}


class HPTM_OpenGitHubPage(Operator):
    bl_idname = "wm.open_github_page"
    bl_label = "Open GitHub Page"

    def execute(self, context):
        webbrowser.open(GITHUB_REPO_URL)
        return {'FINISHED'}


# Register classes
classes = (
    HPTM_OpenGitHubPage,

    HPTMPanel,

    HPTMPanel_IMPORT,
    HPTMPanel_EXPORT,

    HPTM_CreateMeshMenu,
    HPTM_CreateCurveMenu,

    HPTM_AddTextOperator,

    HPTM_SetTargetStringOperator,
    HPTM_RepeatObjectOperator,

    HPTM_DeleteObjectsOperator,
    HPTM_DeleteObjectsProps,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.delete_objects_props = bpy.props.PointerProperty(type=HPTM_DeleteObjectsProps)
    bpy.types.Scene.custom_text = bpy.props.StringProperty(name="Custom Text", default="Enter Text Here")
    bpy.types.Scene.show_custom_text = bpy.props.BoolProperty(name="Show Custom Text", default=False)
    bpy.types.Scene.custom_font_path = bpy.props.StringProperty(name="Custom Font", subtype='FILE_PATH')
    bpy.types.Scene.show_custom_font = bpy.props.BoolProperty(name="Show Custom Font", default=False)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.delete_objects_props
    del bpy.types.Scene.custom_text
    del bpy.types.Scene.show_custom_text
    del bpy.types.Scene.custom_font_path
    del bpy.types.Scene.show_custom_font


if __name__ == "__main__":
    register()