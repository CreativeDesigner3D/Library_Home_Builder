import bpy
from os import path
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
import time
from .. import home_builder_utils
from .. import home_builder_pointers
from .. import home_builder_paths
from .. import home_builder_parts

def get_default_door_jamb():
    ASSET_DIR = home_builder_paths.get_entry_door_jamb_path()
    return path.join(ASSET_DIR,"Generic","Door Jamb.blend") 

def get_window_frame(category,assembly_name):
    ASSET_DIR = home_builder_paths.get_window_frame_path()
    if assembly_name == "":
        return path.join(ASSET_DIR,"Generic","Simple Window Frame.blend") 
    else:
        return path.join(ASSET_DIR, category, assembly_name + ".blend")       

def get_window_insert(category,assembly_name):
    ASSET_DIR = home_builder_paths.get_window_insert_path()
    if assembly_name == "":
        return path.join(ASSET_DIR,"Generic","Glass Panel.blend")
    else:
        return path.join(ASSET_DIR, category, assembly_name + ".blend")    

def get_door_frame(category,assembly_name):
    ASSET_DIR = home_builder_paths.get_entry_door_frame_path()
    if assembly_name == "":
        return path.join(ASSET_DIR,"Generic","Door Frame Square.blend") 
    else:
        return path.join(ASSET_DIR, category, assembly_name + ".blend")     

def get_door_panel(door_panel_category,door_panel_name):
    ASSET_DIR = home_builder_paths.get_entry_door_panel_path()
    if door_panel_name == "":
        return path.join(ASSET_DIR,"Generic","Door Panel Slab.blend") 
    else:
        return path.join(ASSET_DIR, door_panel_category, door_panel_name + ".blend") 

def get_door_handle(door_handle_category,door_handle_name):
    ASSET_DIR = home_builder_paths.get_entry_door_handle_path()
    if door_handle_name == "":
        return path.join(ASSET_DIR,"Generic","Entry Door Handle 1.blend") 
    else:
        return path.join(ASSET_DIR, door_handle_category, door_handle_name + ".blend") 

class Standard_Door(pc_types.Assembly):

    def add_frame(self,door_frame_category="",door_frame_name=""):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')

        door_frame = pc_types.Assembly(self.add_assembly_from_file(get_door_frame(door_frame_category,door_frame_name)))
        door_frame.obj_bp["IS_ENTRY_DOOR_FRAME"] = True
        self.add_assembly(door_frame)
        door_frame.set_name("Door Frame")
        door_frame.loc_x(value=0)
        door_frame.loc_y(value=0)
        door_frame.loc_z(value=0)
        door_frame.dim_x('width',[width])
        door_frame.dim_y('depth',[depth])
        door_frame.dim_z('height',[height])  
        home_builder_pointers.assign_pointer_to_assembly(door_frame,"Entry Door Frame")
        home_builder_utils.update_assembly_id_props(door_frame,self)

    def add_door_handle(self,door_panel,door_handle_category="",door_handle_name=""):
        door_panel_width = door_panel.obj_x.pyclone.get_var('location.x','door_panel_width')
        door_thickness = door_panel.obj_y.pyclone.get_var('location.y','door_thickness')
        handle_vertical_location = self.get_prompt("Handle Vertical Location").get_var('handle_vertical_location')
        entry_door_swing = self.get_prompt("Entry Door Swing").get_var('entry_door_swing')
        handle_location_from_edge = self.get_prompt("Handle Location From Edge").get_var('handle_location_from_edge')

        door_handle_center = door_panel.add_empty('Door Handle Center')
        door_handle_center.empty_display_size = .001
        door_handle_center.pyclone.loc_y('door_thickness/2',[door_thickness])

        door_handle_obj = home_builder_utils.get_object(get_door_handle(door_handle_category,door_handle_name))
        door_handle_obj["IS_ENTRY_DOOR_HANDLE"] = True
        door_panel.add_object(door_handle_obj)
        
        door_handle_obj.pyclone.loc_y(value=0)
        door_handle_obj.pyclone.loc_z('handle_vertical_location',[handle_vertical_location])
        if "Left" in door_panel.obj_bp.name:
            door_handle_obj.pyclone.loc_x('door_panel_width-handle_location_from_edge',[door_panel_width,handle_location_from_edge])
            door_handle_obj.pyclone.hide('IF(entry_door_swing==1,True,False)',[entry_door_swing])
        else:
            door_handle_obj.pyclone.rot_y(value=math.radians(180))
            door_handle_obj.pyclone.loc_x('door_panel_width+handle_location_from_edge',[door_panel_width,handle_location_from_edge])
            door_handle_obj.pyclone.hide('IF(entry_door_swing==0,True,False)',[entry_door_swing])
        home_builder_pointers.assign_pointer_to_object(door_handle_obj,"Entry Door Handle")  

        mirror = door_handle_obj.modifiers.new('Mirror','MIRROR')
        mirror.mirror_object = door_handle_center
        mirror.use_axis[0] = False
        mirror.use_axis[1] = True
        mirror.use_axis[2] = False

    def add_doors(self,door_panel_category="",door_panel_name="",door_handle_category="",door_handle_name=""):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')        
        door_reveal = self.get_prompt("Door Reveal").get_var('door_reveal')
        door_thickness = self.get_prompt("Door Thickness").get_var('door_thickness')
        entry_door_swing = self.get_prompt("Entry Door Swing").get_var('entry_door_swing')
        door_frame_width = self.get_prompt("Door Frame Width").get_var('door_frame_width')
        door_frame_reveal = self.get_prompt("Door Frame Reveal").get_var('door_frame_reveal')
        outswing = self.get_prompt("Outswing").get_var('outswing')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        
        #LEFT DOOR
        l_door_panel = pc_types.Assembly(self.add_assembly_from_file(get_door_panel(door_panel_category,door_panel_name)))
        l_door_panel.set_name("Left Door Panel")
        l_door_panel.obj_bp["IS_ENTRY_DOOR_PANEL"] = True
        self.add_assembly(l_door_panel)
        l_door_panel.loc_x('IF(outswing,width-door_frame_width-door_reveal-door_frame_reveal,door_frame_width+door_reveal+door_frame_reveal)',[outswing,width,door_frame_width,door_reveal,door_frame_reveal])
        l_door_panel.loc_y('IF(outswing,depth,0)',[outswing,depth])
        l_door_panel.loc_z(value = 0)
        l_door_panel.rot_z('IF(outswing,radians(180),0)-door_rotation*open_door',[open_door,door_rotation,outswing])
        l_door_panel.dim_x('IF(entry_door_swing==2,(width-(door_frame_width*2)-(door_reveal*3)-(door_frame_reveal*2))/2,width-(door_frame_width*2)-(door_reveal*2)-(door_frame_reveal*2))',[width,entry_door_swing,door_frame_width,door_reveal,door_frame_reveal])
        l_door_panel.dim_y('door_thickness',[door_thickness])
        l_door_panel.dim_z('height-door_frame_width-door_reveal-door_frame_reveal',[height,door_frame_width,door_reveal,door_frame_reveal])       
        home_builder_pointers.assign_pointer_to_assembly(l_door_panel,"Entry Door Panels")  
        hide = l_door_panel.get_prompt("Hide")
        hide.set_formula('IF(entry_door_swing==1,True,False)',[entry_door_swing]) 

        self.add_door_handle(l_door_panel,door_handle_category,door_handle_name)
        home_builder_utils.update_assembly_id_props(l_door_panel,self)

        #RIGHT DOOR
        r_door_panel = pc_types.Assembly(self.add_assembly_from_file(get_door_panel(door_panel_category,door_panel_name)))
        r_door_panel.set_name("Right Door Panel")
        r_door_panel.obj_bp["IS_ENTRY_DOOR_PANEL"] = True
        self.add_assembly(r_door_panel)
        r_door_panel.loc_x('IF(outswing,door_frame_width+door_reveal+door_frame_reveal,width-door_frame_width-door_reveal-door_frame_reveal)',[outswing,width,door_frame_width,door_reveal,door_frame_reveal])
        r_door_panel.loc_y('IF(outswing,depth,0)',[outswing,depth])
        r_door_panel.loc_z(value = 0)
        r_door_panel.rot_z('IF(outswing,radians(180),0)+door_rotation*open_door',[open_door,door_rotation,outswing])
        r_door_panel.dim_x('IF(entry_door_swing==2,(width-(door_frame_width*2)-(door_reveal*3)-(door_frame_reveal*2))/2,width-(door_frame_width*2)-(door_reveal*2)-(door_frame_reveal*2))*-1',[width,entry_door_swing,door_frame_width,door_reveal,door_frame_reveal])
        r_door_panel.dim_y('door_thickness',[door_thickness])
        r_door_panel.dim_z('height-door_frame_width-door_reveal-door_frame_reveal',[height,door_frame_width,door_reveal,door_frame_reveal])      
        home_builder_pointers.assign_pointer_to_assembly(r_door_panel,"Entry Door Panels")  
        hide = r_door_panel.get_prompt("Hide")
        hide.set_formula('IF(entry_door_swing==0,True,False)',[entry_door_swing]) 

        self.add_door_handle(r_door_panel,door_handle_category,door_handle_name)
        home_builder_utils.update_assembly_id_props(r_door_panel,self)

    def draw_assembly(self):
        self.create_assembly("Door")
        self.obj_bp["IS_DOOR_BP"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.door_prompts" 
        self.obj_bp["MENU_ID"] = "home_builder_MT_cabinet_menu"

        self.add_prompt("Entry Door Swing",'COMBOBOX',0,["Left","Right","Double"])
        self.add_prompt("Door Thickness",'DISTANCE',pc_unit.inch(1.5))
        self.add_prompt("Door Reveal",'DISTANCE',pc_unit.inch(.125))
        self.add_prompt("Door Frame Width",'DISTANCE',pc_unit.inch(3))
        Door_Frame_Reveal = self.add_prompt("Door Frame Reveal",'DISTANCE',pc_unit.inch(.125))
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
        door_frame_reveal = Door_Frame_Reveal.get_var("door_frame_reveal")

        hole = self.add_assembly(home_builder_parts.Hole())
        hole.set_name("Hole")
        hole.loc_x(value=0)
        hole.loc_y('-boolean_overhang_var',[boolean_overhang_var])
        hole.loc_z('-boolean_overhang_var',[boolean_overhang_var])
        hole.rot_z(value=math.radians(0))
        hole.dim_x('width',[width])
        hole.dim_y('depth+(boolean_overhang_var*2)',[depth,boolean_overhang_var])
        hole.dim_z('height+boolean_overhang_var',[height,boolean_overhang_var])

        door_jamb = pc_types.Assembly(self.add_assembly_from_file(get_default_door_jamb()))
        self.add_assembly(door_jamb)
        door_jamb.set_name("Door Jamb")
        door_jamb.loc_x('door_frame_reveal',[door_frame_reveal])
        door_jamb.loc_y(value=0)
        door_jamb.loc_z(value=0)
        door_jamb.dim_x('width-door_frame_reveal*2',[width,door_frame_reveal])
        door_jamb.dim_y('depth',[depth])
        door_jamb.dim_z('height-door_frame_reveal',[height,door_frame_reveal])  
        home_builder_pointers.assign_pointer_to_assembly(door_jamb,"Entry Door Frame")

        self.add_frame()
        

class Standard_Window(pc_types.Assembly):

    def add_window_frame(self,category="",assembly_name=""):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')

        window_frame = pc_types.Assembly(self.add_assembly_from_file(get_window_frame(category,assembly_name)))
        self.add_assembly(window_frame)
        window_frame.obj_bp["IS_WINDOW_FRAME"] = True
        window_frame.set_name("Window Frame")
        window_frame.loc_x(value=0)
        window_frame.loc_y(value=0)
        window_frame.loc_z(value=0)
        window_frame.dim_x('width',[width])
        window_frame.dim_y('depth',[depth])
        window_frame.dim_z('height',[height])  
        home_builder_pointers.assign_pointer_to_assembly(window_frame,"Entry Door Frame")

        left_window_frame_width = window_frame.get_prompt("Left Window Frame Width").get_value()
        right_window_frame_width = window_frame.get_prompt("Right Window Frame Width").get_value()
        top_window_frame_width = window_frame.get_prompt("Top Window Frame Width").get_value()
        bottom_window_frame_width = window_frame.get_prompt("Bottom Window Frame Width").get_value()

        self.get_prompt("Left Window Frame Width").set_value(left_window_frame_width)
        self.get_prompt("Right Window Frame Width").set_value(right_window_frame_width)
        self.get_prompt("Top Window Frame Width").set_value(top_window_frame_width)
        self.get_prompt("Bottom Window Frame Width").set_value(bottom_window_frame_width)

        home_builder_utils.update_assembly_id_props(window_frame,self)
        self.add_array_modifier(window_frame)

    def add_window_insert(self,category="",assembly_name=""):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')        
        left_window_frame_width = self.get_prompt("Left Window Frame Width").get_var("left_window_frame_width")
        right_window_frame_width = self.get_prompt("Right Window Frame Width").get_var("right_window_frame_width")
        top_window_frame_width = self.get_prompt("Top Window Frame Width").get_var("top_window_frame_width")
        bottom_window_frame_width = self.get_prompt("Bottom Window Frame Width").get_var("bottom_window_frame_width")
                
        window_insert = pc_types.Assembly(self.add_assembly_from_file(get_window_insert(category,assembly_name)))
        self.add_assembly(window_insert)
        window_insert.obj_bp["IS_WINDOW_INSERT"] = True
        window_insert.set_name("Window Insert")
        window_insert.loc_x('left_window_frame_width',[left_window_frame_width])
        window_insert.loc_y(value = 0)
        window_insert.loc_z('bottom_window_frame_width',[bottom_window_frame_width])
        window_insert.dim_x('width-left_window_frame_width-right_window_frame_width',[width,left_window_frame_width,right_window_frame_width])
        window_insert.dim_y('depth',[depth])
        window_insert.dim_z('height-top_window_frame_width-bottom_window_frame_width',[height,top_window_frame_width,bottom_window_frame_width])
        home_builder_pointers.assign_materials_to_assembly(window_insert)

        home_builder_utils.update_assembly_id_props(window_insert,self)
        self.add_array_modifier(window_insert)

    def add_array_modifier(self,assembly):
        width = self.obj_x.pyclone.get_var('location.x','width')
        qty = self.get_prompt("Window Quantity").get_var("qty")
        x_offset = self.get_prompt("X Offset").get_var("x_offset")

        for child in assembly.obj_bp.children:
            if child.type != 'EMPTY':
                array = child.modifiers.new('Quantity','ARRAY')   
                array.use_constant_offset = True
                array.use_relative_offset = False
                child.pyclone.modifier(array,'count',-1,'qty',[qty])
                child.pyclone.modifier(array,'constant_offset_displace',0,'width+x_offset',[width,x_offset])

    def draw_assembly(self):
        self.create_assembly("Window")
        self.obj_bp["IS_WINDOW_BP"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.window_prompts" 
        self.obj_bp["MENU_ID"] = "home_builder_MT_cabinet_menu"

        Boolean_Overhang = self.add_prompt("Boolean Overhang",'DISTANCE',pc_unit.inch(1))
        self.add_prompt("Left Window Frame Width",'DISTANCE',pc_unit.inch(3))
        self.add_prompt("Right Window Frame Width",'DISTANCE',pc_unit.inch(3))
        self.add_prompt("Top Window Frame Width",'DISTANCE',pc_unit.inch(3))
        self.add_prompt("Bottom Window Frame Width",'DISTANCE',pc_unit.inch(3))
        self.add_prompt("Window Quantity",'QUANTITY',1)
        self.add_prompt("X Offset",'DISTANCE',pc_unit.inch(10))

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
        self.add_array_modifier(hole)

        self.add_window_frame()
        self.add_window_insert()