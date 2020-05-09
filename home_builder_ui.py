import bpy
import os
from . import home_builder_utils
from .pc_lib import pc_utils

class FILEBROWSER_PT_home_builder_headers(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'UI'
    bl_label = "Library"
    bl_category = "Attributes"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        if len(context.area.spaces) > 1:
            pyclone = pc_utils.get_scene_props(context.scene)
            if pyclone.active_library_name == 'Home Builder Library':
                return True   
        return False

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        props = home_builder_utils.get_scene_props(context.scene)

        row = col.row()
        row.scale_y = 1.3       
        row.label(text="Home Builder v0.1",icon='HOME') 
        row.separator()
        row.popover(panel="HOME_BUILDER_PT_library_settings",text="",icon='SETTINGS')

        row = col.row()
        row.scale_y = 1.3
        row.menu('HOME_BUILDER_MT_category_menu',text=props.active_category,icon='FILEBROWSER')


class HOME_BUILDER_MT_category_menu(bpy.types.Menu):
    bl_label = "Library"

    def draw(self, _context):
        layout = self.layout
        library_path = home_builder_utils.get_library_path()
        dirs = os.listdir(library_path)
        for d in dirs:
            path = os.path.join(library_path,d)
            if os.path.isdir(path):
                layout.operator('home_builder.change_library_category',text=d,icon='SCRIPTPLUGINS').category = d


class HOME_BUILDER_PT_library_settings(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Library"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 32

    def draw(self, context):
        layout = self.layout
        props = home_builder_utils.get_scene_props(context.scene)
        props.draw(layout)


classes = (
    FILEBROWSER_PT_home_builder_headers,
    HOME_BUILDER_MT_category_menu,
    HOME_BUILDER_PT_library_settings,
)

register, unregister = bpy.utils.register_classes_factory(classes)        
