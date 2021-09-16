import bpy
import os
from . import home_builder_utils
from . import home_builder_paths
from .pc_lib import pc_utils
from .cabinets import data_cabinets

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
        layout.operator('home_builder.change_library_category',text='Custom Cabinets',icon='USER').category = "Custom Cabinets"


class HOME_BUILDER_MT_closet_category_menu(bpy.types.Menu):
    bl_label = "Library"

    def draw(self, _context):
        layout = self.layout
        library_path = home_builder_paths.get_library_path()
        path = os.path.join(library_path,"Closets")
        dirs = os.listdir(path)
        for d in dirs:
            path = os.path.join(path,d)
            if os.path.isdir(path):
                layout.operator('home_builder.change_closet_category',text=d,icon='FILEBROWSER').category = d


class HOME_BUILDER_MT_change_catalog_selection(bpy.types.Menu):
    bl_label = "Library"

    def draw(self, context):
        layout = self.layout

        props = home_builder_utils.get_scene_props(context.scene)
        path = props.get_current_catalog_path()
        dirs = os.listdir(path)

        for d in dirs:
            cat_path = os.path.join(path,d)
            if os.path.isdir(cat_path):
                layout.operator('home_builder.change_library_category',text=d,icon='FILEBROWSER').category = d    


class HOME_BUILDER_MT_catalog_menu(bpy.types.Menu):
    bl_label = "Catalog"

    def allow_save_asset_command(self,props):
        if props.library_tabs == 'ROOMS':
            if props.room_tabs == 'WALLS':
                return False
            if props.room_tabs == 'DOORS':
                return False
            if props.room_tabs == 'WINDOWS':
                return False
            if props.room_tabs == 'OBSTACLES':
                return True          
            if props.room_tabs == 'DECORATIONS':
                return True

        if props.library_tabs == 'KITCHENS':
            if props.kitchen_tabs == 'RANGES':
                return False
            if props.kitchen_tabs == 'REFRIGERATORS':
                return False
            if props.kitchen_tabs == 'DISHWASHERS':
                return False
            if props.kitchen_tabs == 'CABINETS':
                return False
            if props.kitchen_tabs == 'PARTS':
                return False
            if props.kitchen_tabs == 'CUSTOM_CABINETS':
                return False
            if props.kitchen_tabs == 'DECORATIONS':
                return True

        if props.library_tabs == 'BATHS':
            if props.bath_tabs == 'TOILETS':
                return False
            if props.bath_tabs == 'BATHS':
                return False
            if props.bath_tabs == 'VANITIES':
                return False
            if props.bath_tabs == 'DECORATIONS':
                return True             

        if props.library_tabs == 'CLOSETS':
            if props.closet_tabs == 'STARTERS':
                return False
            if props.closet_tabs == 'INSERTS':
                return False
            if props.closet_tabs == 'SPLITTERS':
                return False
            if props.closet_tabs == 'CLOSET_PARTS':
                return False
            if props.closet_tabs == 'DECORATIONS':
                return True      

    def draw(self, context):
        fb_path = home_builder_utils.get_file_browser_path(context)
        props = home_builder_utils.get_scene_props(context.scene)
        category_name = props.get_active_catalog_name()        
        layout = self.layout
        if self.allow_save_asset_command(props):
            layout.operator('home_builder.save_decoration_to_library',text="Save Asset to Library",icon='BACK')
        layout.operator('home_builder.open_browser_window',icon='FILEBROWSER').path = fb_path
        layout.separator()
        if 'iMeshh' in category_name:
            layout.operator('wm.url_open',text="Visit iMeshh Website",icon='URL').url = "https://www.imeshh.com/"
        else:
            layout.operator('wm.url_open',text="Download Extended Asset Library",icon='URL').url = "https://creativedesigner3d.com/extended-asset-library/"


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
        box = layout.box()

        props = home_builder_utils.get_scene_props(context.scene)
        
        row = box.row()
        row.scale_y = 1.3
        row.prop(props,'sidebar_tabs',expand=True)

        if props.sidebar_tabs == 'MATERIALS':

            box.prop(props,'material_category',text="",icon='FILE_FOLDER')  
            box.template_icon_view(props,"material_name",show_labels=True)  
            box.operator('home_builder.assign_material',text="Assign Material",icon='BRUSH_DATA')

            if not context.object:
                return

            row = box.row()
            row.prop(props,'show_material_pointer_options',text="Material Pointers",emboss=False,icon='TRIA_DOWN' if props.show_material_pointer_options else 'TRIA_RIGHT')            
            if props.show_material_pointer_options:
                obj_props = home_builder_utils.get_object_props(context.object)

                mat_group = props.material_pointer_groups[obj_props.material_group_index]
                box.label(text="Material Group: " + mat_group.name,icon='COLOR')
                row = box.row()
                row.template_list("MATERIAL_UL_matslots", "", context.object, "material_slots", context.object, "active_material_index", rows=3)  

                col = row.column(align=True)
                col.operator("pc_material.add_material_slot", icon='ADD', text="").object_name = context.object.name
                col.operator("object.material_slot_remove", icon='REMOVE', text="")                
                col.operator('home_builder.update_object_materials',icon='FILE_REFRESH',text="").object_name = context.object.name

                slot = None
                if len(context.object.material_slots) >= context.object.active_material_index + 1:
                    slot = context.object.material_slots[context.object.active_material_index]

                if slot:
                    row = box.row()
                    if len(context.object.pyclone.pointers) >= context.object.active_material_index + 1:
                        pointer_slot = context.object.pyclone.pointers[context.object.active_material_index]
                        row.prop(pointer_slot,'name')
                        row = box.row()
                        row.prop_search(pointer_slot,'pointer_name',mat_group,'pointers',text="Pointer")
                    else:
                        row.operator('pc_material.add_material_pointers').object_name = context.object.name

                if context.object.mode == 'EDIT':
                    row = layout.row(align=True)
                    row.operator("object.material_slot_assign", text="Assign")
                    row.operator("object.material_slot_select", text="Select")
                    row.operator("object.material_slot_deselect", text="Deselect")  

        if props.sidebar_tabs == 'FRONTS':
            box.prop(props,'cabinet_door_category',text="",icon='FILE_FOLDER')  
            box.template_icon_view(props,"cabinet_door_name",show_labels=True)              
            row = box.row()
            row.operator('home_builder.update_selected_cabinet_doors',text="Update Selected Front",icon='RESTRICT_SELECT_OFF')

        if props.sidebar_tabs == 'HARDWARE':
            box.prop(props,'pull_category',text="",icon='FILE_FOLDER')  
            box.template_icon_view(props,"pull_name",show_labels=True)          
            row = box.row()
            row.operator('home_builder.update_selected_pulls',text="Update Selected Hardware",icon='RESTRICT_SELECT_OFF')

        if props.sidebar_tabs == 'BUILD':
            box.operator('pc_assembly.create_new_assembly',text="Create New Assembly",icon='FILE_3D')
            if context.object:
                obj_bp = pc_utils.get_assembly_bp(context.object)
                if obj_bp:
                    row = box.row()
                    row.label(text="Selected Assembly: " + obj_bp.name)
                    row.operator('pc_assembly.select_parent',text="",icon='SORT_DESC')
                    box.prop(props,'selected_part',text="",icon='SNAP_FACE') 
                    box.operator('home_builder.add_part',text="Add Part",icon='BRUSH_DATA').object_name = obj_bp.name


class HOME_BUILDER_PT_home_builder_wall_properties(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Walls"
    bl_category = "Home Builder"    
    # bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.scale_y = 1.3
        row.operator('home_builder.collect_walls')
        if len(props.walls) > 0:
            box.template_list("HOME_BUILDER_UL_walls"," ", props, "walls", props, "wall_index",rows=5,type='DEFAULT')
        if props.wall_index + 1 <= len(props.walls):
            wall = props.walls[props.wall_index]
            box.prop(wall.obj_bp,'name')


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
        layout.operator('home_builder.create_library_pdf_from_folder',icon='FILE')
        layout.operator('home_builder.create_new_asset',icon='ADD')
        

class HOME_BUILDER_MT_pointer_menu(bpy.types.Menu):
    bl_label = "Pointer Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator('home_builder.reload_pointers',icon='FILE_REFRESH')


class HOME_BUILDER_MT_change_global_material_group(bpy.types.Menu):
    bl_label = "Change Material Group"

    def draw(self, context):
        layout = self.layout
        props = home_builder_utils.get_scene_props(context.scene)
        for index, material_group in enumerate(props.material_pointer_groups):
            grp = props.material_pointer_groups[index]
            icon = 'RADIOBUT_ON' if index == props.material_group_index else 'RADIOBUT_OFF'
            layout.operator('home_builder.change_global_material_pointer_group',text=grp.name,icon=icon).material_index = index
        layout.separator()
        layout.operator('home_builder.add_material_pointer_group',icon='ADD')


class HOME_BUILDER_MT_change_product_material_group(bpy.types.Menu):
    bl_label = "Change Material Group"

    def draw(self, context):
        layout = self.layout
        cabinet_bp = home_builder_utils.get_cabinet_bp(context.object)
        if cabinet_bp:
            cabinet_bp_props = home_builder_utils.get_object_props(cabinet_bp)
            scene_props = home_builder_utils.get_scene_props(context.scene)
            for index, material_group in enumerate(scene_props.material_pointer_groups):
                grp = scene_props.material_pointer_groups[index]
                icon = 'RADIOBUT_ON' if index == cabinet_bp_props.material_group_index else 'RADIOBUT_OFF'            
                props = layout.operator('home_builder.change_product_material_pointer_group',text=grp.name,icon=icon)
                props.material_index = index
                props.object_name = cabinet_bp.name


class HOME_BUILDER_UL_assets(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)
        layout.prop(item,'is_selected',text="")


class HOME_BUILDER_UL_walls(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item.obj_bp:
            layout.label(text=item.obj_bp.name)
            if item.wall_mesh.hide_get():
                layout.operator('home_builder.show_hide_walls',text="",icon='HIDE_ON').wall_obj_bp = item.obj_bp.name
            else:
                layout.operator('home_builder.show_hide_walls',text="",icon='HIDE_OFF').wall_obj_bp = item.obj_bp.name


classes = (
    HOME_BUILDER_MT_change_catalog_selection,
    HOME_BUILDER_MT_category_menu,
    HOME_BUILDER_MT_closet_category_menu,
    HOME_BUILDER_MT_catalog_menu,
    HOME_BUILDER_PT_library_settings,
    HOME_BUILDER_MT_asset_commands_menu,
    HOME_BUILDER_PT_home_builder_properties,
    HOME_BUILDER_PT_home_builder_wall_properties,
    HOME_BUILDER_UL_assets,
    HOME_BUILDER_MT_change_global_material_group,
    HOME_BUILDER_MT_change_product_material_group,
    HOME_BUILDER_MT_pointer_menu,
    HOME_BUILDER_UL_walls,
)

register, unregister = bpy.utils.register_classes_factory(classes)        
