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
from bpy_extras.view3d_utils import location_3d_to_region_2d

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
from . import home_builder_enums
from . import home_builder_placement_utils as placement_utils
from importlib import import_module

# from .cabinets import data_cabinet_carcass
# from .cabinets import data_cabinet_exteriors
# from .cabinets import data_cabinet_parts
# from .cabinets import cabinet_utils
# from . import home_builder_pointers
from . import home_builder_utils
# from . import home_builder_paths

class home_builder_OT_drop(Operator):
    bl_idname = "home_builder.drop"
    bl_label = "Home Builder Drop"
    bl_description = "This is called when an asset is dropped from the home builder library"

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
                bpy.ops.home_builder.place_cabinet(obj_bp_name=obj_bp.name,snap_cursor_to_cabinet=False)
            if props.kitchen_tabs == 'DECORATIONS':
                bpy.ops.home_builder.place_decoration(filepath=self.filepath)  

        if props.library_tabs == 'BATHS':
            if props.bath_tabs == 'TOILETS':
                bpy.ops.home_builder.place_bathroom_fixture(filepath=self.filepath)  
            if props.bath_tabs == 'BATHS':
                bpy.ops.home_builder.place_bathroom_fixture(filepath=self.filepath)                  
            if props.bath_tabs == 'VANITIES':
                obj_bp = self.get_custom_cabinet(context,os.path.join(directory,filename + ".blend"))
                bpy.ops.home_builder.place_cabinet(obj_bp_name=obj_bp.name,snap_cursor_to_cabinet=False)
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
    bl_options = {'UNDO'}
    
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
        home_builder_utils.update_id_props(obj,self.room.obj_bp)
        for child in obj.children:
            self.set_placed_properties(child)

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.meshes)

        self.position_object(selected_point,selected_obj)

        if placement_utils.event_is_place_asset(event):
            return self.finish(context)
            
        if placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if placement_utils.event_is_pass_through(event):
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
    bl_options = {'UNDO'}
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    snap_cursor_to_cabinet: bpy.props.BoolProperty(name="Snap Cursor to Cabinet",default=False)

    mouse_x = 0
    mouse_y = 0

    cabinet = None
    selected_cabinet = None
    height_above_floor = 0

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

        if self.snap_cursor_to_cabinet:
            if self.obj_bp_name != "":
                obj_bp = bpy.data.objects[self.obj_bp_name]
            else:
                obj_bp = self.cabinet.obj_bp            
            region = context.region
            co = location_3d_to_region_2d(region,context.region_data,obj_bp.matrix_world.translation)
            region_offset = Vector((region.x,region.y))
            context.window.cursor_warp(*(co + region_offset))  

        self.placement_obj = placement_utils.create_placement_obj(context)

        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_cabinet(self,context):
        if self.obj_bp_name in bpy.data.objects:
            obj_bp = bpy.data.objects[self.obj_bp_name]
            self.cabinet = data_cabinets.Cabinet(obj_bp)
        else:
            directory, file = os.path.split(self.filepath)
            filename, ext = os.path.splitext(file)
            self.cabinet = eval("cabinet_library." + filename.replace(" ","_") + "()")

            if hasattr(self.cabinet,'pre_draw'):
                self.cabinet.pre_draw()
            else:
                self.cabinet.draw()

            self.cabinet.set_name(filename)
        self.set_child_properties(self.cabinet.obj_bp)

        self.height_above_floor = self.cabinet.obj_bp.location.z

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
            if cabinet_type and cabinet_type.get_value() == 'Upper':
                self.cabinet.obj_bp.location.z += props.height_above_floor - self.cabinet.obj_z.location.z

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        #EMPTY MUST BE VISIBLE TO CALCULATE CORRECT SIZE FOR HEIGHT COLLISION
        self.cabinet.obj_z.empty_display_size = .001
        self.cabinet.obj_z.hide_viewport = False

        for calculator in self.calculators:
            calculator.calculate()

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.reset_selection()

        context.view_layer.update()
        ## selected_normal added in to pass this info on from ray cast to position_cabinet
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        ## cursor_z added to allow for multi level placement
        cursor_z = context.scene.cursor.location.z

        self.placement, self.selected_cabinet, self.current_wall = placement_utils.position_cabinet(self.cabinet,
                                                                                                    selected_point,
                                                                                                    selected_obj,
                                                                                                    cursor_z,
                                                                                                    selected_normal,
                                                                                                    self.placement_obj,
                                                                                                    self.height_above_floor)

        if event.type == 'LEFT_ARROW' and event.value == 'PRESS':
            self.cabinet.obj_bp.rotation_euler.z -= math.radians(90)
        if event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
            self.cabinet.obj_bp.rotation_euler.z += math.radians(90)   

        if placement_utils.event_is_place_asset(event):
            self.confirm_placement(context)
            return self.finish(context,event.shift)
            
        if placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if placement_utils.event_is_pass_through(event):
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
    bl_options = {'UNDO'}
    
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

    def remove_old_boolean_modifier(self):
        wall_bp = home_builder_utils.get_wall_bp(self.assembly.obj_bp)
        wall_mesh = None
        for child in wall_bp.children:
            if child.type == 'MESH':
                wall_mesh = child
        obj_bool = self.get_boolean_obj(self.assembly.obj_bp)
        if wall_mesh:
            for mod in wall_mesh.modifiers:
                if mod.type == 'BOOLEAN':
                    if mod.object == obj_bool:
                        wall_mesh.modifiers.remove(mod)
                        
    def create_assembly(self,context):
        if self.obj_bp_name in bpy.data.objects:
            obj_bp = bpy.data.objects[self.obj_bp_name]
            self.assembly = pc_types.Assembly(obj_bp)
            self.remove_old_boolean_modifier()
        else:
            directory, file = os.path.split(self.filepath)
            filename, ext = os.path.splitext(file)
            self.assembly = eval("door_window_library." + filename.replace(" ","_") + "()")     
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
        context.view_layer.update()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        self.position_object(selected_point,selected_obj)

        if placement_utils.event_is_place_asset(event):
            self.add_boolean_modifier(selected_obj)
            self.confirm_placement()
            if hasattr(self.assembly,'add_doors'):
                self.assembly.add_doors()
            self.set_placed_properties(self.assembly.obj_bp)
            return self.finish(context,event.shift)

        if placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if placement_utils.event_is_pass_through(event):
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
        if is_recursive and self.obj_bp_name == "":
            bpy.ops.home_builder.place_door_window(filepath=self.filepath)
        return {'FINISHED'}
        

class home_builder_OT_place_appliance(bpy.types.Operator):
    bl_idname = "home_builder.place_appliance"
    bl_label = "Place Appliance"
    bl_options = {'UNDO'}
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    snap_cursor_to_cabinet: bpy.props.BoolProperty(name="Snap Cursor to Cabinet",default=False)

    appliance = None
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

        if self.snap_cursor_to_cabinet:
            if self.obj_bp_name != "":
                obj_bp = bpy.data.objects[self.obj_bp_name]
            else:
                obj_bp = self.cabinet.obj_bp            
            region = context.region
            co = location_3d_to_region_2d(region,context.region_data,obj_bp.matrix_world.translation)
            region_offset = Vector((region.x,region.y))
            context.window.cursor_warp(*(co + region_offset))  

        self.placement_obj = placement_utils.create_placement_obj(context)

        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_appliance(self,context):
        if self.obj_bp_name in bpy.data.objects:
            obj_bp = bpy.data.objects[self.obj_bp_name]
            self.appliance = pc_types.Assembly(obj_bp)
        else:        
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

        self.height_above_floor = self.appliance.obj_bp.location.z

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

        #EMPTY MUST BE VISIBLE TO CALCULATE CORRECT SIZE FOR HEIGHT COLLISION
        self.appliance.obj_z.empty_display_size = .001
        self.appliance.obj_z.hide_viewport = False

        for calculator in self.calculators:
            calculator.calculate()

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.reset_selection()

        context.view_layer.update()
        ## selected_normal added in to pass this info on from ray cast to position_cabinet
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        ## cursor_z added to allow for multi level placement
        cursor_z = context.scene.cursor.location.z

        placement_utils.position_cabinet(self.appliance,selected_point,selected_obj,cursor_z,selected_normal,self.placement_obj,self.height_above_floor)

        if placement_utils.event_is_place_asset(event):
            self.confirm_placement(context)

            return self.finish(context)
            
        if placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if placement_utils.event_is_pass_through(event):
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
        if self.placement_obj:
            pc_utils.delete_object_and_children(self.placement_obj)             
        self.set_placed_properties(self.appliance.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        self.refresh_data(False)
        context.area.tag_redraw()
        return {'FINISHED'}


class home_builder_OT_place_closet(bpy.types.Operator):
    bl_idname = "home_builder.place_closet"
    bl_label = "Place Closet"
    bl_options = {'UNDO'}
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    mouse_x = 0
    mouse_y = 0

    closet = None
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
        self.get_closet(context)
        self.placement_obj = placement_utils.create_placement_obj(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_closet(self,context):
        directory, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)

        self.closet = eval("closet_library." + filename.replace(" ","_") + "()")

        if hasattr(self.closet,'pre_draw'):
            self.closet.pre_draw()
        else:
            self.closet.draw()

        self.closet.set_name(filename)
        self.set_child_properties(self.closet.obj_bp)

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

        home_builder_utils.update_id_props(obj,self.closet.obj_bp)
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

    def confirm_placement(self,context, override_height):
        if self.current_wall:
            self.closet.opening_qty = max(int(math.ceil(self.closet.obj_x.location.x / pc_unit.inch(38))),1)

        if self.placement == 'LEFT':
            self.closet.obj_bp.parent = self.selected_cabinet.obj_bp.parent
            constraint_obj = self.closet.obj_x
            constraint = self.selected_cabinet.obj_bp.constraints.new('COPY_LOCATION')
            constraint.target = constraint_obj
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = False

        if self.placement == 'RIGHT':
            self.closet.obj_bp.parent = self.selected_cabinet.obj_bp.parent
            constraint_obj = self.selected_cabinet.obj_x
            constraint = self.closet.obj_bp.constraints.new('COPY_LOCATION')
            constraint.target = constraint_obj
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = False

        self.delete_reference_object()

        if hasattr(self.closet,'pre_draw'):
            self.closet.draw()

        if override_height != 0:
            for i in range(1,9):
                opening_height_prompt = self.closet.get_prompt("Opening " + str(i) + " Height")
                if opening_height_prompt:
                    for index, height in enumerate(home_builder_enums.PANEL_HEIGHTS):
                        if not override_height >= float(height[0])/1000:
                            opening_height_prompt.set_value(float(home_builder_enums.PANEL_HEIGHTS[index - 1][0])/1000)
                            break

        self.set_child_properties(self.closet.obj_bp)
        for cal in self.calculators:
            cal.calculate()
        self.refresh_data(False)

    def modal(self, context, event):
        
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        #EMPTY MUST BE VISIBLE TO CALCULATE CORRECT SIZE FOR HEIGHT COLLISION
        self.closet.obj_z.empty_display_size = .001
        self.closet.obj_z.hide_viewport = False

        for calculator in self.calculators:
            calculator.calculate()

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.reset_selection()

        ## selected_normal added in to pass this info on from ray cast to position_cabinet
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        ## cursor_z added to allow for multi level placement
        cursor_z = context.scene.cursor.location.z

        self.placement, self.selected_cabinet, self.current_wall, override_height = placement_utils.position_closet(self.closet,
                                                                                                    selected_point,
                                                                                                    selected_obj,
                                                                                                    cursor_z,
                                                                                                    selected_normal,
                                                                                                    self.placement_obj,
                                                                                                    0)

        if placement_utils.event_is_place_asset(event):
            self.confirm_placement(context,override_height)

            return self.finish(context,event.shift)
            
        if placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if placement_utils.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.closet.obj_bp)
        pc_utils.delete_object_and_children(self.drawing_plane)
        if self.placement_obj:
            pc_utils.delete_object_and_children(self.placement_obj)        
        return {'CANCELLED'}

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.closet.obj_x.hide_viewport = hide
        self.closet.obj_y.hide_viewport = hide
        self.closet.obj_z.hide_viewport = hide
        self.closet.obj_x.empty_display_size = .001
        self.closet.obj_y.empty_display_size = .001
        self.closet.obj_z.empty_display_size = .001
 
    def delete_reference_object(self):
        for obj in self.closet.obj_bp.children:
            if "IS_REFERENCE" in obj:
                pc_utils.delete_object_and_children(obj)
        if self.placement_obj:
            pc_utils.delete_object_and_children(self.placement_obj)

    def finish(self,context,is_recursive):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        self.set_placed_properties(self.closet.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        ## keep placing until event_is_cancel_command
        if is_recursive:
            bpy.ops.home_builder.place_closet(filepath=self.filepath)
        return {'FINISHED'}


class home_builder_OT_place_corner_closet(bpy.types.Operator):
    bl_idname = "home_builder.place_corner_closet"
    bl_label = "Place Corner Closet"
    bl_options = {'UNDO'}
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    mouse_x = 0
    mouse_y = 0

    closet = None
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
        self.get_closet(context)
        self.placement_obj = placement_utils.create_placement_obj(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_closet(self,context):
        directory, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)

        self.closet = eval("closet_library." + filename.replace(" ","_") + "()")

        if hasattr(self.closet,'pre_draw'):
            self.closet.pre_draw()
        else:
            self.closet.draw()

        self.closet.set_name(filename)
        self.set_child_properties(self.closet.obj_bp)

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

        home_builder_utils.update_id_props(obj,self.closet.obj_bp)
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
            self.closet.opening_qty = max(int(round(self.closet.obj_x.location.x / pc_unit.inch(38),0)),1)

        if self.placement == 'LEFT':
            self.closet.obj_bp.parent = self.selected_cabinet.obj_bp.parent
            constraint_obj = self.closet.obj_x
            constraint = self.selected_cabinet.obj_bp.constraints.new('COPY_LOCATION')
            constraint.target = constraint_obj
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = False

        if self.placement == 'RIGHT':
            self.closet.obj_bp.parent = self.selected_cabinet.obj_bp.parent
            constraint_obj = self.selected_cabinet.obj_x
            constraint = self.closet.obj_bp.constraints.new('COPY_LOCATION')
            constraint.target = constraint_obj
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = False

        self.delete_reference_object()

        if hasattr(self.closet,'pre_draw'):
            self.closet.draw()
        self.set_child_properties(self.closet.obj_bp)
        for cal in self.calculators:
            cal.calculate()
        self.refresh_data(False)

    def modal(self, context, event):
        
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        #EMPTY MUST BE VISIBLE TO CALCULATE CORRECT SIZE FOR HEIGHT COLLISION
        self.closet.obj_z.empty_display_size = .001
        self.closet.obj_z.hide_viewport = False

        for calculator in self.calculators:
            calculator.calculate()

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.reset_selection()

        ## selected_normal added in to pass this info on from ray cast to position_cabinet
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        ## cursor_z added to allow for multi level placement
        cursor_z = context.scene.cursor.location.z

        self.placement, self.selected_cabinet, self.selected_wall = placement_utils.position_corner_unit(self.closet,
                                                                                                         selected_point,
                                                                                                         selected_obj,
                                                                                                         cursor_z,
                                                                                                         selected_normal,
                                                                                                         self.placement_obj,
                                                                                                         0)

        if placement_utils.event_is_place_asset(event):
            self.confirm_placement(context)

            return self.finish(context,event.shift)
            
        if placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if placement_utils.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.closet.obj_bp)
        pc_utils.delete_object_and_children(self.drawing_plane)
        if self.placement_obj:
            pc_utils.delete_object_and_children(self.placement_obj)        
        return {'CANCELLED'}

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.closet.obj_x.hide_viewport = hide
        self.closet.obj_y.hide_viewport = hide
        self.closet.obj_z.hide_viewport = hide
        self.closet.obj_x.empty_display_size = .001
        self.closet.obj_y.empty_display_size = .001
        self.closet.obj_z.empty_display_size = .001
 
    def delete_reference_object(self):
        for obj in self.closet.obj_bp.children:
            if "IS_REFERENCE" in obj:
                pc_utils.delete_object_and_children(obj)
        if self.placement_obj:
            pc_utils.delete_object_and_children(self.placement_obj)

    def finish(self,context,is_recursive):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        self.set_placed_properties(self.closet.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        ## keep placing until event_is_cancel_command
        if is_recursive:
            bpy.ops.home_builder.place_closet(filepath=self.filepath)
        return {'FINISHED'}


class home_builder_OT_place_closet_insert(bpy.types.Operator):
    bl_idname = "home_builder.place_closet_insert"
    bl_label = "Place Closet Insert"
    bl_options = {'UNDO'}
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    snap_cursor_to_cabinet: bpy.props.BoolProperty(name="Snap Cursor to Base Point",default=False)

    insert = None

    calculators = []

    exclude_objects = []

    def reset_selection(self):
        pass

    def reset_properties(self):
        self.insert = None
        self.calculators = []
        self.exclude_objects = []

    def execute(self, context):
        self.reset_properties()
        self.get_insert(context)

        if self.snap_cursor_to_cabinet:
            if self.obj_bp_name != "":
                obj_bp = bpy.data.objects[self.obj_bp_name]
            else:
                obj_bp = self.insert.obj_bp            
            region = context.region
            co = location_3d_to_region_2d(region,context.region_data,obj_bp.matrix_world.translation)
            region_offset = Vector((region.x,region.y))
            context.window.cursor_warp(*(co + region_offset))  

        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def position_insert(self,mouse_location,selected_obj,event,cursor_z,selected_normal):
        opening_bp = home_builder_utils.get_opening_bp(selected_obj)
        if opening_bp:
            if "IS_FILLED" not in opening_bp:
                opening = pc_types.Assembly(opening_bp)
                for child in opening.obj_bp.children:
                    if child.type == 'MESH':
                        child.select_set(True)
                loc_pos = opening.obj_bp.matrix_world
                self.insert.obj_bp.location.x = opening.obj_bp.matrix_world[0][3]
                self.insert.obj_bp.location.y = opening.obj_bp.matrix_world[1][3]
                self.insert.obj_bp.location.z = opening.obj_bp.matrix_world[2][3]
                self.insert.obj_bp.rotation_euler.z = loc_pos.to_euler()[2]
                self.insert.obj_x.location.x = opening.obj_x.location.x
                self.insert.obj_y.location.y = opening.obj_y.location.y
                self.insert.obj_z.location.z = opening.obj_z.location.z
                return opening

    def add_exclude_objects(self,obj):
        self.exclude_objects.append(obj)
        for child in obj.children:
            self.add_exclude_objects(child)

    def get_insert(self,context):
        if self.obj_bp_name in bpy.data.objects:
            obj_bp = bpy.data.objects[self.obj_bp_name]
            self.insert = pc_types.Assembly(obj_bp)
        else:        
            directory, file = os.path.split(self.filepath)
            filename, ext = os.path.splitext(file)

            self.insert = eval("closet_library." + filename.replace(" ","_") + "()")

            if hasattr(self.insert,'pre_draw'):
                self.insert.pre_draw()
            else:
                self.insert.draw()

            self.insert.set_name(filename)

        self.add_exclude_objects(self.insert.obj_bp)
        self.set_child_properties(self.insert.obj_bp)

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
        #Dont Update Id Props when duplicating
        if self.obj_bp_name == "":
            home_builder_utils.update_id_props(obj,self.insert.obj_bp)
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
            self.insert.obj_bp.parent = opening.obj_bp.parent
            self.insert.obj_bp.location = opening.obj_bp.location
            self.insert.obj_bp.rotation_euler = (0,0,0)
            self.insert.obj_x.location.x = opening.obj_x.location.x
            self.insert.obj_y.location.y = opening.obj_y.location.y
            self.insert.obj_z.location.z = opening.obj_z.location.z
            o_left_depth = opening.get_prompt('Left Depth').get_var('o_left_depth')
            o_right_depth = opening.get_prompt('Right Depth').get_var('o_right_depth')
            i_left_depth = self.insert.get_prompt('Left Depth')
            i_right_depth = self.insert.get_prompt('Right Depth')
            i_left_depth.set_formula('o_left_depth',[o_left_depth])
            i_right_depth.set_formula('o_right_depth',[o_right_depth])
            
            props = home_builder_utils.get_object_props(self.insert.obj_bp)
            props.insert_opening = opening.obj_bp

            opening.obj_bp["IS_FILLED"] = True
            home_builder_utils.copy_drivers(opening.obj_bp,self.insert.obj_bp)
            home_builder_utils.copy_drivers(opening.obj_x,self.insert.obj_x)
            home_builder_utils.copy_drivers(opening.obj_y,self.insert.obj_y)
            home_builder_utils.copy_drivers(opening.obj_z,self.insert.obj_z)
            home_builder_utils.copy_drivers(opening.obj_prompts,self.insert.obj_prompts)
            for child in opening.obj_bp.children:
                child.hide_viewport = True

        self.delete_reference_object()

        if hasattr(self.insert,'pre_draw'):
            self.insert.draw()
        self.set_child_properties(self.insert.obj_bp)
        for cal in self.calculators:
            cal.calculate()
        self.refresh_data(False)

    def modal(self, context, event):
        
        bpy.ops.object.select_all(action='DESELECT')

        #EMPTY MUST BE VISIBLE TO CALCULATE CORRECT SIZE FOR HEIGHT COLLISION
        self.insert.obj_z.empty_display_size = .001
        self.insert.obj_z.hide_viewport = False

        for calculator in self.calculators:
            calculator.calculate()

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.reset_selection()
        context.view_layer.update()

        ## selected_normal added in to pass this info on from ray cast to position_cabinet
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        ## cursor_z added to allow for multi level placement
        cursor_z = context.scene.cursor.location.z

        opening = self.position_insert(selected_point,selected_obj,event,cursor_z,selected_normal)

        if placement_utils.event_is_place_asset(event):
            self.confirm_placement(context,opening)

            return self.finish(context,event.shift)
            
        if placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if placement_utils.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def position_object(self,selected_point,selected_obj):
        self.insert.obj_bp.location = selected_point

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.insert.obj_bp)
        return {'CANCELLED'}

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.insert.obj_x.hide_viewport = hide
        self.insert.obj_y.hide_viewport = hide
        self.insert.obj_z.hide_viewport = hide
        self.insert.obj_x.empty_display_size = .001
        self.insert.obj_y.empty_display_size = .001
        self.insert.obj_z.empty_display_size = .001
 
    def delete_reference_object(self):
        for obj in self.insert.obj_bp.children:
            if "IS_REFERENCE" in obj:
                pc_utils.delete_object_and_children(obj)

    def finish(self,context,is_recursive):
        context.window.cursor_set('DEFAULT')
        self.set_placed_properties(self.insert.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        if is_recursive and self.obj_bp_name == "":
            bpy.ops.home_builder.place_closet_insert(filepath=self.filepath)
        return {'FINISHED'}


class home_builder_OT_place_closet_part(bpy.types.Operator):
    bl_idname = "home_builder.place_closet_part"
    bl_label = "Place Closet Part"
    bl_options = {'UNDO'}
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    part = None

    exclude_objects = []

    def reset_properties(self):
        self.part = None
        self.exclude_objects = []

    def execute(self, context):
        self.reset_properties()
        self.create_part(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def position_part(self,mouse_location,selected_obj,event,cursor_z,selected_normal):
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
                self.part.obj_bp.rotation_euler.z = z_rot
                self.part.obj_bp.location.x = opening.obj_bp.matrix_world[0][3]
                self.part.obj_bp.location.y = opening.obj_bp.matrix_world[1][3]
                self.part.obj_bp.location.z = self.get_32mm_position(mouse_location) 
                self.part.obj_x.location.x = opening.obj_x.location.x
                self.part.obj_y.location.y = opening.obj_y.location.y
                return opening

    def create_part(self,context):
        path = os.path.join(home_builder_paths.get_assembly_path(),"Part.blend")
        self.part = pc_types.Assembly(filepath=path)
        self.part.obj_z.location.z = pc_unit.inch(.75)

        self.exclude_objects.append(self.part.obj_bp)
        for obj in self.part.obj_bp.children:
            self.exclude_objects.append(obj)

        self.part.set_name("Single Shelf")
        self.part.obj_bp['IS_SINGLE_SHELF'] = True
        self.part.obj_bp['PROMPT_ID'] = 'home_builder.closet_single_shelf_prompts'
        self.set_child_properties(self.part.obj_bp)

    def set_child_properties(self,obj):
        home_builder_utils.update_id_props(obj,self.part.obj_bp)
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
        z_loc = self.part.obj_bp.matrix_world[2][3]
        if opening:
            self.part.obj_bp.parent = opening.obj_bp.parent
            self.part.obj_bp.location.x = opening.obj_bp.location.x
            self.part.obj_bp.location.y = opening.obj_bp.location.y
            self.part.obj_bp.matrix_world[2][3] = z_loc
            self.part.obj_x.location.x = opening.obj_x.location.x
            self.part.obj_y.location.y = opening.obj_y.location.y

            home_builder_utils.copy_drivers(opening.obj_x,self.part.obj_x)
            home_builder_utils.copy_drivers(opening.obj_y,self.part.obj_y)
            home_builder_utils.copy_drivers(opening.obj_prompts,self.part.obj_prompts)
            home_builder_pointers.assign_cabinet_shelf_pointers(self.part)
            home_builder_pointers.assign_materials_to_assembly(self.part)

        self.refresh_data(False)

    def modal(self, context, event):
        
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        #EMPTY MUST BE VISIBLE TO CALCULATE CORRECT SIZE FOR HEIGHT COLLISION
        self.part.obj_z.empty_display_size = .001
        self.part.obj_z.hide_viewport = False

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        ## selected_normal added in to pass this info on from ray cast to position_cabinet
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        ## cursor_z added to allow for multi level placement
        cursor_z = context.scene.cursor.location.z

        opening = self.position_part(selected_point,selected_obj,event,cursor_z,selected_normal)

        if placement_utils.event_is_place_asset(event):
            self.confirm_placement(context,opening)

            return self.finish(context,event.shift)
            
        if placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if placement_utils.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.part.obj_bp)
        return {'CANCELLED'}

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.part.obj_x.hide_viewport = hide
        self.part.obj_y.hide_viewport = hide
        self.part.obj_z.hide_viewport = hide
        self.part.obj_x.empty_display_size = .001
        self.part.obj_y.empty_display_size = .001
        self.part.obj_z.empty_display_size = .001
 
    def delete_reference_object(self):
        for obj in self.part.obj_bp.children:
            if "IS_REFERENCE" in obj:
                pc_utils.delete_object_and_children(obj)

    def finish(self,context,is_recursive):
        context.window.cursor_set('DEFAULT')
        self.set_placed_properties(self.part.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        if is_recursive:
            bpy.ops.home_builder.place_closet_part(filepath=self.filepath)
        return {'FINISHED'}


class home_builder_OT_place_closet_cleat(bpy.types.Operator):
    bl_idname = "home_builder.place_closet_cleat"
    bl_label = "Place Closet Cleat"
    bl_options = {'UNDO'}
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    part = None

    exclude_objects = []

    def reset_properties(self):
        self.part = None

    def execute(self, context):
        self.reset_properties()
        self.create_part(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def position_part(self,mouse_location,selected_obj,event,cursor_z,selected_normal):

        if selected_obj is not None:
            self.drop = True
        else:
            self.drop = False

        opening_bp = home_builder_utils.get_opening_bp(selected_obj)

        if opening_bp:
            opening = pc_types.Assembly(opening_bp)
            for child in opening.obj_bp.children:
                if child.type == 'MESH':
                    if child not in self.exclude_objects:
                        child.select_set(True)

            sel_opening_world_loc = (opening.obj_bp.matrix_world[0][3],
                                     opening.obj_bp.matrix_world[1][3],
                                     opening.obj_bp.matrix_world[2][3])
            
            sel_opening_z_world_loc = (opening.obj_z.matrix_world[0][3],
                                       opening.obj_z.matrix_world[1][3],
                                       opening.obj_z.matrix_world[2][3])

            dist_to_bp = pc_utils.calc_distance(mouse_location,sel_opening_world_loc)
            dist_to_z = pc_utils.calc_distance(mouse_location,sel_opening_z_world_loc)

            position = ''
            if dist_to_bp < dist_to_z:
                position = 'BOTTOM'
                self.part.obj_bp.location.z = 0
                self.part.obj_y.location.y = pc_unit.inch(4)
            else:
                position = 'TOP'
                self.part.obj_y.location.y = -pc_unit.inch(4)
                self.part.obj_bp.location.z = opening.obj_z.location.z

            self.part.obj_bp.parent = opening.obj_bp
            self.part.obj_bp.location.x = 0
            self.part.obj_bp.rotation_euler.x = math.radians(90)
            self.part.obj_bp.location.y = opening.obj_y.location.y
            self.part.obj_x.location.x = opening.obj_x.location.x
            return opening, position
        return None, None

    def create_part(self,context):
        path = os.path.join(home_builder_paths.get_assembly_path(),"Part.blend")
        self.part = pc_types.Assembly(filepath=path)
        self.part.obj_z.location.z = pc_unit.inch(.75)
        self.part.add_prompt("Cleat Inset",'DISTANCE',0)

        self.exclude_objects.append(self.part.obj_bp)
        for obj in self.part.obj_bp.children:
            self.exclude_objects.append(obj)

        self.part.set_name("Cleat")
        self.part.obj_bp['IS_CLEAT_BP'] = True
        self.part.obj_bp['IS_CUTPART_BP'] = True
        self.part.obj_bp['PROMPT_ID'] = 'home_builder.closet_cleat_prompts'
        self.set_child_properties(self.part.obj_bp)

    def set_child_properties(self,obj):
        home_builder_utils.update_id_props(obj,self.part.obj_bp)
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

    def confirm_placement(self,context,opening,placement):
        z_loc = self.part.obj_bp.matrix_world[2][3]
        if opening:
            self.part.obj_bp.location.x = opening.obj_bp.location.x
            self.part.obj_bp.location.y = opening.obj_bp.location.y
            self.part.obj_bp.matrix_world[2][3] = z_loc
            self.part.obj_x.location.x = opening.obj_x.location.x
            cleat_inset = self.part.get_prompt('Cleat Inset').get_var('cleat_inset')

            depth_var = opening.obj_y.pyclone.get_var('location.y','depth_var')
            self.part.loc_y('depth_var-cleat_inset',[depth_var,cleat_inset])    

            if placement == 'TOP':
                z_loc_var = opening.obj_z.pyclone.get_var('location.z','z_loc_var')
                self.part.loc_z('z_loc_var',[z_loc_var])
            
            home_builder_utils.copy_drivers(opening.obj_x,self.part.obj_x)
            home_builder_utils.copy_drivers(opening.obj_prompts,self.part.obj_prompts)
            home_builder_pointers.assign_cabinet_shelf_pointers(self.part)
            home_builder_pointers.assign_materials_to_assembly(self.part)

        self.refresh_data(False)

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        #EMPTY MUST BE VISIBLE TO CALCULATE CORRECT SIZE FOR HEIGHT COLLISION
        self.part.obj_z.empty_display_size = .001
        self.part.obj_z.hide_viewport = False

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        ## selected_normal added in to pass this info on from ray cast to position_cabinet
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        ## cursor_z added to allow for multi level placement
        cursor_z = context.scene.cursor.location.z

        opening, placement = self.position_part(selected_point,selected_obj,event,cursor_z,selected_normal)

        if placement_utils.event_is_place_asset(event):
            self.confirm_placement(context,opening,placement)

            return self.finish(context,event.shift)
            
        if placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if placement_utils.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.part.obj_bp)
        return {'CANCELLED'}

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.part.obj_x.hide_viewport = hide
        self.part.obj_y.hide_viewport = hide
        self.part.obj_z.hide_viewport = hide
        self.part.obj_x.empty_display_size = .001
        self.part.obj_y.empty_display_size = .001
        self.part.obj_z.empty_display_size = .001
 
    def delete_reference_object(self):
        for obj in self.part.obj_bp.children:
            if "IS_REFERENCE" in obj:
                pc_utils.delete_object_and_children(obj)

    def finish(self,context,is_recursive):
        context.window.cursor_set('DEFAULT')
        self.set_placed_properties(self.part.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        if is_recursive:
            bpy.ops.home_builder.place_closet_cleat(filepath=self.filepath)
        return {'FINISHED'}


class home_builder_OT_place_closet_back(bpy.types.Operator):
    bl_idname = "home_builder.place_closet_back"
    bl_label = "Place Closet Back"
    bl_options = {'UNDO'}
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    part = None

    exclude_objects = []

    def reset_properties(self):
        self.part = None

    def execute(self, context):
        self.reset_properties()
        self.create_part(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def position_part(self,mouse_location,selected_obj,event,cursor_z,selected_normal):
        if selected_obj is not None:
            self.drop = True
        else:
            self.drop = False

        opening_bp = home_builder_utils.get_opening_bp(selected_obj)

        if opening_bp:
            opening = pc_types.Assembly(opening_bp)
            for child in opening.obj_bp.children:
                if child.type == 'MESH':
                    if child not in self.exclude_objects:
                        child.select_set(True)

            self.part.obj_bp.parent = opening.obj_bp
            self.part.obj_bp.location.x = 0
            self.part.obj_bp.location.y = opening.obj_y.location.y
            self.part.obj_bp.location.z = 0
            self.part.obj_bp.rotation_euler.x = math.radians(-90)
            self.part.obj_bp.rotation_euler.y = math.radians(-90)
            self.part.obj_x.location.x = opening.obj_z.location.z
            self.part.obj_y.location.y = opening.obj_x.location.x
            self.part.obj_z.location.z = -pc_unit.inch(.75)
            return opening

        return None

    def create_part(self,context):
        path = os.path.join(home_builder_paths.get_assembly_path(),"Part.blend")
        self.part = pc_types.Assembly(filepath=path)
        self.part.obj_z.location.z = pc_unit.inch(.75)
        self.part.add_prompt('Back Inset','DISTANCE',value=0)

        self.exclude_objects.append(self.part.obj_bp)
        for obj in self.part.obj_bp.children:
            self.exclude_objects.append(obj)

        self.part.set_name("Back")
        self.part.obj_bp['IS_CLOSET_BACK_BP'] = True
        self.part.obj_bp['IS_CUTPART_BP'] = True
        self.part.obj_bp['PROMPT_ID'] = 'home_builder.closet_back_prompts'
        self.set_child_properties(self.part.obj_bp)

    def set_child_properties(self,obj):
        home_builder_utils.update_id_props(obj,self.part.obj_bp)
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

            height_var = opening.obj_z.pyclone.get_var('location.z','height_var')
            self.part.dim_x('height_var',[height_var])
            
            width_var = opening.obj_x.pyclone.get_var('location.x','width_var')
            self.part.dim_y('width_var',[width_var])            
     
            back_inset = self.part.get_prompt('Back Inset').get_var('back_inset')

            depth_var = opening.obj_y.pyclone.get_var('location.y','depth_var')
            self.part.loc_y('depth_var-back_inset',[depth_var,back_inset])    

            home_builder_utils.copy_drivers(opening.obj_prompts,self.part.obj_prompts)
            home_builder_pointers.assign_cabinet_shelf_pointers(self.part)
            home_builder_pointers.assign_materials_to_assembly(self.part)

        self.refresh_data(False)

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.update()
        #EMPTY MUST BE VISIBLE TO CALCULATE CORRECT SIZE FOR HEIGHT COLLISION
        self.part.obj_z.empty_display_size = .001
        self.part.obj_z.hide_viewport = False

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        ## selected_normal added in to pass this info on from ray cast to position_cabinet
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        ## cursor_z added to allow for multi level placement
        cursor_z = context.scene.cursor.location.z

        opening = self.position_part(selected_point,selected_obj,event,cursor_z,selected_normal)

        if placement_utils.event_is_place_asset(event):
            self.confirm_placement(context,opening)

            return self.finish(context,event.shift)
            
        if placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if placement_utils.event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.part.obj_bp)
        return {'CANCELLED'}

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.part.obj_x.hide_viewport = hide
        self.part.obj_y.hide_viewport = hide
        self.part.obj_z.hide_viewport = hide
        self.part.obj_x.empty_display_size = .001
        self.part.obj_y.empty_display_size = .001
        self.part.obj_z.empty_display_size = .001
 
    def delete_reference_object(self):
        for obj in self.part.obj_bp.children:
            if "IS_REFERENCE" in obj:
                pc_utils.delete_object_and_children(obj)

    def finish(self,context,is_recursive):
        context.window.cursor_set('DEFAULT')
        self.set_placed_properties(self.part.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        if is_recursive:
            bpy.ops.home_builder.place_closet_back(filepath=self.filepath)
        return {'FINISHED'}


class home_builder_OT_place_slanted_shoe_shelf(bpy.types.Operator):
    bl_idname = "home_builder.slanted_shoe_shelf"
    bl_label = "Place Slanted Shoe Shelf"
    bl_options = {'UNDO'}
    
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

        if placement_utils.event_is_place_asset(event):
            self.confirm_placement(context,opening)

            return self.finish(context)
            
        if placement_utils.event_is_cancel_command(event):
            return placement_utils.event_is_cancel_command(context)

        if placement_utils.event_is_pass_through(event):
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
    bl_options = {'UNDO'}
    
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

        if placement_utils.event_is_place_asset(event):
            return self.finish(context,event.shift)
            
        if placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if placement_utils.event_is_pass_through(event):
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
    bl_options = {'UNDO'}
    
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

        if placement_utils.event_is_place_asset(event):
            return self.finish(context,event.shift)
            
        if placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if placement_utils.event_is_pass_through(event):
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
    bl_options = {'UNDO'}
    
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

        if placement_utils.event_is_place_asset(event):
            return self.finish(context,event.shift)
            
        if placement_utils.event_is_cancel_command(event):
            return self.cancel_drop(context)

        if placement_utils.event_is_pass_through(event):
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
    home_builder_OT_place_corner_closet,
    home_builder_OT_place_closet_insert,
    home_builder_OT_place_closet_part,
    home_builder_OT_place_closet_cleat,
    home_builder_OT_place_closet_back,
    home_builder_OT_place_slanted_shoe_shelf,
    home_builder_OT_place_wall_obstacle,
    home_builder_OT_place_bathroom_fixture,
    home_builder_OT_place_decoration,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
