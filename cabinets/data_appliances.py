import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinet_parts
from .. import home_builder_utils
from .. import home_builder_paths
from . import common_prompts

from os import path

class Range(pc_types.Assembly):
    show_in_library = True
    category_name = 'Appliances'
    obj = None

    def draw(self):
        ASSET_DIR = home_builder_paths.get_asset_folder_path()
        assembly_path = path.join(ASSET_DIR,"Ranges","Generic","Generic Range.blend")  

        self.create_assembly("Range")
        self.obj_bp["IS_APPLIANCE_BP"] = True
        self.obj_y['IS_MIRROR'] = True

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        assembly = pc_types.Assembly(self.add_assembly_from_file(assembly_path))
        assembly.obj_bp["IS_RANGE_BP"] = True

        self.obj_x.location.x = assembly.obj_x.location.x
        self.obj_y.location.y = assembly.obj_y.location.y
        self.obj_z.location.z = assembly.obj_z.location.z

        assembly.dim_x('width',[width])
        assembly.dim_y('depth',[depth])
        assembly.dim_z('height',[height])


class Refrigerator(pc_types.Assembly):
    show_in_library = True
    category_name = 'Appliances'
    obj = None

    def draw(self):
        ASSET_DIR = home_builder_paths.get_asset_folder_path()
        assembly_path = path.join(ASSET_DIR,"Refrigerators","Generic","Generic Refrigerator.blend")

        self.create_assembly("Refrigerator")
        self.obj_bp["IS_APPLIANCE_BP"] = True      
        self.obj_y['IS_MIRROR'] = True

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        assembly = pc_types.Assembly(self.add_assembly_from_file(assembly_path))
        assembly.obj_bp["IS_REFRIGERATOR_BP"] = True
        
        self.obj_x.location.x = assembly.obj_x.location.x
        self.obj_y.location.y = assembly.obj_y.location.y
        self.obj_z.location.z = assembly.obj_z.location.z

        assembly.dim_x('width',[width])
        assembly.dim_y('depth',[depth])
        assembly.dim_z('height',[height])        


class Microwave(pc_types.Assembly):
    show_in_library = True
    category_name = 'Appliances'
    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Microwave")
        self.obj_bp["IS_RANGE_BP"] = True          


class Range_Hood(pc_types.Assembly):
    show_in_library = True
    category_name = 'Appliances'
    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Range Hood")
        self.obj_bp["IS_RANGE_BP"] = True        


class Dishwasher(pc_types.Assembly):
    show_in_library = True
    category_name = 'Appliances'
    obj = None

    def draw(self):
        ASSET_DIR = home_builder_paths.get_asset_folder_path()
        assembly_path = path.join(ASSET_DIR,"Dishwashers","Generic","Generic Dishwasher.blend")

        self.create_assembly("Dishwasher")
        self.obj_bp["IS_APPLIANCE_BP"] = True        
        self.obj_y['IS_MIRROR'] = True

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        assembly = pc_types.Assembly(self.add_assembly_from_file(assembly_path))
        assembly.obj_bp["IS_DISHWASHER_BP"] = True
        
        self.obj_x.location.x = assembly.obj_x.location.x
        self.obj_y.location.y = assembly.obj_y.location.y
        self.obj_z.location.z = assembly.obj_z.location.z

        assembly.dim_x('width',[width])
        assembly.dim_y('depth',[depth])
        assembly.dim_z('height',[height])           

class Sink(pc_types.Assembly):
    # show_in_library = True
    category_name = 'Appliances'
    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Dishwasher")
        self.obj_bp["IS_RANGE_BP"] = True            


class Cook_Top(pc_types.Assembly):
    # show_in_library = True
    category_name = 'Appliances'
    obj = None

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Dishwasher")
        self.obj_bp["IS_RANGE_BP"] = True    
