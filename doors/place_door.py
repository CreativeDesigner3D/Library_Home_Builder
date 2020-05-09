import bpy
import os
from ..pc_lib import pc_utils, pc_types, pc_unit
from . import data_doors

class home_builder_OT_place_door(bpy.types.Operator):
    bl_idname = "home_builder.place_door"
    bl_label = "Place Door"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    
    drawing_plane = None

    door = None
    obj = None
    exclude_objects = []

    class_name = ""

    def execute(self, context):
        self.get_class_name()
        self.create_drawing_plane(context)
        self.create_door()
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def get_class_name(self):
        name, ext = os.path.splitext(os.path.basename(self.filepath))
        self.class_name = name

    def create_door(self):
        # props = home_builder_utils.get_scene_props(bpy.context)
        self.door = eval("data_doors." + self.class_name + "()")
        self.door.draw_door()
        self.set_child_properties(self.door.obj_bp)

    def set_child_properties(self,obj):
        obj["PROMPT_ID"] = "room.wall_prompts"   
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
            if 'IS_BOOLEAN' in obj:
                obj.display_type = 'WIRE' 
                obj.hide_viewport = True
            else:
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
        obj_bool = self.get_boolean_obj(self.door.obj_bp)
        if wall_mesh and obj_bool:
            mod = wall_mesh.modifiers.new(obj_bool.name,'BOOLEAN')
            mod.object = obj_bool
            mod.operation = 'DIFFERENCE'

    def parent_door_to_wall(self,obj_wall_bp):
        x_loc = pc_utils.calc_distance((self.door.obj_bp.location.x,self.door.obj_bp.location.y,0),
                                       (obj_wall_bp.matrix_local[0][3],obj_wall_bp.matrix_local[1][3],0))
        self.door.obj_bp.location = (0,0,0)
        self.door.obj_bp.rotation_euler = (0,0,0)
        self.door.obj_bp.parent = obj_wall_bp
        self.door.obj_bp.location.x = x_loc        

    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        self.position_object(selected_point,selected_obj)

        if self.event_is_place_first_point(event):
            self.add_boolean_modifier(selected_obj)
            self.set_placed_properties(self.door.obj_bp)
            if selected_obj.parent:
                self.parent_door_to_wall(selected_obj.parent)
            self.create_door()
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
        if selected_obj:
            wall_bp = selected_obj.parent
            if self.door.obj_bp and wall_bp:
                self.door.obj_bp.rotation_euler.z = wall_bp.rotation_euler.z
                self.door.obj_bp.location.x = selected_point[0]
                self.door.obj_bp.location.y = selected_point[1]
                self.door.obj_bp.location.z = 0

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.door.obj_bp)
        pc_utils.delete_object_and_children(self.drawing_plane)
        return {'CANCELLED'}

    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        return {'FINISHED'}

classes = (
    home_builder_OT_place_door,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
