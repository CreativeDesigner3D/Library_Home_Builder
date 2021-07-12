import bpy,os,inspect, sys
import math
import subprocess
import datetime
import codecs
from datetime import date
from bpy.types import (Header, 
                       Menu, 
                       Panel, 
                       Operator,
                       PropertyGroup)

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       PointerProperty,
                       EnumProperty,
                       CollectionProperty)
from mathutils import Vector

from .pc_lib import pc_unit, pc_utils, pc_types
from .doors_windows import door_window_library
from .cabinets import cabinet_library
from .cabinets import data_appliances
from .cabinets import data_cabinets
from .closets import closet_library
from .closets import data_closet_parts
from .closets import data_closet_inserts
from .walls import data_walls
from . import home_builder_paths
from . import home_builder_pointers
from importlib import import_module

# from .cabinets import data_cabinet_carcass
# from .cabinets import data_cabinet_exteriors
# from .cabinets import data_cabinet_parts
# from .cabinets import cabinet_utils
# from . import home_builder_pointers
from . import home_builder_utils
# from . import home_builder_paths

def event_is_place_asset(event):
    if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
        return True
    elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS':
        return True
    elif event.type == 'RET' and event.value == 'PRESS':
        return True
    else:
        return False

def event_is_cancel_command(event):
    if event.type in {'RIGHTMOUSE', 'ESC'}:
        return True
    else:
        return False

def event_is_pass_through(event):
    if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
        return True
    else:
        return False

def create_placement_obj(context):
    placement_obj = bpy.data.objects.new('PLACEMENT OBJECT',None)
    placement_obj.location = (0,0,0)
    placement_obj.empty_display_type = 'ARROWS'
    placement_obj.empty_display_size = .1           
    context.view_layer.active_layer_collection.collection.objects.link(placement_obj)
    return placement_obj

class home_builder_OT_drop(Operator):
    bl_idname = "home_builder.drop"
    bl_label = "Home Builder Drop"
    bl_description = "This is called when an asset is dropped from the home builder library"
    bl_options = {'UNDO'}
    
    filepath: StringProperty(name='Library Name')

    def get_custom_cabinet(self,context,filepath):
        parent = None
        with bpy.data.libraries.load(filepath, False, False) as (data_from, data_to):
                data_to.objects = data_from.objects
        for obj in data_to.objects:
            if obj.parent is None:
                parent = obj     
                parent['IS_CABINET_BP'] = True     
            context.view_layer.active_layer_collection.collection.objects.link(obj)
            if obj.type == 'EMPTY':
                obj.hide_viewport = True
        home_builder_utils.assign_current_material_index(parent)
        return parent

    def get_drop_script(self,path):
        if os.path.exists(path):
            f = open(path, "r")
            return f.read()        
        else:
            return ""

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        wm_props = home_builder_utils.get_wm_props(context.window_manager)

        directory, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)
        drop_id = self.get_drop_script(os.path.join(directory,filename + ".txt"))

        if drop_id != "":
            eval(drop_id)
            return {'FINISHED'}

        if props.library_tabs == 'ROOMS':
            if props.room_tabs == 'WALLS':
                bpy.ops.home_builder.place_room(filepath=self.filepath)
            if props.room_tabs == 'DOORS':
                bpy.ops.home_builder.place_door_window(filepath=self.filepath)
            if props.room_tabs == 'WINDOWS':
                bpy.ops.home_builder.place_door_window(filepath=self.filepath)
            if props.room_tabs == 'OBSTACLES':
                bpy.ops.home_builder.place_wall_obstacle(filepath=self.filepath)                
            if props.room_tabs == 'DECORATIONS':
                bpy.ops.home_builder.place_decoration(filepath=self.filepath)      

        if props.library_tabs == 'KITCHENS':
            if props.kitchen_tabs == 'RANGES':
                bpy.ops.home_builder.place_appliance(filepath=self.filepath)
            if props.kitchen_tabs == 'REFRIGERATORS':
                bpy.ops.home_builder.place_appliance(filepath=self.filepath)
            if props.kitchen_tabs == 'DISHWASHERS':
                bpy.ops.home_builder.place_appliance(filepath=self.filepath)                                
            if props.kitchen_tabs == 'CABINETS':
                bpy.ops.home_builder.place_cabinet(filepath=self.filepath)
            if props.kitchen_tabs == 'PARTS':
                pass
            if props.kitchen_tabs == 'CUSTOM_CABINETS':
                obj_bp = self.get_custom_cabinet(context,filepath=os.path.join(directory,filename + ".blend"))
                bpy.ops.home_builder.move_cabinet(obj_bp_name=obj_bp.name,snap_cursor_to_cabinet=False)
            if props.kitchen_tabs == 'DECORATIONS':
                bpy.ops.home_builder.place_decoration(filepath=self.filepath)  

        if props.library_tabs == 'BATHS':
            if props.bath_tabs == 'TOILETS':
                bpy.ops.home_builder.place_bathroom_fixture(filepath=self.filepath)  
            if props.bath_tabs == 'BATHS':
                bpy.ops.home_builder.place_bathroom_fixture(filepath=self.filepath)                  
            if props.bath_tabs == 'VANITIES':
                obj_bp = self.get_custom_cabinet(context,os.path.join(directory,filename + ".blend"))
                bpy.ops.home_builder.move_cabinet(obj_bp_name=obj_bp.name,snap_cursor_to_cabinet=False)
            if props.bath_tabs == 'DECORATIONS':
                bpy.ops.home_builder.place_decoration(filepath=self.filepath)                    

        if props.library_tabs == 'CLOSETS':
            if props.closet_tabs == 'STARTERS':
                bpy.ops.home_builder.place_closet(filepath=self.filepath)
            if props.closet_tabs == 'INSERTS':
                bpy.ops.home_builder.place_closet_insert(filepath=self.filepath)
            if props.closet_tabs == 'SPLITTERS':
                bpy.ops.home_builder.place_closet_insert(filepath=self.filepath)
            if props.closet_tabs == 'CLOSET_PARTS':
                pass                           
            if props.closet_tabs == 'DECORATIONS':
                bpy.ops.home_builder.place_decoration(filepath=self.filepath)         

        return {'FINISHED'}


class home_builder_OT_place_room(bpy.types.Operator):
    bl_idname = "home_builder.place_room"
    bl_label = "Place Room"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    current_wall = None

    starting_point = ()

    parent_obj_dict = {}
    all_objects = []
    meshes = []
    empties = []

    def reset_properties(self):
        self.current_wall = None
        self.starting_point = ()
        self.parent_obj_dict = {}
        self.all_objects = []

    def execute(self, context):
        self.reset_properties()
        self.create_drawing_plane(context)
        self.get_object(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def collect_room_data(self,obj):
        if obj.type == 'MESH':
            self.meshes.append(obj)
        if obj.type == 'EMPTY':
            self.empties.append(obj)
        for child in obj.children:
            self.collect_room_data(child)

    def get_object(self,context):
        directory, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)
        self.room = eval("data_walls." + filename.replace(" ","_") + "()")

        if hasattr(self.room,'pre_draw'):
            self.room.pre_draw()
        else:
            self.room.draw()

        for obj in self.room.obj_bp.children:
            self.all_objects.append(obj)

        self.room.set_name(filename)
        self.collect_room_data(self.room.obj_bp)
        for empty in self.empties:
            empty.hide_viewport = True

    def set_placed_properties(self,obj):
        if "obj_x" in obj:
            obj.hide_viewport = True     
        if "obj_y" in obj:
            obj.hide_viewport = True   
        if "obj_z" in obj:
            obj.hide_viewport = True   
        if "obj_bp" in obj:
            obj.hide_viewport = True           
        if obj.type == 'MESH' and obj.hide_render == False:
            obj.display_type = 'TEXTURED'

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.meshes)

        self.position_object(selected_point,selected_obj)

        if event_is_place_asset(event):
            return self.finish(context)
            
        if event_is_cancel_command(event):
            return self.cancel_drop(context)

        if event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def position_object(self,selected_point,selected_obj):
        self.room.obj_bp.location = selected_point

    def cancel_drop(self,context):
        obj_list = []
        obj_list.append(self.drawing_plane)
        for obj in self.all_objects:
            obj_list.append(obj)
        pc_utils.delete_obj_list(obj_list)
        return {'CANCELLED'}

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        bpy.ops.object.select_all(action='DESELECT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        bpy.ops.object.select_all(action='DESELECT')
        for obj, location in self.parent_obj_dict.items():
            obj.select_set(True)  
            context.view_layer.objects.active = obj     
        for obj in self.all_objects:
            self.set_placed_properties(obj) 
        context.area.tag_redraw()
        return {'FINISHED'}


class home_builder_OT_place_cabinet(bpy.types.Operator):
    bl_idname = "home_builder.place_cabinet"
    bl_label = "Place Cabinet"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    cabinet = None
    selected_cabinet = None

    calculators = []

    drawing_plane = None

    next_wall = None
    current_wall = None
    previous_wall = None

    placement = ''
    placement_obj = None

    assembly = None
    obj = None
    exclude_objects = []

    def reset_selection(self):
        self.current_wall = None
        self.selected_cabinet = None    
        self.next_wall = None
        self.previous_wall = None  
        self.placement = ''

    def reset_properties(self):
        self.cabinet = None
        self.selected_cabinet = None
        self.calculators = []
        self.drawing_plane = None
        self.next_wall = None
        self.current_wall = None
        self.previous_wall = None
        self.placement = ''
        self.assembly = None
        self.obj = None
        self.exclude_objects = []

    def execute(self, context):
        self.reset_properties()
        self.create_drawing_plane(context)
        self.get_cabinet(context)
        self.placement_obj = create_placement_obj(context)

        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def accumulate_z_rotation(self,selected_obj,start = 0,total = True):
        ##recursive parent traverser accumulating all rotations ie. total heirarchy rotation
        rotations = [start]
        if selected_obj.parent:
            
            if total:
                rotations.append(selected_obj.parent.rotation_euler.z)
                return self.accumulate_z_rotation(selected_obj.parent,sum(rotations))
            else:
                ## breaks after one parent
                return selected_obj.parent.rotation_euler.z
        else:
            return start

    def rotate_to_normal(self,selected_normal):
        ## cabinet vector
        base_vect = Vector((0, -1, 0))

        if selected_normal.y == 1:
            ## if Vector(0,1,0) it is a negative vector relationship with cabinet Vector(0,-1,0)
            ## quaternion calcs fail with these, 180 rotation is all thats required
            self.cabinet.obj_bp.rotation_euler.z =+ math.radians(180)

        else:
            ## Vector.rotation_difference() returns quaternion rotation so change mode
            self.cabinet.obj_bp.rotation_mode = 'QUATERNION'
            ## quaternion calc - required rotation to align cab to face
            rot_quat = base_vect.rotation_difference(selected_normal)

            self.cabinet.obj_bp.rotation_quaternion = rot_quat
            self.cabinet.obj_bp.rotation_mode = 'XYZ'

    def get_next_wall(self):
        if not self.current_wall:
            return None

        props = home_builder_utils.get_object_props(self.current_wall.obj_x)
        if props.connected_object:
            wall_bp = home_builder_utils.get_wall_bp(props.connected_object)
            return pc_types.Assembly(wall_bp)

        return None

    def position_cabinet_on_wall(self,mouse_location,wall_bp):
        self.placement = 'WALL'
        self.current_wall = pc_types.Assembly(wall_bp)
        self.cabinet.obj_bp.parent = wall_bp
        self.cabinet.obj_bp.matrix_world[0][3] = mouse_location[0]
        self.cabinet.obj_bp.matrix_world[1][3] = mouse_location[1]              
        self.cabinet.obj_bp.location.z = self.base_height + wall_bp.location.z
        self.placement_obj.parent = self.current_wall.obj_bp
        self.placement_obj.matrix_world[0][3] = mouse_location[0]
        self.placement_obj.matrix_world[1][3] = mouse_location[1] 
        self.cabinet.obj_bp.location.y = 0   

        wall_length = self.current_wall.obj_x.location.x
        cabinet_width = self.cabinet.obj_x.location.x
        x_loc = self.cabinet.obj_bp.location.x

        #SNAP TO LEFT
        if x_loc < .25:
            self.placement = "WALL_LEFT"
            self.cabinet.obj_bp.location.x = 0

        #SNAP TO RIGHT
        if x_loc > wall_length - cabinet_width:
            self.placement = "WALL_RIGHT"
            self.cabinet.obj_bp.location.x = wall_length - cabinet_width

        #TODO: GET NEXT PRODUCT AND UPDATE LOCATION AND SIZE

        if self.selected_normal.y == 1:
            #BACK SIDE OF WALL
            self.cabinet.obj_bp.rotation_euler.z = math.radians(180)
        else:
            self.cabinet.obj_bp.rotation_euler.z = 0

    def position_cabinet_next_to_door_window(self,mouse_location,assembly_bp,selected_obj):
        assembly = data_cabinets.Cabinet(assembly_bp)

        self.placement = home_builder_utils.get_cabinet_placement_location(self.cabinet,assembly,mouse_location)

        cabinet_width = self.cabinet.obj_x.location.x
        sel_assembly_width = assembly.obj_x.location.x
        sel_assembly_world_x = assembly.obj_bp.matrix_world[0][3]
        sel_assembly_world_y = assembly.obj_bp.matrix_world[1][3]
        sel_assembly_width_world_x = assembly.obj_x.matrix_world[0][3]
        sel_assembly_width_world_y = assembly.obj_x.matrix_world[1][3]

        self.cabinet.obj_bp.rotation_euler.z = 0

        if self.placement == 'LEFT':
            self.cabinet.obj_bp.matrix_world[0][3] = sel_assembly_world_x
            self.cabinet.obj_bp.matrix_world[1][3] = sel_assembly_world_y
            self.cabinet.obj_bp.location.x -= cabinet_width
        elif self.placement == 'RIGHT':
            self.cabinet.obj_bp.matrix_world[0][3] = sel_assembly_width_world_x
            self.cabinet.obj_bp.matrix_world[1][3] = sel_assembly_width_world_y                                  
        else:
            self.cabinet.obj_bp.matrix_world[0][3] = sel_assembly_world_x
            self.cabinet.obj_bp.matrix_world[1][3] = sel_assembly_world_y  
            self.cabinet.obj_bp.location.x += (sel_assembly_width/2)  - (cabinet_width/2)        

    def position_cabinet_next_to_cabinet(self,mouse_location,cabinet_bp,selected_obj):
        self.selected_cabinet = data_cabinets.Cabinet(cabinet_bp)
        wall_bp = home_builder_utils.get_wall_bp(cabinet_bp)

        self.placement = home_builder_utils.get_cabinet_placement_location(self.cabinet,self.selected_cabinet,mouse_location)

        sel_cabinet_z_rot = self.selected_cabinet.obj_bp.rotation_euler.z
        cabinet_width = self.cabinet.obj_x.location.x
        sel_cabinet_width = self.selected_cabinet.obj_x.location.x
        sel_cabinet_world_x = self.selected_cabinet.obj_bp.matrix_world[0][3]
        sel_cabinet_world_y = self.selected_cabinet.obj_bp.matrix_world[1][3]
        sel_cabinet_width_world_x = self.selected_cabinet.obj_x.matrix_world[0][3]
        sel_cabinet_width_world_y = self.selected_cabinet.obj_x.matrix_world[1][3]

        if not wall_bp:
            #CABINET NOT ON WALL
            if self.placement == 'LEFT':
                x_loc = sel_cabinet_world_x - math.cos(sel_cabinet_z_rot) * cabinet_width
                y_loc = sel_cabinet_world_y - math.sin(sel_cabinet_z_rot) * cabinet_width
                self.cabinet.obj_bp.matrix_world[0][3] = x_loc
                self.cabinet.obj_bp.matrix_world[1][3] = y_loc
                self.cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  
                if self.selected_cabinet.corner_type == 'Blind':
                    blind_location = self.selected_cabinet.carcasses[0].get_prompt("Blind Panel Location")
                    if blind_location.get_value() == 0:
                        sel_cabinet_depth = self.selected_cabinet.obj_y.location.y
                        self.cabinet.obj_bp.location.x += cabinet_width
                        self.cabinet.obj_bp.location.y += sel_cabinet_depth - cabinet_width
                        self.cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  + math.radians(90)
                        self.placement = 'BLIND_LEFT'
            elif self.placement == 'RIGHT':
                self.cabinet.obj_bp.matrix_world[0][3] = sel_cabinet_width_world_x
                self.cabinet.obj_bp.matrix_world[1][3] = sel_cabinet_width_world_y
                self.cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  
                if self.selected_cabinet.corner_type == 'Blind':
                    blind_location = self.selected_cabinet.carcasses[0].get_prompt("Blind Panel Location")
                    if blind_location.get_value() == 1:   
                        sel_cabinet_depth = self.selected_cabinet.obj_y.location.y
                        self.cabinet.obj_bp.location.y += sel_cabinet_depth
                        self.cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  + math.radians(-90)
                        self.placement = 'BLIND_RIGHT' 
            else:
                x_loc = sel_cabinet_world_x - math.cos(sel_cabinet_z_rot) * ((cabinet_width/2) - (sel_cabinet_width/2))
                y_loc = sel_cabinet_world_y - math.sin(sel_cabinet_z_rot) * ((cabinet_width/2) - (sel_cabinet_width/2))
                self.cabinet.obj_bp.matrix_world[0][3] = x_loc
                self.cabinet.obj_bp.matrix_world[1][3] = y_loc
                self.cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  
        else:
            #CABINET ON WALL
            self.current_wall = pc_types.Assembly(wall_bp)
            self.cabinet.obj_bp.parent = wall_bp
            self.placement_obj.parent = self.current_wall.obj_bp
            self.placement_obj.matrix_world[0][3] = mouse_location[0]
            self.placement_obj.matrix_world[1][3] = mouse_location[1]  

            if self.placement == 'LEFT':
                self.cabinet.obj_bp.matrix_world[0][3] = sel_cabinet_world_x
                self.cabinet.obj_bp.matrix_world[1][3] = sel_cabinet_world_y
                self.cabinet.obj_bp.location.x -= cabinet_width
                self.cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  
                if self.selected_cabinet.corner_type == 'Blind':
                    blind_location = self.selected_cabinet.carcasses[0].get_prompt("Blind Panel Location")
                    if blind_location.get_value() == 0:
                        sel_cabinet_depth = self.selected_cabinet.obj_y.location.y
                        self.cabinet.obj_bp.location.x += cabinet_width
                        self.cabinet.obj_bp.location.y += sel_cabinet_depth - cabinet_width
                        self.cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  + math.radians(90)
                        self.placement = 'BLIND_LEFT'    
                        if self.selected_cabinet.obj_bp.location.x == 0:
                            l_wall = home_builder_utils.get_connected_left_wall(self.current_wall)  
                            if l_wall is None:
                                return
                            self.cabinet.obj_bp.parent = l_wall.obj_bp
                            self.cabinet.obj_bp.rotation_euler.z = 0
                            self.cabinet.obj_bp.location.y = 0
                            self.cabinet.obj_bp.location.x = l_wall.obj_x.location.x - math.fabs(sel_cabinet_depth) - cabinet_width
            elif self.placement == 'RIGHT':
                self.cabinet.obj_bp.matrix_world[0][3] = sel_cabinet_width_world_x
                self.cabinet.obj_bp.matrix_world[1][3] = sel_cabinet_width_world_y
                self.cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  
                if self.selected_cabinet.corner_type == 'Blind':
                    blind_location = self.selected_cabinet.carcasses[0].get_prompt("Blind Panel Location")
                    if blind_location.get_value() == 1:   
                        sel_cabinet_depth = self.selected_cabinet.obj_y.location.y
                        self.cabinet.obj_bp.location.y += sel_cabinet_depth
                        self.cabinet.obj_bp.rotation_euler.z = sel_cabinet_z_rot  + math.radians(-90)
                        self.placement = 'BLIND_RIGHT'   
                        if self.selected_cabinet.obj_bp.location.x >= self.current_wall.obj_x.location.x - sel_cabinet_width - .01:
                            r_wall = home_builder_utils.get_connected_right_wall(self.current_wall)  
                            if r_wall is None:
                                return
                            self.cabinet.obj_bp.parent = r_wall.obj_bp
                            self.cabinet.obj_bp.rotation_euler.z = 0
                            self.cabinet.obj_bp.location.y = 0                            
                            self.cabinet.obj_bp.location.x = math.fabs(sel_cabinet_depth)                                   
            else:
                self.cabinet.obj_bp.matrix_world[0][3] = sel_cabinet_world_x
                self.cabinet.obj_bp.matrix_world[1][3] = sel_cabinet_world_y
                self.cabinet.obj_bp.location.x += (sel_cabinet_width/2)  - (cabinet_width/2)

    def position_cabinet_on_object(self,mouse_location,event,selected_obj,cursor_z):
        self.cabinet.obj_bp.parent = None
        self.cabinet.obj_bp.location.x = mouse_location[0]
        self.cabinet.obj_bp.location.y = mouse_location[1]
        
        if self.selected_normal.z == 0:
            self.rotate_to_normal(self.selected_normal)
            parented_rotation_sum = self.accumulate_z_rotation(selected_obj)
            self.cabinet.obj_bp.rotation_euler.z += selected_obj.rotation_euler.z + parented_rotation_sum

        self.cabinet.obj_bp.location.z = self.base_height + cursor_z

    def position_cabinet(self,mouse_location,selected_obj,event,cursor_z,selected_normal):
        self.selected_normal = selected_normal
        cabinet_bp = home_builder_utils.get_cabinet_bp(selected_obj)
        window_bp = home_builder_utils.get_window_bp(selected_obj)
        door_bp = home_builder_utils.get_door_bp(selected_obj)

        if not cabinet_bp:
            cabinet_bp = home_builder_utils.get_appliance_bp(selected_obj)

        wall_bp = home_builder_utils.get_wall_bp(selected_obj)

        if window_bp:
            self.position_cabinet_next_to_door_window(mouse_location,window_bp,selected_obj)
        elif door_bp:
            self.position_cabinet_next_to_door_window(mouse_location,door_bp,selected_obj)
        elif cabinet_bp:
            self.position_cabinet_next_to_cabinet(mouse_location,cabinet_bp,selected_obj)
        elif wall_bp:
            self.position_cabinet_on_wall(mouse_location,wall_bp)
        else:
            self.position_cabinet_on_object(mouse_location,event,selected_obj,cursor_z)

    def get_cabinet(self,context):
        directory, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)
        self.cabinet = eval("cabinet_library." + filename.replace(" ","_") + "()")

        if hasattr(self.cabinet,'pre_draw'):
            self.cabinet.pre_draw()
        else:
            self.cabinet.draw()

        self.cabinet.set_name(filename)
        self.set_child_properties(self.cabinet.obj_bp)

        ## added base_height to handle upper cabinets in position_cabinet. Can't use += as it accumulates
        ## with each mouseMove event, maintains difference between lower and upper cabinets
        self.base_height = self.cabinet.obj_bp.location.z
        self.base_cabinet = self.cabinet

    def set_child_properties(self,obj):
        if "IS_DRAWERS_BP" in obj and obj["IS_DRAWERS_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Front Height Calculator')
            if calculator:
                calculator.calculate()
                self.calculators.append(calculator)

        if "IS_VERTICAL_SPLITTER_BP" in obj and obj["IS_VERTICAL_SPLITTER_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Opening Height Calculator')
            if calculator:
                calculator.calculate()
                self.calculators.append(calculator)

        home_builder_utils.update_id_props(obj,self.cabinet.obj_bp)
        home_builder_utils.assign_current_material_index(obj)
        if obj.type == 'EMPTY':
            obj.hide_viewport = True    
        if obj.type == 'MESH':
            obj.display_type = 'WIRE'            
        if obj.name != self.drawing_plane.name:
            self.exclude_objects.append(obj)    
        for child in obj.children:
            self.set_child_properties(child)

    def set_placed_properties(self,obj):
        if obj.type == 'MESH':
            obj.display_type = 'TEXTURED'          
        for child in obj.children:
            self.set_placed_properties(child) 

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def confirm_placement(self,context):
        if self.placement == 'LEFT' and self.selected_cabinet:
            self.cabinet.obj_bp.parent = self.selected_cabinet.obj_bp.parent
            constraint_obj = self.cabinet.obj_x
            constraint = self.selected_cabinet.obj_bp.constraints.new('COPY_LOCATION')
            constraint.target = constraint_obj
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = False
            for carcass in self.cabinet.carcasses:
                if self.cabinet.obj_z.location.z == self.selected_cabinet.obj_z.location.z:
                    rfe = carcass.get_prompt('Right Finished End')
                    rfe.set_value(False)

            for carcass in self.selected_cabinet.carcasses:
                if self.cabinet.obj_z.location.z == self.selected_cabinet.obj_z.location.z:
                    lfe = carcass.get_prompt('Left Finished End')
                    lfe.set_value(False)                

        if self.placement == 'RIGHT' and self.selected_cabinet:
            self.cabinet.obj_bp.parent = self.selected_cabinet.obj_bp.parent
            constraint_obj = self.selected_cabinet.obj_x
            constraint = self.cabinet.obj_bp.constraints.new('COPY_LOCATION')
            constraint.target = constraint_obj
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = False
            for carcass in self.cabinet.carcasses:
                if self.cabinet.obj_z.location.z == self.selected_cabinet.obj_z.location.z:
                    lfe = carcass.get_prompt('Left Finished End')
                    lfe.set_value(False)

            for carcass in self.selected_cabinet.carcasses:
                if self.cabinet.obj_z.location.z == self.selected_cabinet.obj_z.location.z:
                    rfe = carcass.get_prompt('Right Finished End')
                    rfe.set_value(False)               

        if hasattr(self.cabinet,'pre_draw'):
            self.cabinet.draw()
        self.set_child_properties(self.cabinet.obj_bp)
        for cal in self.calculators:
            cal.calculate()

        self.refresh_data(False)

        if self.placement == 'WALL_LEFT':
            if self.cabinet.corner_type == 'Blind':
                blind_panel_location = self.cabinet.carcasses[0].get_prompt("Blind Panel Location")
                blind_panel_location.set_value(0)

        if self.placement == 'WALL_RIGHT':
            if self.cabinet.corner_type == 'Blind':
                blind_panel_location = self.cabinet.carcasses[0].get_prompt("Blind Panel Location")
                blind_panel_location.set_value(1)

        if self.placement == 'BLIND_LEFT':
            right_filler = self.cabinet.get_prompt("Right Adjustment Width")
            right_filler.set_value(pc_unit.inch(2))
            self.cabinet.add_right_filler() 

        if self.placement == 'BLIND_RIGHT':
            left_filler = self.cabinet.get_prompt("Left Adjustment Width")
            left_filler.set_value(pc_unit.inch(2))
            self.cabinet.add_left_filler() 

        if self.current_wall:
            props = home_builder_utils.get_scene_props(context.scene)
            cabinet_type = self.cabinet.get_prompt("Cabinet Type")
            self.cabinet.obj_bp.location.z = 0
            if cabinet_type.get_value() == 'Upper':
                self.cabinet.obj_bp.location.z += props.height_above_floor - self.cabinet.obj_z.location.z

    def modal(self, context, event):
        
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        #EMPTY MUST BE VISIBLE TO CALCULATE CORRECT SIZE FOR HEIGHT COLLISION
        self.cabinet.obj_z.empty_display_size = .001
        self.cabinet.obj_z.hide_viewport = False

        for calculator in self.calculators:
            calculator.calculate()

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.reset_selection()

        ## selected_normal added in to pass this info on from ray cast to position_cabinet
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        ## cursor_z added to allow for multi level placement
        cursor_z = context.scene.cursor.location.z

        self.position_cabinet(selected_point,selected_obj,event,cursor_z,selected_normal)

        if event_is_place_asset(event):
            self.confirm_placement(context)
            return self.finish(context,event.shift)
            
        if event_is_cancel_command(event):
            return self.cancel_drop(context)

        if event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.cabinet.obj_bp)
        pc_utils.delete_object_and_children(self.drawing_plane)
        if self.placement_obj:
            pc_utils.delete_object_and_children(self.placement_obj)           
        return {'CANCELLED'}

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.cabinet.obj_x.hide_viewport = hide
        self.cabinet.obj_y.hide_viewport = hide
        self.cabinet.obj_z.hide_viewport = hide
        self.cabinet.obj_x.empty_display_size = .001
        self.cabinet.obj_y.empty_display_size = .001
        self.cabinet.obj_z.empty_display_size = .001
 
    def finish(self,context,is_recursive=False):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        if self.placement_obj:
            pc_utils.delete_object_and_children(self.placement_obj)            
        self.set_placed_properties(self.cabinet.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        if is_recursive:
            bpy.ops.home_builder.place_cabinet(filepath=self.filepath)
        return {'FINISHED'}


class home_builder_OT_place_door_window(bpy.types.Operator):
    bl_idname = "home_builder.place_door_window"
    bl_label = "Place Door or Window"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    
    drawing_plane = None

    assembly = None
    obj = None
    exclude_objects = []
    # window_z_location = 0

    def execute(self, context):
        # props = home_builder_utils.get_scene_props(context.scene)
        # self.window_z_location = props.window_height_from_floor
        self.create_drawing_plane(context)
        self.create_assembly(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def create_assembly(self,context):
        directory, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)

        self.assembly = eval("door_window_library." + filename.replace(" ","_") + "()")

        # self.assembly = wm_props.get_asset(self.filepath)        
        self.assembly.draw_assembly()
        self.set_child_properties(self.assembly.obj_bp)

    def set_child_properties(self,obj):
        if obj.type == 'EMPTY':
            obj.hide_viewport = True    
        if obj.type == 'MESH':
            obj.display_type = 'WIRE'            
        if obj.name != self.drawing_plane.name:
            self.exclude_objects.append(obj)    
        for child in obj.children:
            self.set_child_properties(child)

    def set_placed_properties(self,obj):
        home_builder_utils.update_id_props(obj,self.assembly.obj_bp)
        if obj.type == 'MESH':
            if 'IS_BOOLEAN' in obj:
                obj.display_type = 'WIRE' 
                obj.hide_viewport = True
            else:
                obj.display_type = 'TEXTURED'  
        if obj.type == 'EMPTY':
            obj.hide_viewport = True
        for child in obj.children:
            self.set_placed_properties(child) 

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def get_boolean_obj(self,obj):
        #TODO FIGURE OUT HOW TO DO RECURSIVE SEARCHING 
        #ONLY SERACHES THREE LEVELS DEEP :(
        if 'IS_BOOLEAN' in obj:
            return obj
        for child in obj.children:
            if 'IS_BOOLEAN' in child:
                return child
            for nchild in child.children:
                if 'IS_BOOLEAN' in nchild:
                    return nchild

    def add_boolean_modifier(self,wall_mesh):
        obj_bool = self.get_boolean_obj(self.assembly.obj_bp)
        if wall_mesh and obj_bool:
            mod = wall_mesh.modifiers.new(obj_bool.name,'BOOLEAN')
            mod.object = obj_bool
            mod.operation = 'DIFFERENCE'

    def confirm_placement(self):
        self.assembly.obj_bp.location.y = 0

    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        self.position_object(selected_point,selected_obj)

        if event_is_place_asset(event):
            self.add_boolean_modifier(selected_obj)
            self.confirm_placement()
            if hasattr(self.assembly,'add_doors'):
                self.assembly.add_doors()
            self.set_placed_properties(self.assembly.obj_bp)
            return self.finish(context,event.shift)

        if event_is_cancel_command(event):
            return self.cancel_drop(context)

        if event_is_pass_through(event):
            return {'PASS_THROUGH'} 

        return {'RUNNING_MODAL'} 
            
    def position_object(self,selected_point,selected_obj):
        if selected_obj:
            wall_bp = selected_obj.parent
            if self.assembly.obj_bp and wall_bp:
                self.assembly.obj_bp.parent = wall_bp
                self.assembly.obj_bp.matrix_world[0][3] = selected_point[0]
                self.assembly.obj_bp.matrix_world[1][3] = selected_point[1]
                self.assembly.obj_bp.rotation_euler.z = 0
            else:
                self.assembly.obj_bp.matrix_world[0][3] = selected_point[0]
                self.assembly.obj_bp.matrix_world[1][3] = selected_point[1]                

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.assembly.obj_x.hide_viewport = hide
        self.assembly.obj_y.hide_viewport = hide
        self.assembly.obj_z.hide_viewport = hide
        self.assembly.obj_x.empty_display_size = .001
        self.assembly.obj_y.empty_display_size = .001
        self.assembly.obj_z.empty_display_size = .001

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.assembly.obj_bp)
        pc_utils.delete_object_and_children(self.drawing_plane)
        return {'CANCELLED'}

    def finish(self,context,is_recursive=False):
        context.window.cursor_set('DEFAULT')
        self.refresh_data(False)
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        if is_recursive:
            bpy.ops.home_builder.place_door_window(filepath=self.filepath)
        return {'FINISHED'}
        

class home_builder_OT_place_appliance(bpy.types.Operator):
    bl_idname = "home_builder.place_appliance"
    bl_label = "Place Appliance"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    appliance = None
    selected_cabinet = None

    calculators = []

    drawing_plane = None

    next_wall = None
    current_wall = None
    previous_wall = None

    placement = ''

    assembly = None
    obj = None
    exclude_objects = []

    def reset_selection(self):
        self.current_wall = None
        self.selected_cabinet = None    
        self.next_wall = None
        self.previous_wall = None  
        self.placement = ''

    def reset_properties(self):
        self.appliance = None
        self.selected_cabinet = None
        self.calculators = []
        self.drawing_plane = None
        self.next_wall = None
        self.current_wall = None
        self.previous_wall = None
        self.placement = ''
        self.assembly = None
        self.obj = None
        self.exclude_objects = []

    def execute(self, context):
        self.reset_properties()
        self.create_drawing_plane(context)
        self.get_appliance(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def accumulate_z_rotation(self,selected_obj,start = 0,total = True):
        ##recursive parent traverser accumulating all rotations ie. total heirarchy rotation
        rotations = [start]
        if selected_obj.parent:
            
            if total:
                rotations.append(selected_obj.parent.rotation_euler.z)
                return self.accumulate_z_rotation(selected_obj.parent,sum(rotations))
            else:
                ## breaks after one parent
                return selected_obj.parent.rotation_euler.z
        else:
            return start

    def rotate_to_normal(self,selected_normal):
        ## cabinet vector
        base_vect = Vector((0, -1, 0))

        if selected_normal.y == 1:
            ## if Vector(0,1,0) it is a negative vector relationship with cabinet Vector(0,-1,0)
            ## quaternion calcs fail with these, 180 rotation is all thats required
            self.appliance.obj_bp.rotation_euler.z =+ math.radians(180)

        else:
            ## Vector.rotation_difference() returns quaternion rotation so change mode
            self.appliance.obj_bp.rotation_mode = 'QUATERNION'
            ## quaternion calc - required rotation to align cab to face
            rot_quat = base_vect.rotation_difference(selected_normal)

            self.appliance.obj_bp.rotation_quaternion = rot_quat
            self.appliance.obj_bp.rotation_mode = 'XYZ'

    def position_appliance(self,mouse_location,selected_obj,event,cursor_z,selected_normal):

        ##get roatations from parent heirarchy
        if selected_obj is not None:
            ##this is to block the drop if ray cast has returned nothing as xy is unattainable
            ##without will drop at (0,0,z_cursor) but on its side, could handle the rotation for this
            ##instance but seems like a pointless placement anyway? ties in with left click event
            self.drop = True

            ##get rotations from parent heirarchy
            parented_rotation_sum = self.accumulate_z_rotation(selected_obj)
            self.select_obj_unapplied_rot = selected_obj.rotation_euler.z + parented_rotation_sum
        else:
            self.drop = False
            self.select_obj_unapplied_rot = 0

        self.selected_normal = selected_normal
        cabinet_bp = home_builder_utils.get_cabinet_bp(selected_obj)

        if not cabinet_bp:
            cabinet_bp = home_builder_utils.get_appliance_bp(selected_obj)

        wall_bp = home_builder_utils.get_wall_bp(selected_obj)

        if cabinet_bp:
            self.selected_cabinet = pc_types.Assembly(cabinet_bp)

            sel_cabinet_world_loc = (self.selected_cabinet.obj_bp.matrix_world[0][3],
                                     self.selected_cabinet.obj_bp.matrix_world[1][3],
                                     self.selected_cabinet.obj_bp.matrix_world[2][3])
            
            sel_cabinet_x_world_loc = (self.selected_cabinet.obj_x.matrix_world[0][3],
                                       self.selected_cabinet.obj_x.matrix_world[1][3],
                                       self.selected_cabinet.obj_x.matrix_world[2][3])

            dist_to_bp = pc_utils.calc_distance(mouse_location,sel_cabinet_world_loc)
            dist_to_x = pc_utils.calc_distance(mouse_location,sel_cabinet_x_world_loc)
            rot = self.selected_cabinet.obj_bp.rotation_euler.z
            x_loc = 0
            y_loc = 0

            if wall_bp:
                self.current_wall = pc_types.Assembly(wall_bp)
                rot += self.current_wall.obj_bp.rotation_euler.z
            
            if home_builder_utils.has_height_collision(self.appliance,self.selected_cabinet):
                ## Allows back of cabinet snapping
                ## only way to get back consistently is through getting parent rotation of the back is always
                ## 1.5707963705062866 very close to 0.5 * pi have chucked back to 5 decimal - that precison scares me :)
                ## So wall parenting for non island bench parenting continues to work properly
                ## have added the total input for the accumulate_z function so only
                ## grabs first parent here (not wall_bp but all for non island setting

                if not wall_bp and int(self.accumulate_z_rotation(selected_obj,0,False)*10000) == 15707:
                    rot += math.radians(180)
                    x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] - math.cos(rot) * self.appliance.obj_x.location.x
                    y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] - math.sin(rot) * self.appliance.obj_x.location.x

                elif dist_to_bp < dist_to_x:
                    self.placement = 'LEFT'
                    add_x_loc = 0
                    add_y_loc = 0

                    # if sel_product.obj_bp.mv.placement_type == 'Corner':
                    #     rot += math.radians(90)
                    #     add_x_loc = math.cos(rot) * sel_product.obj_y.location.y
                    #     add_y_loc = math.sin(rot) * sel_product.obj_y.location.y
                    x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] - math.cos(rot) * self.appliance.obj_x.location.x + add_x_loc
                    y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] - math.sin(rot) * self.appliance.obj_x.location.x + add_y_loc
                else:
                    self.placement = 'RIGHT'
                    x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] + math.cos(rot) * self.selected_cabinet.obj_x.location.x
                    y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] + math.sin(rot) * self.selected_cabinet.obj_x.location.x
            else:
                x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] - math.cos(rot) * ((self.appliance.obj_x.location.x/2) - (self.selected_cabinet.obj_x.location.x/2))
                y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] - math.sin(rot) * ((self.appliance.obj_x.location.x/2) - (self.selected_cabinet.obj_x.location.x/2))                

            self.appliance.obj_bp.rotation_euler.z = rot
            self.appliance.obj_bp.location.x = x_loc
            self.appliance.obj_bp.location.y = y_loc

        elif wall_bp:

            self.placement = 'WALL'
            self.current_wall = pc_types.Assembly(wall_bp)
            self.appliance.obj_bp.rotation_euler = self.current_wall.obj_bp.rotation_euler
            ## negative vectors aka directly opposing (cabinet and wall)
            ## in this instance quaternion calcs fail and 180 rotation used to handle
            if self.selected_normal.y == 1:
                self.appliance.obj_bp.rotation_euler.z += math.radians(180)
            self.appliance.obj_bp.location.x = mouse_location[0]
            self.appliance.obj_bp.location.y = mouse_location[1]
            self.appliance.obj_bp.location.z = self.base_height + wall_bp.location.z

        else:

            if event.type == 'LEFT_ARROW' and event.value == 'PRESS':
                self.appliance.obj_bp.rotation_euler.z -= math.radians(90)
            if event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
                self.appliance.obj_bp.rotation_euler.z += math.radians(90)   

            self.appliance.obj_bp.location.x = mouse_location[0]
            self.appliance.obj_bp.location.y = mouse_location[1]

            ## if selected object is vertical ie wall
            ## or ray cast doesn't hit anything returning Vector(0,0,0) ie selected_object
            ## is None and self.drop is False

            if selected_normal.z == 0:
                if self.drop:
                    self.rotate_to_normal(selected_normal)
                    self.appliance.obj_bp.rotation_euler.z += self.select_obj_unapplied_rot

            ## else its not a wall object so treat as free standing cabinet, take rotation of floor
            ## could prob also use transform orientation to allow for custom transform orientations
            else:
                self.appliance.obj_bp.rotation_euler.z = selected_obj.rotation_euler.z

            self.appliance.obj_bp.location.z = self.base_height + cursor_z

    def get_appliance(self,context):
        directory, file = os.path.split(self.filepath)
        path, category = os.path.split(directory)
        filename, ext = os.path.splitext(file)
        props = home_builder_utils.get_scene_props(context.scene)
        if props.kitchen_tabs == 'RANGES':
            self.appliance = data_appliances.Range()
            self.appliance.category = category
            self.appliance.assembly = filename
        if props.kitchen_tabs == 'REFRIGERATORS':
            self.appliance = data_appliances.Refrigerator()
            self.appliance.category = category
            self.appliance.assembly = filename            
        if props.kitchen_tabs == 'DISHWASHERS':
            self.appliance = data_appliances.Dishwasher()
            self.appliance.category = category
            self.appliance.assembly = filename            

        if hasattr(self.appliance,'pre_draw'):
            self.appliance.pre_draw()
        else:
            self.appliance.draw()

        self.appliance.set_name(filename)
        self.set_child_properties(self.appliance.obj_bp)

        ## added base_height to handle upper cabinets in position_cabinet. Can't use += as it accumulates
        ## with each mouseMove event, maintains difference between lower and upper cabinets
        self.base_height = self.appliance.obj_bp.location.z
        self.base_cabinet = self.appliance

    def set_child_properties(self,obj):
        if "IS_DRAWERS_BP" in obj and obj["IS_DRAWERS_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Front Height Calculator')
            if calculator:
                calculator.calculate()
                self.calculators.append(calculator)

        if "IS_VERTICAL_SPLITTER_BP" in obj and obj["IS_VERTICAL_SPLITTER_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Opening Height Calculator')
            if calculator:
                calculator.calculate()
                self.calculators.append(calculator)

        home_builder_utils.update_id_props(obj,self.appliance.obj_bp)
        home_builder_utils.assign_current_material_index(obj)
        if obj.type == 'EMPTY':
            obj.hide_viewport = True    
        if obj.type == 'MESH':
            obj.display_type = 'WIRE'            
        if obj.name != self.drawing_plane.name:
            self.exclude_objects.append(obj)    
        for child in obj.children:
            self.set_child_properties(child)

    def set_placed_properties(self,obj):
        if obj.type == 'MESH':
            obj.display_type = 'TEXTURED'          
        for child in obj.children:
            self.set_placed_properties(child) 

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def confirm_placement(self,context):
        if self.current_wall:
            x_loc = pc_utils.calc_distance((self.appliance.obj_bp.location.x,self.appliance.obj_bp.location.y,0),
                                           (self.current_wall.obj_bp.matrix_local[0][3],self.current_wall.obj_bp.matrix_local[1][3],0))

            ## if backside, Vector(0,1,0) this is a negative vector relationship with cabinet Vector(0,-1,0)
            ## quaternion calcs fail with these, 180 rotation is all thats required

            if self.selected_normal.y == 1:
                self.appliance.obj_bp.rotation_euler = (0, 0,math.radians(180))
                self.appliance.obj_bp.location = (0, self.current_wall.obj_y.location.y, self.appliance.obj_bp.location.z - self.current_wall.obj_bp.location.z)
            elif self.selected_cabinet:
                self.appliance.obj_bp.rotation_euler = self.selected_cabinet.obj_bp.rotation_euler
                self.appliance.obj_bp.location = (0, self.selected_cabinet.obj_bp.location.y, self.appliance.obj_bp.location.z - self.current_wall.obj_bp.location.z)
            else:
                self.appliance.obj_bp.rotation_euler = (0, 0, 0)
                self.appliance.obj_bp.location = (0, 0, self.appliance.obj_bp.location.z - self.current_wall.obj_bp.location.z)
            self.appliance.obj_bp.parent = self.current_wall.obj_bp
            self.appliance.obj_bp.location.x = x_loc

        if self.placement == 'LEFT':
            self.appliance.obj_bp.parent = self.selected_cabinet.obj_bp.parent
            constraint_obj = self.appliance.obj_x
            constraint = self.selected_cabinet.obj_bp.constraints.new('COPY_LOCATION')
            constraint.target = constraint_obj
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = False

        if self.placement == 'RIGHT':
            self.appliance.obj_bp.parent = self.selected_cabinet.obj_bp.parent
            constraint_obj = self.selected_cabinet.obj_x
            constraint = self.appliance.obj_bp.constraints.new('COPY_LOCATION')
            constraint.target = constraint_obj
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = False

        if hasattr(self.appliance,'pre_draw'):
            self.appliance.draw()
        self.set_child_properties(self.appliance.obj_bp)
        for cal in self.calculators:
            cal.calculate()
        self.refresh_data(False)

    def modal(self, context, event):
        
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        #EMPTY MUST BE VISIBLE TO CALCULATE CORRECT SIZE FOR HEIGHT COLLISION
        self.appliance.obj_z.empty_display_size = .001
        self.appliance.obj_z.hide_viewport = False

        for calculator in self.calculators:
            calculator.calculate()

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.reset_selection()

        ## selected_normal added in to pass this info on from ray cast to position_cabinet
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        ## cursor_z added to allow for multi level placement
        cursor_z = context.scene.cursor.location.z

        self.position_appliance(selected_point,selected_obj,event,cursor_z,selected_normal)

        if event_is_place_asset(event) and self.drop:
            self.confirm_placement(context)

            return self.finish(context)
            
        if event_is_cancel_command(event):
            return self.cancel_drop(context)

        if event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.appliance.obj_bp)
        pc_utils.delete_object_and_children(self.drawing_plane)
        return {'CANCELLED'}

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.appliance.obj_x.hide_viewport = hide
        self.appliance.obj_y.hide_viewport = hide
        self.appliance.obj_z.hide_viewport = hide
        self.appliance.obj_x.empty_display_size = .001
        self.appliance.obj_y.empty_display_size = .001
        self.appliance.obj_z.empty_display_size = .001
 
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        self.set_placed_properties(self.appliance.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        self.refresh_data(False)
        context.area.tag_redraw()
        return {'FINISHED'}


class home_builder_OT_place_closet(bpy.types.Operator):
    bl_idname = "home_builder.place_closet"
    bl_label = "Place Closet"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    closet_corner_spacing = 0

    cabinet = None
    selected_cabinet = None

    calculators = []

    drawing_plane = None
    placement_obj = None

    next_wall = None
    current_wall = None
    previous_wall = None

    starting_point = ()
    placement = ''

    assembly = None
    obj = None
    exclude_objects = []

    class_name = ""

    def reset_selection(self):
        self.current_wall = None
        self.selected_cabinet = None    
        self.next_wall = None
        self.previous_wall = None  
        self.placement = ''
        # self.placement_obj = None

    def reset_properties(self):
        self.cabinet = None
        self.selected_cabinet = None
        self.calculators = []
        self.drawing_plane = None
        self.next_wall = None
        self.current_wall = None
        self.previous_wall = None
        self.starting_point = ()
        self.placement = ''
        self.assembly = None
        self.obj = None
        self.exclude_objects = []
        self.class_name = ""

    def execute(self, context):
        self.reset_properties()
        self.create_drawing_plane(context)
        self.get_cabinet(context)
        props = home_builder_utils.get_scene_props(context.scene)
        self.closet_corner_spacing = props.closet_corner_spacing
        self.placement_obj = create_placement_obj(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_wall_products(self,wall,loc_sort='X'):
        """ This returns a sorted list of all of the assemblies base points
            parented to the wall
        """
        list_obj_bp = []
        list_obj_bp.append(self.placement_obj)
        for child in wall.obj_bp.children:
            if 'IS_ASSEMBLY_BP' in child and child.name != self.cabinet.obj_bp.name:
                list_obj_bp.append(child)
        if loc_sort == 'X':
            list_obj_bp.sort(key=lambda obj: obj.location.x, reverse=False)
        if loc_sort == 'Y':
            list_obj_bp.sort(key=lambda obj: obj.location.y, reverse=False)            
        if loc_sort == 'Z':
            list_obj_bp.sort(key=lambda obj: obj.location.z, reverse=False)
        return list_obj_bp

    def get_collision_location(self,mouse_location,direction='LEFT'):
        if self.current_wall:
            self.placement_obj.parent = self.current_wall.obj_bp
            self.placement_obj.matrix_world[0][3] = mouse_location[0]
            self.placement_obj.matrix_world[1][3] = mouse_location[1]   

            list_obj_bp = self.get_wall_products(self.current_wall)
            list_obj_left_bp = []
            list_obj_right_bp = []
            for index, obj_bp in enumerate(list_obj_bp):
                if obj_bp.name == self.placement_obj.name:
                    list_obj_left_bp = list_obj_bp[:index]
                    list_obj_right_bp = list_obj_bp[index + 1:]
                    break

            if direction == 'LEFT':
                list_obj_left_bp.reverse()
                for obj_bp in list_obj_left_bp:
                    prev_ass = pc_types.Assembly(obj_bp)
                    if self.has_height_collision(prev_ass):
                        return obj_bp.location.x + prev_ass.obj_x.location.x
                
                # CHECK NEXT WALL
                left_wall =  home_builder_utils.get_connected_left_wall(self.current_wall)
                if left_wall:
                    rotation_difference = math.degrees(self.current_wall.obj_bp.rotation_euler.z) - math.degrees(left_wall.obj_bp.rotation_euler.z)
                    if rotation_difference < 0 or rotation_difference > 180:
                        list_obj_bp = self.get_wall_products(left_wall)
                        for obj in list_obj_bp:
                            if obj == self.placement_obj:
                                continue                            
                            prev_ass = pc_types.Assembly(obj)
                            product_x = obj.location.x
                            product_width = prev_ass.obj_x.location.x
                            x_dist = left_wall.obj_x.location.x  - (product_x + product_width)
                            product_depth = math.fabs(self.cabinet.obj_y.location.y)
                            if x_dist <= product_depth:
                                if self.has_height_collision(prev_ass): 
                                    return math.fabs(prev_ass.obj_y.location.y) + self.closet_corner_spacing
                return 0
            
            if direction == 'RIGHT':
                for obj_bp in list_obj_right_bp:
                    next_assembly = pc_types.Assembly(obj_bp)
                    if self.has_height_collision(next_assembly):
                        wall_length = self.current_wall.obj_x.location.x
                        return wall_length - obj_bp.location.x
        
                # CHECK NEXT WALL
                right_wall =  home_builder_utils.get_connected_right_wall(self.current_wall)
                if right_wall:
                    rotation_difference = math.degrees(self.current_wall.obj_bp.rotation_euler.z) - math.degrees(right_wall.obj_bp.rotation_euler.z)
                    if rotation_difference > 0 or rotation_difference < -180:
                        list_obj_bp = self.get_wall_products(right_wall)
                        for obj in list_obj_bp:
                            if obj == self.placement_obj:
                                continue
                            next_group = pc_types.Assembly(obj)
                            product_x = obj.location.x
                            product_width = next_group.obj_x.location.x
                            product_depth = math.fabs(self.cabinet.obj_y.location.y)
                            if product_x <= product_depth:
                                if self.has_height_collision(next_group):
                                    product_depth = math.fabs(next_group.obj_y.location.y)
                                    return product_depth +  + self.closet_corner_spacing
        
                return 0

        return 0

    def select_children(self,obj):
        obj.select_set(True)
        for child in obj.children:
            self.select_children(child)

    def position_cabinet(self,mouse_location,selected_obj,event,cursor_z,selected_normal):
        self.cabinet.obj_bp.parent = None
        #GET SELECTION INFO
        wall_bp = home_builder_utils.get_wall_bp(selected_obj)
        cabinet_bp = home_builder_utils.get_cabinet_bp(selected_obj)
        if not cabinet_bp:
            cabinet_bp = home_builder_utils.get_appliance_bp(selected_obj)
        if cabinet_bp:
            self.selected_cabinet = pc_types.Assembly(cabinet_bp)
        if wall_bp:
            self.current_wall = pc_types.Assembly(wall_bp)
        
        if cabinet_bp:
            pass
        elif wall_bp:
            self.placement = 'WALL'
            self.current_wall = pc_types.Assembly(wall_bp)
            self.cabinet.obj_bp.parent = self.current_wall.obj_bp
            self.cabinet.obj_bp.location = (0,0,0)        
            self.cabinet.obj_x.location.x = self.current_wall.obj_x.location.x
            self.select_children(self.cabinet.obj_bp)                
            left_x_loc = self.get_collision_location(mouse_location,direction='LEFT')
            right_x_loc = self.get_collision_location(mouse_location,direction='RIGHT')
            self.cabinet.obj_bp.location.x = left_x_loc
            self.cabinet.obj_x.location.x -= left_x_loc + right_x_loc
        else:
            self.cabinet.obj_bp.location.x = mouse_location[0]
            self.cabinet.obj_bp.location.y = mouse_location[1]

    def get_cabinet(self,context):
        directory, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)

        self.cabinet = eval("closet_library." + filename.replace(" ","_") + "()")

        if hasattr(self.cabinet,'pre_draw'):
            self.cabinet.pre_draw()
            print('PREDRAW')
        else:
            self.cabinet.draw()

        self.cabinet.set_name(filename)
        self.set_child_properties(self.cabinet.obj_bp)

        ## added base_height to handle upper cabinets in position_cabinet. Can't use += as it accumulates
        ## with each mouseMove event, maintains difference between lower and upper cabinets
        self.base_height = self.cabinet.obj_bp.location.z
        self.base_cabinet = self.cabinet

    def has_height_collision(self,assembly):
        cab1_z_1 = self.cabinet.obj_bp.matrix_world[2][3]
        cab1_z_2 = self.cabinet.obj_z.matrix_world[2][3]
        cab2_z_1 = assembly.obj_bp.matrix_world[2][3]
        cab2_z_2 = assembly.obj_z.matrix_world[2][3]
        
        if cab1_z_1 >= cab2_z_1 and cab1_z_1 <= cab2_z_2:
            return True
            
        if cab1_z_2 >= cab2_z_1 and cab1_z_2 <= cab2_z_2:
            return True
    
        if cab2_z_1 >= cab1_z_1 and cab2_z_1 <= cab1_z_2:
            return True
            
        if cab2_z_2 >= cab1_z_1 and cab2_z_2 <= cab1_z_2:
            return True

    def set_child_properties(self,obj):
        if "IS_DRAWERS_BP" in obj and obj["IS_DRAWERS_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Front Height Calculator')
            if calculator:
                calculator.calculate()
                self.calculators.append(calculator)

        if "IS_VERTICAL_SPLITTER_BP" in obj and obj["IS_VERTICAL_SPLITTER_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Opening Height Calculator')
            if calculator:
                calculator.calculate()
                self.calculators.append(calculator)

        home_builder_utils.update_id_props(obj,self.cabinet.obj_bp)
        home_builder_utils.assign_current_material_index(obj)
        if obj.type == 'EMPTY':
            obj.hide_viewport = True    
        if obj.type == 'MESH':
            obj.display_type = 'WIRE'            
        if obj.name != self.drawing_plane.name:
            self.exclude_objects.append(obj)    
        for child in obj.children:
            self.set_child_properties(child)

    def set_placed_properties(self,obj):
        if obj.type == 'MESH' and 'IS_OPENING_MESH' not in obj:
            obj.display_type = 'TEXTURED'          
        for child in obj.children:
            self.set_placed_properties(child) 

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def confirm_placement(self,context):
        if self.current_wall:
            self.cabinet.opening_qty = max(int(round(self.cabinet.obj_x.location.x / pc_unit.inch(38),0)),1)

        if self.placement == 'LEFT':
            self.cabinet.obj_bp.parent = self.selected_cabinet.obj_bp.parent
            constraint_obj = self.cabinet.obj_x
            constraint = self.selected_cabinet.obj_bp.constraints.new('COPY_LOCATION')
            constraint.target = constraint_obj
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = False

        if self.placement == 'RIGHT':
            self.cabinet.obj_bp.parent = self.selected_cabinet.obj_bp.parent
            constraint_obj = self.selected_cabinet.obj_x
            constraint = self.cabinet.obj_bp.constraints.new('COPY_LOCATION')
            constraint.target = constraint_obj
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = False

        self.delete_reference_object()

        if hasattr(self.cabinet,'pre_draw'):
            self.cabinet.draw()
        self.set_child_properties(self.cabinet.obj_bp)
        for cal in self.calculators:
            cal.calculate()
        self.refresh_data(False)

    def modal(self, context, event):
        
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        #EMPTY MUST BE VISIBLE TO CALCULATE CORRECT SIZE FOR HEIGHT COLLISION
        self.cabinet.obj_z.empty_display_size = .001
        self.cabinet.obj_z.hide_viewport = False

        for calculator in self.calculators:
            calculator.calculate()

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.reset_selection()

        ## selected_normal added in to pass this info on from ray cast to position_cabinet
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        ## cursor_z added to allow for multi level placement
        cursor_z = context.scene.cursor.location.z

        self.position_cabinet(selected_point,selected_obj,event,cursor_z,selected_normal)

        if event_is_place_asset(event):
            self.confirm_placement(context)

            return self.finish(context,event.shift)
            
        if event_is_cancel_command(event):
            return self.cancel_drop(context)

        if event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.cabinet.obj_bp)
        pc_utils.delete_object_and_children(self.drawing_plane)
        if self.placement_obj:
            pc_utils.delete_object_and_children(self.placement_obj)        
        return {'CANCELLED'}

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.cabinet.obj_x.hide_viewport = hide
        self.cabinet.obj_y.hide_viewport = hide
        self.cabinet.obj_z.hide_viewport = hide
        self.cabinet.obj_x.empty_display_size = .001
        self.cabinet.obj_y.empty_display_size = .001
        self.cabinet.obj_z.empty_display_size = .001
 
    def delete_reference_object(self):
        for obj in self.cabinet.obj_bp.children:
            if "IS_REFERENCE" in obj:
                pc_utils.delete_object_and_children(obj)
        if self.placement_obj:
            pc_utils.delete_object_and_children(self.placement_obj)

    def finish(self,context,is_recursive):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        self.set_placed_properties(self.cabinet.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        ## keep placing until event_is_cancel_command
        if is_recursive:
            bpy.ops.home_builder.place_closet(filepath=self.filepath)
        return {'FINISHED'}


class home_builder_OT_place_closet_insert(bpy.types.Operator):
    bl_idname = "home_builder.place_closet_insert"
    bl_label = "Place Closet Insert"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    cabinet = None
    selected_cabinet = None

    calculators = []

    next_wall = None
    current_wall = None
    previous_wall = None

    starting_point = ()
    placement = ''

    assembly = None
    obj = None
    exclude_objects = []

    class_name = ""

    def reset_selection(self):
        self.current_wall = None
        self.selected_cabinet = None    
        self.next_wall = None
        self.previous_wall = None  
        self.placement = ''

    def reset_properties(self):
        self.cabinet = None
        self.selected_cabinet = None
        self.calculators = []
        self.next_wall = None
        self.current_wall = None
        self.previous_wall = None
        self.starting_point = ()
        self.placement = ''
        self.assembly = None
        self.obj = None
        self.exclude_objects = []
        self.class_name = ""

    def execute(self, context):
        self.reset_properties()
        self.get_cabinet(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def position_cabinet(self,mouse_location,selected_obj,event,cursor_z,selected_normal):

        if selected_obj is not None:
            self.drop = True
        else:
            self.drop = False

        opening_bp = home_builder_utils.get_opening_bp(selected_obj)

        if opening_bp:
            if "IS_FILLED" not in opening_bp:
                opening = pc_types.Assembly(opening_bp)
                for child in opening.obj_bp.children:
                    if child.type == 'MESH':
                        child.select_set(True)
                self.cabinet.obj_bp.location.x = opening.obj_bp.matrix_world[0][3]
                self.cabinet.obj_bp.location.y = opening.obj_bp.matrix_world[1][3]
                self.cabinet.obj_bp.location.z = opening.obj_bp.matrix_world[2][3]
                self.cabinet.obj_x.location.x = opening.obj_x.location.x
                self.cabinet.obj_y.location.y = opening.obj_x.location.y
                self.cabinet.obj_z.location.z = opening.obj_x.location.z
                return opening

    def get_cabinet(self,context):

        directory, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)

        self.cabinet = eval("closet_library." + filename.replace(" ","_") + "()")

        if hasattr(self.cabinet,'pre_draw'):
            self.cabinet.pre_draw()
            print('PREDRAW')
        else:
            self.cabinet.draw()

        self.cabinet.set_name(filename)
        self.set_child_properties(self.cabinet.obj_bp)

    def set_child_properties(self,obj):
        if "IS_DRAWERS_BP" in obj and obj["IS_DRAWERS_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Front Height Calculator')
            if calculator:
                calculator.calculate()
                self.calculators.append(calculator)

        if "IS_VERTICAL_SPLITTER_BP" in obj and obj["IS_VERTICAL_SPLITTER_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Opening Height Calculator')
            if calculator:
                calculator.calculate()
                self.calculators.append(calculator)

        home_builder_utils.update_id_props(obj,self.cabinet.obj_bp)
        home_builder_utils.assign_current_material_index(obj)
        if obj.type == 'EMPTY':
            obj.hide_viewport = True    
        if obj.type == 'MESH':
            obj.display_type = 'WIRE'            
        for child in obj.children:
            self.set_child_properties(child)

    def set_placed_properties(self,obj):
        if obj.type == 'MESH' and obj.hide_render == False:
            obj.display_type = 'TEXTURED'          
        for child in obj.children:
            self.set_placed_properties(child) 

    def confirm_placement(self,context,opening):
        if opening:
            self.cabinet.obj_bp.parent = opening.obj_bp.parent
            self.cabinet.obj_bp.location = opening.obj_bp.location
            self.cabinet.obj_x.location.x = opening.obj_x.location.x
            self.cabinet.obj_y.location.y = opening.obj_y.location.y
            self.cabinet.obj_z.location.z = opening.obj_z.location.z
            props = home_builder_utils.get_object_props(self.cabinet.obj_bp)
            props.insert_opening = opening.obj_bp

            opening.obj_bp["IS_FILLED"] = True
            home_builder_utils.copy_drivers(opening.obj_bp,self.cabinet.obj_bp)
            home_builder_utils.copy_drivers(opening.obj_x,self.cabinet.obj_x)
            home_builder_utils.copy_drivers(opening.obj_y,self.cabinet.obj_y)
            home_builder_utils.copy_drivers(opening.obj_z,self.cabinet.obj_z)
            home_builder_utils.copy_drivers(opening.obj_prompts,self.cabinet.obj_prompts)
            for child in opening.obj_bp.children:
                child.hide_viewport = True

        self.delete_reference_object()

        if hasattr(self.cabinet,'pre_draw'):
            self.cabinet.draw()
        self.set_child_properties(self.cabinet.obj_bp)
        for cal in self.calculators:
            cal.calculate()
        self.refresh_data(False)

    def modal(self, context, event):
        
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        #EMPTY MUST BE VISIBLE TO CALCULATE CORRECT SIZE FOR HEIGHT COLLISION
        self.cabinet.obj_z.empty_display_size = .001
        self.cabinet.obj_z.hide_viewport = False

        for calculator in self.calculators:
            calculator.calculate()

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.reset_selection()

        ## selected_normal added in to pass this info on from ray cast to position_cabinet
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        ## cursor_z added to allow for multi level placement
        cursor_z = context.scene.cursor.location.z

        opening = self.position_cabinet(selected_point,selected_obj,event,cursor_z,selected_normal)

        if self.event_is_place_first_point(event):
            self.confirm_placement(context,opening)

            return self.finish(context,event.shift)
            
        if self.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if self.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def event_is_place_next_point(self,event):
        if self.starting_point == ():
            return False
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS':
            return True
        elif event.type == 'RET' and event.value == 'PRESS':
            return True
        else:
            return False

    def event_is_place_first_point(self,event):
        if self.starting_point != ():
            return False
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and self.drop:
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS' and self.drop:
            return True
        elif event.type == 'RET' and event.value == 'PRESS' and self.drop:
            return True
        else:
            return False

    def event_is_cancel_command(self,event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            return True
        else:
            return False
    
    def event_is_pass_through(self,event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return True
        else:
            return False

    def position_object(self,selected_point,selected_obj):
        self.cabinet.obj_bp.location = selected_point

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.cabinet.obj_bp)
        return {'CANCELLED'}

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.cabinet.obj_x.hide_viewport = hide
        self.cabinet.obj_y.hide_viewport = hide
        self.cabinet.obj_z.hide_viewport = hide
        self.cabinet.obj_x.empty_display_size = .001
        self.cabinet.obj_y.empty_display_size = .001
        self.cabinet.obj_z.empty_display_size = .001
 
    def delete_reference_object(self):
        for obj in self.cabinet.obj_bp.children:
            if "IS_REFERENCE" in obj:
                pc_utils.delete_object_and_children(obj)

    def finish(self,context,is_recursive):
        context.window.cursor_set('DEFAULT')
        self.set_placed_properties(self.cabinet.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        if is_recursive:
            bpy.ops.home_builder.place_closet_insert(filepath=self.filepath)
        return {'FINISHED'}


class home_builder_OT_place_closet_part(bpy.types.Operator):
    bl_idname = "home_builder.place_closet_part"
    bl_label = "Place Closet Part"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    cabinet = None
    selected_cabinet = None

    calculators = []

    next_wall = None
    current_wall = None
    previous_wall = None

    starting_point = ()
    placement = ''

    assembly = None
    obj = None
    exclude_objects = []

    class_name = ""

    def reset_selection(self):
        self.current_wall = None
        self.selected_cabinet = None    
        self.next_wall = None
        self.previous_wall = None  
        self.placement = ''

    def reset_properties(self):
        self.cabinet = None
        self.selected_cabinet = None
        self.calculators = []
        self.next_wall = None
        self.current_wall = None
        self.previous_wall = None
        self.starting_point = ()
        self.placement = ''
        self.assembly = None
        self.obj = None
        self.exclude_objects = []
        self.class_name = ""

    def execute(self, context):
        self.reset_properties()
        self.create_shelf(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def position_cabinet(self,mouse_location,selected_obj,event,cursor_z,selected_normal):

        if selected_obj is not None:
            self.drop = True
        else:
            self.drop = False

        opening_bp = home_builder_utils.get_opening_bp(selected_obj)

        if opening_bp:
            if "IS_FILLED" not in opening_bp:
                opening = pc_types.Assembly(opening_bp)
                for child in opening.obj_bp.children:
                    if child.type == 'MESH':
                        if child not in self.exclude_objects:
                            child.select_set(True)
                z_rot = opening_bp.matrix_world.to_euler()[2]
                self.cabinet.obj_bp.rotation_euler.z = z_rot
                self.cabinet.obj_bp.location.x = opening.obj_bp.matrix_world[0][3]
                self.cabinet.obj_bp.location.y = opening.obj_bp.matrix_world[1][3]
                self.cabinet.obj_bp.location.z = self.get_32mm_position(mouse_location) 
                self.cabinet.obj_x.location.x = opening.obj_x.location.x
                self.cabinet.obj_y.location.y = opening.obj_y.location.y
                # self.cabinet.obj_z.location.z = opening.obj_x.location.z
                return opening

    def create_shelf(self,context):
        path = os.path.join(home_builder_paths.get_assembly_path(),"Part.blend")
        self.cabinet = pc_types.Assembly(filepath=path)
        self.cabinet.obj_z.location.z = pc_unit.inch(.75)

        self.exclude_objects.append(self.cabinet.obj_bp)
        for obj in self.cabinet.obj_bp.children:
            self.exclude_objects.append(obj)

        self.cabinet.set_name("Single Shelf")
        self.cabinet.obj_bp['IS_SINGLE_SHELF'] = True
        self.cabinet.obj_bp['PROMPT_ID'] = 'home_builder.closet_single_shelf_prompts'
        self.set_child_properties(self.cabinet.obj_bp)

    def set_child_properties(self,obj):
        if "IS_DRAWERS_BP" in obj and obj["IS_DRAWERS_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Front Height Calculator')
            if calculator:
                calculator.calculate()
                self.calculators.append(calculator)

        if "IS_VERTICAL_SPLITTER_BP" in obj and obj["IS_VERTICAL_SPLITTER_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Opening Height Calculator')
            if calculator:
                calculator.calculate()
                self.calculators.append(calculator)

        home_builder_utils.update_id_props(obj,self.cabinet.obj_bp)
        home_builder_utils.assign_current_material_index(obj)
        if obj.type == 'EMPTY':
            obj.hide_viewport = True    
        if obj.type == 'MESH':
            obj.display_type = 'WIRE'            
        for child in obj.children:
            self.set_child_properties(child)

    def set_placed_properties(self,obj):
        if obj.type == 'MESH' and obj.hide_render == False:
            obj.display_type = 'TEXTURED'          
        for child in obj.children:
            self.set_placed_properties(child) 

    def get_32mm_position(self,selected_point):
        number_of_holes =  math.floor((selected_point[2] / pc_unit.millimeter(32)))
        return number_of_holes * pc_unit.millimeter(32)

    def confirm_placement(self,context,opening):
        z_loc = self.cabinet.obj_bp.matrix_world[2][3]
        if opening:
            self.cabinet.obj_bp.parent = opening.obj_bp.parent
            self.cabinet.obj_bp.location.x = opening.obj_bp.location.x
            self.cabinet.obj_bp.location.y = opening.obj_bp.location.y
            self.cabinet.obj_bp.matrix_world[2][3] = z_loc
            self.cabinet.obj_x.location.x = opening.obj_x.location.x
            self.cabinet.obj_y.location.y = opening.obj_y.location.y

            home_builder_utils.copy_drivers(opening.obj_x,self.cabinet.obj_x)
            home_builder_utils.copy_drivers(opening.obj_y,self.cabinet.obj_y)
            home_builder_utils.copy_drivers(opening.obj_prompts,self.cabinet.obj_prompts)
            home_builder_pointers.assign_cabinet_shelf_pointers(self.cabinet)
            home_builder_pointers.assign_materials_to_assembly(self.cabinet)

        self.refresh_data(False)

    def modal(self, context, event):
        
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        #EMPTY MUST BE VISIBLE TO CALCULATE CORRECT SIZE FOR HEIGHT COLLISION
        self.cabinet.obj_z.empty_display_size = .001
        self.cabinet.obj_z.hide_viewport = False

        for calculator in self.calculators:
            calculator.calculate()

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.reset_selection()

        ## selected_normal added in to pass this info on from ray cast to position_cabinet
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        ## cursor_z added to allow for multi level placement
        cursor_z = context.scene.cursor.location.z

        opening = self.position_cabinet(selected_point,selected_obj,event,cursor_z,selected_normal)

        if event_is_place_asset(event):
            self.confirm_placement(context,opening)

            return self.finish(context,event.shift)
            
        if event_is_cancel_command(event):
            return self.cancel_drop(context)

        if event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def position_object(self,selected_point,selected_obj):
        self.cabinet.obj_bp.location = selected_point

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.cabinet.obj_bp)
        return {'CANCELLED'}

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.cabinet.obj_x.hide_viewport = hide
        self.cabinet.obj_y.hide_viewport = hide
        self.cabinet.obj_z.hide_viewport = hide
        self.cabinet.obj_x.empty_display_size = .001
        self.cabinet.obj_y.empty_display_size = .001
        self.cabinet.obj_z.empty_display_size = .001
 
    def delete_reference_object(self):
        for obj in self.cabinet.obj_bp.children:
            if "IS_REFERENCE" in obj:
                pc_utils.delete_object_and_children(obj)

    def finish(self,context,is_recursive):
        context.window.cursor_set('DEFAULT')
        self.set_placed_properties(self.cabinet.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        if is_recursive:
            bpy.ops.home_builder.place_closet_part(filepath=self.filepath)
        return {'FINISHED'}


class home_builder_OT_place_slanted_shoe_shelf(bpy.types.Operator):
    bl_idname = "home_builder.slanted_shoe_shelf"
    bl_label = "Place Slanted Shoe Shelf"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    cabinet = None
    selected_cabinet = None

    calculators = []

    next_wall = None
    current_wall = None
    previous_wall = None

    starting_point = ()
    placement = ''

    assembly = None
    obj = None
    exclude_objects = []

    class_name = ""

    def reset_selection(self):
        self.current_wall = None
        self.selected_cabinet = None    
        self.next_wall = None
        self.previous_wall = None  
        self.placement = ''

    def reset_properties(self):
        self.cabinet = None
        self.selected_cabinet = None
        self.calculators = []
        self.next_wall = None
        self.current_wall = None
        self.previous_wall = None
        self.starting_point = ()
        self.placement = ''
        self.assembly = None
        self.obj = None
        self.exclude_objects = []
        self.class_name = ""

    def execute(self, context):
        self.reset_properties()
        self.create_shelf(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def position_cabinet(self,mouse_location,selected_obj,event,cursor_z,selected_normal):

        if selected_obj is not None:
            self.drop = True
        else:
            self.drop = False

        opening_bp = home_builder_utils.get_opening_bp(selected_obj)

        if opening_bp:
            if "IS_FILLED" not in opening_bp:
                opening = pc_types.Assembly(opening_bp)
                for child in opening.obj_bp.children:
                    if child.type == 'MESH':
                        if child not in self.exclude_objects:
                            print(child)
                            child.select_set(True)
                self.cabinet.obj_bp.location.x = opening.obj_bp.matrix_world[0][3]
                self.cabinet.obj_bp.location.y = opening.obj_bp.matrix_world[1][3]
                self.cabinet.obj_bp.location.z = self.get_32mm_position(mouse_location) 
                self.cabinet.obj_x.location.x = opening.obj_x.location.x
                self.cabinet.obj_y.location.y = opening.obj_y.location.y
                # self.cabinet.obj_z.location.z = opening.obj_x.location.z
                return opening

    def create_shelf(self,context):
        path = os.path.join(home_builder_paths.get_assembly_path(),"Part.blend")
        self.cabinet = data_closet_inserts.Slanted_Shoe_Shelf()
        self.cabinet.pre_draw()
        # self.cabinet = pc_types.Assembly(filepath=path)
        self.cabinet.obj_z.location.z = pc_unit.inch(.75)

        self.exclude_objects.append(self.cabinet.obj_bp)
        for obj in self.cabinet.obj_bp.children:
            self.exclude_objects.append(obj)

        self.cabinet.set_name("Single Shelf")
        self.set_child_properties(self.cabinet.obj_bp)

    def set_child_properties(self,obj):
        if "IS_DRAWERS_BP" in obj and obj["IS_DRAWERS_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Front Height Calculator')
            if calculator:
                calculator.calculate()
                self.calculators.append(calculator)

        if "IS_VERTICAL_SPLITTER_BP" in obj and obj["IS_VERTICAL_SPLITTER_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Opening Height Calculator')
            if calculator:
                calculator.calculate()
                self.calculators.append(calculator)

        home_builder_utils.update_id_props(obj,self.cabinet.obj_bp)
        home_builder_utils.assign_current_material_index(obj)
        if obj.type == 'EMPTY':
            obj.hide_viewport = True    
        if obj.type == 'MESH':
            obj.display_type = 'WIRE'            
        for child in obj.children:
            self.set_child_properties(child)

    def set_placed_properties(self,obj):
        if obj.type == 'MESH' and obj.hide_render == False:
            obj.display_type = 'TEXTURED'          
        for child in obj.children:
            self.set_placed_properties(child) 

    def get_32mm_position(self,selected_point):
        number_of_holes =  math.floor((selected_point[2] / pc_unit.millimeter(32)))
        return number_of_holes * pc_unit.millimeter(32)

    def confirm_placement(self,context,opening):
        z_loc = self.cabinet.obj_bp.location.z
        if opening:
            self.cabinet.obj_bp.parent = opening.obj_bp.parent
            self.cabinet.obj_bp.location.x = opening.obj_bp.location.x
            self.cabinet.obj_bp.location.y = opening.obj_bp.location.y
            self.cabinet.obj_bp.location.z = z_loc
            self.cabinet.obj_x.location.x = opening.obj_x.location.x
            self.cabinet.obj_y.location.y = opening.obj_y.location.y
            self.cabinet.draw()

            home_builder_utils.copy_drivers(opening.obj_x,self.cabinet.obj_x)
            home_builder_utils.copy_drivers(opening.obj_y,self.cabinet.obj_y)
            home_builder_utils.copy_drivers(opening.obj_prompts,self.cabinet.obj_prompts)
            home_builder_pointers.assign_cabinet_shelf_pointers(self.cabinet)
            home_builder_pointers.assign_materials_to_assembly(self.cabinet)

        self.refresh_data(False)

    def modal(self, context, event):
        
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        #EMPTY MUST BE VISIBLE TO CALCULATE CORRECT SIZE FOR HEIGHT COLLISION
        self.cabinet.obj_z.empty_display_size = .001
        self.cabinet.obj_z.hide_viewport = False

        for calculator in self.calculators:
            calculator.calculate()

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.reset_selection()

        ## selected_normal added in to pass this info on from ray cast to position_cabinet
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        ## cursor_z added to allow for multi level placement
        cursor_z = context.scene.cursor.location.z

        opening = self.position_cabinet(selected_point,selected_obj,event,cursor_z,selected_normal)

        if event_is_place_asset(event):
            self.confirm_placement(context,opening)

            return self.finish(context)
            
        if event_is_cancel_command(event):
            return event_is_cancel_command(context)

        if event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def position_object(self,selected_point,selected_obj):
        self.cabinet.obj_bp.location = selected_point

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.cabinet.obj_bp)
        return {'CANCELLED'}

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.cabinet.obj_x.hide_viewport = hide
        self.cabinet.obj_y.hide_viewport = hide
        self.cabinet.obj_z.hide_viewport = hide
        self.cabinet.obj_x.empty_display_size = .001
        self.cabinet.obj_y.empty_display_size = .001
        self.cabinet.obj_z.empty_display_size = .001
 
    def delete_reference_object(self):
        for obj in self.cabinet.obj_bp.children:
            if "IS_REFERENCE" in obj:
                pc_utils.delete_object_and_children(obj)

    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        self.set_placed_properties(self.cabinet.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        ## keep placing until event_is_cancel_command
        bpy.ops.home_builder.place_closet_part(filepath=self.filepath)
        return {'FINISHED'}


class home_builder_OT_place_wall_obstacle(bpy.types.Operator):
    bl_idname = "home_builder.place_wall_obstacle"
    bl_label = "Place Wall Obstacle"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    current_wall = None

    starting_point = ()

    obj = None
    exclude_objects = []

    def reset_properties(self):
        self.current_wall = None
        self.starting_point = ()
        self.obj = None
        self.exclude_objects = []

    def execute(self, context):
        self.reset_properties()
        self.get_object(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_object(self,context):
        directory, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)
        self.obj = home_builder_utils.get_object(os.path.join(directory,filename+".blend"))
        context.view_layer.active_layer_collection.collection.objects.link(self.obj)
        self.set_child_properties(self.obj)

    def set_child_properties(self,obj):  
        if obj.type == 'MESH':
            obj.display_type = 'WIRE'            
        for child in obj.children:
            self.set_child_properties(child)

    def set_placed_properties(self,obj):
        if obj.type == 'MESH' and obj.hide_render == False:
            obj.display_type = 'TEXTURED'          
        for child in obj.children:
            self.set_placed_properties(child) 

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        self.position_object(selected_point,selected_obj)

        if event_is_place_asset(event):
            return self.finish(context,event.shift)
            
        if event_is_cancel_command(event):
            return self.cancel_drop(context)

        if event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def position_object(self,selected_point,selected_obj):
        wall_bp = home_builder_utils.get_wall_bp(selected_obj)
        if wall_bp:
            self.obj.parent = wall_bp
            self.obj.matrix_world[0][3] = selected_point[0]
            self.obj.matrix_world[1][3] = selected_point[1]
            self.obj.matrix_world[2][3] = selected_point[2] 
            self.obj.rotation_euler.z = 0

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.obj)
        return {'CANCELLED'}

    def finish(self,context,is_recursive):
        context.window.cursor_set('DEFAULT')
        self.set_placed_properties(self.obj) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        if is_recursive:
            bpy.ops.home_builder.place_wall_obstacle(filepath=self.filepath)
        return {'FINISHED'}


class home_builder_OT_place_bathroom_fixture(bpy.types.Operator):
    bl_idname = "home_builder.place_bathroom_fixture"
    bl_label = "Place Bathroom Fixture"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    current_wall = None

    starting_point = ()

    parent_obj_dict = {}
    all_objects = []

    def reset_properties(self):
        self.current_wall = None
        self.starting_point = ()
        self.parent_obj_dict = {}
        self.all_objects = []

    def execute(self, context):
        self.reset_properties()
        self.create_drawing_plane(context)
        self.get_object(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_object(self,context):
        path, ext = os.path.splitext(self.filepath)
        object_file_path = os.path.join(path + ".blend")
        with bpy.data.libraries.load(object_file_path, False, False) as (data_from, data_to):
                data_to.objects = data_from.objects
        for obj in data_to.objects:
            obj.display_type = 'WIRE'
            self.all_objects.append(obj)
            if obj.parent is None:
                self.parent_obj_dict[obj] = (obj.location.x, obj.location.y, obj.location.z)            
            context.view_layer.active_layer_collection.collection.objects.link(obj)  

    def set_placed_properties(self,obj):
        if "obj_x" in obj:
            obj.hide_viewport = True     
        if "obj_y" in obj:
            obj.hide_viewport = True   
        if "obj_z" in obj:
            obj.hide_viewport = True   
        if "obj_bp" in obj:
            obj.hide_viewport = True           
        if obj.type == 'MESH' and obj.hide_render == False:
            obj.display_type = 'TEXTURED'

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.all_objects)

        self.position_object(selected_point,selected_obj)

        if event_is_place_asset(event):
            return self.finish(context,event.shift)
            
        if event_is_cancel_command(event):
            return self.cancel_drop(context)

        if event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def position_object(self,selected_point,selected_obj):
        for obj, location in self.parent_obj_dict.items():
            obj.location = selected_point
            obj.location.x += location[0]
            obj.location.y += location[1]
            obj.location.z += location[2]
                    
        wall_bp = home_builder_utils.get_wall_bp(selected_obj)
        if wall_bp:
            for obj, location in self.parent_obj_dict.items():            
                obj.parent = wall_bp
                obj.matrix_world[0][3] = selected_point[0]
                obj.matrix_world[1][3] = selected_point[1]
                obj.matrix_world[2][3] = 0
                obj.rotation_euler.z = 0

    def cancel_drop(self,context):
        obj_list = []
        obj_list.append(self.drawing_plane)
        for obj in self.all_objects:
            obj_list.append(obj)
        pc_utils.delete_obj_list(obj_list)
        return {'CANCELLED'}

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def finish(self,context,is_recursive):
        context.window.cursor_set('DEFAULT')
        bpy.ops.object.select_all(action='DESELECT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        bpy.ops.object.select_all(action='DESELECT')
        for obj, location in self.parent_obj_dict.items():
            obj.select_set(True)  
            context.view_layer.objects.active = obj     
        for obj in self.all_objects:
            self.set_placed_properties(obj) 
        context.area.tag_redraw()
        if is_recursive:
            bpy.ops.home_builder.place_bathroom_fixture(filepath=self.filepath)
        return {'FINISHED'}


class home_builder_OT_place_decoration(bpy.types.Operator):
    bl_idname = "home_builder.place_decoration"
    bl_label = "Place Decoration"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    current_wall = None

    starting_point = ()

    parent_obj_dict = {}
    all_objects = []

    def reset_properties(self):
        self.current_wall = None
        self.starting_point = ()
        self.parent_obj_dict = {}
        self.all_objects = []

    def execute(self, context):
        self.reset_properties()
        self.create_drawing_plane(context)
        self.get_object(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_object(self,context):
        path, ext = os.path.splitext(self.filepath)
        object_file_path = os.path.join(path + ".blend")
        with bpy.data.libraries.load(object_file_path, False, False) as (data_from, data_to):
                data_to.objects = data_from.objects
        for obj in data_to.objects:
            obj.display_type = 'WIRE'
            self.all_objects.append(obj)
            if obj.parent is None:
                self.parent_obj_dict[obj] = (obj.location.x, obj.location.y, obj.location.z)            
            context.view_layer.active_layer_collection.collection.objects.link(obj)  

    def set_placed_properties(self,obj):
        if obj.type == 'MESH' and obj.hide_render == False:
            obj.display_type = 'TEXTURED'          
        for child in obj.children:
            self.set_placed_properties(child) 

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.all_objects)

        self.position_object(selected_point,selected_obj)

        if event_is_place_asset(event):
            return self.finish(context,event.shift)
            
        if event_is_cancel_command(event):
            return self.cancel_drop(context)

        if event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def position_object(self,selected_point,selected_obj):
        for obj, location in self.parent_obj_dict.items():
            obj.location = selected_point
            obj.location.x += location[0]
            obj.location.y += location[1]
            obj.location.z += location[2]

    def cancel_drop(self,context):
        obj_list = []
        obj_list.append(self.drawing_plane)
        for obj in self.all_objects:
            obj_list.append(obj)
        pc_utils.delete_obj_list(obj_list)
        return {'CANCELLED'}

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def finish(self,context,is_recursive):
        context.window.cursor_set('DEFAULT')
        bpy.ops.object.select_all(action='DESELECT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        bpy.ops.object.select_all(action='DESELECT')
        for obj, location in self.parent_obj_dict.items():
            obj.select_set(True)  
            context.view_layer.objects.active = obj     
        for obj in self.all_objects:
            self.set_placed_properties(obj) 
        context.area.tag_redraw()
        if is_recursive:
            bpy.ops.home_builder.place_decoration(filepath=self.filepath)
        return {'FINISHED'}

classes = (
    home_builder_OT_drop,
    home_builder_OT_place_room,
    home_builder_OT_place_door_window,
    home_builder_OT_place_cabinet,
    home_builder_OT_place_appliance,
    home_builder_OT_place_closet,
    home_builder_OT_place_closet_insert,
    home_builder_OT_place_closet_part,
    home_builder_OT_place_slanted_shoe_shelf,
    home_builder_OT_place_wall_obstacle,
    home_builder_OT_place_bathroom_fixture,
    home_builder_OT_place_decoration,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
