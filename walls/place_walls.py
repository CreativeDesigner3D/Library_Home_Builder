import bpy
import os
import math
import time
import inspect
from ..pc_lib import pc_utils, pc_types, pc_unit
from .. import home_builder_utils
from . import data_walls

class home_builder_OT_draw_multiple_walls(bpy.types.Operator):
    bl_idname = "home_builder.draw_multiple_walls"
    bl_label = "Draw Multiple Walls"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    
    drawing_plane = None

    current_wall = None
    previous_wall = None

    starting_point = ()

    assembly = None
    obj = None
    exclude_objects = []

    class_name = ""

    obj_wall_meshes = []

    def reset_properties(self):
        self.drawing_plane = None
        self.current_wall = None
        self.previous_wall = None
        self.starting_point = ()
        self.assembly = None
        self.obj = None
        self.exclude_objects = []
        self.class_name = ""
        self.obj_wall_meshes = []        

    def execute(self, context):
        self.reset_properties()
        self.get_class_name()
        self.create_drawing_plane(context)
        self.create_wall()
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_class_name(self):
        name, ext = os.path.splitext(os.path.basename(self.filepath))
        self.class_name = name

    def create_wall(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)
        directory, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)        
        wall = None
        for name, obj in inspect.getmembers(data_walls):
            if name == filename:        
                wall = obj()
        if not wall:
            wall = data_walls.Wall()
        wall.draw_wall()
        wall.set_name("Wall")
        home_builder_utils.assign_wall_pointers(wall)
        if self.current_wall:
            self.previous_wall = self.current_wall
        self.current_wall = wall
        self.current_wall.obj_x.location.x = 0
        self.current_wall.obj_y.location.y = props.wall_thickness
        self.current_wall.obj_z.location.z = props.wall_height
        self.set_child_properties(self.current_wall.obj_bp)

    def connect_walls(self):
        constraint_obj = self.previous_wall.obj_x
        constraint = self.current_wall.obj_bp.constraints.new('COPY_LOCATION')
        constraint.target = constraint_obj
        constraint.use_x = True
        constraint.use_y = True
        constraint.use_z = True
        #Used to get connected wall for prompts
        constraint_obj.home_builder.connected_object = self.current_wall.obj_bp

    def set_child_properties(self,obj):
        obj["PROMPT_ID"] = "home_builder.wall_prompts"   
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
            self.obj_wall_meshes.append(obj)
        for child in obj.children:
            self.set_placed_properties(child) 

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        self.position_object(selected_point,selected_obj)
        self.set_end_angles()            

        if self.event_is_place_first_point(event):
            self.starting_point = (selected_point[0],selected_point[1],selected_point[2])
            return {'RUNNING_MODAL'}
            
        if self.event_is_place_next_point(event):
            self.set_placed_properties(self.current_wall.obj_bp)
            self.create_wall()
            self.connect_walls()
            self.starting_point = (selected_point[0],selected_point[1],selected_point[2])
            return {'RUNNING_MODAL'}

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

    def set_end_angles(self):
        if self.previous_wall and self.current_wall:
            left_angle = self.current_wall.get_prompt("Left Angle")
            prev_right_angle = self.previous_wall.get_prompt("Right Angle") 

            prev_rot = round(math.degrees(self.previous_wall.obj_bp.rotation_euler.z),0) 
            rot = round(math.degrees(self.current_wall.obj_bp.rotation_euler.z),0)
            diff = int(math.fabs(rot-prev_rot))
            if diff == 0 or diff == 180:
                left_angle.set_value(0)
                prev_right_angle.set_value(0)
            else:
                left_angle.set_value((rot-prev_rot)/2)
                prev_right_angle.set_value((prev_rot-rot)/2)

            self.current_wall.obj_prompts.location = self.current_wall.obj_prompts.location
            self.previous_wall.obj_prompts.location = self.previous_wall.obj_prompts.location   

    def position_object(self,selected_point,selected_obj):
        if self.starting_point == ():
            self.current_wall.obj_bp.location = selected_point
        else:
            x = selected_point[0] - self.starting_point[0]
            y = selected_point[1] - self.starting_point[1]
            parent_rot = self.current_wall.obj_bp.parent.rotation_euler.z if self.current_wall.obj_bp.parent else 0
            if math.fabs(x) > math.fabs(y):
                if x > 0:
                    self.current_wall.obj_bp.rotation_euler.z = math.radians(0) + parent_rot
                else:
                    self.current_wall.obj_bp.rotation_euler.z = math.radians(180) + parent_rot
                self.current_wall.obj_x.location.x = math.fabs(x)
                
            if math.fabs(y) > math.fabs(x):
                if y > 0:
                    self.current_wall.obj_bp.rotation_euler.z = math.radians(90) + parent_rot
                else:
                    self.current_wall.obj_bp.rotation_euler.z = math.radians(-90) + parent_rot
                self.current_wall.obj_x.location.x = math.fabs(y)

    def hide_empties(self,obj):
        for child in obj.children:
            if child.type == 'EMPTY':
                child.hide_viewport = True

    def cancel_drop(self,context):
        if self.previous_wall:
            prev_right_angle = self.previous_wall.get_prompt("Right Angle") 
            prev_right_angle.set_value(0)

        start_time = time.time()
        for obj in self.obj_wall_meshes:
            home_builder_utils.unwrap_obj(context,obj)
            self.hide_empties(obj.parent)
        print("Wall Unwrap: Draw Time --- %s seconds ---" % (time.time() - start_time))

        obj_list = []
        obj_list.append(self.drawing_plane)
        obj_list.append(self.current_wall.obj_bp)
        for child in self.current_wall.obj_bp.children:
            obj_list.append(child)
        pc_utils.delete_obj_list(obj_list)
        return {'CANCELLED'}

classes = (
    home_builder_OT_draw_multiple_walls,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
