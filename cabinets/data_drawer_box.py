import bpy
import time
import math
from os import path
from ..pc_lib import pc_types, pc_unit, pc_utils

from . import common_prompts
from . import data_cabinet_parts
from .. import home_builder_utils
from .. import home_builder_pointers
from .. import home_builder_paths

class Wood_Drawer_Box(pc_types.Assembly):

    def draw(self):
        self.create_assembly()
        self.set_name("Wood Drawer Box")

        hide = self.add_prompt("Hide",'CHECKBOX',False)
        drawer_side_thickness = self.add_prompt("Drawer Side Thickness",'DISTANCE',pc_unit.inch(.75))
        front_back_thickness = self.add_prompt("Front Back Thickness",'DISTANCE',pc_unit.inch(.75))
        bottom_thickness = self.add_prompt("Drawer Bottom Thickness",'DISTANCE',pc_unit.inch(.25))
        drawer_box_bottom_dado_depth = self.add_prompt("Drawer Box Bottom Dado Depth",'DISTANCE',pc_unit.inch(.25))
        drawer_box_z_loc = self.add_prompt("Drawer Bottom Z Location",'DISTANCE',pc_unit.inch(.5))

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        h = hide.get_var('h')
        dt = drawer_side_thickness.get_var('dt')
        fbt = front_back_thickness.get_var('fbt')
        bt = bottom_thickness.get_var('bt')
        dado_depth = drawer_box_bottom_dado_depth.get_var('dado_depth')
        b_z_loc = drawer_box_z_loc.get_var('b_z_loc')

        left_side = data_cabinet_parts.add_cabinet_shelf(self)
        left_side.obj_bp['IS_CUTPART_BP'] = True
        left_side.obj_bp['IS_LEFT_DRAWER_SIDE_BP'] = True
        left_side.set_name("Left Drawer Side")
        left_side.loc_x(value = 0)
        left_side.loc_y(value = 0)
        left_side.loc_z(value = 0)
        left_side.rot_x(value = math.radians(90))
        left_side.rot_y(value = 0)
        left_side.rot_z(value = math.radians(90))
        left_side.dim_x('depth',[depth])
        left_side.dim_y('height',[height])
        left_side.dim_z('dt',[dt])      

        right_side = data_cabinet_parts.add_cabinet_shelf(self)
        right_side.obj_bp['IS_CUTPART_BP'] = True
        right_side.set_name("Right Drawer Side")
        right_side.obj_bp['IS_RIGHT_DRAWER_SIDE_BP'] = True
        right_side.loc_x('width',[width])
        right_side.loc_y(value = 0)
        right_side.loc_z(value = 0)
        right_side.rot_x(value = math.radians(90))
        right_side.rot_y(value = 0)
        right_side.rot_z(value = math.radians(90))
        right_side.dim_x('depth',[depth])
        right_side.dim_y('height',[height])
        right_side.dim_z('-dt',[dt])          

        front = data_cabinet_parts.add_cabinet_shelf(self)
        front.obj_bp['IS_CUTPART_BP'] = True
        front.obj_bp['IS_DRAWER_SUB_FRONT_BP'] = True
        front.set_name("Drawer Front")
        front.loc_x('dt',[dt])
        front.loc_y(value = 0)
        front.loc_z(value = 0)
        front.rot_x(value = math.radians(90))
        front.rot_y(value = 0)
        front.rot_z(value = 0)
        front.dim_x('width-(dt*2)',[width,dt])
        front.dim_y('height',[height])
        front.dim_z('-fbt',[fbt])              

        back = data_cabinet_parts.add_cabinet_shelf(self)
        back.obj_bp['IS_CUTPART_BP'] = True
        back.obj_bp['IS_DRAWER_BACK_BP'] = True
        back.set_name("Drawer Back")
        back.loc_x('dt',[dt])
        back.loc_y('depth',[depth])
        back.loc_z(value = 0)
        back.rot_x(value = math.radians(90))
        back.rot_y(value = 0)
        back.rot_z(value = 0)
        back.dim_x('width-(dt*2)',[width,dt])
        back.dim_y('height',[height])
        back.dim_z('fbt',[fbt])            

        bottom = data_cabinet_parts.add_cabinet_shelf(self)
        bottom.obj_bp['IS_CUTPART_BP'] = True
        bottom.obj_bp['IS_DRAWER_BOTTOM_BP'] = True
        bottom.set_name("Drawer Bottom")
        bottom.loc_x('width-dt+dado_depth',[width,dt,dado_depth])
        bottom.loc_y('fbt-dado_depth',[fbt,dado_depth])
        bottom.loc_z('b_z_loc',[b_z_loc])
        bottom.rot_x(value = 0)
        bottom.rot_y(value = 0)
        bottom.rot_z(value = math.radians(90))
        bottom.dim_x('depth-(dt*2)+(dado_depth*2)',[depth,dt,dado_depth])
        bottom.dim_y('width-(fbt*2)+(dado_depth*2)',[width,fbt,dado_depth])
        bottom.dim_z('-bt',[bt])            