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

def get_default_door_panel():
    ASSET_DIR = home_builder_paths.get_entry_door_panel_path()
    return path.join(ASSET_DIR,"Door Panel Slab.blend") 

class Standard_Door(pc_types.Assembly):

    def add_doors(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')        
        door_reveal = self.get_prompt("Door Reveal").get_var('door_reveal')
        door_thickness = self.get_prompt("Door Thickness").get_var('door_thickness')
        handle_vertical_location = self.get_prompt("Handle Vertical Location").get_var('handle_vertical_location')
        handle_location_from_edge = self.get_prompt("Handle Location From Edge").get_var('handle_location_from_edge')
        entry_door_swing = self.get_prompt("Entry Door Swing").get_var('entry_door_swing')
        door_frame_width = self.get_prompt("Door Frame Width").get_var('door_frame_width')
        outswing = self.get_prompt("Outswing").get_var('outswing')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        
        #LEFT DOOR
        l_door_panel = pc_types.Assembly(self.add_assembly_from_file(get_default_door_panel()))
        l_door_panel.set_name("Left Door Panel")
        self.add_assembly(l_door_panel)
        l_door_panel.loc_x('IF(outswing,width-door_frame_width-door_reveal,door_frame_width+door_reveal)',[outswing,width,door_frame_width,door_reveal])
        l_door_panel.loc_y('IF(outswing,depth,0)',[outswing,depth])
        l_door_panel.loc_z(value = 0)
        l_door_panel.rot_z('IF(outswing,radians(180),0)-door_rotation*open_door',[open_door,door_rotation,outswing])
        l_door_panel.dim_x('IF(entry_door_swing==2,(width-(door_frame_width*2)-(door_reveal*3))/2,width-(door_frame_width*2)-(door_reveal*2))',[width,entry_door_swing,door_frame_width,door_reveal])
        l_door_panel.dim_y('door_thickness',[door_thickness])
        l_door_panel.dim_z('height-door_frame_width-door_reveal',[height,door_frame_width,door_reveal])      
        l_door_panel.dim_z('height-door_frame_width-door_reveal',[height,door_frame_width,door_reveal])   
        home_builder_pointers.assign_pointer_to_assembly(l_door_panel,"Entry Door Panels")  
        hide = l_door_panel.get_prompt("Hide")
        hide.set_formula('IF(entry_door_swing==1,True,False)',[entry_door_swing]) 

        l_door_panel_width = l_door_panel.obj_x.pyclone.get_var('location.x','l_door_panel_width')
        l_door_thickness = l_door_panel.obj_y.pyclone.get_var('location.y','l_door_thickness')

        door_handle_center = l_door_panel.add_empty('Door Handle Center')
        door_handle_center.empty_display_size = .001
        door_handle_center.pyclone.loc_y('l_door_thickness/2',[l_door_thickness])

        door_handle_path = path.join(home_builder_paths.get_entry_door_handle_path(),"Entry Door Handle 1.blend")
        l_door_handle_obj = home_builder_utils.get_object(door_handle_path)
        l_door_panel.add_object(l_door_handle_obj)
        l_door_handle_obj.pyclone.loc_x('l_door_panel_width-handle_location_from_edge',[l_door_panel_width,handle_location_from_edge])
        l_door_handle_obj.pyclone.loc_y(value=0)
        l_door_handle_obj.pyclone.loc_z('handle_vertical_location',[handle_vertical_location])
        l_door_handle_obj.pyclone.hide('IF(entry_door_swing==1,True,False)',[entry_door_swing])
        home_builder_pointers.assign_pointer_to_object(l_door_handle_obj,"Entry Door Handle")  

        mirror = l_door_handle_obj.modifiers.new('Mirror','MIRROR')
        mirror.mirror_object = door_handle_center
        mirror.use_axis[0] = False
        mirror.use_axis[1] = True
        mirror.use_axis[2] = False

        #RIGHT DOOR
        r_door_panel = pc_types.Assembly(self.add_assembly_from_file(get_default_door_panel()))
        r_door_panel.set_name("Right Door Panel")
        self.add_assembly(r_door_panel)
        r_door_panel.loc_x('IF(outswing,door_frame_width+door_reveal,width-door_frame_width-door_reveal)',[outswing,width,door_frame_width,door_reveal])
        r_door_panel.loc_y('IF(outswing,depth,0)',[outswing,depth])
        r_door_panel.loc_z(value = 0)
        r_door_panel.rot_z('IF(outswing,radians(180),0)+door_rotation*open_door',[open_door,door_rotation,outswing])
        r_door_panel.dim_x('IF(entry_door_swing==2,(width-(door_frame_width*2)-(door_reveal*3))/2,width-(door_frame_width*2)-(door_reveal*2))*-1',[width,entry_door_swing,door_frame_width,door_reveal])
        r_door_panel.dim_y('door_thickness',[door_thickness])
        r_door_panel.dim_z('height-door_frame_width-door_reveal',[height,door_frame_width,door_reveal])      
        home_builder_pointers.assign_pointer_to_assembly(r_door_panel,"Entry Door Panels")  
        hide = r_door_panel.get_prompt("Hide")
        hide.set_formula('IF(entry_door_swing==0,True,False)',[entry_door_swing]) 

        r_door_panel_width = r_door_panel.obj_x.pyclone.get_var('location.x','r_door_panel_width')
        r_door_thickness = r_door_panel.obj_y.pyclone.get_var('location.y','r_door_thickness')

        door_handle_center = r_door_panel.add_empty('Door Handle Center')
        door_handle_center.empty_display_size = .001
        door_handle_center.pyclone.loc_y('r_door_thickness/2',[r_door_thickness])

        door_handle_path = path.join(home_builder_paths.get_entry_door_handle_path(),"Entry Door Handle 1.blend")
        r_door_handle_obj = home_builder_utils.get_object(door_handle_path)
        r_door_panel.add_object(r_door_handle_obj)
        r_door_handle_obj.pyclone.loc_x('r_door_panel_width+handle_location_from_edge',[r_door_panel_width,handle_location_from_edge])
        r_door_handle_obj.pyclone.loc_y(value=0)
        r_door_handle_obj.pyclone.loc_z('handle_vertical_location',[handle_vertical_location])
        r_door_handle_obj.pyclone.rot_y(value=math.radians(180))
        r_door_handle_obj.pyclone.hide('IF(entry_door_swing==0,True,False)',[entry_door_swing])
        home_builder_pointers.assign_pointer_to_object(r_door_handle_obj,"Entry Door Handle")  

        mirror = r_door_handle_obj.modifiers.new('Mirror','MIRROR')
        mirror.mirror_object = door_handle_center
        mirror.use_axis[0] = False
        mirror.use_axis[1] = True
        mirror.use_axis[2] = False

    def draw_assembly(self):
        self.create_assembly("Door")
        self.obj_bp["IS_DOOR_BP"] = True

        self.add_prompt("Entry Door Swing",'COMBOBOX',0,["Left","Right","Double"])
        self.add_prompt("Door Thickness",'DISTANCE',pc_unit.inch(1.5))
        self.add_prompt("Door Reveal",'DISTANCE',pc_unit.inch(.125))
        self.add_prompt("Door Frame Width",'DISTANCE',pc_unit.inch(3))
        self.add_prompt("Handle Vertical Location",'DISTANCE',pc_unit.inch(36))
        self.add_prompt("Handle Location From Edge",'DISTANCE',pc_unit.inch(2.5))
        self.add_prompt("Outswing",'CHECKBOX',True)
        self.add_prompt("Open Door",'PERCENTAGE',0)
        self.add_prompt("Door Rotation",'ANGLE',120)
        Boolean_Overhang = self.add_prompt("Boolean Overhang",'DISTANCE',pc_unit.inch(1))
        
        self.obj_x.location.x = pc_unit.inch(36) #Length
        self.obj_y.location.y = pc_unit.inch(6)  #Depth
        self.obj_z.location.z = pc_unit.inch(70)

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        boolean_overhang_var = Boolean_Overhang.get_var("boolean_overhang_var")

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