import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinet_parts
from .. import home_builder_utils
from . import common_prompts
from os import path

class Door(pc_types.Assembly):

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

        #VARS
        x = self.obj_x.pyclone.get_var('location.x','x')
        z = self.obj_z.pyclone.get_var('location.z','z')          
        left_overlay = self.get_prompt("Left Overlay").get_var('left_overlay')
        right_overlay = self.get_prompt("Right Overlay").get_var('right_overlay')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        door_swing = self.get_prompt("Door Swing").get_var('door_swing')
        door_swing = self.get_prompt("Door Swing").get_var('door_swing')
        top_overlay = self.get_prompt("Top Overlay").get_var('top_overlay')
        bottom_overlay = self.get_prompt("Bottom Overlay").get_var('bottom_overlay')
        left_overlay = self.get_prompt("Left Overlay").get_var('left_overlay')
        right_overlay = self.get_prompt("Right Overlay").get_var('right_overlay')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        base_pull_vertical_location = self.get_prompt("Base Pull Vertical Location").get_var('base_pull_vertical_location')
        tall_pull_vertical_location = self.get_prompt("Tall Pull Vertical Location").get_var('tall_pull_vertical_location')
        upper_pull_vertical_location = self.get_prompt("Upper Pull Vertical Location").get_var('upper_pull_vertical_location')
        pull_horizontal_location = self.get_prompt("Pull Horizontal Location").get_var('pull_horizontal_location')
        cabinet_type = self.get_prompt("Cabinet Type").get_var('cabinet_type')

        #LEFT DOOR
        l_door = data_cabinet_parts.add_door_part(self)
        l_door.set_name('Left Door Panel')
        l_door.loc_x('-left_overlay',[left_overlay])
        l_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        l_door.loc_z('-bottom_overlay',[bottom_overlay])
        l_door.rot_x(value = math.radians(90))
        l_door.rot_y(value = math.radians(-90))
        l_door.rot_z('-door_rotation*open_door',[door_rotation,open_door])
        l_door.dim_x('z+top_overlay+bottom_overlay',[z,top_overlay,bottom_overlay])
        l_door.dim_y('IF(door_swing==2,((x+left_overlay+right_overlay)-vertical_gap)/2,x+left_overlay+right_overlay)*-1',
                     [door_swing,x,left_overlay,right_overlay,vertical_gap])
        l_door.dim_z('front_thickness',[front_thickness])
        hide = l_door.get_prompt("Hide")
        hide.set_formula('IF(door_swing==1,True,False)',[door_swing])
        home_builder_utils.flip_normals(l_door)

        door_width = l_door.obj_y.pyclone.get_var('location.y','door_width')
        door_length = l_door.obj_x.pyclone.get_var('location.x','door_length')
        hide_left_door = hide.get_var('hide_left_door')

        #LEFT DOOR PULL
        pull_obj = home_builder_utils.get_pull(props.pull_category,props.pull_name)
        l_door.add_object(pull_obj)
        pull_obj.pyclone.loc_y('door_width+pull_horizontal_location',[door_width,pull_horizontal_location])
        pull_obj.pyclone.loc_z('front_thickness',[front_thickness])
        pull_length = str(round(pull_obj.dimensions.x/2,2))
        base = 'door_length-base_pull_vertical_location-' + pull_length
        tall = 'tall_pull_vertical_location-' + pull_length
        upper = 'upper_pull_vertical_location+' + pull_length
        pull_obj.pyclone.loc_x('IF(cabinet_type==0,' + base + ',IF(cabinet_type==1,' + tall + ',' +upper + '))',
        [cabinet_type,door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location])       
        pull_obj.rotation_euler.x = math.radians(-90)
        pull_obj.pyclone.hide('hide_left_door',[hide_left_door])
        home_builder_utils.assign_materials_to_object(pull_obj)

        #RIGHT DOOR
        r_door = data_cabinet_parts.add_door_part(self)
        r_door.set_name('Right Door Panel')
        r_door.loc_x('x+right_overlay',[x,right_overlay])
        r_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        r_door.loc_z('-bottom_overlay',[bottom_overlay])
        r_door.rot_x(value = math.radians(90))
        r_door.rot_y(value = math.radians(-90))     
        r_door.rot_z('door_rotation*open_door',[door_rotation,open_door])   
        r_door.dim_x('z+top_overlay+bottom_overlay',[z,top_overlay,bottom_overlay])
        r_door.dim_y('IF(door_swing==2,((x+left_overlay+right_overlay)-vertical_gap)/2,x+left_overlay+right_overlay)',
                     [door_swing,x,left_overlay,right_overlay,vertical_gap])
        r_door.dim_z('front_thickness',[front_thickness])
        hide = r_door.get_prompt("Hide")
        hide.set_formula('IF(door_swing==0,True,False)',[door_swing]) 

        door_width = r_door.obj_y.pyclone.get_var('location.y','door_width')
        door_length = r_door.obj_x.pyclone.get_var('location.x','door_length')
        hide_right_door = hide.get_var('hide_right_door')

        #RIGHT DOOR PULL
        pull_obj = home_builder_utils.get_pull(props.pull_category,props.pull_name)
        r_door.add_object(pull_obj)
        pull_obj.pyclone.loc_y('door_width-pull_horizontal_location',[door_width,pull_horizontal_location])
        pull_obj.pyclone.loc_z('front_thickness',[front_thickness])
        pull_length = str(round(pull_obj.dimensions.x/2,2))
        base = 'door_length-base_pull_vertical_location-' + pull_length
        tall = 'tall_pull_vertical_location-' + pull_length
        upper = 'upper_pull_vertical_location+' + pull_length
        pull_obj.pyclone.loc_x('IF(cabinet_type==0,' + base + ',IF(cabinet_type==1,' + tall + ',' +upper + '))',
        [cabinet_type,door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location])       
        pull_obj.rotation_euler.x = math.radians(-90)
        pull_obj.pyclone.hide('hide_right_door',[hide_right_door])
        home_builder_utils.assign_materials_to_object(pull_obj)


class Drawers(pc_types.Assembly):
    category_name = "Doors"

    drawer_qty = 3

    def add_drawer_front(self,index,prev_drawer_empty,calculator):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        drawer_front_height = self.get_prompt("Drawer Front " + str(index) + " Height").get_var(calculator.name,'drawer_front_height')
        # drawer_front_height = self.get_prompt("Drawer Front " + str(index) + " Height").get_var('drawer_front_height')
        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        z = self.obj_z.pyclone.get_var('location.z','z')
        top_overlay = self.get_prompt("Top Overlay").get_var('top_overlay')
        bottom_overlay = self.get_prompt("Bottom Overlay").get_var('bottom_overlay')
        left_overlay = self.get_prompt("Left Overlay").get_var('left_overlay')
        right_overlay = self.get_prompt("Right Overlay").get_var('right_overlay')
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

        pull_obj = home_builder_utils.get_pull(props.pull_category,props.pull_name)
        self.add_object(pull_obj)
        pull_obj.pyclone.loc_y('-front_thickness',[front_thickness])
        pull_obj.pyclone.loc_z('drawer_z_loc+(drawer_front_height/2)',[drawer_z_loc,drawer_front_height])
        pull_obj.pyclone.loc_x('x/2',[x])
        pull_obj.rotation_euler.y = math.radians(180)
        home_builder_utils.assign_materials_to_object(pull_obj)

        return front_empty

    def draw(self):
        self.create_assembly("Drawers")
        self.obj_bp["IS_DRAWERS_BP"] = True
        self.obj_bp["IS_EXTERIOR_BP"] = True

        common_prompts.add_cabinet_prompts(self)
        common_prompts.add_door_prompts(self)
        common_prompts.add_front_prompts(self)
        common_prompts.add_front_overlay_prompts(self)
        common_prompts.add_drawer_pull_prompts(self)

        calc_distance_obj = self.add_empty('Calc Distance Obj')
        calc_distance_obj.empty_display_size = .001
        front_height_calculator = self.obj_prompts.pyclone.add_calculator("Front Height Calculator",calc_distance_obj)

        drawer = None
        for i in range(self.drawer_qty):
            front_height_calculator.add_calculator_prompt('Drawer Front ' + str(i + 1) + ' Height')
            drawer = self.add_drawer_front(i + 1,drawer,front_height_calculator)

        z = self.obj_z.pyclone.get_var('location.z','z')
        top_overlay = self.get_prompt("Top Overlay").get_var('top_overlay')
        bottom_overlay = self.get_prompt("Bottom Overlay").get_var('bottom_overlay')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        
        front_height_calculator.set_total_distance('z+top_overlay+bottom_overlay-vertical_gap*' + str(self.drawer_qty-1),[z,top_overlay,bottom_overlay,vertical_gap])