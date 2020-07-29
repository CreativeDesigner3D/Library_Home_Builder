import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinet_parts
from .. import home_builder_utils
from . import common_prompts

from os import path

def add_cabinet_top(assembly):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    height = assembly.obj_z.pyclone.get_var('location.z','height')
    depth = assembly.obj_y.pyclone.get_var('location.y','depth')
    material_thickness = assembly.get_prompt("Material Thickness").get_var("material_thickness")

    top = data_cabinet_parts.add_carcass_part(assembly)
    top.set_name('Top')
    top.loc_x('material_thickness',[material_thickness])
    top.loc_y(value=0)
    top.loc_z('height',[height])
    top.dim_x('width-(material_thickness*2)',[width,material_thickness])
    top.dim_y('depth',[depth])
    top.dim_z('-material_thickness',[material_thickness])
    return top

def add_cabinet_bottom(assembly):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    depth = assembly.obj_y.pyclone.get_var('location.y','depth')

    toe_kick_height = assembly.get_prompt("Toe Kick Height").get_var("toe_kick_height")
    material_thickness = assembly.get_prompt("Material Thickness").get_var("material_thickness")

    bottom = data_cabinet_parts.add_carcass_part(assembly)
    bottom.set_name('Bottom')
    bottom.loc_x('material_thickness',[material_thickness])
    bottom.loc_y(value=0)
    bottom.loc_z('toe_kick_height',[toe_kick_height])
    bottom.dim_x('width-(material_thickness*2)',[width,material_thickness])
    bottom.dim_y('depth',[depth])
    bottom.dim_z('material_thickness',[material_thickness])
    home_builder_utils.flip_normals(bottom)
    return bottom

def add_upper_cabinet_bottom(assembly):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    depth = assembly.obj_y.pyclone.get_var('location.y','depth')
    material_thickness = assembly.get_prompt("Material Thickness").get_var("material_thickness")

    bottom = data_cabinet_parts.add_carcass_part(assembly)
    bottom.set_name('Bottom')
    bottom.loc_x('material_thickness',[material_thickness])
    bottom.loc_y(value=0)
    bottom.loc_z(value=0)
    bottom.dim_x('width-(material_thickness*2)',[width,material_thickness])
    bottom.dim_y('depth',[depth])
    bottom.dim_z('material_thickness',[material_thickness])
    home_builder_utils.flip_normals(bottom)
    return bottom

def add_cabinet_back(assembly):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    height = assembly.obj_z.pyclone.get_var('location.z','height')
    material_thickness = assembly.get_prompt("Material Thickness").get_var("material_thickness")
    toe_kick_height = assembly.get_prompt("Toe Kick Height").get_var("toe_kick_height")

    back = data_cabinet_parts.add_carcass_part(assembly)
    back.set_name('Back')
    back.loc_x('width-material_thickness',[width,material_thickness])
    back.loc_y(value=0)
    back.loc_z('toe_kick_height+material_thickness',[toe_kick_height,material_thickness])
    back.rot_y(value=math.radians(-90))
    back.rot_z(value=math.radians(90))
    back.dim_x('height-toe_kick_height-(material_thickness*2)',[height,toe_kick_height,material_thickness])
    back.dim_y('width-(material_thickness*2)',[width,material_thickness])
    back.dim_z('material_thickness',[material_thickness])
    return back

def add_upper_cabinet_back(assembly):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    height = assembly.obj_z.pyclone.get_var('location.z','height')
    material_thickness = assembly.get_prompt("Material Thickness").get_var("material_thickness")

    back = data_cabinet_parts.add_carcass_part(assembly)
    back.set_name('Back')
    back.loc_x('width-material_thickness',[width,material_thickness])
    back.loc_y(value=0)
    back.loc_z('material_thickness',[material_thickness])
    back.rot_y(value=math.radians(-90))
    back.rot_z(value=math.radians(90))
    back.dim_x('height-(material_thickness*2)',[height,material_thickness])
    back.dim_y('width-(material_thickness*2)',[width,material_thickness])
    back.dim_z('material_thickness',[material_thickness])
    return back

def add_toe_kick(assembly):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    depth = assembly.obj_y.pyclone.get_var('location.y','depth')
    material_thickness = assembly.get_prompt("Material Thickness").get_var("material_thickness")
    toe_kick_height = assembly.get_prompt("Toe Kick Height").get_var("toe_kick_height")
    toe_kick_setback = assembly.get_prompt("Toe Kick Setback").get_var("toe_kick_setback")

    toe_kick = data_cabinet_parts.add_carcass_part(assembly)
    toe_kick.set_name('Toe Kick')
    toe_kick.loc_x('material_thickness',[material_thickness])
    toe_kick.loc_y('depth+toe_kick_setback+material_thickness',[depth,toe_kick_setback,material_thickness])
    toe_kick.loc_z(value=0)
    toe_kick.rot_x(value=math.radians(90))
    toe_kick.dim_x('width-(material_thickness*2)',[width,material_thickness])
    toe_kick.dim_y('toe_kick_height',[toe_kick_height])
    toe_kick.dim_z('material_thickness',[material_thickness])
    return toe_kick

def add_cabinet_sides(assembly,add_toe_kick_notch):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    depth = assembly.obj_y.pyclone.get_var('location.y','depth')
    height = assembly.obj_z.pyclone.get_var('location.z','height')
    material_thickness = assembly.get_prompt("Material Thickness").get_var("material_thickness")

    left_side = data_cabinet_parts.add_carcass_part(assembly)
    left_side.obj_bp["IS_LEFT_SIDE_BP"] = True
    left_side.set_name('Left Side')
    left_side.loc_x(value=0)
    left_side.loc_y(value=0)
    left_side.loc_z(value=0)
    left_side.rot_y(value=math.radians(-90))
    left_side.dim_x('height',[height])
    left_side.dim_y('depth',[depth])
    left_side.dim_z('-material_thickness',[material_thickness])

    right_side = data_cabinet_parts.add_carcass_part(assembly)
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

    if add_toe_kick_notch:
        toe_kick_height = assembly.get_prompt("Toe Kick Height").get_var("toe_kick_height")
        toe_kick_setback = assembly.get_prompt("Toe Kick Setback").get_var("toe_kick_setback")
        boolean_overhang = assembly.get_prompt("Boolean Overhang").get_var("boolean_overhang")

        left_notch = data_cabinet_parts.Square_Cutout()
        assembly.add_assembly(left_notch)
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

        right_notch = data_cabinet_parts.Square_Cutout()
        assembly.add_assembly(right_notch)
        right_notch.assign_boolean(right_side)
        right_notch.set_name('Right Square Cutout')
        right_notch.loc_x('width+boolean_overhang/2',[width,boolean_overhang])
        right_notch.loc_y('depth-boolean_overhang/2',[depth,boolean_overhang])
        right_notch.loc_z('-boolean_overhang',[boolean_overhang])
        right_notch.rot_y(value=math.radians(-90))
        right_notch.dim_x('toe_kick_height+boolean_overhang',[toe_kick_height,boolean_overhang])
        right_notch.dim_y('toe_kick_setback+boolean_overhang/2',[toe_kick_setback,boolean_overhang])
        right_notch.dim_z('material_thickness+boolean_overhang',[material_thickness,boolean_overhang])  

    return left_side, right_side

class Base_Simple(pc_types.Assembly):

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Carcass")
        self.obj_bp["IS_CARCASS_BP"] = True

        self.obj_x.location.x = pc_unit.inch(18) 
        self.obj_y.location.y = -props.base_cabinet_depth
        self.obj_z.location.z = props.base_cabinet_height

        common_prompts.add_cabinet_prompts(self)
        common_prompts.add_carcass_prompts(self)
        common_prompts.add_base_assembly_prompts(self)

        cabinet_type = self.get_prompt("Cabinet Type")
        cabinet_type.set_value(0)

        add_cabinet_bottom(self)
        add_cabinet_top(self)
        add_cabinet_sides(self,add_toe_kick_notch=False)
        add_cabinet_back(self)
        add_toe_kick(self)


class Base_Advanced(pc_types.Assembly):

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Carcass")
        self.obj_bp["IS_CARCASS_BP"] = True

        common_prompts.add_cabinet_prompts(self)
        common_prompts.add_carcass_prompts(self)
        common_prompts.add_base_assembly_prompts(self)

        cabinet_type = self.get_prompt("Cabinet Type")
        cabinet_type.set_value(0)

        self.obj_x.location.x = pc_unit.inch(18) 
        self.obj_y.location.y = -props.base_cabinet_depth
        self.obj_z.location.z = props.base_cabinet_height

        add_cabinet_bottom(self)
        add_cabinet_top(self)
        add_cabinet_sides(self,add_toe_kick_notch=True)
        add_cabinet_back(self)
        add_toe_kick(self)


class Tall_Advanced(pc_types.Assembly):

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Carcass")
        self.obj_bp["IS_CARCASS_BP"] = True

        common_prompts.add_cabinet_prompts(self)
        common_prompts.add_carcass_prompts(self)
        common_prompts.add_base_assembly_prompts(self)

        cabinet_type = self.get_prompt("Cabinet Type")
        cabinet_type.set_value(1)

        self.obj_x.location.x = pc_unit.inch(18) 
        self.obj_y.location.y = -props.tall_cabinet_depth
        self.obj_z.location.z = props.tall_cabinet_height

        add_cabinet_bottom(self)
        add_cabinet_top(self)
        add_cabinet_sides(self,add_toe_kick_notch=True)
        add_cabinet_back(self)
        add_toe_kick(self)


class Upper_Advanced(pc_types.Assembly):

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Carcass")
        self.obj_bp["IS_CARCASS_BP"] = True

        common_prompts.add_cabinet_prompts(self)
        common_prompts.add_carcass_prompts(self)

        cabinet_type = self.get_prompt("Cabinet Type")
        cabinet_type.set_value(2)

        self.obj_x.location.x = pc_unit.inch(18) 
        self.obj_y.location.y = -props.upper_cabinet_depth
        self.obj_z.location.z = props.upper_cabinet_height

        add_upper_cabinet_bottom(self)
        add_cabinet_top(self)
        add_cabinet_sides(self,add_toe_kick_notch=False)
        add_upper_cabinet_back(self)


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