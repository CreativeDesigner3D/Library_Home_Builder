import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinet_parts
from .. import home_builder_utils
from .. import home_builder_pointers
from . import common_prompts
from os import path

def add_overlay_prompts(assembly):
    hot = assembly.get_prompt("Half Overlay Top").get_var('hot')
    hob = assembly.get_prompt("Half Overlay Bottom").get_var('hob')
    hol = assembly.get_prompt("Half Overlay Left").get_var('hol')
    hor = assembly.get_prompt("Half Overlay Right").get_var('hor')
    material_thickness = assembly.get_prompt("Material Thickness").get_var('material_thickness')
    vertical_gap = assembly.get_prompt("Vertical Gap").get_var('vertical_gap')

    overlay_prompt_obj = assembly.add_empty('Overlay Prompt Obj')

    to = overlay_prompt_obj.pyclone.add_prompt('DISTANCE',"Top Overlay")
    bo = overlay_prompt_obj.pyclone.add_prompt('DISTANCE',"Bottom Overlay")
    lo = overlay_prompt_obj.pyclone.add_prompt('DISTANCE',"Left Overlay")
    ro = overlay_prompt_obj.pyclone.add_prompt('DISTANCE',"Right Overlay")

    to.set_formula('IF(hot,(material_thickness-vertical_gap)/2,material_thickness-vertical_gap)',[hot,material_thickness,vertical_gap])
    bo.set_formula('IF(hob,(material_thickness-vertical_gap)/2,material_thickness-vertical_gap)',[hob,material_thickness,vertical_gap])
    lo.set_formula('IF(hol,(material_thickness-vertical_gap)/2,material_thickness-vertical_gap)',[hol,material_thickness,vertical_gap])
    ro.set_formula('IF(hor,(material_thickness-vertical_gap)/2,material_thickness-vertical_gap)',[hor,material_thickness,vertical_gap])

    return to, bo, lo, ro

class Door(pc_types.Assembly):

    door_swing = 0 # Left = 0, Right = 1, Double = 2
    cabinet_type = '' #Base, Tall, Upper
    prompts = {}

    def set_pull_props(self,obj):
        obj['IS_CABINET_PULL'] = True
        home_builder_pointers.assign_pointer_to_object(obj,"Pull Finish")  
        if self.cabinet_type == 'Base':
            home_builder_utils.get_object_props(obj).pointer_name = "Base Cabinet Pulls"
        if self.cabinet_type == 'Tall':
            home_builder_utils.get_object_props(obj).pointer_name = "Tall Cabinet Pulls"
        if self.cabinet_type == 'Upper':
            home_builder_utils.get_object_props(obj).pointer_name = "Upper Cabinet Pulls"

    def set_prompts(self):
        for key in self.prompts:
            if key in self.obj_prompts.pyclone.prompts:
                if key in self.obj_prompts.pyclone.prompts:
                    prompt = self.obj_prompts.pyclone.prompts[key]
                    prompt.set_value(self.prompts[key])

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Double Door")
        self.obj_bp["IS_DOORS_BP"] = True
        self.obj_bp["IS_EXTERIOR_BP"] = True
        
        common_prompts.add_cabinet_prompts(self)
        common_prompts.add_door_prompts(self)
        common_prompts.add_front_prompts(self)
        common_prompts.add_front_overlay_prompts(self)
        common_prompts.add_pull_prompts(self)
        common_prompts.add_thickness_prompts(self)

        door_swing_prompt = self.get_prompt("Door Swing")
        door_swing_prompt.set_value(self.door_swing)

        #VARS
        x = self.obj_x.pyclone.get_var('location.x','x')
        z = self.obj_z.pyclone.get_var('location.z','z')        
        pull_length = self.get_prompt("Pull Length")  
        pull_length_var = self.get_prompt("Pull Length").get_var('pull_length_var')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        door_swing = door_swing_prompt.get_var('door_swing')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        base_pull_vertical_location = self.get_prompt("Base Pull Vertical Location").get_var('base_pull_vertical_location')
        tall_pull_vertical_location = self.get_prompt("Tall Pull Vertical Location").get_var('tall_pull_vertical_location')
        upper_pull_vertical_location = self.get_prompt("Upper Pull Vertical Location").get_var('upper_pull_vertical_location')
        pull_horizontal_location = self.get_prompt("Pull Horizontal Location").get_var('pull_horizontal_location')

        to, bo, lo, ro = add_overlay_prompts(self)

        to_var = to.get_var("to_var")
        bo_var = bo.get_var("bo_var")
        lo_var = lo.get_var("lo_var")
        ro_var = ro.get_var("ro_var")

        #LEFT DOOR
        l_door = data_cabinet_parts.add_door_part(self)
        l_door.set_name('Left Door Panel')
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
        home_builder_utils.flip_normals(l_door)

        door_width = l_door.obj_y.pyclone.get_var('location.y','door_width')
        door_length = l_door.obj_x.pyclone.get_var('location.x','door_length')
        hide_left_door = hide.get_var('hide_left_door')

        #LEFT DOOR PULL
        l_pull_empty = l_door.add_empty('Left Pull Empty')
        l_pull_empty.empty_display_size = .01
        pull_obj = home_builder_utils.get_pull(props.pull_category,props.pull_name)
        l_door.add_object(pull_obj)
        pull_obj.parent = l_pull_empty
        
        l_pull_empty.pyclone.loc_y('door_width+pull_horizontal_location',[door_width,pull_horizontal_location])
        l_pull_empty.pyclone.loc_z('front_thickness',[front_thickness])

        pull_length.set_value(round(pull_obj.dimensions.x,2))
        if self.cabinet_type == 'Base':
            l_pull_empty.pyclone.loc_x('door_length-base_pull_vertical_location-(pull_length_var/2)',
            [door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location,pull_length_var])  
        if self.cabinet_type == 'Tall':
            l_pull_empty.pyclone.loc_x('tall_pull_vertical_location-(pull_length_var/2)',
            [door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location,pull_length_var])  
        if self.cabinet_type == 'Upper': 
            l_pull_empty.pyclone.loc_x('upper_pull_vertical_location+(pull_length_var/2)',
            [door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location,pull_length_var])     
        l_pull_empty.rotation_euler.x = math.radians(-90)
        pull_obj.pyclone.hide('hide_left_door',[hide_left_door])
        self.set_pull_props(pull_obj)

        #RIGHT DOOR
        r_door = data_cabinet_parts.add_door_part(self)
        r_door.set_name('Right Door Panel')
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

        door_width = r_door.obj_y.pyclone.get_var('location.y','door_width')
        door_length = r_door.obj_x.pyclone.get_var('location.x','door_length')
        hide_right_door = hide.get_var('hide_right_door')

        #RIGHT DOOR PULL
        r_pull_empty = r_door.add_empty('Right Pull Empty')
        r_pull_empty.empty_display_size = .01
        pull_obj = home_builder_utils.get_pull(props.pull_category,props.pull_name)
        r_door.add_object(pull_obj)
        pull_obj.parent = r_pull_empty

        r_pull_empty.pyclone.loc_y('door_width-pull_horizontal_location',[door_width,pull_horizontal_location])
        r_pull_empty.pyclone.loc_z('front_thickness',[front_thickness])
        pull_length.set_value(round(pull_obj.dimensions.x,2))
        if self.cabinet_type == 'Base':
            r_pull_empty.pyclone.loc_x('door_length-base_pull_vertical_location-(pull_length_var/2)',
            [door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location,pull_length_var])    
        if self.cabinet_type == 'Tall':
            r_pull_empty.pyclone.loc_x('tall_pull_vertical_location-(pull_length_var/2)',
            [door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location,pull_length_var])  
        if self.cabinet_type == 'Upper':
            r_pull_empty.pyclone.loc_x('upper_pull_vertical_location+(pull_length_var/2)',
            [door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location,pull_length_var])    
        r_pull_empty.rotation_euler.x = math.radians(-90)
        pull_obj.pyclone.hide('hide_right_door',[hide_right_door])
        self.set_pull_props(pull_obj)

        self.set_prompts()


class Drawers(pc_types.Assembly):
    category_name = "Doors"

    drawer_qty = 3

    def add_drawer_front(self,index,prev_drawer_empty,calculator,to,lo,ro):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        drawer_front_height = self.get_prompt("Drawer Front " + str(index) + " Height").get_var(calculator.name,'drawer_front_height')
        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        z = self.obj_z.pyclone.get_var('location.z','z')
        top_overlay = to.get_var('top_overlay')
        left_overlay = lo.get_var('left_overlay')
        right_overlay = ro.get_var('right_overlay')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        drawer_pull_vertical_location = self.get_prompt("Drawer Pull Vertical Location").get_var('drawer_pull_vertical_location')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')

        front_empty = self.add_empty('Front Z Location ' + str(index))
        front_empty.empty_display_size = .001

        if prev_drawer_empty:
            prev_drawer_z_loc = prev_drawer_empty.pyclone.get_var('location.z','prev_drawer_z_loc')
            front_empty.pyclone.loc_z('prev_drawer_z_loc-drawer_front_height-vertical_gap',[prev_drawer_z_loc,drawer_front_height,vertical_gap])
        else:
            front_empty.pyclone.loc_z('z-drawer_front_height+top_overlay',[z,drawer_front_height,top_overlay])        
        
        drawer_z_loc = front_empty.pyclone.get_var('location.z',"drawer_z_loc")

        drawer_front = data_cabinet_parts.add_door_part(self)
        drawer_front.set_name('Drawer Front')
        drawer_front.loc_x('-left_overlay',[left_overlay])
        drawer_front.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        drawer_front.loc_z('drawer_z_loc',[drawer_z_loc])
        drawer_front.rot_x(value = math.radians(90))
        drawer_front.rot_y(value = math.radians(-90))
        drawer_front.dim_x('drawer_front_height',[drawer_front_height])
        drawer_front.dim_y('(x+left_overlay+right_overlay)*-1',[x,left_overlay,right_overlay])
        drawer_front.dim_z('front_thickness',[front_thickness])
        home_builder_utils.flip_normals(drawer_front)

        pull_empty = self.add_empty('Pull Empty')
        pull_empty.empty_display_size = .01

        pull_obj = home_builder_utils.get_pull(props.pull_category,props.pull_name)
        pull_obj['IS_CABINET_PULL'] = True
        home_builder_utils.get_object_props(pull_obj).pointer_name = "Drawer Pulls"
        self.add_object(pull_obj)
        pull_obj.parent = pull_empty
        pull_empty.pyclone.loc_y('-front_thickness',[front_thickness])
        pull_empty.pyclone.loc_z('drawer_z_loc+(drawer_front_height/2)',[drawer_z_loc,drawer_front_height])
        pull_empty.pyclone.loc_x('x/2',[x])
        pull_empty.rotation_euler.y = math.radians(180)
        home_builder_pointers.assign_pointer_to_object(pull_obj,"Pull Finish")

        return front_empty

    def draw(self):
        self.create_assembly("Drawers")
        self.obj_bp["IS_DRAWERS_BP"] = True
        self.obj_bp["IS_EXTERIOR_BP"] = True

        common_prompts.add_cabinet_prompts(self)
        common_prompts.add_door_prompts(self)
        common_prompts.add_thickness_prompts(self)
        common_prompts.add_front_prompts(self)
        common_prompts.add_front_overlay_prompts(self)
        common_prompts.add_drawer_pull_prompts(self)

        to, bo, lo, ro = add_overlay_prompts(self)

        calc_distance_obj = self.add_empty('Calc Distance Obj')
        calc_distance_obj.empty_display_size = .001
        front_height_calculator = self.obj_prompts.pyclone.add_calculator("Front Height Calculator",calc_distance_obj)

        drawer = None
        for i in range(self.drawer_qty):
            front_height_calculator.add_calculator_prompt('Drawer Front ' + str(i + 1) + ' Height')
            drawer = self.add_drawer_front(i + 1,drawer,front_height_calculator,to,lo,ro)

        z = self.obj_z.pyclone.get_var('location.z','z')
        top_overlay = to.get_var('top_overlay')
        bottom_overlay = bo.get_var('bottom_overlay')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        
        front_height_calculator.set_total_distance('z+top_overlay+bottom_overlay-vertical_gap*' + str(self.drawer_qty-1),[z,top_overlay,bottom_overlay,vertical_gap])