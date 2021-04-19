import bpy
import time
import math
from os import path
from ..pc_lib import pc_types, pc_unit, pc_utils

from . import common_prompts
from . import data_closet_parts
from .. import home_builder_utils
from .. import home_builder_pointers

class Shelves(pc_types.Assembly):
    show_in_library = True
    category_name = "CLOSETS"
    subcategory_name = "INSERTS"

    def add_adj_prompts(self):
        self.add_prompt(name="Shelf Qty",
                        prompt_type='QUANTITY',
                        value=5,
                        tab_index=0)

    def add_shelves(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        shelf_qty = self.get_prompt("Shelf Quantity").get_var("shelf_qty")
        shelf_clip_gap = self.get_prompt("Shelf Clip Gap").get_var("shelf_clip_gap")
        shelf_thickness = self.get_prompt("Shelf Thickness").get_var("shelf_thickness")
        
        adj_shelf = data_closet_parts.add_closet_array_part(self)
        is_locked_shelf = adj_shelf.add_prompt("Is Locked Shelf",'CHECKBOX',True)
        is_lock_shelf_var = is_locked_shelf.get_var("is_lock_shelf_var")
        adj_shelf_setback = adj_shelf.add_prompt("Adj Shelf Setback",'DISTANCE',pc_unit.inch(.25))
        adj_shelf_setback_var = adj_shelf_setback.get_var("adj_shelf_setback_var")
        fixed_shelf_setback = adj_shelf.add_prompt("Fixed Shelf Setback",'DISTANCE',pc_unit.inch(.25))
        fixed_shelf_setback_var = fixed_shelf_setback.get_var("fixed_shelf_setback_var")
        
        adj_shelf.loc_x('IF(is_lock_shelf_var,0,shelf_clip_gap)',[shelf_clip_gap,is_lock_shelf_var])
        adj_shelf.loc_y('depth',[depth])
        adj_shelf.loc_z('((height-(shelf_thickness*shelf_qty))/(shelf_qty+1))',[height,shelf_thickness,shelf_qty])
        adj_shelf.rot_x(value = 0)
        adj_shelf.rot_y(value = 0)
        adj_shelf.rot_z(value = 0)
        adj_shelf.dim_x('width-IF(is_lock_shelf_var,0,shelf_clip_gap*2)',[width,is_lock_shelf_var,shelf_clip_gap])
        adj_shelf.dim_y('-depth+IF(is_lock_shelf_var,fixed_shelf_setback_var,adj_shelf_setback_var)',[depth,is_lock_shelf_var,fixed_shelf_setback_var,adj_shelf_setback_var])
        adj_shelf.dim_z('shelf_thickness',[shelf_thickness])
        hide = adj_shelf.get_prompt("Hide")
        z_quantity = adj_shelf.get_prompt("Z Quantity")
        z_offset = adj_shelf.get_prompt("Z Offset")

        hide.set_formula('IF(shelf_qty==0,True,False)',[shelf_qty]) 
        z_quantity.set_formula('shelf_qty',[shelf_qty]) 
        z_offset.set_formula('((height-(shelf_thickness*shelf_qty))/(shelf_qty+1))+shelf_thickness',[height,shelf_thickness,shelf_qty]) 

    def pre_draw(self):
        self.create_assembly()

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = data_closet_parts.add_closet_opening(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def draw(self):

        shelf_thickness = self.add_prompt("Shelf Thickness",'DISTANCE',pc_unit.inch(1)) 
        shelf_clip_gap = self.add_prompt("Shelf Clip Gap",'DISTANCE',pc_unit.inch(1)) 
        shelf_qty = self.add_prompt("Shelf Quantity",'QUANTITY',3) 
        
        self.add_shelves()

    def render(self):
        self.pre_draw()
        self.draw()


class Hanging_Rod(pc_types.Assembly):
    show_in_library = True
    category_name = "CLOSETS"
    subcategory_name = "INSERTS"

    def add_hanging_rod(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        hanging_rod_location_from_top = self.get_prompt("Hanging Rod Location From Top").get_var("hanging_rod_location_from_top")
        hanging_rod_setback = self.get_prompt("Hanging Rod Setback").get_var("hanging_rod_setback")
        # shelf_clip_gap = self.get_prompt("Shelf Clip Gap").get_var("shelf_clip_gap")
        # shelf_thickness = self.get_prompt("Shelf Thickness").get_var("shelf_thickness")
        
        hanging_rod = data_closet_parts.add_closet_oval_hanging_rod(self)
        hangers = data_closet_parts.add_closet_hangers(self)

        # is_locked_shelf = adj_shelf.add_prompt("Is Locked Shelf",'CHECKBOX',True)
        # is_lock_shelf_var = is_locked_shelf.get_var("is_lock_shelf_var")
        # adj_shelf_setback = adj_shelf.add_prompt("Adj Shelf Setback",'DISTANCE',pc_unit.inch(.25))
        # adj_shelf_setback_var = adj_shelf_setback.get_var("adj_shelf_setback_var")
        # fixed_shelf_setback = adj_shelf.add_prompt("Fixed Shelf Setback",'DISTANCE',pc_unit.inch(.25))
        # fixed_shelf_setback_var = fixed_shelf_setback.get_var("fixed_shelf_setback_var")
        
        hanging_rod.loc_x(value = 0)
        hanging_rod.loc_y('hanging_rod_setback',[hanging_rod_setback])
        hanging_rod.loc_z('height-hanging_rod_location_from_top',[height,hanging_rod_location_from_top])
        hanging_rod.rot_x(value = 0)
        hanging_rod.rot_y(value = 0)
        hanging_rod.rot_z(value = 0)
        hanging_rod.dim_x('width',[width])
        hanging_rod.dim_y(value = 0)
        hanging_rod.dim_z(value = 0)

        if hangers:
            hangers.loc_x(value = 0)
            hangers.loc_y('hanging_rod_setback',[hanging_rod_setback])
            hangers.loc_z('height-hanging_rod_location_from_top',[height,hanging_rod_location_from_top])
            hangers.rot_x(value = 0)
            hangers.rot_y(value = 0)
            hangers.rot_z(value = 0)
            hangers.dim_x('width',[width])
            hangers.dim_y(value = 0)
            hangers.dim_z(value = 0)        
        # hide = adj_shelf.get_prompt("Hide")
        # z_quantity = adj_shelf.get_prompt("Z Quantity")
        # z_offset = adj_shelf.get_prompt("Z Offset")

        # hide.set_formula('IF(shelf_qty==0,True,False)',[shelf_qty]) 
        # z_quantity.set_formula('shelf_qty',[shelf_qty]) 
        # z_offset.set_formula('((height-(shelf_thickness*shelf_qty))/(shelf_qty+1))+shelf_thickness',[height,shelf_thickness,shelf_qty]) 

    def pre_draw(self):
        self.create_assembly()

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = data_closet_parts.add_closet_opening(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def draw(self):

        shelf_thickness = self.add_prompt("Hanging Rod Location From Top",'DISTANCE',pc_unit.inch(2.145)) 
        shelf_clip_gap = self.add_prompt("Hanging Rod Setback",'DISTANCE',pc_unit.inch(2)) 

        self.add_hanging_rod()

    def render(self):
        self.pre_draw()
        self.draw()        


class Doors(pc_types.Assembly):
    show_in_library = True
    category_name = "CLOSETS"
    subcategory_name = "INSERTS"

    def add_overlay_prompts(self):
        hot = self.get_prompt("Half Overlay Top").get_var('hot')
        hob = self.get_prompt("Half Overlay Bottom").get_var('hob')
        hol = self.get_prompt("Half Overlay Left").get_var('hol')
        hor = self.get_prompt("Half Overlay Right").get_var('hor')
        material_thickness = self.get_prompt("Material Thickness").get_var('material_thickness')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        tr = self.get_prompt("Top Reveal").get_var('tr')
        br = self.get_prompt("Bottom Reveal").get_var('br')
        lr = self.get_prompt("Left Reveal").get_var('lr')
        rr = self.get_prompt("Right Reveal").get_var('rr')

        overlay_prompt_obj = self.add_empty('Overlay Prompt Obj')
        overlay_prompt_obj.empty_display_size = .01

        to = overlay_prompt_obj.pyclone.add_prompt('DISTANCE',"Top Overlay")
        bo = overlay_prompt_obj.pyclone.add_prompt('DISTANCE',"Bottom Overlay")
        lo = overlay_prompt_obj.pyclone.add_prompt('DISTANCE',"Left Overlay")
        ro = overlay_prompt_obj.pyclone.add_prompt('DISTANCE',"Right Overlay")

        to.set_formula('IF(hot,(material_thickness-vertical_gap)/2,material_thickness-tr)',[hot,material_thickness,vertical_gap,tr])
        bo.set_formula('IF(hob,(material_thickness-vertical_gap)/2,material_thickness-br)',[hob,material_thickness,vertical_gap,br])
        lo.set_formula('IF(hol,(material_thickness-vertical_gap)/2,material_thickness-lr)',[hol,material_thickness,vertical_gap,lr])
        ro.set_formula('IF(hor,(material_thickness-vertical_gap)/2,material_thickness-rr)',[hor,material_thickness,vertical_gap,rr])

        return to, bo, lo, ro

    def pre_draw(self):
        self.create_assembly()

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = data_closet_parts.add_closet_opening(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def draw(self):
        self.add_prompt("Material Thickness",'DISTANCE',pc_unit.inch(.75))  
        common_prompts.add_door_prompts(self)
        common_prompts.add_front_prompts(self)
        common_prompts.add_front_overlay_prompts(self)

        props = home_builder_utils.get_scene_props(bpy.context.scene)
        front_pointer = props.cabinet_door_pointers["Base Cabinet Doors"]

        door_swing_prompt = self.get_prompt("Door Swing")
        door_swing_prompt.set_value(2)

        x = self.obj_x.pyclone.get_var('location.x','x')
        z = self.obj_z.pyclone.get_var('location.z','z')        
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        door_swing = door_swing_prompt.get_var('door_swing')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        door_swing = self.get_prompt("Door Swing").get_var('door_swing')

        to, bo, lo, ro = self.add_overlay_prompts()

        to_var = to.get_var("to_var")
        bo_var = bo.get_var("bo_var")
        lo_var = lo.get_var("lo_var")
        ro_var = ro.get_var("ro_var")

        #LEFT DOOR
        l_door = data_closet_parts.add_door_part(self,front_pointer)
        l_door.loc_x('-lo_var',[lo_var])
        l_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        l_door.loc_z('-bo_var',[bo_var])
        l_door.rot_x(value = math.radians(90))
        l_door.rot_y(value = math.radians(-90))
        l_door.rot_z('-door_rotation*open_door',[door_rotation,open_door])
        l_door.dim_x('z+to_var+bo_var',[z,to_var,bo_var])
        l_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)*-1',[door_swing,x,lo_var,ro_var,vertical_gap])            
        l_door.dim_z('front_thickness',[front_thickness])
        hide = l_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==1,True,False)',[door_swing])
        # self.add_door_pull(l_door,pull_pointer)

        #RIGHT DOOR
        r_door = data_closet_parts.add_door_part(self,front_pointer)
        r_door.loc_x('x+ro_var',[x,ro_var])
        r_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        r_door.loc_z('-bo_var',[bo_var])
        r_door.rot_x(value = math.radians(90))
        r_door.rot_y(value = math.radians(-90))
        r_door.rot_z('door_rotation*open_door',[door_rotation,open_door])   
        r_door.dim_x('z+to_var+bo_var',[z,to_var,bo_var])
        r_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)',[door_swing,x,lo_var,ro_var,vertical_gap])     
        r_door.dim_z('front_thickness',[front_thickness])
        hide = r_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==0,True,False)',[door_swing])
        # self.add_door_pull(r_door,pull_pointer)

    def render(self):
        self.pre_draw()
        self.draw()        