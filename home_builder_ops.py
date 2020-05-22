import bpy,os,inspect

from bpy.types import (Header, 
                       Menu, 
                       Panel, 
                       Operator,
                       PropertyGroup)

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       PointerProperty,
                       EnumProperty,
                       CollectionProperty)

from .pc_lib import pc_unit, pc_utils, pc_types
from .walls import library_walls
from .cabinets import cabinet_library
from . import home_builder_utils

class room_builder_OT_activate(Operator):
    bl_idname = "room_builder.activate"
    bl_label = "Activate Room Builder"
    bl_description = "This activates the room builder"
    bl_options = {'UNDO'}
    
    library_name: StringProperty(name='Library Name')

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        library_path = home_builder_utils.get_library_path()
        dirs = os.listdir(library_path)

        if props.active_category in dirs:
            path = os.path.join(library_path,props.active_category)
        else:
            props.active_category = dirs[0]
            path = os.path.join(library_path,props.active_category)

        pc_utils.update_file_browser_path(context,path)
        return {'FINISHED'}

class room_builder_OT_drop(Operator):
    bl_idname = "room_builder.drop"
    bl_label = "Activate Room Builder"
    bl_description = "This is called when an asset is dropped from the home builder library"
    bl_options = {'UNDO'}
    
    filepath: StringProperty(name='Library Name')

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)

        directory, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)

        if props.active_category == 'Walls':
            if 'Archipack' in self.filepath and hasattr(bpy.types,'ARCHIPACK_OT_wall2_draw'):
                bpy.ops.archipack.wall2_draw('INVOKE_DEFAULT')
            else:
                bpy.ops.home_builder.draw_multiple_walls(filepath=self.filepath)

        if props.active_category == 'Cabinets':
            bpy.ops.home_builder.place_cabinet(filepath=self.filepath)

        if props.active_category == 'Fences':
            pass

        if props.active_category == 'Doors':
            bpy.ops.home_builder.place_door(filepath=self.filepath)

        if props.active_category == 'Windows':
            pass

        return {'FINISHED'}


class home_builder_OT_change_library_category(bpy.types.Operator):
    bl_idname = "home_builder.change_library_category"
    bl_label = "Change Library Category"
    bl_description = "This changes the active library category"

    category: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        props.active_category = self.category
        path = os.path.join(home_builder_utils.get_library_path(),self.category)
        if os.path.exists(path):
            pc_utils.update_file_browser_path(context,path)
        return {'FINISHED'}


class KITCHEN_OT_disconnect_constraint(bpy.types.Operator):
    bl_idname = "home_builder.disconnect_constraint"
    bl_label = "Disconnect Constraint"
    
    obj_name: bpy.props.StringProperty(name="Base Point Name")

    def execute(self, context):
        obj = bpy.data.objects[self.obj_name]
        obj.constraints.clear()
        return {'FINISHED'}

classes = (
    room_builder_OT_activate,
    room_builder_OT_drop,
    home_builder_OT_change_library_category,
    KITCHEN_OT_disconnect_constraint,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
