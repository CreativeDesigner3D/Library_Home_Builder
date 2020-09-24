import bpy
import os
import math
from ..pc_lib import pc_utils, pc_types, pc_unit
from .. import home_builder_utils

class home_builder_OT_place_door_window(bpy.types.Operator):
    bl_idname = "home_builder.place_door_window"
    bl_label = "Place Door or Window"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    
    drawing_plane = None

    assembly = None
    obj = None
    exclude_objects = []
    window_z_location = 0

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        self.window_z_location = props.window_height_from_floor
        self.create_drawing_plane(context)
        self.create_assembly(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def create_assembly(self,context):
        wm_props = home_builder_utils.get_wm_props(context.window_manager)
        self.assembly = wm_props.get_asset(self.filepath)        
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
        obj["PROMPT_ID"] = "home_builder.window_door_prompts"   
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

    def parent_window_to_wall(self,obj_wall_bp):
        x_loc = pc_utils.calc_distance((self.assembly.obj_bp.location.x,self.assembly.obj_bp.location.y,0),
                                       (obj_wall_bp.matrix_local[0][3],obj_wall_bp.matrix_local[1][3],0))
        self.assembly.obj_bp.location = (0,0,0)
        self.assembly.obj_bp.rotation_euler = (0,0,0)
        self.assembly.obj_bp.parent = obj_wall_bp
        self.assembly.obj_bp.location.x = x_loc      
        if "IS_WINDOW_BP" in self.assembly.obj_bp:
            self.assembly.obj_bp.location.z = self.window_z_location  
        else:
            self.assembly.obj_bp.location.z = 0  

    def modal(self, context, event):
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

        selected_point, selected_obj = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        self.position_object(selected_point,selected_obj)

        if self.event_is_place_first_point(event):
            self.add_boolean_modifier(selected_obj)
            if selected_obj.parent:
                self.parent_window_to_wall(selected_obj.parent)
            if hasattr(self.assembly,'add_doors'):
                self.assembly.add_doors()
            self.set_placed_properties(self.assembly.obj_bp)
            self.create_assembly(context)
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
            if self.assembly.obj_bp and wall_bp:
                self.assembly.obj_bp.rotation_euler.z = wall_bp.rotation_euler.z
                self.assembly.obj_bp.location.x = selected_point[0]
                self.assembly.obj_bp.location.y = selected_point[1]
                if "IS_WINDOW_BP" in self.assembly.obj_bp:
                    self.assembly.obj_bp.location.z = self.window_z_location
                else:
                    self.assembly.obj_bp.location.z = 0

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.assembly.obj_bp)
        pc_utils.delete_object_and_children(self.drawing_plane)
        return {'CANCELLED'}

    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        return {'FINISHED'}


class home_builder_OT_window_door_prompts(bpy.types.Operator):
    bl_idname = "home_builder.window_door_prompts"
    bl_label = "Window Door Prompts"

    assembly_name: bpy.props.StringProperty(name="Window Name",default="")

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    assembly = None

    def update_product_size(self):
        if 'IS_MIRROR' in self.assembly.obj_x and self.assembly.obj_x['IS_MIRROR']:
            self.assembly.obj_x.location.x = -self.width
        else:
            self.assembly.obj_x.location.x = self.width

        if 'IS_MIRROR' in self.assembly.obj_y and self.assembly.obj_y['IS_MIRROR']:
            self.assembly.obj_y.location.y = -self.depth
        else:
            self.assembly.obj_y.location.y = self.depth
        
        if 'IS_MIRROR' in self.assembly.obj_z and self.assembly.obj_z['IS_MIRROR']:
            self.assembly.obj_z.location.z = -self.height
        else:
            self.assembly.obj_z.location.z = self.height

    def check(self, context):
        self.update_product_size()
        return True

    def execute(self, context):
        return {'FINISHED'}

    def get_assemblies(self,context):
        pass

    def invoke(self,context,event):
        bp = home_builder_utils.get_window_bp(context.object)
        if bp is None:
            bp = home_builder_utils.get_door_bp(context.object)
        self.assembly = pc_types.Assembly(bp)
        self.depth = math.fabs(self.assembly.obj_y.location.y)
        self.height = math.fabs(self.assembly.obj_z.location.z)
        self.width = math.fabs(self.assembly.obj_x.location.x)
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def draw_product_size(self,layout,context):
        unit_system = context.scene.unit_settings.system

        box = layout.box()
        row = box.row()
        
        col = row.column(align=True)
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.assembly.obj_x):
            x = math.fabs(self.assembly.obj_x.location.x)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',x))
            row1.label(text='Width: ' + value)
        else:
            row1.label(text='Width:')
            row1.prop(self,'width',text="")
            row1.prop(self.assembly.obj_x,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.assembly.obj_z):
            z = math.fabs(self.assembly.obj_z.location.z)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))            
            row1.label(text='Height: ' + value)
        else:
            row1.label(text='Height:')
            row1.prop(self,'height',text="")
            row1.prop(self.assembly.obj_z,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.assembly.obj_y):
            y = math.fabs(self.assembly.obj_y.location.y)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',y))                 
            row1.label(text='Depth: ' + value)
        else:
            row1.label(text='Depth:')
            row1.prop(self,'depth',text="")
            row1.prop(self.assembly.obj_y,'hide_viewport',text="")
            
        if len(self.assembly.obj_bp.constraints) > 0:
            col = row.column(align=True)
            col.label(text="Location:")
            col.operator('home_builder.disconnect_constraint',text='Disconnect Constraint',icon='CONSTRAINT').obj_name = self.door.obj_bp.name
        else:
            col = row.column(align=True)
            col.label(text="Location X:")
            col.label(text="Location Y:")
            col.label(text="Location Z:")
        
            col = row.column(align=True)
            col.prop(self.assembly.obj_bp,'location',text="")
        
        row = box.row()
        row.label(text='Rotation Z:')
        row.prop(self.assembly.obj_bp,'rotation_euler',index=2,text="")  

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(layout,context)


classes = (
    home_builder_OT_place_door_window,
    home_builder_OT_window_door_prompts,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()