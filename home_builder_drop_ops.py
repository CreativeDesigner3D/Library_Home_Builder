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
from .cabinets import cabinet_library
from .cabinets import data_appliances
from .closets import closet_library

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

def has_height_collision(active_assembly,assembly):
    cab1_z_1 = active_assembly.obj_bp.matrix_world[2][3]
    cab1_z_2 = active_assembly.obj_z.matrix_world[2][3]
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

    def position_cabinet(self,mouse_location,selected_obj,event,cursor_z,selected_normal):

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
            
            if has_height_collision(self.cabinet,self.selected_cabinet):
                ## Allows back of cabinet snapping
                ## only way to get back consistently is through getting parent rotation of the back is always
                ## 1.5707963705062866 very close to 0.5 * pi have chucked back to 5 decimal - that precison scares me :)
                ## So wall parenting for non island bench parenting continues to work properly
                ## have added the total input for the accumulate_z function so only
                ## grabs first parent here (not wall_bp but all for non island setting

                if not wall_bp and int(self.accumulate_z_rotation(selected_obj,0,False)*10000) == 15707:
                    rot += math.radians(180)
                    x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] - math.cos(rot) * self.cabinet.obj_x.location.x
                    y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] - math.sin(rot) * self.cabinet.obj_x.location.x

                elif dist_to_bp < dist_to_x:
                    self.placement = 'LEFT'
                    add_x_loc = 0
                    add_y_loc = 0

                    # if sel_product.obj_bp.mv.placement_type == 'Corner':
                    #     rot += math.radians(90)
                    #     add_x_loc = math.cos(rot) * sel_product.obj_y.location.y
                    #     add_y_loc = math.sin(rot) * sel_product.obj_y.location.y
                    x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] - math.cos(rot) * self.cabinet.obj_x.location.x + add_x_loc
                    y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] - math.sin(rot) * self.cabinet.obj_x.location.x + add_y_loc
                else:
                    self.placement = 'RIGHT'
                    x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] + math.cos(rot) * self.selected_cabinet.obj_x.location.x
                    y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] + math.sin(rot) * self.selected_cabinet.obj_x.location.x
            else:
                x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] - math.cos(rot) * ((self.cabinet.obj_x.location.x/2) - (self.selected_cabinet.obj_x.location.x/2))
                y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] - math.sin(rot) * ((self.cabinet.obj_x.location.x/2) - (self.selected_cabinet.obj_x.location.x/2))                

            self.cabinet.obj_bp.rotation_euler.z = rot
            self.cabinet.obj_bp.location.x = x_loc
            self.cabinet.obj_bp.location.y = y_loc

        elif wall_bp:

            self.placement = 'WALL'
            self.current_wall = pc_types.Assembly(wall_bp)
            self.cabinet.obj_bp.rotation_euler = self.current_wall.obj_bp.rotation_euler
            ## negative vectors aka directly opposing (cabinet and wall)
            ## in this instance quaternion calcs fail and 180 rotation used to handle
            if self.selected_normal.y == 1:
                self.cabinet.obj_bp.rotation_euler.z += math.radians(180)
            self.cabinet.obj_bp.location.x = mouse_location[0]
            self.cabinet.obj_bp.location.y = mouse_location[1]
            self.cabinet.obj_bp.location.z = self.base_height + wall_bp.location.z

        else:

            if event.type == 'LEFT_ARROW' and event.value == 'PRESS':
                self.cabinet.obj_bp.rotation_euler.z -= math.radians(90)
            if event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
                self.cabinet.obj_bp.rotation_euler.z += math.radians(90)   

            self.cabinet.obj_bp.location.x = mouse_location[0]
            self.cabinet.obj_bp.location.y = mouse_location[1]

            ## if selected object is vertical ie wall
            ## or ray cast doesn't hit anything returning Vector(0,0,0) ie selected_object
            ## is None and self.drop is False

            if selected_normal.z == 0:
                if self.drop:
                    self.rotate_to_normal(selected_normal)
                    self.cabinet.obj_bp.rotation_euler.z += self.select_obj_unapplied_rot

            ## else its not a wall object so treat as free standing cabinet, take rotation of floor
            ## could prob also use transform orientation to allow for custom transform orientations
            else:
                self.cabinet.obj_bp.rotation_euler.z = selected_obj.rotation_euler.z

            self.cabinet.obj_bp.location.z = self.base_height + cursor_z

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
        if self.current_wall:
            x_loc = pc_utils.calc_distance((self.cabinet.obj_bp.location.x,self.cabinet.obj_bp.location.y,0),
                                           (self.current_wall.obj_bp.matrix_local[0][3],self.current_wall.obj_bp.matrix_local[1][3],0))

            ## if backside, Vector(0,1,0) this is a negative vector relationship with cabinet Vector(0,-1,0)
            ## quaternion calcs fail with these, 180 rotation is all thats required

            if self.selected_normal.y == 1:
                self.cabinet.obj_bp.rotation_euler = (0, 0,math.radians(180))
                self.cabinet.obj_bp.location = (0, self.current_wall.obj_y.location.y, self.cabinet.obj_bp.location.z - self.current_wall.obj_bp.location.z)
            elif self.selected_cabinet:
                self.cabinet.obj_bp.rotation_euler = self.selected_cabinet.obj_bp.rotation_euler
                self.cabinet.obj_bp.location = (0, self.selected_cabinet.obj_bp.location.y, self.cabinet.obj_bp.location.z - self.current_wall.obj_bp.location.z)
            else:
                self.cabinet.obj_bp.rotation_euler = (0, 0, 0)
                self.cabinet.obj_bp.location = (0, 0, self.cabinet.obj_bp.location.z - self.current_wall.obj_bp.location.z)
            self.cabinet.obj_bp.parent = self.current_wall.obj_bp
            self.cabinet.obj_bp.location.x = x_loc

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

        if event_is_place_asset(event) and self.drop:
            self.confirm_placement(context)

            return self.finish(context)
            
        if event_is_cancel_command(event):
            return self.cancel_drop(context)

        if event_is_pass_through(event):
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.cabinet.obj_bp)
        pc_utils.delete_object_and_children(self.drawing_plane)
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
 
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        self.set_placed_properties(self.cabinet.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        ## keep placing until event_is_cancel_command
        bpy.ops.home_builder.place_cabinet(filepath=self.filepath)
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
            
            if has_height_collision(self.appliance,self.selected_cabinet):
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
        filename, ext = os.path.splitext(file)
        self.appliance = eval("data_appliances." + filename.replace(" ","_") + "()")

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
        context.area.tag_redraw()
        ## keep placing until event_is_cancel_command
        # bpy.ops.home_builder.place_appliance(filepath=self.filepath)
        return {'FINISHED'}


class home_builder_OT_place_closet(bpy.types.Operator):
    bl_idname = "home_builder.place_closet"
    bl_label = "Place Closet"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    cabinet = None
    selected_cabinet = None

    calculators = []

    drawing_plane = None

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

    def position_cabinet(self,mouse_location,selected_obj,event,cursor_z,selected_normal):

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
            
            if self.has_height_collision(self.selected_cabinet):
                ## Allows back of cabinet snapping
                ## only way to get back consistently is through getting parent rotation of the back is always
                ## 1.5707963705062866 very close to 0.5 * pi have chucked back to 5 decimal - that precison scares me :)
                ## So wall parenting for non island bench parenting continues to work properly
                ## have added the total input for the accumulate_z function so only
                ## grabs first parent here (not wall_bp but all for non island setting

                if not wall_bp and int(self.accumulate_z_rotation(selected_obj,0,False)*10000) == 15707:
                    rot += math.radians(180)
                    x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] - math.cos(rot) * self.cabinet.obj_x.location.x
                    y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] - math.sin(rot) * self.cabinet.obj_x.location.x

                elif dist_to_bp < dist_to_x:
                    self.placement = 'LEFT'
                    add_x_loc = 0
                    add_y_loc = 0

                    # if sel_product.obj_bp.mv.placement_type == 'Corner':
                    #     rot += math.radians(90)
                    #     add_x_loc = math.cos(rot) * sel_product.obj_y.location.y
                    #     add_y_loc = math.sin(rot) * sel_product.obj_y.location.y
                    x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] - math.cos(rot) * self.cabinet.obj_x.location.x + add_x_loc
                    y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] - math.sin(rot) * self.cabinet.obj_x.location.x + add_y_loc
                else:
                    self.placement = 'RIGHT'
                    x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] + math.cos(rot) * self.selected_cabinet.obj_x.location.x
                    y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] + math.sin(rot) * self.selected_cabinet.obj_x.location.x
            else:
                x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] - math.cos(rot) * ((self.cabinet.obj_x.location.x/2) - (self.selected_cabinet.obj_x.location.x/2))
                y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] - math.sin(rot) * ((self.cabinet.obj_x.location.x/2) - (self.selected_cabinet.obj_x.location.x/2))                

            self.cabinet.obj_bp.rotation_euler.z = rot
            self.cabinet.obj_bp.location.x = x_loc
            self.cabinet.obj_bp.location.y = y_loc

        elif wall_bp:

            self.placement = 'WALL'
            self.current_wall = pc_types.Assembly(wall_bp)
            self.cabinet.obj_bp.rotation_euler = self.current_wall.obj_bp.rotation_euler
            ## negative vectors aka directly opposing (cabinet and wall)
            ## in this instance quaternion calcs fail and 180 rotation used to handle
            if self.selected_normal.y == 1:
                self.cabinet.obj_bp.rotation_euler.z += math.radians(180)
            self.cabinet.obj_bp.location.x = self.current_wall.obj_bp.matrix_world[0][3]
            self.cabinet.obj_bp.location.y = self.current_wall.obj_bp.matrix_world[1][3]
            self.cabinet.obj_bp.location.z = self.base_height + wall_bp.location.z
            self.cabinet.obj_x.location.x = self.current_wall.obj_x.location.x

            #TODO: Look for return walls and set offsets based on other closets
        else:

            if event.type == 'LEFT_ARROW' and event.value == 'PRESS':
                self.cabinet.obj_bp.rotation_euler.z -= math.radians(90)
            if event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
                self.cabinet.obj_bp.rotation_euler.z += math.radians(90)   

            self.cabinet.obj_bp.location.x = mouse_location[0]
            self.cabinet.obj_bp.location.y = mouse_location[1]

            ## if selected object is vertical ie wall
            ## or ray cast doesn't hit anything returning Vector(0,0,0) ie selected_object
            ## is None and self.drop is False

            if selected_normal.z == 0:
                if self.drop:
                    self.rotate_to_normal(selected_normal)
                    self.cabinet.obj_bp.rotation_euler.z += self.select_obj_unapplied_rot

            ## else its not a wall object so treat as free standing cabinet, take rotation of floor
            ## could prob also use transform orientation to allow for custom transform orientations
            else:
                self.cabinet.obj_bp.rotation_euler.z = selected_obj.rotation_euler.z

            self.cabinet.obj_bp.location.z = self.base_height + cursor_z

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
        if obj.type == 'MESH' and obj.hide_render == False:
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
            x_loc = pc_utils.calc_distance((self.cabinet.obj_bp.location.x,self.cabinet.obj_bp.location.y,0),
                                           (self.current_wall.obj_bp.matrix_local[0][3],self.current_wall.obj_bp.matrix_local[1][3],0))

            ## if backside, Vector(0,1,0) this is a negative vector relationship with cabinet Vector(0,-1,0)
            ## quaternion calcs fail with these, 180 rotation is all thats required

            if self.selected_normal.y == 1:
                self.cabinet.obj_bp.rotation_euler = (0, 0,math.radians(180))
                self.cabinet.obj_bp.location = (0, self.current_wall.obj_y.location.y, self.cabinet.obj_bp.location.z - self.current_wall.obj_bp.location.z)
            elif self.selected_cabinet:
                self.cabinet.obj_bp.rotation_euler = self.selected_cabinet.obj_bp.rotation_euler
                self.cabinet.obj_bp.location = (0, self.selected_cabinet.obj_bp.location.y, self.cabinet.obj_bp.location.z - self.current_wall.obj_bp.location.z)
            else:
                self.cabinet.obj_bp.rotation_euler = (0, 0, 0)
                self.cabinet.obj_bp.location = (0, 0, self.cabinet.obj_bp.location.z - self.current_wall.obj_bp.location.z)
            self.cabinet.obj_bp.parent = self.current_wall.obj_bp
            self.cabinet.obj_bp.location.x = x_loc


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

        if self.event_is_place_first_point(event):
            self.confirm_placement(context)

            return self.finish(context)
            
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
        pc_utils.delete_object_and_children(self.drawing_plane)
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
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        self.set_placed_properties(self.cabinet.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        ## keep placing until event_is_cancel_command
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

            home_builder_utils.copy_drivers(opening.obj_bp,self.cabinet.obj_bp)
            home_builder_utils.copy_drivers(opening.obj_x,self.cabinet.obj_x)
            home_builder_utils.copy_drivers(opening.obj_y,self.cabinet.obj_y)
            home_builder_utils.copy_drivers(opening.obj_z,self.cabinet.obj_z)
            home_builder_utils.copy_drivers(opening.obj_prompts,self.cabinet.obj_prompts)

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

            return self.finish(context)
            
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

    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        self.set_placed_properties(self.cabinet.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        ## keep placing until event_is_cancel_command
        bpy.ops.home_builder.place_closet_insert(filepath=self.filepath)
        return {'FINISHED'}


classes = (
    home_builder_OT_place_cabinet,
    home_builder_OT_place_appliance,
    home_builder_OT_place_closet,
    home_builder_OT_place_closet_insert,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
