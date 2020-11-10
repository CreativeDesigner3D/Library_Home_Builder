import bpy
import os
from . import home_builder_utils
from . import home_builder_paths
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
        library_path = home_builder_paths.get_library_path()
        dirs = os.listdir(library_path)
        for d in dirs:
            path = os.path.join(library_path,d)
            if os.path.isdir(path):
                layout.operator('home_builder.change_library_category',text=d,icon='FILEBROWSER').category = d


class HOME_BUILDER_PT_library_settings(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Library"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 32

    def draw(self, context):
        layout = self.layout
        props = home_builder_utils.get_scene_props(context.scene)
        props.draw(layout)


class HOME_BUILDER_MT_asset_commands_menu(bpy.types.Menu):
    bl_label = "Asset Commands"

    def draw(self, context):

        props = home_builder_utils.get_scene_props(context.scene)
        path = props.get_active_category_path()
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator('home_builder.save_asset_to_library',icon='BACK')
        layout.operator('home_builder.create_thumbnails_for_selected_assets',icon='FILE_IMAGE')
        layout.operator('home_builder.open_browser_window',icon='FILEBROWSER').path = path
        layout.operator('home_builder.create_library_pdf',icon='FILE')
        layout.operator('home_builder.create_new_asset',icon='ADD')
        


class HOME_BUILDER_MT_pointer_menu(bpy.types.Menu):
    bl_label = "Pointer Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator('home_builder.reload_pointers',icon='FILE_REFRESH')


class HOME_BUILDER_UL_assets(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)
        layout.prop(item,'is_selected',text="")

classes = (
    FILEBROWSER_PT_home_builder_headers,
    HOME_BUILDER_MT_category_menu,
    HOME_BUILDER_PT_library_settings,
    HOME_BUILDER_MT_asset_commands_menu,
    HOME_BUILDER_UL_assets,
    HOME_BUILDER_MT_pointer_menu,
)

register, unregister = bpy.utils.register_classes_factory(classes)        
