import bpy

class HOME_BUILDER_MT_home_builder_menu(bpy.types.Menu):
    bl_label = "Home Builder"

    def draw(self, _context):
        layout = self.layout
        layout.operator('home_builder.create_cabinet_list_report',text="Cabinet List Report",icon='TEXT')

def draw_home_builder(self,context):
    layout = self.layout
    layout.menu('HOME_BUILDER_MT_home_builder_menu')

def register():
    bpy.utils.register_class(HOME_BUILDER_MT_home_builder_menu)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_home_builder)

def unregister():
    bpy.utils.unregister_class(HOME_BUILDER_MT_home_builder_menu)
    bpy.types.VIEW3D_MT_edit_mesh.remove(draw_home_builder)