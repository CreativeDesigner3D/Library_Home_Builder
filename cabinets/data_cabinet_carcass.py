import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinet_parts
from .. import home_builder_utils
from .. import home_builder_pointers
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
    bottom.obj_bp["IS_BOTTOM_BP"] = True
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
    bottom.obj_bp["IS_BOTTOM_BP"] = True
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
    finished_back = assembly.get_prompt("Finished Back")

    back = data_cabinet_parts.add_carcass_part(assembly)
    back.obj_bp["IS_BACK_BP"] = True
    back.set_name('Back')
    back.loc_x('width-material_thickness',[width,material_thickness])
    back.loc_y(value=0)
    back.loc_z('toe_kick_height+material_thickness',[toe_kick_height,material_thickness])
    back.rot_y(value=math.radians(-90))
    back.rot_z(value=math.radians(90))
    back.dim_x('height-toe_kick_height-(material_thickness*2)',[height,toe_kick_height,material_thickness])
    back.dim_y('width-(material_thickness*2)',[width,material_thickness])
    back.dim_z('material_thickness',[material_thickness])
    home_builder_pointers.update_cabinet_back_material(back,finished_back.get_value())
    return back

def add_upper_cabinet_back(assembly):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    height = assembly.obj_z.pyclone.get_var('location.z','height')
    material_thickness = assembly.get_prompt("Material Thickness").get_var("material_thickness")
    finished_back = assembly.get_prompt("Finished Back")

    back = data_cabinet_parts.add_carcass_part(assembly)
    back.obj_bp["IS_BACK_BP"] = True
    back.set_name('Back')
    back.loc_x('width-material_thickness',[width,material_thickness])
    back.loc_y(value=0)
    back.loc_z('material_thickness',[material_thickness])
    back.rot_y(value=math.radians(-90))
    back.rot_z(value=math.radians(90))
    back.dim_x('height-(material_thickness*2)',[height,material_thickness])
    back.dim_y('width-(material_thickness*2)',[width,material_thickness])
    back.dim_z('material_thickness',[material_thickness])
    home_builder_pointers.update_cabinet_back_material(back,finished_back.get_value())
    return back

def add_toe_kick(assembly):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    depth = assembly.obj_y.pyclone.get_var('location.y','depth')
    material_thickness = assembly.get_prompt("Material Thickness").get_var("material_thickness")
    toe_kick_height = assembly.get_prompt("Toe Kick Height").get_var("toe_kick_height")
    toe_kick_setback = assembly.get_prompt("Toe Kick Setback").get_var("toe_kick_setback")

    toe_kick = data_cabinet_parts.add_double_sided_part(assembly)
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
    left_finished_end = assembly.get_prompt("Left Finished End")
    right_finished_end = assembly.get_prompt("Right Finished End")
    finished_back = assembly.get_prompt("Finished Back")

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
    home_builder_pointers.update_side_material(left_side,left_finished_end.get_value(),finished_back.get_value())
    home_builder_pointers.update_side_material(right_side,right_finished_end.get_value(),finished_back.get_value())

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

def add_kick_lighting(assembly):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    depth = assembly.obj_y.pyclone.get_var('location.y','depth')
    material_thickness = assembly.get_prompt("Material Thickness").get_var("material_thickness")
    add_bottom_light = assembly.get_prompt("Add Bottom Light").get_var("add_bottom_light")
    lighting_width = assembly.get_prompt("Lighting Width").get_var("lighting_width")
    lighting_dim_from_front = assembly.get_prompt("Lighting Dim From Front").get_var("lighting_dim_from_front")
    lighting_inset_from_sides = assembly.get_prompt("Lighting Inset From Sides").get_var("lighting_inset_from_sides")
    toe_kick_height = assembly.get_prompt("Toe Kick Height").get_var("toe_kick_height")

    light = data_cabinet_parts.add_lighting_strip_part(assembly)
    light.set_name('Kick Lighting')
    light.loc_x('lighting_inset_from_sides',[lighting_inset_from_sides])
    light.loc_y('depth+lighting_dim_from_front',[depth,lighting_dim_from_front])
    light.loc_z('toe_kick_height',[toe_kick_height])
    light.rot_y(value=0)
    light.dim_x('width-(lighting_inset_from_sides*2)',[width,lighting_inset_from_sides])
    light.dim_y('lighting_width',[lighting_width])
    light.dim_z(value=-.001)
    home_builder_utils.flip_normals(light)    
    hide = light.get_prompt("Hide")
    hide.set_formula('IF(add_bottom_light==True,False,True)',[add_bottom_light])   

    light_obj = assembly.add_light('Kick Light','AREA')
    light_obj.data.shape = 'RECTANGLE'
    light_obj.data.energy = .5
    light_obj.pyclone.loc_x('width/2',[width])
    light_obj.pyclone.loc_y('depth+lighting_dim_from_front',[depth,lighting_dim_from_front])
    light_obj.pyclone.loc_z('toe_kick_height',[toe_kick_height])
    light_obj.pyclone.add_data_driver('size',-1,'width-(lighting_inset_from_sides*2)',[width,lighting_inset_from_sides])
    light_obj.pyclone.add_data_driver('size_y',-1,'lighting_width',[lighting_width])
    light_obj.pyclone.hide('IF(add_bottom_light==True,False,True)',[add_bottom_light])   
 
def add_under_cabinet_lighting(assembly):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    depth = assembly.obj_y.pyclone.get_var('location.y','depth')
    add_bottom_light = assembly.get_prompt("Add Bottom Light").get_var("add_bottom_light")
    lighting_width = assembly.get_prompt("Lighting Width").get_var("lighting_width")
    lighting_dim_from_front = assembly.get_prompt("Lighting Dim From Front").get_var("lighting_dim_from_front")
    lighting_inset_from_sides = assembly.get_prompt("Lighting Inset From Sides").get_var("lighting_inset_from_sides")

    light = data_cabinet_parts.add_lighting_strip_part(assembly)
    light.set_name('Under Cabinet Light')
    light.loc_x('lighting_inset_from_sides',[lighting_inset_from_sides])
    light.loc_y('depth+lighting_dim_from_front',[depth,lighting_dim_from_front])
    light.loc_z(value=0)
    light.rot_y(value=0)
    light.dim_x('width-(lighting_inset_from_sides*2)',[width,lighting_inset_from_sides])
    light.dim_y('lighting_width',[lighting_width])
    light.dim_z(value=-.001)
    home_builder_utils.flip_normals(light)    
    hide = light.get_prompt("Hide")
    hide.set_formula('IF(add_bottom_light==True,False,True)',[add_bottom_light])   

    light_obj = assembly.add_light('Under Cabinet Light','AREA')
    light_obj.data.shape = 'RECTANGLE'
    light_obj.data.energy = .5
    light_obj.pyclone.loc_x('width/2',[width])
    light_obj.pyclone.loc_y('depth+lighting_dim_from_front',[depth,lighting_dim_from_front])
    light_obj.pyclone.loc_z(value=0)
    light_obj.pyclone.add_data_driver('size',-1,'width-(lighting_inset_from_sides*2)',[width,lighting_inset_from_sides])
    light_obj.pyclone.add_data_driver('size_y',-1,'lighting_width',[lighting_width])
    light_obj.pyclone.hide('IF(add_bottom_light==True,False,True)',[add_bottom_light])

def add_side_lighting(assembly):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    height = assembly.obj_z.pyclone.get_var('location.z','height')
    depth = assembly.obj_y.pyclone.get_var('location.y','depth')
    material_thickness = assembly.get_prompt("Material Thickness").get_var("material_thickness")
    add_side_light = assembly.get_prompt("Add Side Light").get_var("add_side_light")
    lighting_width = assembly.get_prompt("Lighting Width").get_var("lighting_width")
    lighting_dim_from_front = assembly.get_prompt("Lighting Dim From Front").get_var("lighting_dim_from_front")
    lighting_inset_from_sides = assembly.get_prompt("Lighting Inset From Sides").get_var("lighting_inset_from_sides")
    toe_kick_height = assembly.get_prompt("Toe Kick Height")

    l_light = data_cabinet_parts.add_lighting_strip_part(assembly)
    l_light.set_name('Top Cabinet Light')
    l_light.loc_x('material_thickness',[material_thickness])
    l_light.loc_y('depth+lighting_dim_from_front',[depth,lighting_dim_from_front])
    l_light.rot_y(value=math.radians(-90))
    if toe_kick_height:
        kick_height = toe_kick_height.get_var('kick_height')    
        l_light.loc_z('kick_height+material_thickness',[kick_height,material_thickness])
        l_light.dim_x('height-(lighting_inset_from_sides*2)-kick_height',[height,lighting_inset_from_sides,kick_height])
    else:
        l_light.dim_x('height-(lighting_inset_from_sides*2)',[height,lighting_inset_from_sides])
        l_light.loc_z('material_thickness',[material_thickness])
    l_light.dim_y('lighting_width',[lighting_width])
    l_light.dim_z(value=-.001)
    home_builder_utils.flip_normals(l_light)    
    hide = l_light.get_prompt("Hide")
    hide.set_formula('IF(add_side_light==True,False,True)',[add_side_light])   

    l_light_obj = assembly.add_light('Under Cabinet Light','AREA')
    l_light_obj.data.shape = 'RECTANGLE'
    l_light_obj.data.energy = .5
    l_light_obj.pyclone.loc_x('material_thickness+.001',[material_thickness])
    l_light_obj.pyclone.loc_y('depth+lighting_dim_from_front+(lighting_width)/2',[depth,lighting_dim_from_front,lighting_width])
    if toe_kick_height:
        kick_height = toe_kick_height.get_var('kick_height')
        l_light_obj.pyclone.loc_z('(height+kick_height)/2',[height,kick_height])
        l_light_obj.pyclone.add_data_driver('size',-1,'height-(lighting_inset_from_sides*2)-kick_height',
        [height,lighting_inset_from_sides,kick_height])
    else:
        l_light_obj.pyclone.loc_z('height/2',[height,material_thickness])
        l_light_obj.pyclone.add_data_driver('size',-1,'height-(lighting_inset_from_sides*2)',
        [height,lighting_inset_from_sides])
    l_light_obj.pyclone.rot_y(value=math.radians(-90))
    l_light_obj.pyclone.add_data_driver('size_y',-1,'lighting_width',[lighting_width])
    l_light_obj.pyclone.hide('IF(add_side_light==True,False,True)',[add_side_light])

    r_light = data_cabinet_parts.add_lighting_strip_part(assembly)
    r_light.set_name('Top Cabinet Light')
    r_light.loc_x('width-material_thickness-.001',[width,material_thickness])
    r_light.loc_y('depth+lighting_dim_from_front+(lighting_width)/2',[depth,lighting_dim_from_front,lighting_width])
    r_light.loc_z('height-material_thickness',[height,material_thickness])
    r_light.rot_y(value=math.radians(90))
    if toe_kick_height:
        kick_height = toe_kick_height.get_var('kick_height')
        r_light.dim_x('height-(lighting_inset_from_sides*2)-kick_height',[height,lighting_inset_from_sides,kick_height])
    else:
        r_light.dim_x('height-(lighting_inset_from_sides*2)',[height,lighting_inset_from_sides])
    r_light.dim_y('lighting_width',[lighting_width])
    r_light.dim_z(value=-.001)
    home_builder_utils.flip_normals(r_light)    
    hide = r_light.get_prompt("Hide")
    hide.set_formula('IF(add_side_light==True,False,True)',[add_side_light])   

    r_light_obj = assembly.add_light('Under Cabinet Light','AREA')
    r_light_obj.data.shape = 'RECTANGLE'
    r_light_obj.data.energy = .5
    r_light_obj.pyclone.loc_x('width-material_thickness',[width,material_thickness])
    r_light_obj.pyclone.loc_y('depth+lighting_dim_from_front',[depth,lighting_dim_from_front])
    if toe_kick_height:
        kick_height = toe_kick_height.get_var('kick_height')
        r_light_obj.pyclone.loc_z('(height+kick_height)/2',[height,kick_height])
        r_light_obj.pyclone.add_data_driver('size',-1,'height-(lighting_inset_from_sides*2)-kick_height',[height,lighting_inset_from_sides,kick_height])
    else:
        r_light_obj.pyclone.loc_z('height/2',[height,material_thickness])
        r_light_obj.pyclone.add_data_driver('size',-1,'height-(lighting_inset_from_sides*2)',[height,lighting_inset_from_sides])
    r_light_obj.pyclone.rot_y(value=math.radians(90))
    r_light_obj.pyclone.add_data_driver('size_y',-1,'lighting_width',[lighting_width])
    r_light_obj.pyclone.hide('IF(add_side_light==True,False,True)',[add_side_light])

def add_top_lighting(assembly):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    height = assembly.obj_z.pyclone.get_var('location.z','height')
    depth = assembly.obj_y.pyclone.get_var('location.y','depth')
    material_thickness = assembly.get_prompt("Material Thickness").get_var("material_thickness")
    add_top_light = assembly.get_prompt("Add Top Light").get_var("add_top_light")
    lighting_width = assembly.get_prompt("Lighting Width").get_var("lighting_width")
    lighting_dim_from_front = assembly.get_prompt("Lighting Dim From Front").get_var("lighting_dim_from_front")
    lighting_inset_from_sides = assembly.get_prompt("Lighting Inset From Sides").get_var("lighting_inset_from_sides")

    light = data_cabinet_parts.add_lighting_strip_part(assembly)
    light.set_name('Top Cabinet Light')
    light.loc_x('lighting_inset_from_sides',[lighting_inset_from_sides])
    light.loc_y('depth+lighting_dim_from_front',[depth,lighting_dim_from_front])
    light.loc_z('height-material_thickness',[height,material_thickness])
    light.rot_y(value=0)
    light.dim_x('width-(lighting_inset_from_sides*2)',[width,lighting_inset_from_sides])
    light.dim_y('lighting_width',[lighting_width])
    light.dim_z(value=-.001)
    home_builder_utils.flip_normals(light)    
    hide = light.get_prompt("Hide")
    hide.set_formula('IF(add_top_light==True,False,True)',[add_top_light])   

    light_obj = assembly.add_light('Under Cabinet Light','AREA')
    light_obj.data.shape = 'RECTANGLE'
    light_obj.data.energy = .5
    light_obj.pyclone.loc_x('width/2',[width])
    light_obj.pyclone.loc_y('depth+lighting_dim_from_front',[depth,lighting_dim_from_front])
    light_obj.pyclone.loc_z('height-material_thickness',[height,material_thickness])
    light_obj.pyclone.add_data_driver('size',-1,'width-(lighting_inset_from_sides*2)',[width,lighting_inset_from_sides])
    light_obj.pyclone.add_data_driver('size_y',-1,'lighting_width',[lighting_width])
    light_obj.pyclone.hide('IF(add_top_light==True,False,True)',[add_top_light])

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
        cabinet_type.set_value("Base")

        add_cabinet_bottom(self)
        add_cabinet_top(self)
        add_cabinet_sides(self,add_toe_kick_notch=False)
        add_cabinet_back(self)
        add_toe_kick(self)

class Carcass(pc_types.Assembly):

    left_side = None
    right_side = None
    back = None
    bottom = None
    top = None
    interior = None
    exterior = None

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  
        if obj_bp:
            for child in obj_bp.children:   
                if "IS_LEFT_SIDE_BP" in child:
                    self.left_side = pc_types.Assembly(child)
                if "IS_RIGHT_SIDE_BP" in child:
                    self.right_side = pc_types.Assembly(child)    
                if "IS_BACK_BP" in child:
                    self.back = pc_types.Assembly(child)   
                if "IS_BOTTOM_BP" in child:
                    self.bottom = pc_types.Assembly(child)
                if "IS_TOP_BP" in child:
                    self.top = pc_types.Assembly(child)          
                if "IS_INTERIOR_BP" in child:
                    self.interior = pc_types.Assembly(child)    
                if "IS_EXTERIOR_BP" in child:
                    self.exterior = pc_types.Assembly(child)                                                      

    def add_insert(self,insert):
        # x_loc_carcass = self.obj_bp.pyclone.get_var('location.x','x_loc_carcass')
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        material_thickness = self.get_prompt('Material Thickness').get_var('material_thickness')
        carcass_type = self.get_prompt("Carcass Type")

        #ADD NAME OF EXTERIOR TO 
        #PASS PROMPTS IN CORRECT
        insert.carcass_type = carcass_type.get_value()

        insert = self.add_assembly(insert)
        insert.loc_x('material_thickness',[material_thickness])
        insert.loc_y('depth',[depth])
        if carcass_type.get_value() == "Upper": #UPPER CABINET
            insert.loc_z('material_thickness',[material_thickness])
            insert.dim_z('height-(material_thickness*2)',[height,material_thickness])
        else:
            toe_kick_height = self.get_prompt('Toe Kick Height').get_var('toe_kick_height')
            insert.loc_z('toe_kick_height+material_thickness',[toe_kick_height,material_thickness])
            insert.dim_z('height-toe_kick_height-(material_thickness*2)',[height,toe_kick_height,material_thickness])
        
        insert.dim_x('width-(material_thickness*2)',[width,material_thickness])
        insert.dim_y('fabs(depth)',[depth])
        insert.obj_x.empty_display_size = .001
        insert.obj_y.empty_display_size = .001
        insert.obj_z.empty_display_size = .001
        insert.obj_bp.empty_display_size = .001
        insert.obj_prompts.empty_display_size = .001

        bpy.context.view_layer.update()

        # calculator = insert.get_calculator('Front Height Calculator')
        # if calculator:
        #     calculator.calculate()
        
        return insert


class Base_Advanced(Carcass):

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Carcass")
        self.obj_bp["IS_CARCASS_BP"] = True

        # common_prompts.add_cabinet_prompts(self)
        common_prompts.add_thickness_prompts(self)
        common_prompts.add_carcass_prompts(self)
        common_prompts.add_base_assembly_prompts(self)
        common_prompts.add_cabinet_lighting_prompts(self)
        
        carcass_type = self.get_prompt("Carcass Type")
        carcass_type.set_value("Base")

        self.obj_x.location.x = pc_unit.inch(18) 
        self.obj_y.location.y = -props.base_cabinet_depth
        self.obj_z.location.z = props.base_cabinet_height

        add_cabinet_bottom(self)
        add_cabinet_top(self)
        self.left_side, self.right_side = add_cabinet_sides(self,add_toe_kick_notch=True)
        self.back = add_cabinet_back(self)
        add_toe_kick(self)
        # add_top_lighting(self)
        # add_kick_lighting(self)
        # add_side_lighting(self)


class Tall_Advanced(Carcass):

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Carcass")
        self.obj_bp["IS_CARCASS_BP"] = True

        # common_prompts.add_cabinet_prompts(self)
        common_prompts.add_thickness_prompts(self)
        common_prompts.add_carcass_prompts(self)
        common_prompts.add_base_assembly_prompts(self)
        common_prompts.add_cabinet_lighting_prompts(self)

        carcass_type = self.get_prompt("Carcass Type")
        carcass_type.set_value("Tall")

        self.obj_x.location.x = pc_unit.inch(18) 
        self.obj_y.location.y = -props.tall_cabinet_depth
        self.obj_z.location.z = props.tall_cabinet_height

        add_cabinet_bottom(self)
        add_cabinet_top(self)
        add_cabinet_sides(self,add_toe_kick_notch=True)
        add_cabinet_back(self)
        add_toe_kick(self)
        # add_top_lighting(self)
        # add_kick_lighting(self)
        # add_side_lighting(self)

class Upper_Advanced(Carcass):

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Carcass")
        self.obj_bp["IS_CARCASS_BP"] = True

        common_prompts.add_cabinet_prompts(self)
        common_prompts.add_thickness_prompts(self)
        common_prompts.add_carcass_prompts(self)
        common_prompts.add_cabinet_lighting_prompts(self)

        carcass_type = self.get_prompt("Carcass Type")
        carcass_type.set_value("Upper")

        self.obj_x.location.x = pc_unit.inch(18) 
        self.obj_y.location.y = -props.upper_cabinet_depth
        self.obj_z.location.z = props.upper_cabinet_height

        add_upper_cabinet_bottom(self)
        add_cabinet_top(self)
        add_cabinet_sides(self,add_toe_kick_notch=False)
        add_upper_cabinet_back(self)
        # add_top_lighting(self)
        # add_under_cabinet_lighting(self)
        # add_side_lighting(self)


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