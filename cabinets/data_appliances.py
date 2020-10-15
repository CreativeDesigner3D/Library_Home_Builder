import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinet_parts
from .. import home_builder_utils
from .. import home_builder_paths
from . import common_prompts
from . import cabinet_utils
from os import path

def get_range(category,assembly_name):
    ASSET_DIR = home_builder_paths.get_range_path()
    if assembly_name == "":
        return path.join(ASSET_DIR,"Generic","Generic Range.blend")  
    else:
        return path.join(ASSET_DIR, category, assembly_name + ".blend")       

def get_range_hood(category,assembly_name):
    ASSET_DIR = home_builder_paths.get_range_hood_path()
    if assembly_name == "":
        return path.join(ASSET_DIR,"Generic","Generic Range.blend")  
    else:
        return path.join(ASSET_DIR, category, assembly_name + ".blend")       
        
class Range(pc_types.Assembly):
    show_in_library = True
    category_name = 'Appliances'
    obj = None

    range_appliance = None
    range_hood_appliance = None

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  
        if obj_bp:
            for child in obj_bp.children:   
                if "IS_RANGE_BP" in child:
                    self.range_appliance = pc_types.Assembly(child)
                if "IS_RANGE_HOOD_BP" in child:
                    self.range_hood_appliance = pc_types.Assembly(child)    

    def update_range_hood_location(self):
        if self.range_hood_appliance:
            self.range_hood_appliance.obj_bp.location.x = (self.obj_x.location.x/2) - (self.range_hood_appliance.obj_x.location.x)/2
            self.range_hood_appliance.obj_bp.location.z = pc_unit.inch(70)

    def add_range_hood(self,category="",assembly_name=""):
        self.range_hood_appliance = pc_types.Assembly(self.add_assembly_from_file(get_range_hood(category,assembly_name)))
        self.range_hood_appliance.obj_bp["IS_RANGE_HOOD_BP"] = True
        self.range_hood_appliance.obj_x.empty_display_size = pc_unit.inch(.5)
        self.range_hood_appliance.obj_y.empty_display_size = pc_unit.inch(.5)
        self.range_hood_appliance.obj_z.empty_display_size = pc_unit.inch(.5)

        if not self.range_hood_appliance.obj_x.lock_location[0]:
            width = self.obj_x.pyclone.get_var('location.x','width')
            self.range_hood_appliance.dim_x('width',[width])

        self.update_range_hood_location()

    def add_range(self,category="",assembly_name=""):
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        self.range_appliance = pc_types.Assembly(self.add_assembly_from_file(get_range(category,assembly_name)))
        self.range_appliance.obj_bp["IS_RANGE_BP"] = True
        self.range_appliance.obj_x.empty_display_size = pc_unit.inch(.5)
        self.range_appliance.obj_y.empty_display_size = pc_unit.inch(.5)
        self.range_appliance.obj_z.empty_display_size = pc_unit.inch(.5)

        self.obj_x.location.x = self.range_appliance.obj_x.location.x
        self.obj_y.location.y = self.range_appliance.obj_y.location.y
        self.obj_z.location.z = self.range_appliance.obj_z.location.z
        self.obj_x.lock_location[0] = self.range_appliance.obj_x.lock_location[0]
        self.obj_y.lock_location[1] = self.range_appliance.obj_y.lock_location[1]
        self.obj_z.lock_location[2] = self.range_appliance.obj_z.lock_location[2]

        if self.range_appliance.obj_x.lock_location[0]:
            self.obj_x.location.x = self.range_appliance.obj_x.location.x
        else:
            width = self.obj_x.pyclone.get_var('location.x','width')
            self.range_appliance.dim_x('width',[width])
        
        if self.range_appliance.obj_y.lock_location[1]:
            self.obj_y.location.y = self.range_appliance.obj_y.location.y
        else:
            depth = self.obj_y.pyclone.get_var('location.y','depth')
            self.range_appliance.dim_y('depth',[depth])

        if self.range_appliance.obj_x.lock_location[2]:
            self.obj_z.location.z = self.range_appliance.obj_z.location.z
        else:
            height = self.obj_z.pyclone.get_var('location.z','height')
            self.range_appliance.dim_z('height',[height])   
        
        home_builder_utils.update_assembly_id_props(self.range_appliance,self)

    def draw(self):
        self.create_assembly("Range")
        self.obj_bp["IS_APPLIANCE_BP"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.range_prompts"
        self.obj_y['IS_MIRROR'] = True
        self.add_prompt("Add Range Hood",'CHECKBOX',False)
        self.add_range()


class Refrigerator(pc_types.Assembly):
    show_in_library = True
    category_name = 'Appliances'
    obj = None

    def draw(self):
        ASSET_DIR = home_builder_paths.get_asset_folder_path()
        assembly_path = path.join(ASSET_DIR,"Refrigerators","Generic","Generic Refrigerator.blend")

        self.create_assembly("Refrigerator")
        self.obj_bp["IS_APPLIANCE_BP"] = True    
        self.obj_bp["PROMPT_ID"] = "home_builder.refrigerator_prompts"  
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
        props = home_builder_utils.get_scene_props(bpy.context.scene)
        ASSET_DIR = home_builder_paths.get_asset_folder_path()
        assembly_path = path.join(ASSET_DIR,"Dishwashers","Generic","Generic Dishwasher.blend")

        self.create_assembly("Dishwasher")
        self.obj_bp["IS_APPLIANCE_BP"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.dishwasher_prompts"       
        self.obj_y['IS_MIRROR'] = True

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        assembly = pc_types.Assembly(self.add_assembly_from_file(assembly_path))
        assembly.obj_bp["IS_DISHWASHER_BP"] = True
        
        self.obj_x.location.x = assembly.obj_x.location.x
        self.obj_y.location.y = -props.base_cabinet_depth
        self.obj_z.location.z = props.base_cabinet_height

        assembly.dim_x('width',[width])
        assembly.dim_y('depth',[depth])
        assembly.dim_z('height',[height])     

        cabinet_utils.add_countertop(self)      

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
