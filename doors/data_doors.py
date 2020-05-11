import bpy
from os import path
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
import time
from .. import home_builder_utils

ASSET_DIR = home_builder_utils.get_asset_folder_path()
DOOR_FRAME = path.join(ASSET_DIR,"Door Frames","Door Frame.blend")

class Hole(pc_types.Assembly):

    def draw(self):
        start_time = time.time()
        self.create_assembly("Hole")

        self.obj_x.location.x = pc_unit.inch(120) #Length
        self.obj_y.location.y = pc_unit.inch(4)   #Depth
        self.obj_z.location.z = pc_unit.inch(2)   #Thickness

        #When assigning vertices to a hook the transformation is made so the size must be 0
        # size = (self.obj_x.location.x,self.obj_y.location.y,self.obj_z.location.z)
        size = (0,0,0)
        obj_mesh = pc_utils.create_cube_mesh("Hole",size)
        self.add_object(obj_mesh)
        obj_mesh['IS_BOOLEAN'] = True

        vgroup = obj_mesh.vertex_groups[self.obj_x.name]
        vgroup.add([2,3,6,7],1,'ADD')        

        vgroup = obj_mesh.vertex_groups[self.obj_y.name]
        vgroup.add([1,2,5,6],1,'ADD')

        vgroup = obj_mesh.vertex_groups[self.obj_z.name]
        vgroup.add([4,5,6,7],1,'ADD')        

        hook = obj_mesh.modifiers.new('XHOOK','HOOK')
        hook.object = self.obj_x
        hook.vertex_indices_set([2,3,6,7])

        hook = obj_mesh.modifiers.new('YHOOK','HOOK')
        hook.object = self.obj_y
        hook.vertex_indices_set([1,2,5,6])

        hook = obj_mesh.modifiers.new('ZHOOK','HOOK')
        hook.object = self.obj_z
        hook.vertex_indices_set([4,5,6,7])

        #THIS OPERATION TAKES THE LONGEST
        # obj_mesh.bp_props.hook_vertex_group_to_object(self.obj_x.name,self.obj_x)
        # obj_mesh.bp_props.hook_vertex_group_to_object(self.obj_y.name,self.obj_y)
        # obj_mesh.bp_props.hook_vertex_group_to_object(self.obj_z.name,self.obj_z)
        print("HOLE: Draw Time --- %s seconds ---" % (time.time() - start_time))

class Door(pc_types.Assembly):
    show_in_library = True

    def draw_door(self):
        self.create_assembly("Door")

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

        hole = self.add_assembly(Hole())
        hole.set_name("Hole")
        hole.loc_x(value=0)
        hole.loc_y('-boolean_overhang_var',[boolean_overhang_var])
        hole.loc_z('-boolean_overhang_var',[boolean_overhang_var])
        hole.rot_z(value=math.radians(0))
        hole.dim_x('width',[width])
        hole.dim_y('depth+(boolean_overhang_var*2)',[depth,boolean_overhang_var])
        hole.dim_z('height+boolean_overhang_var',[height,boolean_overhang_var])

        door_frame = pc_types.Assembly(self.add_assembly_from_file(DOOR_FRAME))
        self.add_assembly(door_frame)
        door_frame.set_name("Door Frame")
        door_frame.loc_x(value=0)
        door_frame.loc_y(value=0)
        door_frame.loc_z(value=0)
        door_frame.dim_x('width',[width])
        door_frame.dim_y('depth',[depth])
        door_frame.dim_z('height',[height])  
        home_builder_utils.assign_door_frame_pointers(door_frame)

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
        # home_builder_utils.assign_door_panel_pointers(door)