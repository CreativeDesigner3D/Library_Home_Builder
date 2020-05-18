import bpy
import os
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from .. import home_builder_utils

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

        if self.previous_wall:
            prev_left_angle = self.previous_wall.get_prompt("Left Angle")
            prev_right_angle = self.previous_wall.get_prompt("Right Angle") 
            prev_rot = math.degrees(self.previous_wall.obj_bp.rotation_euler.z)  

        if self.next_wall:
            next_left_angle = self.next_wall.get_prompt("Left Angle")
            next_rot = math.degrees(self.next_wall.obj_bp.rotation_euler.z)  

        rot = math.degrees(self.current_wall.obj_bp.rotation_euler.z)

        left_angle.set_value((rot-prev_rot)/2)

        if self.next_wall:
            right_angle.set_value((rot-next_rot)/2)
            next_left_angle.set_value((next_rot-rot)/2)

        if self.previous_wall:
            prev_right_angle.set_value((prev_rot-rot)/2)

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
        return wm.invoke_props_dialog(self, width=300)

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
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.cabinet.obj_z):
            z = math.fabs(self.cabinet.obj_z.location.z)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))            
            row1.label(text='Height: ' + value)
        else:
            row1.label(text='Height:')
            row1.prop(self,'height',text="")
            row1.prop(self.cabinet.obj_z,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.cabinet.obj_y):
            y = math.fabs(self.cabinet.obj_y.location.y)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',y))                 
            row1.label(text='Depth: ' + value)
        else:
            row1.label(text='Depth:')
            row1.prop(self,'depth',text="")
            row1.prop(self.cabinet.obj_y,'hide_viewport',text="")
            
        if len(self.cabinet.obj_bp.constraints) > 0:
            col = row.column(align=True)
            col.label(text="Location:")
            col.operator('kitchen.disconnect_cabinet_constraint',text='Disconnect Constraint',icon='CONSTRAINT').obj_name = self.cabinet.obj_bp.name
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

    def draw(self, context):
        layout = self.layout

        left_angle = self.current_wall.get_prompt("Left Angle")
        right_angle = self.current_wall.get_prompt("Right Angle")

        col = layout.column(align=True)
        col.prop(self.current_wall.obj_x,'location',index=0,text="Length")
        col.prop(self.current_wall.obj_y,'location',index=1,text="Thickness")
        col.prop(self.current_wall.obj_z,'location',index=2,text="Height")

        col = layout.column(align=True)
        col.prop(self.current_wall.obj_bp,'rotation_euler',index=2,text="Rotation")

        left_angle.draw(layout)
        right_angle.draw(layout)

        layout.label(text=str(left_angle.get_value()))
        layout.label(text=str(right_angle.get_value()))

classes = (
    home_builder_OT_wall_prompts,
)

register, unregister = bpy.utils.register_classes_factory(classes)        
