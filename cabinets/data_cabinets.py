import bpy
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import common_prompts
from . import data_cabinet_parts
from . import data_cabinet_carcass
from . import data_countertops
from . import data_cabinet_doors
from . import cabinet_utils
from .. import home_builder_utils
import time
import math

class Standard_Cabinet(pc_types.Assembly):
    show_in_library = True
    
    carcass = None
    interior = None
    exterior = None
    splitter = None

    def draw(self):
        start_time = time.time()
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly()
        self.obj_bp["IS_CABINET_BP"] = True
        self.obj_y['IS_MIRROR'] = True

        common_prompts.add_cabinet_prompts(self)

        carcass = self.add_assembly(self.carcass)
        cabinet_type = carcass.get_prompt("Cabinet Type")
        if self.exterior:
            cabinet_utils.add_exterior_to_cabinet(self,carcass,self.exterior,cabinet_type.get_value())
        if self.interior:
            cabinet_utils.add_interior_to_cabinet(self,carcass,self.interior,cabinet_type.get_value())
        if cabinet_type.get_value() == 0:
            cabinet_utils.add_countertop(self)

        self.obj_x.location.x = pc_unit.inch(18) 
        if cabinet_type.get_value() == 0:
            self.obj_y.location.y = -props.base_cabinet_depth
            self.obj_z.location.z = props.base_cabinet_height
        if cabinet_type.get_value() == 1:
            self.obj_y.location.y = -props.tall_cabinet_depth
            self.obj_z.location.z = props.tall_cabinet_height
        if cabinet_type.get_value() == 2:
            self.obj_y.location.y = -props.upper_cabinet_depth
            self.obj_z.location.z = props.upper_cabinet_height
            self.obj_bp.location.z = props.height_above_floor - props.upper_cabinet_height

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')

        carcass.set_name('Carcass')
        carcass.loc_x(value=0)
        carcass.loc_y(value=0)
        carcass.loc_z(value=0)
        carcass.dim_x('width',[width])
        carcass.dim_y('depth',[depth])
        carcass.dim_z('height',[height])

        print("Cabinet: Draw Time --- %s seconds ---" % (time.time() - start_time))

    def render(self):
        left_side = None
        right_side = None

        for child in self.carcass.obj_bp.children:
            if "IS_LEFT_SIDE_BP" in child and child["IS_LEFT_SIDE_BP"]:
                left_side = pc_types.Assembly(child)
            if "IS_RIGHT_SIDE_BP" in child and child["IS_RIGHT_SIDE_BP"]:
                right_side = pc_types.Assembly(child)

        left_finished_end = self.carcass.get_prompt('Left Finished End')
        right_finished_end = self.carcass.get_prompt('Right Finished End')
        if left_finished_end:
            left_finished_end.set_value(True)
        if right_finished_end:
            right_finished_end.set_value(True)            
        home_builder_utils.update_side_material(left_side,left_finished_end.get_value())
        home_builder_utils.update_side_material(right_side,right_finished_end.get_value())