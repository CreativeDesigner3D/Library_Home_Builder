import bpy
import os
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_closets
from .. import home_builder_utils
from .. import home_builder_paths
from .. import home_builder_enums
from .. import home_builder_pointers
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

class home_builder_OT_closet_prompts(bpy.types.Operator):
    bl_idname = "home_builder.closet_prompts"
    bl_label = "Closet Prompts"

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    product_tabs: bpy.props.EnumProperty(name="Product Tabs",
                                         items=[('MAIN',"Main","Main Options"),
                                                ('CONSTRUCTION',"Construction","Construction Options"),
                                                ('MACHINING',"Machining","Machining Options")])

    opening_1_height: bpy.props.EnumProperty(name="Opening 1 Height",
                                    items=home_builder_enums.PANEL_HEIGHTS,
                                    default = '2131')
    
    opening_2_height: bpy.props.EnumProperty(name="Opening 2 Height",
                                    items=home_builder_enums.PANEL_HEIGHTS,
                                    default = '2131')
    
    opening_3_height: bpy.props.EnumProperty(name="Opening 3 Height",
                                    items=home_builder_enums.PANEL_HEIGHTS,
                                    default = '2131')
    
    opening_4_height: bpy.props.EnumProperty(name="Opening 4 Height",
                                    items=home_builder_enums.PANEL_HEIGHTS,
                                    default = '2131')
    
    opening_5_height: bpy.props.EnumProperty(name="Opening 5 Height",
                                    items=home_builder_enums.PANEL_HEIGHTS,
                                    default = '2131')
    
    opening_6_height: bpy.props.EnumProperty(name="Opening 6 Height",
                                    items=home_builder_enums.PANEL_HEIGHTS,
                                    default = '2131')
    
    opening_7_height: bpy.props.EnumProperty(name="Opening 7 Height",
                                    items=home_builder_enums.PANEL_HEIGHTS,
                                    default = '2131')
    
    opening_8_height: bpy.props.EnumProperty(name="Opening 8 Height",
                                    items=home_builder_enums.PANEL_HEIGHTS,
                                    default = '2131')
    
    closet = None
    calculators = []

    def reset_variables(self):
        #BLENDER CRASHES IF TAB IS SET TO EXTERIOR
        #THIS IS BECAUSE POPUP DIALOGS CANNOT DISPLAY UILISTS ON INVOKE
        self.product_tabs = 'MAIN'
        self.closet = None
        self.calculators = []

    def update_product_size(self):
        if 'IS_MIRROR' in self.closet.obj_x and self.closet.obj_x['IS_MIRROR']:
            self.closet.obj_x.location.x = -self.width
        else:
            self.closet.obj_x.location.x = self.width

        if 'IS_MIRROR' in self.closet.obj_y and self.closet.obj_y['IS_MIRROR']:
            self.closet.obj_y.location.y = -self.depth
        else:
            self.closet.obj_y.location.y = self.depth
        
        if 'IS_MIRROR' in self.closet.obj_z and self.closet.obj_z['IS_MIRROR']:
            self.closet.obj_z.location.z = -self.height
        else:
            self.closet.obj_z.location.z = self.height

        for i in range(1,9):
            opening_height = self.closet.get_prompt("Opening " + str(i) + " Height")
            if opening_height:
                height = eval("float(self.opening_" + str(i) + "_height)/1000")
                opening_height.set_value(height)

    def update_materials(self,context):
        pass

    def update_fillers(self,context):
        pass
        # left_adjustment_width = self.cabinet.get_prompt("Left Adjustment Width")
        # right_adjustment_width = self.cabinet.get_prompt("Right Adjustment Width")
        # if left_adjustment_width.get_value() > 0 and self.cabinet.left_filler is None:
        #     self.cabinet.add_left_filler()
        #     home_builder_utils.update_assembly_id_props(self.cabinet.left_filler,self.cabinet)
        # if right_adjustment_width.get_value() > 0 and self.cabinet.right_filler is None:
        #     self.cabinet.add_right_filler()   
        #     home_builder_utils.update_assembly_id_props(self.cabinet.right_filler,self.cabinet)          
        # if left_adjustment_width.get_value() == 0 and self.cabinet.left_filler is not None:
        #     pc_utils.delete_object_and_children(self.cabinet.left_filler.obj_bp)
        #     self.cabinet.left_filler = None
        # if right_adjustment_width.get_value() == 0 and self.cabinet.right_filler is not None:
        #     pc_utils.delete_object_and_children(self.cabinet.right_filler.obj_bp)
        #     self.cabinet.right_filler = None   

    def set_default_heights(self):
        for i in range(1,9):
            opening_height_prompt = self.closet.get_prompt("Opening " + str(i) + " Height")
            if opening_height_prompt:
                opening_height = round(pc_unit.meter_to_millimeter(opening_height_prompt.get_value()),0)
                for index, height in enumerate(home_builder_enums.PANEL_HEIGHTS):
                    if not opening_height >= int(height[0]):
                        exec('self.opening_' + str(i) + '_height = home_builder_enums.PANEL_HEIGHTS[index - 1][0]')                                                                                                                                                                                                        
                        break

    def check(self, context):
        self.update_product_size()
        self.update_fillers(context)     
        self.update_materials(context)
        for calculator in self.calculators:
            calculator.calculate()
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)

    def invoke(self,context,event):
        self.reset_variables()
        self.get_assemblies(context)
        self.depth = math.fabs(self.closet.obj_y.location.y)
        self.height = math.fabs(self.closet.obj_z.location.z)
        self.width = math.fabs(self.closet.obj_x.location.x)
        self.set_default_heights()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_closet_bp(context.object)
        self.closet = data_closets.Closet_Starter(bp)
        self.get_calculators(self.closet.obj_bp)

    def draw_product_size(self,layout,context):
        unit_system = context.scene.unit_settings.system

        box = layout.box()
        row = box.row()
        
        col = row.column(align=True)
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.closet.obj_x):
            x = math.fabs(self.closet.obj_x.location.x)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',x))
            row1.label(text='Width: ' + value)
        else:
            row1.label(text='Width:')
            row1.prop(self,'width',text="")
            row1.prop(self.closet.obj_x,'hide_viewport',text="")
            row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.closet.obj_x.name

        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.closet.obj_z):
            z = math.fabs(self.closet.obj_z.location.z)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))            
            row1.label(text='Height: ' + value)
        else:
            row1.label(text='Height:')
            row1.prop(self,'height',text="")
            row1.prop(self.closet.obj_z,'hide_viewport',text="")
            row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.closet.obj_z.name
        
        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.closet.obj_y):
            y = math.fabs(self.closet.obj_y.location.y)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',y))                 
            row1.label(text='Depth: ' + value)
        else:
            row1.label(text='Depth:')
            row1.prop(self,'depth',text="")
            row1.prop(self.closet.obj_y,'hide_viewport',text="")
            row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.closet.obj_y.name
            
        if len(self.closet.obj_bp.constraints) > 0:
            col = row.column(align=True)
            col.label(text="Location:")
            col.operator('home_builder.disconnect_constraint',text='Disconnect Constraint',icon='CONSTRAINT').obj_name = self.closet.obj_bp.name
        else:
            col = row.column(align=True)
            col.label(text="Location X:")
            col.label(text="Location Y:")
            col.label(text="Location Z:")
        
            col = row.column(align=True)
            col.prop(self.closet.obj_bp,'location',text="")
        
        row = box.row()
        row.label(text='Rotation Z:')
        row.prop(self.closet.obj_bp,'rotation_euler',index=2,text="")  

        row = box.row()
        row.label(text='Height from Floor:')
        row.prop(self.closet.obj_bp,'location',index=2,text="")          

        props = home_builder_utils.get_scene_props(context.scene)
        row = box.row()
        row.alignment = 'LEFT'
        row.prop(props,'show_cabinet_placement_options',emboss=False,icon='TRIA_DOWN' if props.show_cabinet_tools else 'TRIA_RIGHT')
        if props.show_cabinet_placement_options:
            row = box.row()
            row.label(text="TODO: Implement Closet Placement Options")

    def draw_construction_prompts(self,layout,context):
        pass

    def get_number_of_equal_widths(self):
        number_of_equal_widths = 0
        
        for i in range(1,9):
            width = self.closet.get_prompt("Opening " + str(i) + " Width")
            if width:
                number_of_equal_widths += 1 if width.equal else 0
            else:
                break
            
        return number_of_equal_widths

    def draw_closet_prompts(self,layout,context):
        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.label(text="Opening:")
        row.label(text="",icon='BLANK1')
        row.label(text="Width:")
        row.label(text="Height:")
        row.label(text="Depth:")
        
        box = col.box()

        for i in range(1,9):
            width = self.closet.get_prompt("Opening " + str(i) + " Width")
            height = self.closet.get_prompt("Opening " + str(i) + " Height")
            depth = self.closet.get_prompt("Opening " + str(i) + " Depth")
            floor = self.closet.get_prompt("Opening " + str(i) + " Floor Mounted")
            if width:
                row = box.row()
                row.prop(floor,'checkbox_value',text=str(i) + ": " + "Floor" if floor.get_value() else str(i) + ": " + "Hanging",icon='TRIA_DOWN' if floor.get_value() else 'TRIA_UP')                
                if width.equal == False:
                    row.prop(width,'equal',text="")
                else:
                    if self.get_number_of_equal_widths() != 1:
                        row.prop(width,'equal',text="")
                    else:
                        row.label(text="",icon='BLANK1')                
                # row.prop(width,'distance_value',text="Width")
                if width.equal:
                    row.label(text=str(pc_unit.meter_to_active_unit(width.distance_value)) + '"')
                else:
                    row.prop(width,'distance_value',text="")
                # row.prop(floor,'checkbox_value',text="",icon='TRIA_DOWN' if floor.get_value() else 'TRIA_UP')
                row.prop(self,'opening_' + str(i) + '_height',text="")
                row.prop(depth,'distance_value',text="")

    def draw(self, context):
        layout = self.layout
        info_box = layout.box()
        
        obj_props = home_builder_utils.get_object_props(self.closet.obj_bp)
        scene_props = home_builder_utils.get_scene_props(context.scene)

        mat_group = scene_props.material_pointer_groups[obj_props.material_group_index]
        
        row = info_box.row(align=True)
        row.prop(self.closet.obj_bp,'name',text="Name")
        row.separator()
        row.menu('HOME_BUILDER_MT_change_product_material_group',text=mat_group.name,icon='COLOR')
        row.operator('home_builder.update_product_material_group',text="",icon='FILE_REFRESH').object_name = self.closet.obj_bp.name

        self.draw_product_size(layout,context)

        prompt_box = layout.box()

        row = prompt_box.row(align=True)
        row.prop_enum(self, "product_tabs", 'MAIN') 
        row.prop_enum(self, "product_tabs", 'CONSTRUCTION') 
        row.prop_enum(self, "product_tabs", 'MACHINING')

        if self.product_tabs == 'MAIN':
            self.draw_closet_prompts(prompt_box,context)   
        
        if self.product_tabs == 'CONSTRUCTION':
            self.draw_construction_prompts(prompt_box,context)

        if self.product_tabs == 'MACHINING':
            pass
            # for carcass in reversed(self.cabinet.carcasses):
            #     if carcass.exterior:
            #         box = prompt_box.box()
            #         box.label(text=carcass.exterior.obj_bp.name)
            #         carcass.exterior.draw_prompts(box,context)


class home_builder_OT_closet_door_prompts(bpy.types.Operator):
    bl_idname = "home_builder.closet_door_prompts"
    bl_label = "Closet Door Prompts"

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    product_tabs: bpy.props.EnumProperty(name="Product Tabs",
                                         items=[('MAIN',"Main","Main Options"),
                                                ('CONSTRUCTION',"Construction","Construction Options"),
                                                ('MACHINING',"Machining","Machining Options")])

    opening_1_height: bpy.props.EnumProperty(name="Opening 1 Height",
                                    items=home_builder_enums.PANEL_HEIGHTS,
                                    default = '2131')
    
    insert = None
    calculators = []

    def check(self, context):
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_closet_doors_bp(context.object)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        hot = self.insert.get_prompt("Half Overlay Top")
        hob = self.insert.get_prompt("Half Overlay Bottom")
        hol = self.insert.get_prompt("Half Overlay Left")   
        hor = self.insert.get_prompt("Half Overlay Right")   
        
        box = layout.box()
        box.label(text="Front Half Overlays")
        row = box.row()
        row.prop(hot,'checkbox_value',text="Top") 
        row.prop(hob,'checkbox_value',text="Bottom") 
        row.prop(hol,'checkbox_value',text="Left") 
        row.prop(hor,'checkbox_value',text="Right") 


class home_builder_OT_closet_shelves_prompts(bpy.types.Operator):
    bl_idname = "home_builder.closet_shelves_prompts"
    bl_label = "Closet Shelves Prompts"

    insert = None
    calculators = []

    def check(self, context):
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_closet_shelves_bp(context.object)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        shelf_qty = self.insert.get_prompt("Shelf Quantity")
        layout.prop(shelf_qty,'quantity_value',text="Shelf Quantity")


class home_builder_OT_closet_drawer_prompts(bpy.types.Operator):
    bl_idname = "home_builder.closet_drawer_prompts"
    bl_label = "Closet Drawer Prompts"

    insert = None
    calculators = []

    def check(self, context):
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_closet_drawers_bp(context.object)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        drawer_qty = self.insert.get_prompt("Drawer Quantity")
        box.prop(drawer_qty,'quantity_value',text="Drawer Quantity")
        for i in range(1,7):
            if drawer_qty.get_value() > i - 1:
                drawer_height = self.insert.get_prompt("Drawer " + str(i) + " Height")
                box.prop(drawer_height,'distance_value',text="Drawer " + str(i) + " Height")

        hot = self.insert.get_prompt("Half Overlay Top")
        hob = self.insert.get_prompt("Half Overlay Bottom")
        hol = self.insert.get_prompt("Half Overlay Left")   
        hor = self.insert.get_prompt("Half Overlay Right")   
        
        box = layout.box()
        box.label(text="Front Half Overlays")
        row = box.row()
        row.prop(hot,'checkbox_value',text="Top") 
        row.prop(hob,'checkbox_value',text="Bottom") 
        row.prop(hol,'checkbox_value',text="Left") 
        row.prop(hor,'checkbox_value',text="Right") 


class home_builder_OT_show_closet_properties(bpy.types.Operator):
    bl_idname = "home_builder.show_closet_properties"
    bl_label = "Show Closet Properties"

    def execute(self, context):
        obj = context.object
        closet_bp = home_builder_utils.get_closet_bp(obj)
        closet = data_closets.Closet_Starter(closet_bp)
        wm_props = home_builder_utils.get_wm_props(context.window_manager)
        for i in range(1,9):
            width = closet.get_prompt("Opening " + str(i) + " Width")
            if width:
                wm_width = eval("wm_props.closet_" + str(i) + "_width")
                print('WM1',wm_width)
                wm_width = width.distance_value
                print('WM2',wm_width)
                print(width.distance_value)
                # eval("wm_props.closet_" + str(i) + "_width = width.get_value()")

        return {'FINISHED'}


class home_builder_OT_change_closet_openings(bpy.types.Operator):
    bl_idname = "home_builder.change_closet_openings"
    bl_label = "Change Closet Openings"

    quantity: bpy.props.IntProperty(name="Quantity")

    closet = None
    calculators = []

    def invoke(self,context,event):
        self.calculators = []
        obj = context.object
        closet_bp = home_builder_utils.get_closet_bp(obj)
        self.closet = data_closets.Closet_Starter(closet_bp)     
        for i in range(1,9):
            opening_height_prompt = self.closet.get_prompt("Opening " + str(i) + " Width")
            if not opening_height_prompt:
                self.quantity = i - 1
                break
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Opening Quantity:")
        row.prop(self,'quantity',text="")

    def delete_reference_object(self,obj_bp):
        for obj in obj_bp.children:
            if "IS_REFERENCE" in obj:
                pc_utils.delete_object_and_children(obj)

    def execute(self, context):
        parent = self.closet.obj_bp.parent
        x_loc = self.closet.obj_bp.location.x
        y_loc = self.closet.obj_bp.location.y
        z_loc = self.closet.obj_bp.location.z
        z_rot = self.closet.obj_bp.rotation_euler.z
        length = self.closet.obj_x.location.x
        pc_utils.delete_object_and_children(self.closet.obj_bp)

        new_closet = data_closets.Closet_Starter()
        new_closet.opening_qty = self.quantity
        new_closet.pre_draw()
        new_closet.draw()
        new_closet.obj_bp.parent = parent
        new_closet.obj_bp.location.x = x_loc
        new_closet.obj_bp.location.y = y_loc
        new_closet.obj_bp.location.z = z_loc
        new_closet.obj_bp.rotation_euler.z = z_rot
        new_closet.obj_x.location.x = length
        self.delete_reference_object(new_closet.obj_bp)
        self.get_calculators(new_closet.obj_bp)
        for calculator in self.calculators:
            calculator.calculate()
        return {'FINISHED'}

classes = (
    home_builder_OT_closet_prompts,
    home_builder_OT_show_closet_properties,
    home_builder_OT_closet_shelves_prompts,
    home_builder_OT_closet_door_prompts,
    home_builder_OT_closet_drawer_prompts,
    home_builder_OT_change_closet_openings,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()            