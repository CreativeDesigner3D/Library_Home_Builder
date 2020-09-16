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
    category_name = "Cabinets"
    
    width = pc_unit.inch(18)

    carcass = None
    interior = None
    exterior = None
    splitter = None

    def draw(self):
        start_time = time.time()
        
        self.obj_bp["IS_CABINET_BP"] = True
        self.obj_y['IS_MIRROR'] = True

        cabinet_type = self.carcass.get_prompt("Cabinet Type")
        if self.exterior:
            self.carcass.add_insert(self,self.exterior)
        if self.splitter:
            self.carcass.add_insert(self,self.splitter)            
        if self.interior:
            self.carcass.add_insert(self,self.interior)

        #BASE CABINET
        if cabinet_type.get_value() == 'Base':
            cabinet_utils.add_countertop(self)
            common_prompts.add_sink_prompts(self)

        print("Cabinet: Draw Time --- %s seconds ---" % (time.time() - start_time))

    def pre_draw(self):
        self.create_assembly()
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        common_prompts.add_cabinet_prompts(self)
        common_prompts.add_filler_prompts(self)
        
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        left_adjment_width = self.get_prompt("Left Adjustment Width").get_var('left_adjment_width')
        right_adjment_width = self.get_prompt("Right Adjustment Width").get_var('right_adjment_width')

        self.carcass = self.add_assembly(self.carcass)
        self.carcass.set_name('Carcass')
        self.carcass.loc_x('left_adjment_width',[left_adjment_width])
        self.carcass.loc_y(value=0)
        self.carcass.loc_z(value=0)
        self.carcass.dim_x('width-left_adjment_width-right_adjment_width',[width,left_adjment_width,right_adjment_width])
        self.carcass.dim_y('depth',[depth])
        self.carcass.dim_z('height',[height])

        cabinet_type = self.carcass.get_prompt("Cabinet Type")
        self.obj_x.location.x = self.width 
        if cabinet_type.get_value() == 'Base':
            self.obj_y.location.y = -props.base_cabinet_depth
            self.obj_z.location.z = props.base_cabinet_height
        if cabinet_type.get_value() == 'Tall':
            self.obj_y.location.y = -props.tall_cabinet_depth
            self.obj_z.location.z = props.tall_cabinet_height
        if cabinet_type.get_value() == 'Upper':
            self.obj_y.location.y = -props.upper_cabinet_depth
            self.obj_z.location.z = props.upper_cabinet_height
            self.obj_bp.location.z = props.height_above_floor - props.upper_cabinet_height

    def render(self):
        left_side = None
        right_side = None

        for child in self.carcass.obj_bp.children:
            if "IS_LEFT_SIDE_BP" in child and child["IS_LEFT_SIDE_BP"]:
                left_side = pc_types.Assembly(child)
            if "IS_RIGHT_SIDE_BP" in child and child["IS_RIGHT_SIDE_BP"]:
                right_side = pc_types.Assembly(child)
            if "IS_BACK_BP" in child and child["IS_BACK_BP"]:
                back = pc_types.Assembly(child)

        left_finished_end = self.carcass.get_prompt('Left Finished End')
        right_finished_end = self.carcass.get_prompt('Right Finished End')
        finished_back = self.carcass.get_prompt('Finished Back')
        if left_finished_end:
            left_finished_end.set_value(True)
        if right_finished_end:
            right_finished_end.set_value(True)            
        home_builder_utils.update_side_material(left_side,left_finished_end.get_value(),finished_back.get_value())
        home_builder_utils.update_side_material(right_side,right_finished_end.get_value(),finished_back.get_value())