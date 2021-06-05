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

        # box = layout.box()
        # row = box.row()
        # row.prop(props,'show_2d_view_options',text="2D View Commands",emboss=False,icon='TRIA_DOWN' if props.show_2d_view_options else 'TRIA_RIGHT')            
        # if props.show_2d_view_options:
        #     box.operator('home_builder.create_2d_views',text="Create Wall Elevation Views",icon='CON_SIZELIMIT')
        #     box.operator('home_builder.create_2d_cabinet_views',text="Create Cabinet Views",icon='CON_SIZELIMIT')

        # box = layout.box()
        # row = box.row()
        # row.prop(props,'show_report_options',text="Reports",emboss=False,icon='TRIA_DOWN' if props.show_report_options else 'TRIA_RIGHT')            
        # if props.show_report_options:
        #     box.operator('home_builder.create_cabinet_list_report',text="Cabinet List Report",icon='TEXT')

        box = layout.box()
        row = box.row()
        row.prop(props,'show_material_options',text="Material Selection",emboss=False,icon='TRIA_DOWN' if props.show_material_options else 'TRIA_RIGHT')            
        if props.show_material_options:
            box.prop(props,'material_category',text="",icon='FILE_FOLDER')  
            box.template_icon_view(props,"material_name",show_labels=True)  
            box.operator('home_builder.assign_material',text="Assign Material",icon='BRUSH_DATA')

        if not context.object:
            return
        else:
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

        obj_bp = pc_utils.get_assembly_bp(context.object)
        cabinet_bp = home_builder_utils.get_cabinet_bp(context.object)
        exterior_bp = home_builder_utils.get_exterior_bp(context.object)
        wall_bp = home_builder_utils.get_wall_bp(context.object)
        closet_bp = home_builder_utils.get_closet_bp(context.object)

        if obj_bp:
            box = layout.box()
            row = box.row()
            row.prop(props,'show_add_part_options',text="Add Part",emboss=False,icon='TRIA_DOWN' if props.show_add_part_options else 'TRIA_RIGHT')            
            if props.show_add_part_options:
                row = box.row()
                row.label(text="Selected Assembly: " + obj_bp.name)
                row.operator('pc_assembly.select_parent',text="",icon='SORT_DESC')

                box.prop(props,'selected_part',text="",icon='SNAP_FACE') 
                box.operator('home_builder.add_part',text="Add Part",icon='BRUSH_DATA').object_name = obj_bp.name

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
                col.prop(cabinet_bp,'name')
                col.separator()
                col.menu('HOME_BUILDER_MT_change_product_material_group',text="Material Group",icon='COLOR')
                col.separator()
                col.operator('home_builder.cabinet_prompts',icon='WINDOW')
                col.operator('home_builder.move_cabinet',text="Place Cabinet",icon='OBJECT_ORIGIN').obj_bp_name = cabinet_bp.name
                col.operator('home_builder.free_move_cabinet',text="Grab",icon='VIEW_PAN').obj_bp_name = cabinet_bp.name
                col.operator('home_builder.duplicate_cabinet',text="Duplicate",icon='DUPLICATE').obj_bp_name = cabinet_bp.name  
                if exterior_bp:
                    col.operator('home_builder.add_drawer',text="Add Drawer",icon='UGLYPACKAGE')
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

        if closet_bp:
            box = layout.box()
            row = box.row()
            row.prop(props,'show_closet_options',text="Closet Commands",emboss=False,icon='TRIA_DOWN' if props.show_closet_options else 'TRIA_RIGHT')
            if props.show_closet_options:
                col = box.column(align=True)
                col.operator('home_builder.closet_prompts',icon='WINDOW')
                col.operator('home_builder.change_closet_openings',icon='WINDOW')
                col.operator('home_builder.change_closet_offsets',text="Change Closet Offsets",icon='ARROW_LEFTRIGHT')
                # col.operator('home_builder.move_cabinet',text="Place Closet",icon='OBJECT_ORIGIN').obj_bp_name = closet_bp.name
                col.operator('home_builder.free_move_cabinet',text="Grab Closet",icon='VIEW_PAN').obj_bp_name = closet_bp.name                
                col.operator('home_builder.add_drawer',text="Add Drawer",icon='UGLYPACKAGE')
                col.separator()
                col.operator('home_builder.delete_assembly',text="Delete Closet",icon='X').obj_name = closet_bp.name

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


classes = (
    HOME_BUILDER_MT_category_menu,
    HOME_BUILDER_MT_closet_category_menu,
    HOME_BUILDER_PT_library_settings,
    HOME_BUILDER_MT_asset_commands_menu,
    HOME_BUILDER_PT_home_builder_properties,
    HOME_BUILDER_UL_assets,
    HOME_BUILDER_MT_change_global_material_group,
    HOME_BUILDER_MT_change_product_material_group,
    HOME_BUILDER_MT_pointer_menu,
)

register, unregister = bpy.utils.register_classes_factory(classes)        
