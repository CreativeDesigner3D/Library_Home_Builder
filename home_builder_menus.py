import bpy
from . import home_builder_utils

class HOME_BUILDER_MT_home_builder_menu(bpy.types.Menu):
    bl_label = "Home Builder"

    def draw(self, _context):
        layout = self.layout
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
        layout.label(text="COMMING SOON") 

class HOME_BUILDER_MT_closets(bpy.types.Menu):
    bl_label = "Closets"

    def draw(self, context):
        bp = home_builder_utils.get_closet_bp(context.object)
        layout = self.layout
        layout.operator('home_builder.closet_prompts',icon='WINDOW')
        layout.operator('home_builder.change_closet_openings',icon='WINDOW')
        layout.operator('home_builder.change_closet_offsets',text="Change Closet Offsets",icon='ARROW_LEFTRIGHT')
        layout.operator('home_builder.free_move_cabinet',text="Grab Closet",icon='VIEW_PAN').obj_bp_name = bp.name                
        layout.operator('home_builder.add_drawer',text="Add Drawer",icon='UGLYPACKAGE')
        layout.operator('home_builder.edit_part',text="Edit Part Shape",icon='EDITMODE_HLT')
        layout.separator()
        layout.operator('home_builder.delete_closet_opening',text="Delete Insert",icon='X')
        layout.operator('home_builder.delete_assembly',text="Delete Closet",icon='X').obj_name = bp.name

class HOME_BUILDER_MT_cabinets(bpy.types.Menu):
    bl_label = "Cabinets"

    def draw(self, context):
        cabinet_bp = home_builder_utils.get_cabinet_bp(context.object)
        exterior_bp = home_builder_utils.get_exterior_bp(context.object)
        layout = self.layout
        layout.operator('home_builder.cabinet_prompts',icon='WINDOW')
        layout.operator('home_builder.move_cabinet',text="Place Cabinet",icon='OBJECT_ORIGIN').obj_bp_name = cabinet_bp.name
        layout.operator('home_builder.free_move_cabinet',text="Grab",icon='VIEW_PAN').obj_bp_name = cabinet_bp.name
        layout.operator('home_builder.duplicate_cabinet',text="Duplicate",icon='DUPLICATE').obj_bp_name = cabinet_bp.name  
        layout.operator('home_builder.edit_part',text="Edit Part Shape",icon='EDITMODE_HLT')
        
        if exterior_bp:
            layout.operator('home_builder.add_drawer',text="Add Drawer",icon='UGLYPACKAGE')
            layout.operator('home_builder.change_cabinet_exterior',text="Change Cabinet Exterior",icon='FILE_REFRESH')
        layout.separator()
        layout.operator('home_builder.delete_assembly',text="Delete Cabinet",icon='X').obj_name = cabinet_bp.name        


class HOME_BUILDER_MT_walls(bpy.types.Menu):
    bl_label = "Walls"

    def draw(self, context):
        wall_bp = home_builder_utils.get_wall_bp(context.object)
        layout = self.layout
        layout.operator('home_builder.wall_prompts',text="Wall Prompts",icon='WINDOW') 
        layout.operator('home_builder.edit_part',text="Edit Wall Shape",icon='EDITMODE_HLT')       


def draw_home_builder(self,context):
    layout = self.layout
    layout.menu('HOME_BUILDER_MT_home_builder_menu')

def draw_view3d_menu(self,context):
    layout = self.layout
    if context.object:
        wall_bp = home_builder_utils.get_wall_bp(context.object)
        closet_bp = home_builder_utils.get_closet_bp(context.object)
        cabinet_bp = home_builder_utils.get_cabinet_bp(context.object)
        if wall_bp:
            layout.menu('HOME_BUILDER_MT_walls')        
        if closet_bp:
            layout.menu('HOME_BUILDER_MT_closets')
        if cabinet_bp:
            layout.menu('HOME_BUILDER_MT_cabinets')


def register():
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_menu)
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_reports)
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_2d_commands)
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_training)
    bpy.utils.register_class(HOME_BUILDER_MT_walls)
    bpy.utils.register_class(HOME_BUILDER_MT_closets)
    bpy.utils.register_class(HOME_BUILDER_MT_cabinets)
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
    bpy.types.VIEW3D_MT_edit_mesh.remove(draw_home_builder)
    bpy.types.VIEW3D_MT_editor_menus.remove(draw_view3d_menu)