import bpy
import os
import inspect
from .pc_lib import pc_utils
from . import home_builder_ui
from . import home_builder_ops
from . import home_builder_props
from . import home_builder_utils
from .walls import place_walls
from .cabinets import place_cabinet
from .doors import place_door
from bpy.app.handlers import persistent

bl_info = {
    "name": "Home Builder Library",
    "author": "Andrew Peel",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Asset Library",
    "description": "Library designed to help with architectural and interior design",
    "warning": "",
    "wiki_url": "",
    "category": "Asset Library",
}


@persistent
def load_library_on_file_load(scene=None):
    pyclone = pc_utils.get_wm_props(bpy.context.window_manager)
    if "Home Builder Library" not in pyclone.libraries:
        library = pyclone.add_library(name="Home Builder Library",
                                      activate_id='room_builder.activate',
                                      drop_id='room_builder.drop',
                                      icon='HOME')

@persistent
def load_pointers(scene=None):
    home_builder_utils.write_pointer_files()
    home_builder_utils.update_pointer_properties()

def register():
    home_builder_ui.register()
    home_builder_ops.register()
    home_builder_props.register()
    place_walls.register()
    place_cabinet.register()
    place_door.register()

    load_library_on_file_load()
    bpy.app.handlers.load_post.append(load_library_on_file_load)
    bpy.app.handlers.load_post.append(load_pointers)

def unregister():
    home_builder_ui.unregister()
    home_builder_ops.unregister()
    home_builder_props.unregister()
    place_walls.unregister()
    place_cabinet.unregister()
    place_door.unregister()

    bpy.app.handlers.load_post.remove(load_library_on_file_load)  
    bpy.app.handlers.load_post.remove(load_pointers)

    pyclone = pc_utils.get_wm_props(bpy.context.window_manager)
    pyclone.remove_library("Home Builder Library")

