import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinet_parts
from .. import home_builder_utils
from . import common_prompts

from os import path

class Range(pc_types.Assembly):

    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Range")
        self.obj_bp["IS_RANGE_BP"] = True


class Refrigerator(pc_types.Assembly):

    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Refrigerator")
        self.obj_bp["IS_RANGE_BP"] = True      


class Microwave(pc_types.Assembly):

    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Microwave")
        self.obj_bp["IS_RANGE_BP"] = True          


class Range_Hood(pc_types.Assembly):

    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Range Hood")
        self.obj_bp["IS_RANGE_BP"] = True        


class Dishwasher(pc_types.Assembly):

    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Dishwasher")
        self.obj_bp["IS_RANGE_BP"] = True        


class Sink(pc_types.Assembly):

    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Dishwasher")
        self.obj_bp["IS_RANGE_BP"] = True            


class Cook_Top(pc_types.Assembly):

    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Dishwasher")
        self.obj_bp["IS_RANGE_BP"] = True    
