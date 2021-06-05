import bpy

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

def draw_home_builder(self,context):
    layout = self.layout
    layout.menu('HOME_BUILDER_MT_home_builder_menu')

def register():
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_menu)
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_reports)
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_2d_commands)
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_training)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_home_builder)

def unregister():
    bpy.utils.unregister_class(HOME_BUILDER_MT_home_builder_menu)
    bpy.utils.unregister_class(HOME_BUILDER_MT_home_builder_reports)
    bpy.utils.unregister_class(HOME_BUILDER_MT_home_builder_2d_commands)
    bpy.utils.unregister_class(HOME_BUILDER_MT_home_builder_training)
    bpy.types.VIEW3D_MT_edit_mesh.remove(draw_home_builder)