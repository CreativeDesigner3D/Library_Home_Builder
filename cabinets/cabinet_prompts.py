import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from .. import home_builder_utils

class home_builder_OT_cabinet_prompts(bpy.types.Operator):
    bl_idname = "home_builder.cabinet_prompts"
    bl_label = "Cabinet Prompts"

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    product_tabs: bpy.props.EnumProperty(name="Product Tabs",
                                         items=[('CARCASS',"Carcass","Carcass Options"),
                                                ('EXTERIOR',"Exterior","Exterior Options"),
                                                ('INTERIOR',"Interior","Interior Options"),
                                                ('SPLITTER',"Openings","Openings Options")])

    drawer_calculator = None

    left_side = None
    right_side = None

    cabinet = None
    carcass = None
    countertop = None
    doors = None
    drawers = None
    interior = None

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
        left_finished_end = self.carcass.get_prompt("Left Finished End")
        right_finished_end = self.carcass.get_prompt("Right Finished End")
        home_builder_utils.update_side_material(self.left_side,left_finished_end.get_value())
        home_builder_utils.update_side_material(self.right_side,right_finished_end.get_value())

    def check(self, context):
        self.update_product_size()
        if self.drawer_calculator:
            self.drawer_calculator.calculate()
        self.update_materials(context)
        return True

    def execute(self, context):
        return {'FINISHED'}

    def get_assemblies(self,context):
        for child in self.cabinet.obj_bp.children:
            if "IS_CARCASS_BP" in child and child["IS_CARCASS_BP"]:
                self.carcass = pc_types.Assembly(child)      
            if "IS_INTERIOR_BP" in child and child["IS_INTERIOR_BP"]:
                self.interior = pc_types.Assembly(child)              
            if "IS_EXTERIOR_BP" in child and child["IS_EXTERIOR_BP"]:
                self.exterior = pc_types.Assembly(child)                     
            if "IS_COUNTERTOP_BP" in child and child["IS_COUNTERTOP_BP"]:
                self.countertop = pc_types.Assembly(child)   
            if "IS_DRAWERS_BP" in child and child["IS_DRAWERS_BP"]:
                self.drawers = pc_types.Assembly(child)   
                self.drawer_calculator = self.drawers.get_calculator('Front Height Calculator')
            if "IS_DOORS_BP" in child and child["IS_DOORS_BP"]:
                self.doors = pc_types.Assembly(child)

        for child in self.carcass.obj_bp.children:
            if "IS_LEFT_SIDE_BP" in child and child["IS_LEFT_SIDE_BP"]:
                self.left_side = pc_types.Assembly(child)
            if "IS_RIGHT_SIDE_BP" in child and child["IS_RIGHT_SIDE_BP"]:
                self.right_side = pc_types.Assembly(child)            

    def invoke(self,context,event):
        bp = home_builder_utils.get_cabinet_bp(context.object)
        self.cabinet = pc_types.Assembly(bp)
        self.depth = math.fabs(self.cabinet.obj_y.location.y)
        self.height = math.fabs(self.cabinet.obj_z.location.z)
        self.width = math.fabs(self.cabinet.obj_x.location.x)
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

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

    def draw_carcass_prompts(self,layout,context):
        left_finished_end = self.carcass.get_prompt("Left Finished End")
        right_finished_end = self.carcass.get_prompt("Right Finished End")

        toe_kick_height = self.carcass.get_prompt("Toe Kick Height")
        toe_kick_setback = self.carcass.get_prompt("Toe Kick Setback")

        left_finished_end.draw(layout)
        right_finished_end.draw(layout)
        toe_kick_height.draw(layout)
        toe_kick_setback.draw(layout)

    def draw_countertop_prompts(self,layout,context):
        ctop_front = self.cabinet.get_prompt("Countertop Overhang Front")
        ctop_back = self.cabinet.get_prompt("Countertop Overhang Back")
        ctop_left = self.cabinet.get_prompt("Countertop Overhang Left")
        ctop_right = self.cabinet.get_prompt("Countertop Overhang Right")

        ctop_front.draw(layout)
        ctop_back.draw(layout)       
        ctop_left.draw(layout)  
        ctop_right.draw(layout)         

    def draw_door_prompts(self,layout,context):
        open_door = self.doors.get_prompt("Open Door")
        open_door.draw(layout)

    def draw_drawer_prompts(self,layout,context):
        for prompt in self.drawer_calculator.prompts:
            prompt.draw(layout)

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(layout,context)

        prompt_box = layout.box()

        row = prompt_box.row(align=True)
        row.prop_enum(self, "product_tabs", 'CARCASS') 
        row.prop_enum(self, "product_tabs", 'EXTERIOR') 
        row.prop_enum(self, "product_tabs", 'INTERIOR') 

        if self.product_tabs == 'CARCASS':
            self.draw_carcass_prompts(prompt_box,context)
            self.draw_countertop_prompts(prompt_box,context)

        if self.product_tabs == 'EXTERIOR':
            if self.doors:
                self.draw_door_prompts(prompt_box,context)
            if self.drawer_calculator:
                self.draw_drawer_prompts(prompt_box,context)


def register():
    bpy.utils.register_class(home_builder_OT_cabinet_prompts)     

def unregister():
    bpy.utils.unregister_class(home_builder_OT_cabinet_prompts)        