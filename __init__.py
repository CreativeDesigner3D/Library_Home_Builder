import bpy
import os
import inspect
from .pc_lib import pc_utils
from . import home_builder_ui
from . import home_builder_ops
from . import home_builder_props
from . import home_builder_pointers
from . import home_builder_utils
from .walls import wall_ops
from .cabinets import cabinet_ops
from .doors import door_ops
from .windows import window_ops
from bpy.app.handlers import persistent

bl_info = {
    "name": "Home Builder Library",
    "author": "Andrew Peel",
    "version": (0, 0, 2),
    "blender": (2, 80, 0),
    "location": "Asset Library",
    "description": "Library designed to help with architectural and interior design",
    "warning": "",
    "wiki_url": "",
    "category": "Asset Library",
}


@persistent
def load_library_on_file_load(scene=None):
    pc_utils.register_library(name="Home Builder Library",
                              activate_id='room_builder.activate',
                              drop_id='room_builder.drop',
                              icon='HOME')
    wm_props = home_builder_utils.get_wm_props(bpy.context.window_manager)
    wm_props.get_assets()
    
@persistent
def load_pointers(scene=None):
    home_builder_pointers.write_pointer_files()
    home_builder_pointers.update_pointer_properties()

def register():
    home_builder_props.register()
    home_builder_ui.register()
    home_builder_ops.register()
    wall_ops.register()
    cabinet_ops.register()
    door_ops.register()
    window_ops.register()

    load_library_on_file_load()
    bpy.app.handlers.load_post.append(load_library_on_file_load)
    bpy.app.handlers.load_post.append(load_pointers)

def unregister():
    home_builder_props.unregister()
    home_builder_ui.unregister()
    home_builder_ops.unregister()
    wall_ops.unregister()
    cabinet_ops.unregister()
    door_ops.unregister()
    window_ops.unregister()

    bpy.app.handlers.load_post.remove(load_library_on_file_load)  
    bpy.app.handlers.load_post.remove(load_pointers)

    pc_utils.unregister_library("Home Builder Library")

