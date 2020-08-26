import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinet_parts
from .. import home_builder_utils
from .. import home_builder_paths
from . import common_prompts

from os import path

ASSET_DIR = home_builder_paths.get_asset_folder_path()
APPLIANCE = path.join(ASSET_DIR,"Ranges","Thermador","Thermador PRD304GHU.blend")

class Range(pc_types.Assembly):
    show_in_library = True
    obj = None

    def draw(self):
        # props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Range")
        self.obj_bp["IS_APPLIANCE_BP"] = True

        assembly = pc_types.Assembly(self.add_assembly_from_file(APPLIANCE))
        assembly.obj_bp["IS_RANGE_BP"] = True
        
        self.obj_x.location.x = assembly.obj_x.location.x
        self.obj_y.location.y = assembly.obj_y.location.y
        self.obj_z.location.z = assembly.obj_z.location.z


class Refrigerator(pc_types.Assembly):
    show_in_library = True
    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Refrigerator")
        self.obj_bp["IS_RANGE_BP"] = True      


class Microwave(pc_types.Assembly):
    show_in_library = True
    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Microwave")
        self.obj_bp["IS_RANGE_BP"] = True          


class Range_Hood(pc_types.Assembly):
    show_in_library = True
    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Range Hood")
        self.obj_bp["IS_RANGE_BP"] = True        


class Dishwasher(pc_types.Assembly):
    show_in_library = True
    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Dishwasher")
        self.obj_bp["IS_RANGE_BP"] = True        


class Sink(pc_types.Assembly):
    show_in_library = True
    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Dishwasher")
        self.obj_bp["IS_RANGE_BP"] = True            


class Cook_Top(pc_types.Assembly):
    show_in_library = True
    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Dishwasher")
        self.obj_bp["IS_RANGE_BP"] = True    
