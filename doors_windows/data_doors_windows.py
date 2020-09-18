import bpy
from os import path
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
import time
from .. import home_builder_utils
from .. import home_builder_pointers
from .. import home_builder_paths
from .. import home_builder_parts

def get_default_window_frame():
    ASSET_DIR = home_builder_paths.get_asset_folder_path()
    return path.join(ASSET_DIR,"Window Frames","Window Frame.blend")

def get_default_window_insert():
    ASSET_DIR = home_builder_paths.get_asset_folder_path()
    return path.join(ASSET_DIR,"Window Inserts","Window Insert 1.blend")

def get_default_door_frame():
    ASSET_DIR = home_builder_paths.get_asset_folder_path()
    return path.join(ASSET_DIR,"Door Frames","Door Frame.blend") 

class Standard_Door(pc_types.Assembly):

    def draw_assembly(self):
        self.create_assembly("Door")
        self.obj_bp["IS_DOOR_BP"] = True

        Boolean_Overhang = self.add_prompt("Boolean Overhang",'DISTANCE',pc_unit.inch(1))
        Door_Thickness = self.add_prompt("Door Thickness",'DISTANCE',pc_unit.inch(1.5))
        Door_Reveal = self.add_prompt("Door Reveal",'DISTANCE',pc_unit.inch(.125))
        Door_Frame_Width = self.add_prompt("Door Frame Width",'DISTANCE',pc_unit.inch(3))

        self.obj_x.location.x = pc_unit.inch(36) #Length
        self.obj_y.location.y = pc_unit.inch(6)  #Depth
        self.obj_z.location.z = pc_unit.inch(70)

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        boolean_overhang_var = Boolean_Overhang.get_var("boolean_overhang_var")
        door_reveal = Door_Reveal.get_var("door_reveal")
        door_thickness = Door_Thickness.get_var("door_thickness")

        hole = self.add_assembly(home_builder_parts.Hole())
        hole.set_name("Hole")
        hole.loc_x(value=0)
        hole.loc_y('-boolean_overhang_var',[boolean_overhang_var])
        hole.loc_z('-boolean_overhang_var',[boolean_overhang_var])
        hole.rot_z(value=math.radians(0))
        hole.dim_x('width',[width])
        hole.dim_y('depth+(boolean_overhang_var*2)',[depth,boolean_overhang_var])
        hole.dim_z('height+boolean_overhang_var',[height,boolean_overhang_var])

        door_frame = pc_types.Assembly(self.add_assembly_from_file(get_default_door_frame()))
        self.add_assembly(door_frame)
        door_frame.set_name("Door Frame")
        door_frame.loc_x(value=0)
        door_frame.loc_y(value=0)
        door_frame.loc_z(value=0)
        door_frame.dim_x('width',[width])
        door_frame.dim_y('depth',[depth])
        door_frame.dim_z('height',[height])  
        home_builder_pointers.assign_pointer_to_assembly(door_frame,"Entry Door Frame")

        Door_Frame_Width = door_frame.get_prompt("Door Frame Width")

        if Door_Frame_Width:
            door_frame_width = door_frame.get_prompt("Door Frame Width").get_var('door_frame_width')
        else:
            door_frame_width = self.get_prompt("Door Frame Width").get_var('door_frame_width')

        # door = self.add_assembly(data_parts.Cube())
        # door.set_name("Door")
        # door.loc_x('door_frame_width+door_reveal',[door_frame_width,door_reveal])
        # door.loc_y(value = 0)
        # door.loc_z(value = 0)
        # door.rot_z(value=math.radians(0))
        # door.dim_x('width-(door_frame_width*2)-(door_reveal*2)',[width,door_frame_width,door_reveal])
        # door.dim_y('door_thickness',[door_thickness])
        # door.dim_z('height-door_frame_width-door_reveal',[height,door_frame_width,door_reveal])      
        # home_builder_pointers.assign_pointer_to_assembly(door_frame,"Entry Door Panels")  


class Standard_Window(pc_types.Assembly):

    def draw_assembly(self):
        self.create_assembly("Window")
        self.obj_bp["IS_WINDOW_BP"] = True

        Boolean_Overhang = self.add_prompt("Boolean Overhang",'DISTANCE',pc_unit.inch(1))
        Window_Frame_Width = self.add_prompt("Window Frame Width",'DISTANCE',pc_unit.inch(3))

        self.obj_x.location.x = pc_unit.inch(36) #Length
        self.obj_y.location.y = pc_unit.inch(6)  #Depth
        self.obj_z.location.z = pc_unit.inch(40)

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        boolean_overhang_var = Boolean_Overhang.get_var("boolean_overhang_var")

        hole = self.add_assembly(home_builder_parts.Hole())
        hole.set_name("Hole")
        hole.loc_x(value=0)
        hole.loc_y('-boolean_overhang_var',[boolean_overhang_var])
        hole.loc_z(value=0)
        hole.rot_z(value=math.radians(0))
        hole.dim_x('width',[width])
        hole.dim_y('depth+(boolean_overhang_var*2)',[depth,boolean_overhang_var])
        hole.dim_z('height',[height])

        window_frame = pc_types.Assembly(self.add_assembly_from_file(get_default_window_frame()))
        self.add_assembly(window_frame)
        window_frame.set_name("Window Frame")
        window_frame.loc_x(value=0)
        window_frame.loc_y(value=0)
        window_frame.loc_z(value=0)
        window_frame.dim_x('width',[width])
        window_frame.dim_y('depth',[depth])
        window_frame.dim_z('height',[height])  
        home_builder_pointers.assign_pointer_to_assembly(window_frame,"Entry Door Frame")

        Window_Frame_Width = window_frame.get_prompt("Window Frame Width")

        if Window_Frame_Width:
            window_frame_width = window_frame.get_prompt("Window Frame Width").get_var('window_frame_width')
        else:
            window_frame_width = self.get_prompt("Window Frame Width").get_var('window_frame_width')

        glass = pc_types.Assembly()
        glass.create_assembly("Glass")
        glass.create_cube("Glass")
        self.add_assembly(glass)
        glass.loc_x(value=0)
        glass.loc_y('depth/2',[depth])
        glass.loc_z(value=0)
        glass.dim_x('width',[width])
        glass.dim_y(value=pc_unit.inch(.25))
        glass.dim_z('height',[height])  
        home_builder_pointers.assign_pointer_to_assembly(glass,"Glass")

        glass_thickness = glass.obj_y.pyclone.get_var('location.y','glass_thickness')
        glass_setback = glass.obj_bp.pyclone.get_var('location.y','glass_setback')

        window_insert = pc_types.Assembly(self.add_assembly_from_file(get_default_window_insert()))
        self.add_assembly(window_frame)
        window_insert.set_name("Window Insert")
        window_insert.loc_x(value=0)
        window_insert.loc_y('glass_setback-.01',[glass_setback])
        window_insert.loc_z(value=0)
        window_insert.dim_x('width',[width])
        window_insert.dim_y('glass_thickness+.02',[glass_thickness])
        window_insert.dim_z('height',[height])             
        home_builder_pointers.assign_materials_to_assembly(window_insert)