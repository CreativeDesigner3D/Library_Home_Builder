import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinet_parts
from .. import home_builder_utils
from . import common_prompts
from os import path

class Door(pc_types.Assembly):
    category_name = "Doors"
    prompt_id = "room.part_prompts"
    placement_id = "room.draw_multiple_walls"

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Door")
        self.obj_bp["IS_DOORS_BP"] = True

        common_prompts.add_door_prompts(self)
        common_prompts.add_front_prompts(self)
        common_prompts.add_front_overlay_prompts(self)
        common_prompts.add_pull_prompts(self)

        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        z = self.obj_z.pyclone.get_var('location.z','z')
        top_overlay = self.get_prompt("Top Overlay").get_var('top_overlay')
        bottom_overlay = self.get_prompt("Bottom Overlay").get_var('bottom_overlay')
        left_overlay = self.get_prompt("Left Overlay").get_var('left_overlay')
        right_overlay = self.get_prompt("Right Overlay").get_var('right_overlay')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        pull_vertical_location = self.get_prompt("Pull Vertical Location").get_var('pull_vertical_location')
        pull_horizontal_location = self.get_prompt("Pull Horizontal Location").get_var('pull_horizontal_location')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        open_door = self.get_prompt("Open Door").get_var('open_door')

        door = data_cabinet_parts.add_door_part(self)
        door.set_name('Door')
        door.loc_x('-left_overlay',[left_overlay])
        door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        door.loc_z('-bottom_overlay',[bottom_overlay])
        door.rot_x(value = math.radians(90))
        door.rot_y(value = math.radians(-90))
        door.rot_z('-door_rotation*open_door',[door_rotation,open_door])
        door.dim_x('z+top_overlay+bottom_overlay',[z,top_overlay,bottom_overlay])
        door.dim_y('(x+left_overlay+right_overlay)*-1',[x,left_overlay,right_overlay])
        door.dim_z('front_thickness',[front_thickness])      
        home_builder_utils.flip_normals(door)  

        door_width = door.obj_y.pyclone.get_var('location.y','door_width')
        door_length = door.obj_x.pyclone.get_var('location.x','door_length')
        door_thickness = door.obj_z.pyclone.get_var('location.z','door_thickness')

        pull_obj = home_builder_utils.get_pull(props.pull_category,props.pull_name)
        door.add_object(pull_obj)
        pull_obj.pyclone.loc_y('door_width+pull_horizontal_location',[door_width,pull_horizontal_location])
        pull_obj.pyclone.loc_z('door_thickness',[door_thickness])
        pull_obj.pyclone.loc_x('door_length-pull_vertical_location-'+str(pull_obj.dimensions.x)+'/2',[door_length,pull_vertical_location])        
        pull_obj.rotation_euler.x = math.radians(-90)
        home_builder_utils.assign_materials_to_object(pull_obj)

class Drawers(pc_types.Assembly):
    category_name = "Doors"
    prompt_id = "room.part_prompts"
    placement_id = "room.draw_multiple_walls"

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
        pull_vertical_location = self.get_prompt("Pull Vertical Location").get_var('pull_vertical_location')
        pull_horizontal_location = self.get_prompt("Pull Horizontal Location").get_var('pull_horizontal_location')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')

        front_empty = self.add_empty('Front Z Location ' + str(index))

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
        pull_obj.pyclone.loc_x('x/2',[x,pull_horizontal_location])
        pull_obj.rotation_euler.y = math.radians(180)
        home_builder_utils.assign_materials_to_object(pull_obj)

        return front_empty

    def draw(self):
        self.create_assembly("Drawers")
        self.obj_bp["IS_DRAWERS_BP"] = True

        common_prompts.add_door_prompts(self)
        common_prompts.add_front_prompts(self)
        common_prompts.add_front_overlay_prompts(self)
        common_prompts.add_pull_prompts(self)

        front_height_calculator = self.obj_prompts.pyclone.add_calculator("Front Height Calculator")

        drawer = None
        for i in range(self.drawer_qty):
            front_height_calculator.add_calculator_prompt('Drawer Front ' + str(i + 1) + ' Height')
            drawer = self.add_drawer_front(i + 1,drawer,front_height_calculator)

        z = self.obj_z.pyclone.get_var('location.z','z')
        top_overlay = self.get_prompt("Top Overlay").get_var('top_overlay')
        bottom_overlay = self.get_prompt("Bottom Overlay").get_var('bottom_overlay')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        
        front_height_calculator.set_total_distance('z+top_overlay+bottom_overlay-vertical_gap*' + str(self.drawer_qty-1),[z,top_overlay,bottom_overlay,vertical_gap])