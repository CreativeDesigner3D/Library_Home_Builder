import bpy
from . import home_builder_utils
from .pc_lib import pc_utils

class HOME_BUILDER_MT_home_builder_menu(bpy.types.Menu):
    bl_label = "Home Builder"

    def draw(self, _context):
        layout = self.layout
        layout.operator('home_builder.unit_settings',text="Change Units",icon='SETTINGS')
        layout.menu('HOME_BUILDER_MT_home_builder_reports',icon='TEXT')
        layout.menu('HOME_BUILDER_MT_home_builder_2d_commands',icon='CON_SIZELIMIT')
        layout.menu('HOME_BUILDER_MT_home_builder_training',icon='QUESTION')


class HOME_BUILDER_MT_home_builder_reports(bpy.types.Menu):
    bl_label = "Reports"

    def draw(self, _context):
        layout = self.layout
        layout.operator('home_builder.create_cabinet_list_report',text="Cabinet List Report",icon='TEXT')


class HOME_BUILDER_MT_home_builder_2d_commands(bpy.types.Menu):
    bl_label = "2D Layouts"

    def draw(self, _context):
        layout = self.layout
        layout.operator('home_builder.create_2d_views',text="Create Wall Elevation Views",icon='CON_SIZELIMIT')
        layout.operator('home_builder.create_2d_cabinet_views',text="Create Cabinet Views",icon='CON_SIZELIMIT')             


class HOME_BUILDER_MT_home_builder_training(bpy.types.Menu):
    bl_label = "Training"

    def draw(self, _context):
        layout = self.layout
        layout.operator(
            "wm.url_open", text="Kitchen Design Tutorial", icon='URL',
        ).url = "https://youtu.be/LOn8SLp6kFg"        
        layout.operator(
            "wm.url_open", text="Closet Design Tutorial", icon='URL',
        ).url = "https://youtu.be/WGcZkVCLzWI"  


class HOME_BUILDER_MT_closets(bpy.types.Menu):
    bl_label = "Closet Commands"

    def draw(self, context):
        bp = home_builder_utils.get_closet_bp(context.object)
        layout = self.layout
        layout.operator('home_builder.closet_prompts',icon='WINDOW')
        layout.operator('home_builder.change_closet_openings',icon='WINDOW')
        layout.operator('home_builder.change_closet_offsets',text="Change Closet Offsets",icon='ARROW_LEFTRIGHT')
        layout.operator('home_builder.free_move_object',text="Grab Closet",icon='VIEW_PAN').obj_bp_name = bp.name  
        layout.operator('home_builder.duplicate_closet_insert',text="Duplicate Insert",icon='DUPLICATE')
        layout.operator('home_builder.add_drawer',text="Add Drawer",icon='UGLYPACKAGE')
        layout.operator('home_builder.edit_part',text="Edit Part Shape",icon='EDITMODE_HLT')
        layout.separator()
        layout.operator('home_builder.delete_closet_opening',text="Delete Insert",icon='X')
        layout.operator('home_builder.delete_assembly',text="Delete Closet",icon='X').obj_name = bp.name


class HOME_BUILDER_MT_closets_corner(bpy.types.Menu):
    bl_label = "Closet Corner Commands"

    def draw(self, context):
        bp = home_builder_utils.get_closet_inside_corner_bp(context.object)
        layout = self.layout
        layout.operator('home_builder.closet_inside_corner_prompts',icon='WINDOW')
        layout.operator('home_builder.free_move_object',text="Grab Closet",icon='VIEW_PAN').obj_bp_name = bp.name
        layout.operator('home_builder.edit_part',text="Edit Part Shape",icon='EDITMODE_HLT')
        layout.separator()
        layout.operator('home_builder.delete_assembly',text="Delete Closet",icon='X').obj_name = bp.name


class HOME_BUILDER_MT_cabinets(bpy.types.Menu):
    bl_label = "Cabinet Commands"

    def draw(self, context):
        obj_bp = pc_utils.get_assembly_bp(context.object)
        cabinet_bp = home_builder_utils.get_cabinet_bp(context.object)
        exterior_bp = home_builder_utils.get_exterior_bp(context.object)
        wall_bp = home_builder_utils.get_wall_bp(context.object)

        layout = self.layout
        layout.operator('home_builder.cabinet_prompts',icon='WINDOW')
        layout.separator()
        props = layout.operator('home_builder.place_cabinet',text="Place Cabinet",icon='OBJECT_ORIGIN')
        props.obj_bp_name = cabinet_bp.name
        props.snap_cursor_to_cabinet = True
        if wall_bp:
            layout.operator('home_builder.place_wall_cabinet',text="Place Cabinet on Wall",icon='EMPTY_ARROWS')
        layout.operator('home_builder.free_move_object',text="Grab Cabinet",icon='VIEW_PAN').obj_bp_name = cabinet_bp.name
        layout.operator('home_builder.duplicate_cabinet',text="Duplicate",icon='DUPLICATE').obj_bp_name = cabinet_bp.name  
        layout.separator()
        layout.operator('home_builder.part_prompts',text="Part Prompts - " + obj_bp.name,icon='WINDOW')
        layout.operator('home_builder.edit_part',text="Edit Part Shape",icon='EDITMODE_HLT')
        
        if exterior_bp:
            layout.separator()
            layout.operator('home_builder.add_drawer',text="Add Drawer",icon='UGLYPACKAGE')
            layout.operator('home_builder.change_cabinet_exterior',text="Change Cabinet Exterior",icon='FILE_REFRESH')
        layout.separator()
        layout.operator('home_builder.delete_assembly',text="Delete Cabinet",icon='X').obj_name = cabinet_bp.name        


class HOME_BUILDER_MT_appliances(bpy.types.Menu):
    bl_label = "Appliance Commands"

    def draw(self, context):
        appliance_bp = home_builder_utils.get_appliance_bp(context.object)
        layout = self.layout
        layout.operator(appliance_bp['PROMPT_ID'],text="Appliance Prompts",icon='WINDOW') 
        props = layout.operator('home_builder.place_appliance',text="Place Appliance",icon='OBJECT_ORIGIN')
        props.obj_bp_name = appliance_bp.name
        props.snap_cursor_to_cabinet = True        
        layout.operator('home_builder.free_move_object',text="Grab Appliance",icon='VIEW_PAN').obj_bp_name = appliance_bp.name
        layout.operator('home_builder.edit_part',text="Edit Appliance Shape",icon='EDITMODE_HLT')
        layout.operator('home_builder.delete_assembly',text="Delete Appliance",icon='X').obj_name = appliance_bp.name      


class HOME_BUILDER_MT_walls(bpy.types.Menu):
    bl_label = "Wall Commands"

    def draw(self, context):
        wall_bp = home_builder_utils.get_wall_bp(context.object)
        layout = self.layout
        layout.operator('home_builder.wall_prompts',text="Wall Prompts",icon='WINDOW') 
        layout.operator('home_builder.free_move_object',text="Grab Wall",icon='VIEW_PAN').obj_bp_name = wall_bp.name
        layout.operator('home_builder.edit_part',text="Edit Wall Shape",icon='EDITMODE_HLT')       


class HOME_BUILDER_MT_windows(bpy.types.Menu):
    bl_label = "Window Commands"

    def draw(self, context):
        window_bp = home_builder_utils.get_window_bp(context.object)
        layout = self.layout
        layout.operator('home_builder.window_prompts',text="Wall Prompts",icon='WINDOW') 
        props = layout.operator('home_builder.place_door_window',text="Place Window",icon='OBJECT_ORIGIN')
        props.obj_bp_name = window_bp.name
        props.filepath = ""
        layout.operator('home_builder.free_move_object',text="Grab Window",icon='VIEW_PAN').obj_bp_name = window_bp.name  
        layout.separator()
        layout.operator('home_builder.delete_assembly',text="Delete Window",icon='X').obj_name = window_bp.name       
  

class HOME_BUILDER_MT_doors(bpy.types.Menu):
    bl_label = "Door Commands"

    def draw(self, context):
        door_bp = home_builder_utils.get_door_bp(context.object)
        layout = self.layout
        layout.operator('home_builder.door_prompts',text="Door Prompts",icon='WINDOW')  
        props = layout.operator('home_builder.place_door_window',text="Place Door",icon='OBJECT_ORIGIN')
        props.obj_bp_name = door_bp.name
        props.filepath = ""
        layout.operator('home_builder.free_move_object',text="Grab Door",icon='VIEW_PAN').obj_bp_name = door_bp.name  
        layout.separator()
        layout.operator('home_builder.delete_assembly',text="Delete Door",icon='X').obj_name = door_bp.name  


def draw_home_builder(self,context):
    layout = self.layout
    layout.menu('HOME_BUILDER_MT_home_builder_menu')

def draw_view3d_menu(self,context):
    layout = self.layout
    if context.object:
        wall_bp = home_builder_utils.get_wall_bp(context.object)
        closet_bp = home_builder_utils.get_closet_bp(context.object)
        corner_closet_bp = home_builder_utils.get_closet_inside_corner_bp(context.object)
        cabinet_bp = home_builder_utils.get_cabinet_bp(context.object)
        window_bp = home_builder_utils.get_window_bp(context.object)
        door_bp = home_builder_utils.get_door_bp(context.object)
        appliance_bp = home_builder_utils.get_appliance_bp(context.object)
        if wall_bp:
            layout.menu('HOME_BUILDER_MT_walls',text="Walls")        
        if closet_bp:
            layout.menu('HOME_BUILDER_MT_closets',text="Closets")
        if corner_closet_bp:
            layout.menu('HOME_BUILDER_MT_closets_corner',text="Corner Closets")
        if cabinet_bp:
            layout.menu('HOME_BUILDER_MT_cabinets',text="Cabinets")
        if window_bp:
            layout.menu('HOME_BUILDER_MT_windows',text="Windows")
        if door_bp:
            layout.menu('HOME_BUILDER_MT_doors',text="Doors")
        if appliance_bp:
            layout.menu('HOME_BUILDER_MT_appliances',text="Appliance")

def register():
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_menu)
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_reports)
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_2d_commands)
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_training)
    bpy.utils.register_class(HOME_BUILDER_MT_walls)
    bpy.utils.register_class(HOME_BUILDER_MT_closets)
    bpy.utils.register_class(HOME_BUILDER_MT_cabinets)
    bpy.utils.register_class(HOME_BUILDER_MT_windows)
    bpy.utils.register_class(HOME_BUILDER_MT_doors)
    bpy.utils.register_class(HOME_BUILDER_MT_appliances)
    bpy.utils.register_class(HOME_BUILDER_MT_closets_corner)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_home_builder)
    bpy.types.VIEW3D_MT_editor_menus.append(draw_view3d_menu)
    

def unregister():
    bpy.utils.unregister_class(HOME_BUILDER_MT_home_builder_menu)
    bpy.utils.unregister_class(HOME_BUILDER_MT_home_builder_reports)
    bpy.utils.unregister_class(HOME_BUILDER_MT_home_builder_2d_commands)
    bpy.utils.unregister_class(HOME_BUILDER_MT_home_builder_training)
    bpy.utils.unregister_class(HOME_BUILDER_MT_walls)
    bpy.utils.unregister_class(HOME_BUILDER_MT_closets)
    bpy.utils.unregister_class(HOME_BUILDER_MT_cabinets)
    bpy.utils.unregister_class(HOME_BUILDER_MT_windows)
    bpy.utils.unregister_class(HOME_BUILDER_MT_doors)
    bpy.utils.unregister_class(HOME_BUILDER_MT_appliances)
    bpy.utils.unregister_class(HOME_BUILDER_MT_closets_corner)
    bpy.types.VIEW3D_MT_edit_mesh.remove(draw_home_builder)
    bpy.types.VIEW3D_MT_editor_menus.remove(draw_view3d_menu)