import bpy
import os
from . import home_builder_utils
from . import home_builder_paths
from .pc_lib import pc_utils
from .cabinets import data_cabinets

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

        if props.active_category == 'Custom Cabinets' and context.object:
            obj_bp = pc_utils.get_assembly_bp(context.object)

            if obj_bp:
                row = layout.row()
                row.label(text='Selected Assembly: ' + obj_bp.name)
                row.operator('pc_assembly.select_parent',text="",icon='SORT_DESC')
                row = layout.row()
                row.operator('home_builder.save_custom_cabinet',text="Save Custom Cabinet",icon='SCREEN_BACK')    
            else:
                row = layout.row()
                row.label(text='Selected Assembly to Save')            


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
        layout.separator()
        layout.operator('home_builder.change_library_category',text='Custom Cabinets',icon='FILEBROWSER').category = "Custom Cabinets"


class HOME_BUILDER_PT_library_settings(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_label = "Library"
    bl_region_type = 'HEADER'
    bl_ui_units_x = 32

    def draw(self, context):
        layout = self.layout
        props = home_builder_utils.get_scene_props(context.scene)
        props.draw(layout)


class HOME_BUILDER_PT_home_builder_properties(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Home Builder"
    bl_category = "Home Builder"    
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        props = home_builder_utils.get_scene_props(context.scene)

        box = layout.box()
        row = box.row()
        row.prop(props,'show_2d_view_options',text="2D View Commands",emboss=False,icon='TRIA_DOWN' if props.show_2d_view_options else 'TRIA_RIGHT')            
        if props.show_2d_view_options:
            box.operator('home_builder.create_2d_views',text="Create Wall Elevation Views",icon='CON_SIZELIMIT')
            box.operator('home_builder.create_2d_cabinet_views',text="Create Cabinet Views",icon='CON_SIZELIMIT')

        if not context.object:
            return

        obj_bp = pc_utils.get_assembly_bp(context.object)
        cabinet_bp = home_builder_utils.get_cabinet_bp(context.object)
        exterior_bp = home_builder_utils.get_exterior_bp(context.object)
        wall_bp = home_builder_utils.get_wall_bp(context.object)

        if wall_bp:
            box = layout.box()
            row = box.row()
            row.prop(props,'show_wall_options',text="Wall Commands",emboss=False,icon='TRIA_DOWN' if props.show_wall_options else 'TRIA_RIGHT')
            if props.show_wall_options:
                row = box.row()
                row.operator('home_builder.wall_prompts',text="Wall Prompts",icon='WINDOW')

        if cabinet_bp:
            box = layout.box()
            row = box.row()
            row.prop(props,'show_cabinet_tools',text="Cabinet Commands",emboss=False,icon='TRIA_DOWN' if props.show_cabinet_tools else 'TRIA_RIGHT')
            if props.show_cabinet_tools:
                col = box.column(align=True)
                col.label(text="Name - " + cabinet_bp.name)
                col.operator('home_builder.cabinet_prompts',icon='WINDOW')
                col.operator('home_builder.move_cabinet',text="Place Cabinet",icon='OBJECT_ORIGIN').obj_bp_name = cabinet_bp.name
                col.operator('home_builder.free_move_cabinet',text="Grab",icon='VIEW_PAN').obj_bp_name = cabinet_bp.name
                col.operator('home_builder.duplicate_cabinet',text="Duplicate",icon='DUPLICATE').obj_bp_name = cabinet_bp.name  
                if exterior_bp:
                    col.operator('home_builder.change_cabinet_exterior',text="Change Cabinet Exterior",icon='FILE_REFRESH')
                
                col.operator('home_builder.delete_assembly',text="Delete Cabinet",icon='X').obj_name = cabinet_bp.name
                


            row = box.row()
            row.prop(props,'show_cabinet_front_tools',text="Cabinet Fronts",emboss=False,icon='TRIA_DOWN' if props.show_cabinet_front_tools else 'TRIA_RIGHT')
            if props.show_cabinet_front_tools:
                box.prop(props,'cabinet_door_category',text="",icon='FILE_FOLDER')  
                box.template_icon_view(props,"cabinet_door_name",show_labels=True)              
                row = box.row()
                row.operator('home_builder.update_selected_cabinet_doors',text="Update Selected Front",icon='RESTRICT_SELECT_OFF')

            row = box.row()
            row.prop(props,'show_hardware_tools',text="Cabinet Hardware",emboss=False,icon='TRIA_DOWN' if props.show_hardware_tools else 'TRIA_RIGHT')            
            if props.show_hardware_tools:
                box.prop(props,'pull_category',text="",icon='FILE_FOLDER')  
                box.template_icon_view(props,"pull_name",show_labels=True)          
                row = box.row()
                row.operator('home_builder.update_selected_pulls',text="Update Selected Hardware",icon='RESTRICT_SELECT_OFF')

        #TODO
        #Appliances
        #Doors and Windows

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
        # layout.operator('home_builder.create_library_pdf',icon='FILE')
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
    HOME_BUILDER_PT_home_builder_properties,
    HOME_BUILDER_UL_assets,
    HOME_BUILDER_MT_pointer_menu,
)

register, unregister = bpy.utils.register_classes_factory(classes)        
