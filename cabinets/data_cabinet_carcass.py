import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinet_parts
from .. import home_builder_utils
from . import common_prompts

from os import path

class Base_Simple(pc_types.Assembly):

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Carcass")

        self.obj_x.location.x = pc_unit.inch(18) 
        self.obj_y.location.y = -props.base_cabinet_depth
        self.obj_z.location.z = props.base_cabinet_height

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')

        toe_kick_height = self.obj_prompts.pyclone.add_prompt('DISTANCE',"Toe Kick Height")
        toe_kick_height.set_value(pc_unit.inch(4))
        toe_kick_setback = self.obj_prompts.pyclone.add_prompt('DISTANCE',"Toe Kick Setback")
        toe_kick_setback.set_value(pc_unit.inch(3.25))
        material_thickness = self.obj_prompts.pyclone.add_prompt('DISTANCE',"Material Thickness")
        material_thickness.set_value(pc_unit.inch(.75))
        run_sides_to_floor = self.obj_prompts.pyclone.add_prompt('CHECKBOX',"Run Sides to Floor")
        run_sides_to_floor.set_value(pc_unit.inch(.75))

        toe_kick_height = toe_kick_height.get_var("toe_kick_height")
        toe_kick_setback = toe_kick_setback.get_var("toe_kick_setback")
        material_thickness = material_thickness.get_var("material_thickness")

        bottom = self.add_assembly(data_cabinet_parts.Cutpart())
        bottom.set_name('Bottom')
        bottom.loc_x('material_thickness',[material_thickness])
        bottom.loc_y(value=0)
        bottom.loc_z('toe_kick_height',[toe_kick_height])
        bottom.dim_x('width-(material_thickness*2)',[width,material_thickness])
        bottom.dim_y('depth',[depth])
        bottom.dim_z('material_thickness',[material_thickness])
        kitchen_utils.flip_normals(bottom)

        top = self.add_assembly(data_cabinet_parts.Cutpart())
        top.set_name('Top')
        top.loc_x('material_thickness',[material_thickness])
        top.loc_y(value=0)
        top.loc_z('height',[height])
        top.dim_x('width-(material_thickness*2)',[width,material_thickness])
        top.dim_y('depth',[depth])
        top.dim_z('-material_thickness',[material_thickness])

        left_side = self.add_assembly(data_cabinet_parts.Cutpart())
        left_side.set_name('Left Side')
        left_side.loc_x(value=0)
        left_side.loc_y(value=0)
        left_side.loc_z(value=0)
        left_side.rot_y(value=math.radians(-90))
        left_side.dim_x('height',[height])
        left_side.dim_y('depth',[depth])
        left_side.dim_z('-material_thickness',[material_thickness])

        right_side = self.add_assembly(data_cabinet_parts.Cutpart())
        right_side.set_name('Left Side')
        right_side.loc_x('width',[width])
        right_side.loc_y(value=0)
        right_side.loc_z(value=0)
        right_side.rot_y(value=math.radians(-90))
        right_side.dim_x('height',[height])
        right_side.dim_y('depth',[depth])
        right_side.dim_z('material_thickness',[material_thickness])
        kitchen_utils.flip_normals(right_side)

        back = self.add_assembly(data_cabinet_parts.Cutpart())
        back.set_name('Back')
        back.loc_x('width-material_thickness',[width,material_thickness])
        back.loc_y(value=0)
        back.loc_z('toe_kick_height+material_thickness',[toe_kick_height,material_thickness])
        back.rot_y(value=math.radians(-90))
        back.rot_z(value=math.radians(90))
        back.dim_x('height-toe_kick_height-(material_thickness*2)',[height,toe_kick_height,material_thickness])
        back.dim_y('width-(material_thickness*2)',[width,material_thickness])
        back.dim_z('material_thickness',[material_thickness])

        toe_kick = self.add_assembly(data_cabinet_parts.Cutpart())
        toe_kick.set_name('Toe Kick')
        toe_kick.loc_x('material_thickness',[material_thickness])
        toe_kick.loc_y('depth+toe_kick_setback',[depth,toe_kick_setback])
        toe_kick.loc_z(value=0)
        toe_kick.rot_x(value=math.radians(90))
        toe_kick.dim_x('width-(material_thickness*2)',[width,material_thickness])
        toe_kick.dim_y('toe_kick_height',[toe_kick_height])
        toe_kick.dim_z('material_thickness',[material_thickness])

class Base_Advanced(pc_types.Assembly):
    carcass_type = 'Base'

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Carcass")
        self.obj_bp["IS_CARCASS_BP"] = True

        common_prompts.add_carcass_prompts(self)

        self.obj_x.location.x = pc_unit.inch(18) 
        self.obj_y.location.y = -props.base_cabinet_depth
        self.obj_z.location.z = props.base_cabinet_height

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')

        toe_kick_height = self.get_prompt("Toe Kick Height").get_var("toe_kick_height")
        toe_kick_setback = self.get_prompt("Toe Kick Setback").get_var("toe_kick_setback")
        material_thickness = self.get_prompt("Material Thickness").get_var("material_thickness")
        boolean_overhang = self.get_prompt("Boolean Overhang").get_var("boolean_overhang")

        bottom = data_cabinet_parts.add_carcass_part(self)
        bottom.set_name('Bottom')
        bottom.loc_x('material_thickness',[material_thickness])
        bottom.loc_y(value=0)
        bottom.loc_z('toe_kick_height',[toe_kick_height])
        bottom.dim_x('width-(material_thickness*2)',[width,material_thickness])
        bottom.dim_y('depth',[depth])
        bottom.dim_z('material_thickness',[material_thickness])
        home_builder_utils.flip_normals(bottom)

        top = data_cabinet_parts.add_carcass_part(self)
        top.set_name('Top')
        top.loc_x('material_thickness',[material_thickness])
        top.loc_y(value=0)
        top.loc_z('height',[height])
        top.dim_x('width-(material_thickness*2)',[width,material_thickness])
        top.dim_y('depth',[depth])
        top.dim_z('-material_thickness',[material_thickness])

        left_side = data_cabinet_parts.add_carcass_part(self)
        left_side.obj_bp["IS_LEFT_SIDE_BP"] = True
        left_side.set_name('Left Side')
        left_side.loc_x(value=0)
        left_side.loc_y(value=0)
        left_side.loc_z(value=0)
        left_side.rot_y(value=math.radians(-90))
        left_side.dim_x('height',[height])
        left_side.dim_y('depth',[depth])
        left_side.dim_z('-material_thickness',[material_thickness])

        left_notch = data_cabinet_parts.Square_Cutout()
        self.add_assembly(left_notch)
        left_notch.assign_boolean(left_side)
        left_notch.set_name('Left Square Cutout')
        left_notch.loc_x('-boolean_overhang/2',[boolean_overhang])
        left_notch.loc_y('depth-boolean_overhang/2',[depth,boolean_overhang])
        left_notch.loc_z('-boolean_overhang',[boolean_overhang])
        left_notch.rot_y(value=math.radians(-90))
        left_notch.dim_x('toe_kick_height+boolean_overhang',[toe_kick_height,boolean_overhang])
        left_notch.dim_y('toe_kick_setback+boolean_overhang/2',[toe_kick_setback,boolean_overhang])
        left_notch.dim_z('-material_thickness-boolean_overhang',[material_thickness,boolean_overhang])   
        home_builder_utils.flip_normals(left_notch)    

        right_side = data_cabinet_parts.add_carcass_part(self)
        right_side.obj_bp["IS_RIGHT_SIDE_BP"] = True
        right_side.set_name('Right Side')
        right_side.loc_x('width',[width])
        right_side.loc_y(value=0)
        right_side.loc_z(value=0)
        right_side.rot_y(value=math.radians(-90))
        right_side.dim_x('height',[height])
        right_side.dim_y('depth',[depth])
        right_side.dim_z('material_thickness',[material_thickness])
        home_builder_utils.flip_normals(right_side)

        right_notch = data_cabinet_parts.Square_Cutout()
        self.add_assembly(right_notch)
        right_notch.assign_boolean(right_side)
        right_notch.set_name('Right Square Cutout')
        right_notch.loc_x('width+boolean_overhang/2',[width,boolean_overhang])
        right_notch.loc_y('depth-boolean_overhang/2',[depth,boolean_overhang])
        right_notch.loc_z('-boolean_overhang',[boolean_overhang])
        right_notch.rot_y(value=math.radians(-90))
        right_notch.dim_x('toe_kick_height+boolean_overhang',[toe_kick_height,boolean_overhang])
        right_notch.dim_y('toe_kick_setback+boolean_overhang/2',[toe_kick_setback,boolean_overhang])
        right_notch.dim_z('material_thickness+boolean_overhang',[material_thickness,boolean_overhang])   
        # home_builder_utils.flip_normals(right_notch)    

        back = data_cabinet_parts.add_carcass_part(self)
        back.set_name('Back')
        back.loc_x('width-material_thickness',[width,material_thickness])
        back.loc_y(value=0)
        back.loc_z('toe_kick_height+material_thickness',[toe_kick_height,material_thickness])
        back.rot_y(value=math.radians(-90))
        back.rot_z(value=math.radians(90))
        back.dim_x('height-toe_kick_height-(material_thickness*2)',[height,toe_kick_height,material_thickness])
        back.dim_y('width-(material_thickness*2)',[width,material_thickness])
        back.dim_z('material_thickness',[material_thickness])

        toe_kick = data_cabinet_parts.add_carcass_part(self)
        toe_kick.set_name('Toe Kick')
        toe_kick.loc_x('material_thickness',[material_thickness])
        toe_kick.loc_y('depth+toe_kick_setback+material_thickness',[depth,toe_kick_setback,material_thickness])
        toe_kick.loc_z(value=0)
        toe_kick.rot_x(value=math.radians(90))
        toe_kick.dim_x('width-(material_thickness*2)',[width,material_thickness])
        toe_kick.dim_y('toe_kick_height',[toe_kick_height])
        toe_kick.dim_z('material_thickness',[material_thickness])

class Refrigerator(pc_types.Assembly):
    category_name = "Carcass"
    prompt_id = "room.part_prompts"
    placement_id = "room.draw_multiple_walls"

class Transition(pc_types.Assembly):
    category_name = "Carcass"
    prompt_id = "room.part_prompts"
    placement_id = "room.draw_multiple_walls"

class Blind_Corner(pc_types.Assembly):
    category_name = "Carcass"
    prompt_id = "room.part_prompts"
    placement_id = "room.draw_multiple_walls"

class Inside_Corner(pc_types.Assembly):
    category_name = "Carcass"
    prompt_id = "room.part_prompts"
    placement_id = "room.draw_multiple_walls"

class Outside_Corner(pc_types.Assembly):
    category_name = "Carcass"
    prompt_id = "room.part_prompts"
    placement_id = "room.draw_multiple_walls"