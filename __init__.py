import site
import os
import sys
PATH = os.path.join(os.path.dirname(__file__),"python_libs")
sys.path.append(PATH)

import bpy
import inspect
from . import addon_updater_ops
from .pc_lib import pc_utils
from . import home_builder_props
from . import home_builder_ui
from . import home_builder_menus
from . import home_builder_ops
from . import home_builder_drop_ops
from . import home_builder_pointers
from . import home_builder_utils
from .walls import wall_ops
from .cabinets import cabinet_ops
from .closets import closet_ops
from .doors_windows import door_window_ops
from bpy.app.handlers import persistent

bl_info = {
    "name": "Home Builder Library",
    "author": "Andrew Peel",
    "version": (0, 5, 1),
    "blender": (2, 93, 0),
    "location": "Asset Library",
    "description": "Library designed to help with architectural and interior design",
    "warning": "",
    "wiki_url": "",
    "category": "Asset Library",
}

@persistent
def load_library_on_file_load(scene=None):
    pc_utils.register_library(name="Home Builder Library",
                              activate_id='home_builder.activate',
                              drop_id='home_builder.drop',
                              namespace="home_builder",
                              icon='HOME')
    wm_props = home_builder_utils.get_wm_props(bpy.context.window_manager)
    wm_props.get_assets()
    
@persistent
def load_pointers(scene=None):
    # home_builder_pointers.write_pointer_files()
    home_builder_pointers.update_pointer_properties()

class Home_Builder_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    assets_filepath: bpy.props.StringProperty(
        name="Assets Filepath",
        subtype='FILE_PATH',
    )

    auto_check_update: bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False)

    updater_interval_months: bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0)

    updater_interval_days: bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31)

    updater_interval_hours: bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23)

    updater_interval_minutes: bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "assets_filepath")
        addon_updater_ops.update_settings_ui(self, context)

def register():
    bpy.utils.register_class(Home_Builder_AddonPreferences)
    addon_updater_ops.register(bl_info)
    home_builder_props.register()
    home_builder_ui.register()
    home_builder_ops.register()
    home_builder_drop_ops.register()
    home_builder_menus.register()
    wall_ops.register()
    cabinet_ops.register()
    closet_ops.register()
    door_window_ops.register()
    home_builder_utils.addon_version = bl_info['version']

    load_library_on_file_load()
    bpy.app.handlers.load_post.append(load_library_on_file_load)
    bpy.app.handlers.load_post.append(load_pointers)

def unregister():
    try:
        home_builder_props.unregister()
        home_builder_ui.unregister()
        home_builder_ops.unregister()
        home_builder_drop_ops.unregister()
        home_builder_menus.unregister()
        wall_ops.unregister()
        cabinet_ops.unregister()
        closet_ops.unregister()
        door_window_ops.unregister()

        bpy.app.handlers.load_post.remove(load_library_on_file_load)  
        bpy.app.handlers.load_post.remove(load_pointers)

        pc_utils.unregister_library("Home Builder Library")
    except:
        pass

