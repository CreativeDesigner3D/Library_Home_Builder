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
        # col.operator('home_builder.move_cabinet',text="Place Closet",icon='OBJECT_ORIGIN').obj_bp_name = bp.name
        layout.operator('home_builder.free_move_cabinet',text="Grab Closet",icon='VIEW_PAN').obj_bp_name = bp.name                
        layout.operator('home_builder.add_drawer',text="Add Drawer",icon='UGLYPACKAGE')
        layout.separator()
        layout.operator('home_builder.delete_assembly',text="Delete Closet",icon='X').obj_name = bp.name

def draw_home_builder(self,context):
    layout = self.layout
    layout.menu('HOME_BUILDER_MT_home_builder_menu')

def draw_closet_menu(self,context):
    layout = self.layout
    if context.object:
        bp = home_builder_utils.get_closet_bp(context.object)
        if bp:
            layout.menu('HOME_BUILDER_MT_closets')


def register():
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_menu)
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_reports)
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_2d_commands)
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_training)
    bpy.utils.register_class(HOME_BUILDER_MT_closets)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_home_builder)
    bpy.types.VIEW3D_MT_editor_menus.append(draw_closet_menu)
    

def unregister():
    bpy.utils.unregister_class(HOME_BUILDER_MT_home_builder_menu)
    bpy.utils.unregister_class(HOME_BUILDER_MT_home_builder_reports)
    bpy.utils.unregister_class(HOME_BUILDER_MT_home_builder_2d_commands)
    bpy.utils.unregister_class(HOME_BUILDER_MT_home_builder_training)
    bpy.utils.unregister_class(HOME_BUILDER_MT_closets)
    bpy.types.VIEW3D_MT_edit_mesh.remove(draw_home_builder)
    bpy.types.VIEW3D_MT_editor_menus.remove(draw_closet_menu)