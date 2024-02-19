bl_info = {
    "name": "HPTM Tools Shelfs",
    "author": "HPTM",
    "version": (0, 0, 1),
    "blender": (4, 0, 2),
    "location": "View3D > UI > Tools Shelfs",
    "description": "Add a Tools Shelf UI for HPTM",
    "doc_url": "{BLENDER_MANUAL_URL}/addons/3d_view/math_vis_console.html",
    "support": "COMMUNITY",
    "category": "3D View",
    "warning": "wwww",
    "tracker_url": "wwww",
}

import bpy
from bpy.types import Operator, Panel, Menu
from bpy.props import StringProperty, PointerProperty, BoolProperty

import os
import io
import tempfile
import requests
import zipfile
import shutil

# GitHub repository information
GITHUB_REPO_OWNER = "HippotamusZz"
GITHUB_REPO_NAME = "BlenderToolsShelftUI"
GITHUB_RELEASE_TAG = ".".join(map(str, bl_info["version"]))

def download_and_extract_release():
    try:
        # Download the main branch zip file from GitHub
        zip_url = f"https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/archive/main.zip"
        response = requests.get(zip_url, stream=True)
        
        # Check if the request was successful (status code 200)
        response.raise_for_status()

        # Create a temporary directory to extract the contents
        temp_dir = tempfile.mkdtemp()

        # Save the zip file to disk
        zip_path = os.path.join(temp_dir, 'addon_update.zip')
        with open(zip_path, 'wb') as zip_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    zip_file.write(chunk)

        # Extract the contents of the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Clean up the downloaded zip file
        os.remove(zip_path)

        return temp_dir

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        raise Exception(f"Failed to download from {zip_url}. HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        raise Exception(f"Failed to download from {zip_url}. Error: {e}")


# Main Class
class HPTMPanel(bpy.types.Panel):
    bl_label = "HPTM - Tools Shelfs UI"
    bl_idname = "VIEW_3D_PT_HPTM_UI"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tools Shelfs UI"

    def draw(self, context):
        layout = self.layout

        # Head
        row = layout.row()
        row.label(text=f"Tools Shelfs UI {GITHUB_RELEASE_TAG}", icon='BLENDER')
    
        # Purge Button
        row.operator("addon.update_from_github", text="Update from GitHub", icon="URL")
        row = layout.row()
        row.operator("outliner.orphans_purge", text="Purge", icon="ERROR")
   
        layout.separator(factor=2)

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

        # Operator to delete objects by name
        row.operator("object.delete_objects", text="Delete By Name", icon="CANCEL")
        layout.separator(factor=1)

        # Create Objects
        box = layout.box()
        box.label(text="Object", icon='OUTLINER_OB_MESH')
        box.menu("OBJECT_MT_create_objects_menu", text="Add Object", icon='MESH_CUBE')
        layout.separator(factor=1)

        # Display custom text based on the checkbox status
        box = layout.box()
        box.label(text="Text", icon='FILE_FONT')
        box.prop(context.scene, "show_custom_text", text="Custom Text")
        box.prop(context.scene, "show_custom_font", text="Custom Font")

        if context.scene.show_custom_text:
            box.prop(context.scene, "custom_text", text="")

        if context.scene.show_custom_font:
            box.prop(context.scene, "custom_font_path", text="Custom Font")


        # Create Text
        box.operator("object.add_text_operator", text="Add Text")
        layout.separator(factor=1)

        # Create Camera
        box = layout.box()
        box.label(text="Camera", icon='CAMERA_DATA')
        box.operator("object.camera_add", text="Camera", icon="VIEW_CAMERA")
        layout.separator(factor=1)


# Sub Class
# Import Panel Class
class HPTMPanel_IMPORT(bpy.types.Panel):
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
class HPTMPanel_EXPORT(bpy.types.Panel):
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


class OBJECT_MT_create_objects_menu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_create_objects_menu"
    bl_label = "Create Objects"

    def draw(self, context):
        layout = self.layout
        primitives = [
            ("Cube", "MESH_CUBE"),
            ("Cylinder", "MESH_CYLINDER"),
            ("Ico_Sphere", "MESH_UVSPHERE"),
            ("Uv_Sphere", "MESH_UVSPHERE"),
            ("Plane", "MESH_PLANE"),
            ("Circle", "MESH_CIRCLE"),
            ("Cone", "MESH_CONE"),
            ("Torus", "MESH_TORUS"),
        ]

        for label, icon in primitives:
            operator_name = "mesh.primitive_" + label.lower() + "_add"
            layout.operator(operator_name, text=label, icon=icon)


class HPTM_SetTargetStringOperator(bpy.types.Operator):
    bl_idname = "object.set_target_string"
    bl_label = "Set Target String"

    def execute(self, context):
        selected_objects = context.selected_objects
        if selected_objects:
            context.scene.delete_objects_props.target_string = selected_objects[0].name

        return {'FINISHED'}


# Delete Objects Operator
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


# Delete Objects Properties
class HPTM_DeleteObjectsProps(bpy.types.PropertyGroup):
    target_string: bpy.props.StringProperty(
        name="Object Name",
        default="object name",
        description="Objects containing this string in their name will be deleted"
    )


# Add Text Operator
class HPTM_AddTextOperator(Operator):
    bl_label = "Add Text"
    bl_idname = "object.add_text_operator"

    def execute(self, context):
        custom_text = context.scene.custom_text or "HPTM"

        if custom_text:
            bpy.ops.object.text_add()
            text_obj = bpy.context.active_object
            text_obj.data.body = custom_text

        else:
            custom_text = "HPTM"
            bpy.ops.object.text_add()
            text_obj = bpy.context.active_object
            text_obj.data.body = custom_text

        if context.scene.show_custom_font and context.scene.custom_font_path:
            text_obj.data.font = bpy.data.fonts.load(context.scene.custom_font_path)

        return {'FINISHED'}


class HPTM_RepeatObjectOperator(Operator):
    bl_idname = "object.repeat_object"
    bl_label = "Repeat Object"
    bl_description = "Duplicates the selected object"

    def execute(self, context):
        # Duplicate selected object
        bpy.ops.object.duplicate(linked=False)
        return {'FINISHED'}

# Operator to update the add-on from GitHub
class UpdateFromGitHubOperator(bpy.types.Operator):
    bl_idname = "addon.update_from_github"
    bl_label = "Update from GitHub"
    bl_description = "Update the add-on to the latest version from GitHub"

    def execute(self, context):
        temp_dir = download_and_extract_release()

        addon_dir = os.path.dirname(os.path.realpath(__file__))
        for item in os.listdir(temp_dir):
            src = os.path.join(temp_dir, item)
            dst = os.path.join(addon_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, symlinks=True)
            else:
                shutil.copy2(src, dst)

        shutil.rmtree(temp_dir)

        bpy.ops.script.reload()

        self.report({'INFO'}, "Add-on updated successfully")
        return {'FINISHED'}

# Register classes
classes = (
    HPTMPanel,
    HPTMPanel_IMPORT,
    HPTMPanel_EXPORT,
    HPTM_DeleteObjectsOperator,
    HPTM_DeleteObjectsProps,
    HPTM_AddTextOperator,
    OBJECT_MT_create_objects_menu,
    HPTM_SetTargetStringOperator,
    HPTM_RepeatObjectOperator,
    UpdateFromGitHubOperator,
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
    del bpy.types.Scene.last_action

if __name__ == "__main__":
    register()
