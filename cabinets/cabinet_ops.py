import bpy
import os
import math
import inspect
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import cabinet_library
from . import cabinet_utils
from . import data_cabinets
from . import data_cabinet_carcass
from . import data_appliances
from . import data_cabinet_exteriors
from .. import home_builder_utils
from .. import home_builder_paths
from .. import home_builder_enums
from .. import home_builder_pointers
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

def update_range(self,context):
    self.range_changed = True

def update_range_hood(self,context):
    self.range_hood_changed = True

def update_exterior(self,context):
    self.exterior_changed = True

def update_dishwasher(self,context):
    self.dishwasher_changed = True

def update_refrigerator(self,context):
    self.refrigerator_changed = True

def update_sink(self,context):
    self.sink_changed = True

def update_faucet(self,context):
    self.faucet_changed = True

def update_cooktop(self,context):
    self.cooktop_changed = True

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

        wm_props = home_builder_utils.get_wm_props(context.window_manager)
        self.cabinet = wm_props.get_asset(self.filepath)
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


class home_builder_OT_move_cabinet(bpy.types.Operator):
    bl_idname = "home_builder.move_cabinet"
    bl_label = "Move Cabinet"
    
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

    def position_cabinet(self,mouse_location,selected_obj,event):
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
                if dist_to_bp < dist_to_x:
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
            self.cabinet.obj_bp.location.x = mouse_location[0]
            self.cabinet.obj_bp.location.y = mouse_location[1]

        else:

            if event.type == 'LEFT_ARROW' and event.value == 'PRESS':
                self.cabinet.obj_bp.rotation_euler.z -= math.radians(90)
            if event.type == 'RIGHT_ARROW' and event.value == 'PRESS':
                self.cabinet.obj_bp.rotation_euler.z += math.radians(90)   

            self.cabinet.obj_bp.location.x = mouse_location[0]
            self.cabinet.obj_bp.location.y = mouse_location[1]

    def get_cabinet(self,context):
        obj = bpy.data.objects[self.obj_bp_name]
        obj_bp = home_builder_utils.get_cabinet_bp(obj)
        self.cabinet = pc_types.Assembly(obj_bp)
        self.cabinet.obj_bp.constraints.clear()
        self.cabinet.obj_bp.parent = None
        self.set_child_properties(self.cabinet.obj_bp)

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
        if obj.name != self.drawing_plane.name:
            self.exclude_objects.append(obj)            
        if obj.type == 'MESH':
            obj.display_type = 'WIRE'          
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

            self.cabinet.obj_bp.location = (0,0,self.cabinet.obj_bp.location.z)
            self.cabinet.obj_bp.rotation_euler = (0,0,0)
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
        self.refresh_data(False)  

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        context.area.tag_redraw()

        for calculator in self.calculators:
            calculator.calculate()

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.reset_selection()

        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        self.position_cabinet(selected_point,selected_obj,event)

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
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return True
        elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS':
            return True
        elif event.type == 'RET' and event.value == 'PRESS':
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
        return {'FINISHED'}


class home_builder_OT_cabinet_prompts(bpy.types.Operator):
    bl_idname = "home_builder.cabinet_prompts"
    bl_label = "Cabinet Prompts"

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name",default="")

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    product_tabs: bpy.props.EnumProperty(name="Product Tabs",
                                         items=[('MAIN',"Main","Main Options"),
                                                ('CARCASS',"Carcass","Carcass Options"),
                                                ('EXTERIOR',"Exterior","Exterior Options"),
                                                ('INTERIOR',"Interior","Interior Options"),
                                                ('SPLITTER',"Openings","Openings Options")])

    cabinet = None

    sink_changed: bpy.props.BoolProperty(name="Sink Changed",default=False)
    sink_category: bpy.props.EnumProperty(name="Sink Category",
        items=home_builder_enums.enum_sink_categories,
        update=home_builder_enums.update_sink_category)
    sink_name: bpy.props.EnumProperty(name="Sink Name",
        items=home_builder_enums.enum_sink_names,
        update=update_sink)

    faucet_changed: bpy.props.BoolProperty(name="Faucet Changed",default=False)
    faucet_category: bpy.props.EnumProperty(name="Faucet Category",
        items=home_builder_enums.enum_faucet_categories,
        update=home_builder_enums.update_faucet_category)
    faucet_name: bpy.props.EnumProperty(name="Faucet Name",
        items=home_builder_enums.enum_faucet_names,
        update=update_faucet)

    cooktop_changed: bpy.props.BoolProperty(name="Cooktop Changed",default=False)
    cooktop_category: bpy.props.EnumProperty(name="Cooktop Category",
        items=home_builder_enums.enum_cooktop_categories,
        update=home_builder_enums.update_cooktop_category)
    cooktop_name: bpy.props.EnumProperty(name="Cooktop Name",
        items=home_builder_enums.enum_cooktop_names,
        update=update_cooktop)

    range_hood_changed: bpy.props.BoolProperty(name="Range Hood Changed",default=False)
    range_hood_category: bpy.props.EnumProperty(name="Range Hood Category",
        items=home_builder_enums.enum_range_hood_categories,
        update=home_builder_enums.update_range_hood_category)
    range_hood_name: bpy.props.EnumProperty(name="Range Hood Name",
        items=home_builder_enums.enum_range_hood_names,
        update=update_range_hood)

    def reset_variables(self):
        #BLENDER CRASHES IF TAB IS SET TO EXTERIOR
        #THIS IS BECAUSE POPUP DIALOGS CANNOT DISPLAY UILISTS ON INVOKE
        self.product_tabs = 'MAIN'
        self.cabinet = None

    def update_product_size(self):
        if 'IS_MIRROR' in self.cabinet.obj_x and self.cabinet.obj_x['IS_MIRROR']:
            self.cabinet.obj_x.location.x = -self.width
        else:
            self.cabinet.obj_x.location.x = self.width

        if 'IS_MIRROR' in self.cabinet.obj_y and self.cabinet.obj_y['IS_MIRROR']:
            self.cabinet.obj_y.location.y = -self.depth
        else:
            self.cabinet.obj_y.location.y = self.depth
        
        if 'IS_MIRROR' in self.cabinet.obj_z and self.cabinet.obj_z['IS_MIRROR']:
            self.cabinet.obj_z.location.z = -self.height
        else:
            self.cabinet.obj_z.location.z = self.height

    def update_materials(self,context):
        for carcass in self.cabinet.carcasses:
            left_finished_end = carcass.get_prompt("Left Finished End")
            right_finished_end = carcass.get_prompt("Right Finished End")
            finished_back = carcass.get_prompt("Finished Back")
            finished_top = carcass.get_prompt("Finished Top")
            finished_bottom = carcass.get_prompt("Finished Bottom")
            if carcass.design_carcass:
                home_builder_pointers.update_design_carcass_pointers(carcass.design_carcass,
                                                                     left_finished_end.get_value(),
                                                                     right_finished_end.get_value(),
                                                                     finished_back.get_value(),
                                                                     finished_top.get_value(),
                                                                     finished_bottom.get_value())
                home_builder_pointers.update_design_base_assembly_pointers(carcass.design_base_assembly,
                                                                           left_finished_end.get_value(),
                                                                           right_finished_end.get_value(),
                                                                           finished_back.get_value())                                                                     
            else:
                if finished_back and left_finished_end and right_finished_end:
                    home_builder_pointers.update_side_material(carcass.left_side,left_finished_end.get_value(),finished_back.get_value(),finished_top.get_value(),finished_bottom.get_value())
                    home_builder_pointers.update_side_material(carcass.right_side,right_finished_end.get_value(),finished_back.get_value(),finished_top.get_value(),finished_bottom.get_value())
                    home_builder_pointers.update_top_material(carcass.top,finished_back.get_value(),finished_top.get_value())
                    home_builder_pointers.update_bottom_material(carcass.bottom,finished_back.get_value(),finished_bottom.get_value())
                    home_builder_pointers.update_cabinet_back_material(carcass.back,finished_back.get_value())

    def update_fillers(self,context):
        left_adjustment_width = self.cabinet.get_prompt("Left Adjustment Width")
        right_adjustment_width = self.cabinet.get_prompt("Right Adjustment Width")
        if left_adjustment_width.get_value() > 0 and self.cabinet.left_filler is None:
            self.cabinet.add_left_filler()
            home_builder_utils.update_assembly_id_props(self.cabinet.left_filler,self.cabinet)
        if right_adjustment_width.get_value() > 0 and self.cabinet.right_filler is None:
            self.cabinet.add_right_filler()   
            home_builder_utils.update_assembly_id_props(self.cabinet.right_filler,self.cabinet)          
        if left_adjustment_width.get_value() == 0 and self.cabinet.left_filler is not None:
            pc_utils.delete_object_and_children(self.cabinet.left_filler.obj_bp)
            self.cabinet.left_filler = None
        if right_adjustment_width.get_value() == 0 and self.cabinet.right_filler is not None:
            pc_utils.delete_object_and_children(self.cabinet.right_filler.obj_bp)
            self.cabinet.right_filler = None   

    def update_range_hood(self,context):
        if self.range_hood_changed:
            self.range_hood_changed = False
            add_range_hood = self.cabinet.get_prompt("Add Range Hood")
            if self.cabinet.range_hood_appliance:
                pc_utils.delete_object_and_children(self.cabinet.range_hood_appliance.obj_bp)   

            if add_range_hood.get_value():
                self.cabinet.add_range_hood(self.range_hood_category,self.range_hood_name)
                home_builder_utils.hide_empties(self.cabinet.obj_bp)
            context.view_layer.objects.active = self.cabinet.obj_bp
            self.get_assemblies(context)

    def update_sink(self,context):
        if self.sink_changed:
            self.sink_changed = False
            add_sink = self.cabinet.get_prompt("Add Sink")
            if self.cabinet.sink_appliance:
                pc_utils.delete_object_and_children(self.cabinet.sink_appliance.obj_bp)   

            if add_sink.get_value():
                self.cabinet.add_sink(self.sink_category,self.sink_name)
                home_builder_utils.hide_empties(self.cabinet.obj_bp)
            context.view_layer.objects.active = self.cabinet.obj_bp
            self.get_assemblies(context)

    def update_cooktop(self,context):
        if self.cooktop_changed:
            self.cooktop_changed = False
            add_cooktop = self.cabinet.get_prompt("Add Cooktop")
            if self.cabinet.cooktop_appliance:
                pc_utils.delete_object_and_children(self.cabinet.cooktop_appliance.obj_bp)   

            if add_cooktop.get_value():
                self.cabinet.add_cooktop(self.cooktop_category,self.cooktop_name)
                home_builder_utils.hide_empties(self.cabinet.obj_bp)
            context.view_layer.objects.active = self.cabinet.obj_bp
            self.get_assemblies(context)

    def update_faucet(self,context):
        if self.faucet_changed:
            self.faucet_changed = False
            add_faucet = self.cabinet.get_prompt("Add Faucet")
            if self.cabinet.faucet_appliance:
                pc_utils.delete_object_and_children(self.cabinet.faucet_appliance)   

            if add_faucet.get_value():
                self.cabinet.add_faucet(self.faucet_category,self.faucet_name)
                home_builder_utils.hide_empties(self.cabinet.obj_bp)
            context.view_layer.objects.active = self.cabinet.obj_bp
            self.get_assemblies(context)

    def check(self, context):
        self.update_product_size()
        self.update_fillers(context)
        self.update_sink(context)
        self.update_range_hood(context)
        self.update_cooktop(context)
        self.update_faucet(context)        
        self.update_materials(context)
        self.cabinet.update_range_hood_location()
        return True

    def execute(self, context):
        add_faucet = self.cabinet.get_prompt("Add Faucet")
        add_cooktop = self.cabinet.get_prompt("Add Cooktop")
        add_sink = self.cabinet.get_prompt("Add Sink")
        add_range_hood = self.cabinet.get_prompt("Add Range Hood")
        if add_faucet:
            if self.cabinet.faucet_appliance and not add_faucet.get_value():
                pc_utils.delete_object_and_children(self.cabinet.faucet_appliance)   
        if add_cooktop:
            if self.cabinet.cooktop_appliance and not add_cooktop.get_value():
                pc_utils.delete_object_and_children(self.cabinet.cooktop_appliance.obj_bp)   
        if add_sink:
            if self.cabinet.sink_appliance and not add_sink.get_value():
                pc_utils.delete_object_and_children(self.cabinet.sink_appliance.obj_bp)   
        if add_range_hood:
            if self.cabinet.range_hood_appliance and not add_range_hood.get_value():
                pc_utils.delete_object_and_children(self.cabinet.range_hood_appliance.obj_bp)                       
        return {'FINISHED'}

    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)

    def invoke(self,context,event):
        self.reset_variables()
        self.get_assemblies(context)
        self.cabinet_name = self.cabinet.obj_bp.name
        self.depth = math.fabs(self.cabinet.obj_y.location.y)
        self.height = math.fabs(self.cabinet.obj_z.location.z)
        self.width = math.fabs(self.cabinet.obj_x.location.x)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_cabinet_bp(context.object)
        self.cabinet = data_cabinets.Cabinet(bp)

    def draw_sink_prompts(self,layout,context):
        add_sink = self.cabinet.get_prompt("Add Sink")

        if not add_sink:
            return False

        layout.prop(add_sink,'checkbox_value',text="Add Sink")
        if add_sink.get_value():
            layout.prop(self,'sink_category',text="",icon='FILE_FOLDER')  
            if len(self.sink_name) > 0:
                layout.template_icon_view(self,"sink_name",show_labels=True)  

    def draw_faucet_prompts(self,layout,context):
        add_faucet = self.cabinet.get_prompt("Add Faucet")

        if not add_faucet:
            return False

        layout.prop(add_faucet,'checkbox_value',text="Add Faucet")
        if add_faucet.get_value():
            layout.prop(self,'faucet_category',text="",icon='FILE_FOLDER')  
            if len(self.sink_name) > 0:
                layout.template_icon_view(self,"faucet_name",show_labels=True)  

    def draw_cooktop_prompts(self,layout,context):
        add_cooktop = self.cabinet.get_prompt("Add Cooktop")

        if not add_cooktop:
            return False

        layout.prop(add_cooktop,'checkbox_value',text="Add Cooktop")
        if add_cooktop.get_value():
            layout.prop(self,'cooktop_category',text="",icon='FILE_FOLDER')
            layout.template_icon_view(self,"cooktop_name",show_labels=True)

    def draw_range_hood_prompts(self,layout,context):
        add_range_hood = self.cabinet.get_prompt("Add Range Hood")

        if not add_range_hood:
            return False

        layout.prop(add_range_hood,'checkbox_value',text="Add Range Hood")
        if add_range_hood.get_value():
            layout.prop(self,'range_hood_category',text="",icon='FILE_FOLDER')  
            layout.template_icon_view(self,"range_hood_name",show_labels=True)

    def draw_product_size(self,layout,context):
        unit_system = context.scene.unit_settings.system

        box = layout.box()
        row = box.row()
        
        col = row.column(align=True)
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.cabinet.obj_x):
            x = math.fabs(self.cabinet.obj_x.location.x)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',x))
            row1.label(text='Width: ' + value)
        else:
            row1.label(text='Width:')
            row1.prop(self,'width',text="")
            row1.prop(self.cabinet.obj_x,'hide_viewport',text="")
            row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.cabinet.obj_x.name

        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.cabinet.obj_z):
            z = math.fabs(self.cabinet.obj_z.location.z)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))            
            row1.label(text='Height: ' + value)
        else:
            row1.label(text='Height:')
            row1.prop(self,'height',text="")
            row1.prop(self.cabinet.obj_z,'hide_viewport',text="")
            row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.cabinet.obj_z.name
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.cabinet.obj_y):
            y = math.fabs(self.cabinet.obj_y.location.y)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',y))                 
            row1.label(text='Depth: ' + value)
        else:
            row1.label(text='Depth:')
            row1.prop(self,'depth',text="")
            row1.prop(self.cabinet.obj_y,'hide_viewport',text="")
            row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.cabinet.obj_y.name
            
        if len(self.cabinet.obj_bp.constraints) > 0:
            col = row.column(align=True)
            col.label(text="Location:")
            col.operator('home_builder.disconnect_constraint',text='Disconnect Constraint',icon='CONSTRAINT').obj_name = self.cabinet.obj_bp.name
        else:
            col = row.column(align=True)
            col.label(text="Location X:")
            col.label(text="Location Y:")
            col.label(text="Location Z:")
        
            col = row.column(align=True)
            col.prop(self.cabinet.obj_bp,'location',text="")
        
        row = box.row()
        row.label(text='Rotation Z:')
        row.prop(self.cabinet.obj_bp,'rotation_euler',index=2,text="")  

        row = box.row()
        row.label(text='Height from Floor:')
        row.prop(self.cabinet.obj_bp,'location',index=2,text="")          

        props = home_builder_utils.get_scene_props(context.scene)
        row = box.row()
        row.alignment = 'LEFT'
        row.prop(props,'show_cabinet_placement_options',emboss=False,icon='TRIA_DOWN' if props.show_cabinet_tools else 'TRIA_RIGHT')
        if props.show_cabinet_placement_options:
            row = box.row()
            row.label(text="TODO: Implement Cabinet Placement Options")

    def draw_carcass_prompts(self,layout,context):
        for carcass in self.cabinet.carcasses:
            left_finished_end = carcass.get_prompt("Left Finished End")
            right_finished_end = carcass.get_prompt("Right Finished End")
            finished_back = carcass.get_prompt("Finished Back")
            finished_top = carcass.get_prompt("Finished Top")
            finished_bottom = carcass.get_prompt("Finished Bottom")
            toe_kick_height = carcass.get_prompt("Toe Kick Height")
            toe_kick_setback = carcass.get_prompt("Toe Kick Setback")
            # add_bottom_light = carcass.get_prompt("Add Bottom Light")
            # add_top_light = carcass.get_prompt("Add Top Light")
            # add_side_light = carcass.get_prompt("Add Side Light")
  
            col = layout.column(align=True)
            box = col.box()
            row = box.row()
            row.label(text="Carcass - " + carcass.obj_bp.name)

            if toe_kick_height and toe_kick_setback:
                row = box.row()
                row.label(text="Base Assembly:")   
                row.prop(toe_kick_height,'distance_value',text="Height")
                row.prop(toe_kick_setback,'distance_value',text="Setback")   

            if left_finished_end and right_finished_end and finished_back and finished_top and finished_bottom:
                row = box.row()
                row.label(text="Finish:")
                row.prop(left_finished_end,'checkbox_value',text="Left")
                row.prop(right_finished_end,'checkbox_value',text="Right")
                row.prop(finished_top,'checkbox_value',text="Top")
                row.prop(finished_bottom,'checkbox_value',text="Bottom")
                row.prop(finished_back,'checkbox_value',text="Back")

            # if add_bottom_light and add_top_light and add_side_light:
            #     row = box.row()
            #     row.label(text="Cabinet Lighting:")   
            #     row.prop(add_bottom_light,'checkbox_value',text="Bottom")
            #     row.prop(add_top_light,'checkbox_value',text="Top")
            #     row.prop(add_side_light,'checkbox_value',text="Side")  

    def draw_cabinet_prompts(self,layout,context):
        bottom_cabinet_height = self.cabinet.get_prompt("Bottom Cabinet Height")    
        left_adjustment_width = self.cabinet.get_prompt("Left Adjustment Width")       
        right_adjustment_width = self.cabinet.get_prompt("Right Adjustment Width")    
        add_sink = self.cabinet.get_prompt("Add Sink")
        add_faucet = self.cabinet.get_prompt("Add Faucet")
        add_cooktop = self.cabinet.get_prompt("Add Cooktop")
        add_range_hood = self.cabinet.get_prompt("Add Range Hood")        
        ctop_front = self.cabinet.get_prompt("Countertop Overhang Front")
        ctop_back = self.cabinet.get_prompt("Countertop Overhang Back")
        ctop_left = self.cabinet.get_prompt("Countertop Overhang Left")
        ctop_right = self.cabinet.get_prompt("Countertop Overhang Right")
        ctop_left = self.cabinet.get_prompt("Countertop Overhang Left")   

        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.label(text="Cabinet Options - " + self.cabinet.obj_bp.name)

        if bottom_cabinet_height:
            row = box.row()
            row.label(text="Bottom Cabinet Height:")
            row.prop(bottom_cabinet_height,'distance_value',text="")           
   
        if left_adjustment_width and right_adjustment_width:
            row = box.row()
            row.label(text="Filler Amount:")
            row.prop(left_adjustment_width,'distance_value',text="Left")
            row.prop(right_adjustment_width,'distance_value',text="Right")

        if ctop_front and ctop_back and ctop_left and ctop_right:
            row = box.row()
            row.label(text="Top Overhang:")       
            row.prop(ctop_front,'distance_value',text="Front")      
            row.prop(ctop_back,'distance_value',text="Rear")  
            row.prop(ctop_left,'distance_value',text="Left")  
            row.prop(ctop_right,'distance_value',text="Right")    

        if add_sink and add_faucet:
            box = layout.box()
            box.label(text="Cabinet Sink Selection")
            split = box.split()
            self.draw_sink_prompts(split.column(),context)
            self.draw_faucet_prompts(split.column(),context)

        if add_cooktop and add_range_hood:
            box = layout.box()
            box.label(text="Cabinet Cooktop Selection")
            split = box.split()
            self.draw_cooktop_prompts(split.column(),context)
            self.draw_range_hood_prompts(split.column(),context)

    def draw(self, context):
        layout = self.layout
        info_box = layout.box()
        
        obj_props = home_builder_utils.get_object_props(self.cabinet.obj_bp)
        scene_props = home_builder_utils.get_scene_props(context.scene)

        mat_group = scene_props.material_pointer_groups[obj_props.material_group_index]
        
        row = info_box.row(align=True)
        row.prop(self.cabinet.obj_bp,'name',text="Name")
        row.separator()
        row.menu('HOME_BUILDER_MT_change_product_material_group',text=mat_group.name,icon='COLOR')
        row.operator('home_builder.update_product_material_group',text="",icon='FILE_REFRESH').object_name = self.cabinet.obj_bp.name

        self.draw_product_size(layout,context)

        prompt_box = layout.box()

        row = prompt_box.row(align=True)
        row.prop_enum(self, "product_tabs", 'MAIN') 
        row.prop_enum(self, "product_tabs", 'CARCASS') 
        row.prop_enum(self, "product_tabs", 'EXTERIOR') 
        row.prop_enum(self, "product_tabs", 'INTERIOR') 

        if self.product_tabs == 'MAIN':
            self.draw_cabinet_prompts(prompt_box,context)   
        
        if self.product_tabs == 'CARCASS':
            self.draw_carcass_prompts(prompt_box,context)

        if self.product_tabs == 'EXTERIOR':
            for carcass in reversed(self.cabinet.carcasses):
                if carcass.exterior:
                    box = prompt_box.box()
                    box.label(text=carcass.exterior.obj_bp.name)
                    carcass.exterior.draw_prompts(box,context)

        if self.product_tabs == 'INTERIOR':
            for carcass in reversed(self.cabinet.carcasses):
                if carcass.interior:
                    box = prompt_box.box()
                    box.label(text=carcass.interior.obj_bp.name)
                    carcass.interior.draw_prompts(box,context)


class home_builder_OT_change_cabinet_exterior(bpy.types.Operator):
    bl_idname = "home_builder.change_cabinet_exterior"
    bl_label = "Change Cabinet Exterior"

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name",default="")

    exterior: bpy.props.EnumProperty(name="Exterior",
                                     items=data_cabinet_exteriors.exterior_selection,
                                    update=update_exterior)

    exterior_changed: bpy.props.BoolProperty(name="Exterior Changed")

    selected_exteriors = []

    def check(self, context):
        if self.exterior_changed:
            new_exteriors = []
            if self.exterior != 'SELECT_EXTERIOR':
                for exterior in self.selected_exteriors:
                    if self.exterior != 'OPEN':
                        carcass_bp = home_builder_utils.get_carcass_bp(exterior)
                        carcass = data_cabinet_carcass.Carcass(carcass_bp)
                        new_exterior = data_cabinet_exteriors.get_class_from_name(self.exterior)
                        carcass.add_insert(new_exterior)
                        home_builder_utils.update_object_and_children_id_props(new_exterior.obj_bp,carcass.obj_bp)
                        new_exterior.update_calculators()
                        new_exteriors.append(new_exterior.obj_bp)
                    pc_utils.delete_object_and_children(exterior)        

                self.selected_exteriors = []
                for exterior in new_exteriors:
                    self.selected_exteriors.append(exterior)
                    home_builder_utils.hide_empties(exterior)                    
                self.exterior_changed = False

        return True

    def execute(self, context):
        return {'FINISHED'}

    def get_assemblies(self,context):
        pass

    def get_selected_exteriors(self,context):
        self.selected_exteriors = []
        for obj in context.selected_objects:
            bp = home_builder_utils.get_exterior_bp(obj)
            if bp not in self.selected_exteriors:
                self.selected_exteriors.append(bp)

    def invoke(self,context,event):
        self.exterior = 'SELECT_EXTERIOR'
        self.get_selected_exteriors(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'exterior')
        box = layout.box()
        box.label(text="Selected Exteriors:")
        col = box.column(align=True)
        for bp in self.selected_exteriors:
            col.label(text=bp.name)          


class Appliance_Prompts(bpy.types.Operator):

    def update_product_size(self,assembly):
        if 'IS_MIRROR' in assembly.obj_x and assembly.obj_x['IS_MIRROR']:
            assembly.obj_x.location.x = -self.width
        else:
            assembly.obj_x.location.x = self.width

        if 'IS_MIRROR' in assembly.obj_y and assembly.obj_y['IS_MIRROR']:
            assembly.obj_y.location.y = -self.depth
        else:
            assembly.obj_y.location.y = self.depth
        
        if 'IS_MIRROR' in assembly.obj_z and assembly.obj_z['IS_MIRROR']:
            assembly.obj_z.location.z = -self.height
        else:
            assembly.obj_z.location.z = self.height

    def draw_product_size(self,assembly,layout,context):
        unit_system = context.scene.unit_settings.system

        box = layout.box()
        row = box.row()
        
        col = row.column(align=True)
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(assembly.obj_x) or assembly.obj_x.lock_location[0]:
            x = math.fabs(assembly.obj_x.location.x)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',x))
            row1.label(text='Width: ' + value)
        else:
            row1.label(text='Width:')
            row1.prop(self,'width',text="")
            row1.prop(assembly.obj_x,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(assembly.obj_z) or assembly.obj_z.lock_location[2]:
            z = math.fabs(assembly.obj_z.location.z)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))            
            row1.label(text='Height: ' + value)
        else:
            row1.label(text='Height:')
            row1.prop(self,'height',text="")
            row1.prop(assembly.obj_z,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(assembly.obj_y) or assembly.obj_y.lock_location[1]:
            y = math.fabs(assembly.obj_y.location.y)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',y))                 
            row1.label(text='Depth: ' + value)
        else:
            row1.label(text='Depth:')
            row1.prop(self,'depth',text="")
            row1.prop(assembly.obj_y,'hide_viewport',text="")
            
        if len(assembly.obj_bp.constraints) > 0:
            col = row.column(align=True)
            col.label(text="Location:")
            col.operator('home_builder.disconnect_constraint',text='Disconnect Constraint',icon='CONSTRAINT').obj_name = assembly.obj_bp.name
        else:
            col = row.column(align=True)
            col.label(text="Location X:")
            col.label(text="Location Y:")
            col.label(text="Location Z:")
        
            col = row.column(align=True)
            col.prop(assembly.obj_bp,'location',text="")
        
        row = box.row()
        row.label(text='Rotation Z:')
        row.prop(assembly.obj_bp,'rotation_euler',index=2,text="")  




class home_builder_OT_range_prompts(Appliance_Prompts):
    bl_idname = "home_builder.range_prompts"
    bl_label = "Range Prompts"

    appliance_bp_name: bpy.props.StringProperty(name="Appliance BP Name",default="")
    add_range_hood: bpy.props.BoolProperty(name="Add Range Hood",default=False)
    range_changed: bpy.props.BoolProperty(name="Range Changed",default=False)
    range_hood_changed: bpy.props.BoolProperty(name="Range Changed",default=False)

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    range_category: bpy.props.EnumProperty(name="Range Category",
        items=home_builder_enums.enum_range_categories,
        update=home_builder_enums.update_range_category)
    range_name: bpy.props.EnumProperty(name="Range Name",
        items=home_builder_enums.enum_range_names,
        update=update_range)

    range_hood_category: bpy.props.EnumProperty(name="Range Hood Category",
        items=home_builder_enums.enum_range_hood_categories,
        update=home_builder_enums.update_range_hood_category)
    range_hood_name: bpy.props.EnumProperty(name="Range Hood Name",
        items=home_builder_enums.enum_range_hood_names,
        update=update_range_hood)

    product = None

    def reset_variables(self,context):
        self.product = None
        home_builder_enums.update_range_category(self,context)
        home_builder_enums.update_range_hood_category(self,context)

    def check(self, context):
        self.update_product_size(self.product)
        self.update_range(context)
        self.update_range_hood(context)
        self.product.update_range_hood_location()
        return True

    def update_range(self,context):
        if self.range_changed:
            self.range_changed = False

            if self.product.range_appliance:
                pc_utils.delete_object_and_children(self.product.range_appliance.obj_bp)                

            self.product.add_range(self.range_category,self.range_name)
            self.width = self.product.range_appliance.obj_x.location.x
            self.depth = math.fabs(self.product.range_appliance.obj_y.location.y)
            self.height = self.product.range_appliance.obj_z.location.z
            context.view_layer.objects.active = self.product.obj_bp
            home_builder_utils.hide_empties(self.product.obj_bp)
            self.get_assemblies(context)

    def update_range_hood(self,context):
        if self.range_hood_changed:
            self.range_hood_changed = False
            add_range_hood = self.product.get_prompt("Add Range Hood")
            add_range_hood.set_value(self.add_range_hood)
            if self.product.range_hood_appliance:
                pc_utils.delete_object_and_children(self.product.range_hood_appliance.obj_bp)   

            if self.add_range_hood:
                self.product.add_range_hood(self.range_hood_category,self.range_hood_name)
                home_builder_utils.hide_empties(self.product.obj_bp)
            context.view_layer.objects.active = self.product.obj_bp
            self.get_assemblies(context)

    def execute(self, context):
        return {'FINISHED'}

    def get_assemblies(self,context):
        bp = home_builder_utils.get_appliance_bp(context.object)
        self.product = data_appliances.Range(bp)

    def invoke(self,context,event):
        self.reset_variables(context)
        self.get_assemblies(context)
        add_range_hood = self.product.get_prompt("Add Range Hood")
        self.add_range_hood = add_range_hood.get_value()        
        self.depth = math.fabs(self.product.obj_y.location.y)
        self.height = math.fabs(self.product.obj_z.location.z)
        self.width = math.fabs(self.product.obj_x.location.x)        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def draw_range_prompts(self,layout,context):
        layout.label(text="")
        box = layout.box()
        box.prop(self,'range_category',text="",icon='FILE_FOLDER')  
        box.template_icon_view(self,"range_name",show_labels=True)  

    def draw_range_hood_prompts(self,layout,context):
        layout.prop(self,'add_range_hood',text="Add Range Hood")
        
        if not self.add_range_hood:
            return False
        else:
            box = layout.box()
            box.prop(self,'range_hood_category',text="",icon='FILE_FOLDER')  
            box.template_icon_view(self,"range_hood_name",show_labels=True)  

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(self.product,layout,context)
        split = layout.split()
        self.draw_range_prompts(split.column(),context)
        self.draw_range_hood_prompts(split.column(),context)


class home_builder_OT_dishwasher_prompts(Appliance_Prompts):
    bl_idname = "home_builder.dishwasher_prompts"
    bl_label = "Dishwasher Prompts"

    appliance_bp_name: bpy.props.StringProperty(name="Appliance BP Name",default="")
    dishwasher_changed: bpy.props.BoolProperty(name="Range Changed",default=False)

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    dishwasher_category: bpy.props.EnumProperty(name="Dishwasher Category",
        items=home_builder_enums.enum_dishwasher_categories,
        update=home_builder_enums.update_dishwasher_category)
    dishwasher_name: bpy.props.EnumProperty(name="Dishwasher Name",
        items=home_builder_enums.enum_dishwasher_names,
        update=update_dishwasher)

    product = None

    def reset_variables(self,context):
        self.product = None
        home_builder_enums.update_dishwasher_category(self,context)

    def check(self, context):
        self.update_product_size(self.product)
        self.update_dishwasher(context)
        return True

    def update_dishwasher(self,context):
        if self.dishwasher_changed:
            self.dishwasher_changed = False

            if self.product:
                pc_utils.delete_object_and_children(self.product.dishwasher.obj_bp)                

            self.product.add_dishwasher(self.dishwasher_category,self.dishwasher_name)
            self.width = self.product.obj_x.location.x
            self.depth = math.fabs(self.product.obj_y.location.y)
            self.height = self.product.obj_z.location.z
            context.view_layer.objects.active = self.product.obj_bp
            home_builder_utils.hide_empties(self.product.obj_bp)
            self.get_assemblies(context)

    def execute(self, context):
        return {'FINISHED'}

    def get_assemblies(self,context):
        bp = home_builder_utils.get_appliance_bp(context.object)
        self.product = data_appliances.Dishwasher(bp)

    def invoke(self,context,event):
        self.reset_variables(context)
        self.get_assemblies(context)
     
        self.depth = math.fabs(self.product.obj_y.location.y)
        self.height = math.fabs(self.product.obj_z.location.z)
        self.width = math.fabs(self.product.obj_x.location.x)        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def draw_dishwasher_prompts(self,layout,context):
        layout.label(text="")
        box = layout.box()
        box.prop(self,'dishwasher_category',text="",icon='FILE_FOLDER')  
        box.template_icon_view(self,"dishwasher_name",show_labels=True)  

    def draw_countertop_prompts(self,layout,context):
        ctop_front = self.product.get_prompt("Countertop Overhang Front")
        ctop_back = self.product.get_prompt("Countertop Overhang Back")
        ctop_left = self.product.get_prompt("Countertop Overhang Left")
        ctop_right = self.product.get_prompt("Countertop Overhang Right")
        ctop_left = self.product.get_prompt("Countertop Overhang Left")   

        col = layout.column(align=True)
        box = col.box()      
   
        # if left_adjustment_width and right_adjustment_width:
        #     row = box.row()
        #     row.label(text="Filler Amount:")
        #     row.prop(left_adjustment_width,'distance_value',text="Left")
        #     row.prop(right_adjustment_width,'distance_value',text="Right")

        if ctop_front and ctop_back and ctop_left and ctop_right:
            row = box.row()
            row.label(text="Countertop Overhang:")     
            row = box.row()  
            row.prop(ctop_front,'distance_value',text="Front")      
            row.prop(ctop_back,'distance_value',text="Rear")  
            row.prop(ctop_left,'distance_value',text="Left")  
            row.prop(ctop_right,'distance_value',text="Right")            

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(self.product,layout,context)
        self.draw_countertop_prompts(layout,context)
        split = layout.split()
        self.draw_dishwasher_prompts(split.column(),context)


class home_builder_OT_refrigerator_prompts(Appliance_Prompts):
    bl_idname = "home_builder.refrigerator_prompts"
    bl_label = "Refrigerator Prompts"

    appliance_bp_name: bpy.props.StringProperty(name="Appliance BP Name",default="")
    refrigerator_changed: bpy.props.BoolProperty(name="Refrigerator Changed",default=False)

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    refrigerator_category: bpy.props.EnumProperty(name="Refrigerator Category",
        items=home_builder_enums.enum_refrigerator_categories,
        update=home_builder_enums.update_refrigerator_category)
    refrigerator_name: bpy.props.EnumProperty(name="Refrigerator Name",
        items=home_builder_enums.enum_refrigerator_names,
        update=update_refrigerator)

    product = None

    def reset_variables(self,context):
        self.product = None
        home_builder_enums.update_refrigerator_category(self,context)

    def check(self, context):
        self.update_product_size(self.product)
        self.update_refrigerator(context)
        return True

    def update_refrigerator(self,context):
        if self.refrigerator_changed:
            self.refrigerator_changed = False

            if self.product:
                pc_utils.delete_object_and_children(self.product.refrigerator.obj_bp)                

            self.product.add_refrigerator(self.refrigerator_category,self.refrigerator_name)
            self.width = self.product.obj_x.location.x
            self.depth = math.fabs(self.product.obj_y.location.y)
            self.height = self.product.obj_z.location.z
            context.view_layer.objects.active = self.product.obj_bp
            home_builder_utils.hide_empties(self.product.obj_bp)
            self.get_assemblies(context)

    def execute(self, context):
        return {'FINISHED'}

    def get_assemblies(self,context):
        bp = home_builder_utils.get_appliance_bp(context.object)
        self.product = data_appliances.Refrigerator(bp)

    def invoke(self,context,event):
        self.reset_variables(context)
        self.get_assemblies(context)
     
        self.depth = math.fabs(self.product.obj_y.location.y)
        self.height = math.fabs(self.product.obj_z.location.z)
        self.width = math.fabs(self.product.obj_x.location.x)        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def draw_refrigerator_selection(self,layout,context):
        box = layout.box()
        box.prop(self,'refrigerator_category',text="",icon='FILE_FOLDER')  
        box.template_icon_view(self,"refrigerator_name",show_labels=True)          

    def draw_refrigerator_prompts(self,layout,context):
        box = layout.box()
        y_loc = self.product.get_prompt("Refrigerator Y Location")
        y_loc.draw(box,allow_edit=False)

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(self.product,layout,context)
        self.draw_refrigerator_prompts(layout,context)
        self.draw_refrigerator_selection(layout,context)


class HOMEBUILDER_MT_cabinet_menu(bpy.types.Menu):
    bl_label = "Cabinet Commands"

    def draw(self, context):
        layout = self.layout
        obj_bp = pc_utils.get_assembly_bp(context.object)
        cabinet_bp = home_builder_utils.get_cabinet_bp(context.object)
        appliance_bp = home_builder_utils.get_appliance_bp(context.object)
        exterior_bp = home_builder_utils.get_exterior_bp(context.object)

        layout.operator_context = 'INVOKE_DEFAULT'

        if cabinet_bp:
            layout.operator('home_builder.move_cabinet',text="Move Cabinet - " + cabinet_bp.name,icon='OBJECT_ORIGIN').obj_bp_name = cabinet_bp.name
            layout.operator('home_builder.free_move_cabinet',text="Grab Cabinet - " + cabinet_bp.name,icon='VIEW_PAN').obj_bp_name = cabinet_bp.name
            layout.operator('home_builder.duplicate_cabinet',text="Duplicate Cabinet - " + cabinet_bp.name,icon='DUPLICATE').obj_bp_name = cabinet_bp.name
            layout.separator()
            
        if exterior_bp:
            layout.operator('home_builder.change_cabinet_exterior',text="Change Cabinet Exterior",icon='FILE_REFRESH')
            layout.separator()

        layout.operator('home_builder.part_prompts',text="Part Prompts - " + obj_bp.name,icon='WINDOW')
        layout.operator('home_builder.edit_part',icon='EDITMODE_HLT')
        layout.separator()
        layout.operator('home_builder.delete_assembly',text="Delete Cabinet",icon='X').obj_name = cabinet_bp.name


class home_builder_OT_delete_cabinet(bpy.types.Operator):
    bl_idname = "home_builder.delete_cabinet"
    bl_label = "Delete Cabinet"

    def execute(self, context):
        obj_bp = home_builder_utils.get_cabinet_bp(context.object)
        pc_utils.delete_object_and_children(obj_bp)
        return {'FINISHED'}


class home_builder_OT_delete_part(bpy.types.Operator):
    bl_idname = "home_builder.delete_part"
    bl_label = "Delete Cabinet"

    def execute(self, context):
        obj_bp = pc_utils.get_assembly_bp(context.object)
        pc_utils.delete_object_and_children(obj_bp)
        return {'FINISHED'}


class home_builder_OT_part_prompts(bpy.types.Operator):
    bl_idname = "home_builder.part_prompts"
    bl_label = "Delete Cabinet"

    assembly = None

    def invoke(self,context,event):
        bp = pc_utils.get_assembly_bp(context.object)
        self.assembly = pc_types.Assembly(bp)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        self.assembly.obj_prompts.pyclone.draw_prompts(box)

    def execute(self, context):
        return {'FINISHED'}


class home_builder_OT_update_prompts(bpy.types.Operator):
    bl_idname = "home_builder.update_prompts"
    bl_label = "Update Prompts"

    def execute(self, context):
        return {'FINISHED'}


class home_builder_OT_edit_part(bpy.types.Operator):
    bl_idname = "home_builder.edit_part"
    bl_label = "Edit Part"

    def execute(self, context):
        obj_bps = []
        for obj in context.selected_objects:
            obj_bp = pc_utils.get_assembly_bp(obj)
            if obj_bp is not None and obj_bp not in obj_bps:
                obj_bps.append(obj_bp)

        for obj_bp in obj_bps:
            for child in obj_bp.children:
                if child.type == 'MESH':
                    home_builder_utils.apply_hook_modifiers(context,child)

        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}


class home_builder_OT_update_cabinet_lighting(bpy.types.Operator):
    bl_idname = "home_builder.update_cabinet_lighting"
    bl_label = "Update Cabinet Lighting"

    def execute(self, context):
        scene_props = home_builder_utils.get_scene_props(context.scene)
        carcass_bp_list = []
        for obj in context.visible_objects:
            bp = home_builder_utils.get_carcass_bp(obj)
            if bp and bp not in carcass_bp_list:
                carcass_bp_list.append(bp)
        
        for carcass_bp in carcass_bp_list:
            carcass = pc_types.Assembly(carcass_bp)
            add_top_lighting = carcass.get_prompt("Add Top Light")
            add_side_lighting = carcass.get_prompt("Add Side Light")
            add_bottom_lighting = carcass.get_prompt("Add Bottom Light")

            if add_bottom_lighting:
                add_bottom_lighting.set_value(scene_props.add_toe_kick_lighting)
            if add_side_lighting:
                add_side_lighting.set_value(scene_props.add_side_inside_lighting)
            if add_top_lighting:
                add_top_lighting.set_value(scene_props.add_top_inside_lighting)

        return {'FINISHED'}


class home_builder_OT_duplicate_cabinet(bpy.types.Operator):
    bl_idname = "home_builder.duplicate_cabinet"
    bl_label = "Duplicate Cabinet"

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    @classmethod
    def poll(cls, context):
        obj_bp = home_builder_utils.get_cabinet_bp(context.object)
        if obj_bp:
            return True
        else:
            return False

    def select_obj_and_children(self,obj):
        obj.hide_viewport = False
        obj.select_set(True)
        for child in obj.children:
            obj.hide_viewport = False
            child.select_set(True)
            self.select_obj_and_children(child)

    def hide_empties_and_boolean_meshes(self,obj):
        if obj.type == 'EMPTY' or obj.hide_render:
            obj.hide_viewport = True
        for child in obj.children:
            self.hide_empties_and_boolean_meshes(child)

    def execute(self, context):
        obj = context.object
        obj_bp = home_builder_utils.get_cabinet_bp(obj)
        cabinet = pc_types.Assembly(obj_bp)
        bpy.ops.object.select_all(action='DESELECT')
        self.select_obj_and_children(cabinet.obj_bp)
        bpy.ops.object.duplicate_move()
        self.hide_empties_and_boolean_meshes(cabinet.obj_bp)

        obj = context.object
        new_obj_bp = home_builder_utils.get_cabinet_bp(obj)
        new_cabinet = pc_types.Assembly(new_obj_bp)
        self.hide_empties_and_boolean_meshes(new_cabinet.obj_bp)

        bpy.ops.home_builder.move_cabinet(obj_bp_name=new_cabinet.obj_bp.name)

        return {'FINISHED'}


class home_builder_OT_free_move_cabinet(bpy.types.Operator):
    bl_idname = "home_builder.free_move_cabinet"
    bl_label = "Free Move Cabinet"

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    @classmethod
    def poll(cls, context):
        obj_bp = home_builder_utils.get_cabinet_bp(context.object)
        if obj_bp:
            return True
        else:
            return False

    def execute(self, context):
        obj = context.object
        obj_bp = home_builder_utils.get_cabinet_bp(obj)
        cabinet = pc_types.Assembly(obj_bp)
        bpy.ops.object.select_all(action='DESELECT')

        cabinet.obj_bp.hide_viewport = False
        cabinet.obj_bp.select_set(True)

        region = context.region
        co = location_3d_to_region_2d(region,context.region_data,cabinet.obj_bp.matrix_world.translation)
        region_offset = Vector((region.x,region.y))
        context.window.cursor_warp(*(co + region_offset))
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(home_builder_OT_place_cabinet)  
    bpy.utils.register_class(home_builder_OT_cabinet_prompts)  
    bpy.utils.register_class(home_builder_OT_change_cabinet_exterior)  
    bpy.utils.register_class(home_builder_OT_range_prompts)  
    bpy.utils.register_class(home_builder_OT_dishwasher_prompts)  
    bpy.utils.register_class(home_builder_OT_refrigerator_prompts)  
    bpy.utils.register_class(HOMEBUILDER_MT_cabinet_menu)     
    bpy.utils.register_class(home_builder_OT_delete_cabinet)    
    bpy.utils.register_class(home_builder_OT_delete_part)    
    bpy.utils.register_class(home_builder_OT_part_prompts)    
    bpy.utils.register_class(home_builder_OT_edit_part)  
    bpy.utils.register_class(home_builder_OT_update_cabinet_lighting)  
    bpy.utils.register_class(home_builder_OT_update_prompts)  
    bpy.utils.register_class(home_builder_OT_move_cabinet)  
    bpy.utils.register_class(home_builder_OT_duplicate_cabinet)  
    bpy.utils.register_class(home_builder_OT_free_move_cabinet)


def unregister():
    bpy.utils.unregister_class(home_builder_OT_place_cabinet)
    bpy.utils.unregister_class(home_builder_OT_cabinet_prompts)
    bpy.utils.unregister_class(home_builder_OT_change_cabinet_exterior)
    bpy.utils.unregister_class(home_builder_OT_range_prompts)
    bpy.utils.unregister_class(home_builder_OT_dishwasher_prompts)
    bpy.utils.unregister_class(home_builder_OT_refrigerator_prompts)
    bpy.utils.unregister_class(HOMEBUILDER_MT_cabinet_menu)
    bpy.utils.unregister_class(home_builder_OT_delete_cabinet)
    bpy.utils.unregister_class(home_builder_OT_delete_part)
    bpy.utils.unregister_class(home_builder_OT_part_prompts)
    bpy.utils.unregister_class(home_builder_OT_edit_part)
    bpy.utils.unregister_class(home_builder_OT_update_cabinet_lighting)
    bpy.utils.unregister_class(home_builder_OT_update_prompts)
    bpy.utils.unregister_class(home_builder_OT_move_cabinet)
    bpy.utils.unregister_class(home_builder_OT_duplicate_cabinet)
    bpy.utils.unregister_class(home_builder_OT_free_move_cabinet)
