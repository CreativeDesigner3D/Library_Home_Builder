import bpy
import os
import math
import time
import inspect
from ..pc_lib import pc_utils, pc_types, pc_unit
from .. import home_builder_utils
from .. import home_builder_pointers
from . import wall_library

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
        for name, obj in inspect.getmembers(wall_library):
            if name == filename.replace(" ","_"):        
                wall = obj()
        if not wall:
            wall = wall_library.Wall()
        wall.draw_wall()
        wall.set_name("Wall")
        home_builder_pointers.assign_pointer_to_assembly(wall,"Walls")
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
        home_builder_utils.get_object_props(constraint_obj).connected_object = self.current_wall.obj_bp

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
            if not obj.hide_viewport:
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


class home_builder_OT_wall_prompts(bpy.types.Operator):
    bl_idname = "home_builder.wall_prompts"
    bl_label = "Wall Prompts"

    current_wall = None
    previous_wall = None
    next_wall = None

    def execute(self, context):
        return {'FINISHED'}

    def check(self, context):
        prev_rot = 0
        next_rot = 0
        left_angle = self.current_wall.get_prompt("Left Angle")
        right_angle = self.current_wall.get_prompt("Right Angle")    
        rot = math.degrees(self.current_wall.obj_bp.rotation_euler.z)

        if self.previous_wall:
            prev_left_angle = self.previous_wall.get_prompt("Left Angle")
            prev_right_angle = self.previous_wall.get_prompt("Right Angle") 
            prev_rot = math.degrees(self.previous_wall.obj_bp.rotation_euler.z)  

        if self.next_wall:
            next_left_angle = self.next_wall.get_prompt("Left Angle")
            next_rot = math.degrees(self.next_wall.obj_bp.rotation_euler.z)  

        if self.next_wall:
            right_angle.set_value((rot-next_rot)/2)
            next_left_angle.set_value((next_rot-rot)/2)

        if self.previous_wall:
            prev_right_angle.set_value((prev_rot-rot)/2)
            left_angle.set_value((rot-prev_rot)/2)

        self.current_wall.obj_prompts.location = self.current_wall.obj_prompts.location
        if self.previous_wall:
            self.previous_wall.obj_prompts.location = self.previous_wall.obj_prompts.location
        if self.next_wall:
            self.next_wall.obj_prompts.location = self.next_wall.obj_prompts.location
        return True

    def get_next_wall(self,context):
        obj_x = self.current_wall.obj_x
        connected_obj = obj_x.home_builder.connected_object
        if connected_obj:
            self.next_wall = pc_types.Assembly(connected_obj) 

    def get_previous_wall(self,context):
        if len(self.current_wall.obj_bp.constraints) > 0:
            obj_bp = self.current_wall.obj_bp.constraints[0].target.parent
            self.previous_wall = pc_types.Assembly(obj_bp)    

    def invoke(self,context,event):
        wall_bp = home_builder_utils.get_wall_bp(context.object)
        self.next_wall = None
        self.previous_wall = None
        self.current_wall = pc_types.Assembly(wall_bp)   
        self.get_previous_wall(context)
        self.get_next_wall(context)
        wm = context.window_manager           
        return wm.invoke_props_dialog(self, width=370)

    def draw_product_size(self,layout,context):
        unit_system = context.scene.unit_settings.system

        box = layout.box()
        row = box.row()
        
        col = row.column(align=True)
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.current_wall.obj_x):
            x = math.fabs(self.current_wall.obj_x.location.x)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',x))
            row1.label(text='Length: ' + value)
        else:
            row1.label(text='Length:')
            row1.prop(self.current_wall.obj_x,'location',index=0,text="")
            row1.prop(self.current_wall.obj_x,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.current_wall.obj_z):
            z = math.fabs(self.current_wall.obj_z.location.z)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))            
            row1.label(text='Height: ' + value)
        else:
            row1.label(text='Height:')
            row1.prop(self.current_wall.obj_z,'location',index=2,text="")
            row1.prop(self.current_wall.obj_z,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.current_wall.obj_y):
            y = math.fabs(self.current_wall.obj_y.location.y)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',y))                 
            row1.label(text='Thickness: ' + value)
        else:
            row1.label(text='Thickness:')
            row1.prop(self.current_wall.obj_y,'location',index=1,text="")
            row1.prop(self.current_wall.obj_y,'hide_viewport',text="")
            
        if len(self.current_wall.obj_bp.constraints) > 0:
            col = row.column(align=True)
            col.label(text="Location:")
            col.operator('home_builder.disconnect_constraint',text='Disconnect Wall',icon='CONSTRAINT').obj_name = self.current_wall.obj_bp.name
        else:
            col = row.column(align=True)
            col.label(text="Location X:")
            col.label(text="Location Y:")
            col.label(text="Location Z:")
        
            col = row.column(align=True)
            col.prop(self.current_wall.obj_bp,'location',text="")
        
        row = box.row()
        row.label(text='Rotation Z:')
        row.prop(self.current_wall.obj_bp,'rotation_euler',index=2,text="")  

    def draw_brick_wall_props(self,layout,context):
        brick_length = self.current_wall.get_prompt("Brick Length")
        brick_height = self.current_wall.get_prompt("Brick Height")
        mortar_thickness = self.current_wall.get_prompt("Mortar Thickness")
        mortar_inset = self.current_wall.get_prompt("Mortar Inset")

        box = layout.box()
        box.label(text="Brick Options")        
        brick_length.draw(box,allow_edit=False)
        brick_height.draw(box,allow_edit=False)
        mortar_thickness.draw(box,allow_edit=False)
        mortar_inset.draw(box,allow_edit=False)

    def draw_framed_wall_props(self,layout,context):
        stud_spacing_distance = self.current_wall.get_prompt("Stud Spacing Distance")
        material_thickness = self.current_wall.get_prompt("Material Thickness")

        box = layout.box()
        box.label(text="Framing Wall Options")        
        stud_spacing_distance.draw(box,allow_edit=False)
        material_thickness.draw(box,allow_edit=False)

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(layout,context)

        brick_length = self.current_wall.get_prompt("Brick Length")
        if brick_length:
            self.draw_brick_wall_props(layout,context)

        stud_spacing_distance = self.current_wall.get_prompt("Stud Spacing Distance")
        if stud_spacing_distance:
            self.draw_framed_wall_props(layout,context)

        box = layout.box()
        box.label(text="Room Tools",icon='MODIFIER')
        row = box.row()
        row.operator('home_builder.add_room_light',text='Add Room Light',icon='LIGHT_SUN')
        row.operator('home_builder.draw_floor_plane',text='Add Floor',icon='MESH_PLANE')
        
        # left_angle = self.current_wall.get_prompt("Left Angle")
        # right_angle = self.current_wall.get_prompt("Right Angle")

        # col = layout.column(align=True)
        # col.prop(self.current_wall.obj_x,'location',index=0,text="Length")
        # col.prop(self.current_wall.obj_y,'location',index=1,text="Thickness")
        # col.prop(self.current_wall.obj_z,'location',index=2,text="Height")

        # col = layout.column(align=True)
        # col.prop(self.current_wall.obj_bp,'rotation_euler',index=2,text="Rotation")

        # left_angle.draw(layout)
        # right_angle.draw(layout)

        # layout.label(text=str(left_angle.get_value()))
        # layout.label(text=str(right_angle.get_value()))

classes = (
    home_builder_OT_wall_prompts,
    home_builder_OT_draw_multiple_walls
)

register, unregister = bpy.utils.register_classes_factory(classes)        
