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

def update_closet_height(self,context):
    ''' EVENT changes height for all closet openings
    '''
    self.opening_1_height = self.set_height
    self.opening_2_height = self.set_height
    self.opening_3_height = self.set_height
    self.opening_4_height = self.set_height
    self.opening_5_height = self.set_height
    self.opening_6_height = self.set_height
    self.opening_7_height = self.set_height
    self.opening_8_height = self.set_height
    
    obj_product_bp = home_builder_utils.get_closet_bp(context.active_object)
    product = pc_types.Assembly(obj_product_bp)
    if self.is_base:
        product.obj_z.location.z = pc_unit.millimeter(float(self.set_height))

    for i in range(1,10):
        opening_height = product.get_prompt("Opening " + str(i) + " Height")
        if opening_height:
            opening_height.set_value(pc_unit.millimeter(float(self.set_height)))

def update_closet_depth(self,context):
    ''' EVENT changes depth for all closet openings
    '''
    obj_product_bp = home_builder_utils.get_closet_bp(context.active_object)
    product = pc_types.Assembly(obj_product_bp)
    if self.is_base:
        product.obj_y.location.y = -self.set_depth

    for i in range(1,10):
        opening_depth = product.get_prompt("Opening " + str(i) + " Depth")
        if opening_depth:
            opening_depth.set_value(self.set_depth)

def update_corner_closet_height(self,context):
    ''' EVENT changes height for corner closet
    '''
    obj_product_bp = home_builder_utils.get_closet_inside_corner_bp(context.active_object)
    product = pc_types.Assembly(obj_product_bp)
    is_hanging = product.get_prompt('Is Hanging')
    if is_hanging.get_value():
        panel_height = product.get_prompt('Panel Height')
        panel_height.set_value(pc_unit.millimeter(float(self.set_height)))
    else:
        product.obj_z.location.z = pc_unit.millimeter(float(self.set_height))

class home_builder_OT_duplicate_closet_insert(bpy.types.Operator):
    bl_idname = "home_builder.duplicate_closet_insert"
    bl_label = "Duplicate Closet Insert"

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    @classmethod
    def poll(cls, context):
        obj_bp = home_builder_utils.get_closet_insert_bp(context.object)
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

    def hide_empties(self,obj):
        if obj.type == 'EMPTY':
            obj.hide_viewport = True
        for child in obj.children:
            self.hide_empties(child)

    def delete_drivers(self,obj):
        if obj.animation_data:
            for driver in obj.animation_data.drivers:
                obj.driver_remove(driver.data_path)

    def execute(self, context):
        obj = context.object
        obj_bp = home_builder_utils.get_closet_insert_bp(obj)
        cabinet = pc_types.Assembly(obj_bp)
        bpy.ops.object.select_all(action='DESELECT')
        self.select_obj_and_children(cabinet.obj_bp)
        bpy.ops.object.duplicate_move()
        self.hide_empties(cabinet.obj_bp)

        obj = context.object
        new_obj_bp = home_builder_utils.get_closet_insert_bp(obj)
        new_cabinet = pc_types.Assembly(new_obj_bp)
        new_cabinet.obj_bp.parent = None
        self.delete_drivers(new_cabinet.obj_bp)
        self.delete_drivers(new_cabinet.obj_x)
        self.delete_drivers(new_cabinet.obj_y)
        self.delete_drivers(new_cabinet.obj_z)

        self.hide_empties(new_cabinet.obj_bp)

        bpy.ops.home_builder.place_closet_insert(obj_bp_name=new_cabinet.obj_bp.name)

        return {'FINISHED'}


class home_builder_OT_closet_prompts(bpy.types.Operator):
    bl_idname = "home_builder.closet_prompts"
    bl_label = "Closet Prompts"

    is_base: bpy.props.BoolProperty(name="Is Base")

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)

    product_tabs: bpy.props.EnumProperty(name="Product Tabs",
                                         items=[('MAIN',"Main","Main Options"),
                                                ('CONSTRUCTION',"Construction","Construction Options"),
                                                ('MACHINING',"Machining","Machining Options")])

    set_height: bpy.props.EnumProperty(name="Set Height",
                                       items=home_builder_enums.PANEL_HEIGHTS,
                                       default = '2131',
                                       update = update_closet_height)

    set_depth: bpy.props.FloatProperty(name="Set Depth",unit='LENGTH',precision=4,update=update_closet_depth)

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
        self.closet.obj_x.location.x = self.width
        for i in range(1,9):
            opening_height = self.closet.get_prompt("Opening " + str(i) + " Height")
            if opening_height:
                height = eval("float(self.opening_" + str(i) + "_height)/1000")
                opening_height.set_value(height)

    def update_materials(self,context):
        pass

    def update_bridge_parts(self,context):
        left_bridge = self.closet.get_prompt("Bridge Left")
        right_bridge = self.closet.get_prompt("Bridge Right")
        if left_bridge.get_value() == True and len(self.closet.left_bridge_parts) == 0:
            self.closet.add_left_blind_parts()
            for part in self.closet.left_bridge_parts:
                home_builder_utils.update_assembly_id_props(part,self.closet)
        if left_bridge.get_value() == False and len(self.closet.left_bridge_parts) > 0:
            for part in self.closet.left_bridge_parts:
                pc_utils.delete_object_and_children(part.obj_bp)
            self.closet.left_bridge_parts = []
        if right_bridge.get_value() == True and len(self.closet.right_bridge_parts) == 0:
            self.closet.add_right_blind_parts()
            for part in self.closet.right_bridge_parts:
                home_builder_utils.update_assembly_id_props(part,self.closet)
        if right_bridge.get_value() == False and len(self.closet.right_bridge_parts) > 0:
            for part in self.closet.right_bridge_parts:
                pc_utils.delete_object_and_children(part.obj_bp)
            self.closet.right_bridge_parts = []

    def update_fillers(self,context):
        left_side_wall_filler = self.closet.get_prompt("Left Side Wall Filler")
        right_side_wall_filler = self.closet.get_prompt("Right Side Wall Filler")
        if left_side_wall_filler.get_value() > 0 and self.closet.left_filler is None:
            self.closet.add_left_filler()
            home_builder_utils.update_assembly_id_props(self.closet.left_filler,self.closet)
        if right_side_wall_filler.get_value() > 0 and self.closet.right_filler is None:
            self.closet.add_right_filler()   
            home_builder_utils.update_assembly_id_props(self.closet.right_filler,self.closet)          
        if left_side_wall_filler.get_value() == 0 and self.closet.left_filler is not None:
            pc_utils.delete_object_and_children(self.closet.left_filler.obj_bp)
            self.closet.left_filler = None
        if right_side_wall_filler.get_value() == 0 and self.closet.right_filler is not None:
            pc_utils.delete_object_and_children(self.closet.right_filler.obj_bp)
            self.closet.right_filler = None   

    def set_default_size(self):
        self.width = self.closet.obj_x.location.x
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
        self.update_bridge_parts(context) 
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
        self.set_default_size()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_closet_bp(context.object)
        self.closet = data_closets.Closet_Starter(bp)
        self.is_base = self.closet.is_base
        if self.is_base:
            self.set_depth = math.fabs(self.closet.obj_y.location.y)
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
            row1.prop(self,'width',index=0,text="")
            row1.prop(self.closet.obj_x,'hide_viewport',text="")
            row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.closet.obj_x.name

        row1 = col.row(align=True)
        if pc_utils.object_has_driver(self.closet.obj_z):
            z = math.fabs(self.closet.obj_z.location.z)
            value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))            
            row1.label(text='Set Height: ' + value)
        else:
            row1.label(text='Set Height:')
            row1.prop(self,'set_height',text="")
            row1.prop(self.closet.obj_z,'hide_viewport',text="")
            row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.closet.obj_z.name

        if not self.closet.is_base:
            row1 = col.row(align=True)
            if pc_utils.object_has_driver(self.closet.obj_z):
                z = math.fabs(self.closet.obj_z.location.z)
                value = str(bpy.utils.units.to_string(unit_system,'LENGTH',z))            
                row1.label(text='Hanging Height: ' + value)
            else:
                row1.label(text='Hanging Height:')
                row1.prop(self.closet.obj_z,'location',index=2,text="")
                row1.prop(self.closet.obj_z,'hide_viewport',text="")
                row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.closet.obj_z.name
        else:
            row1 = col.row(align=True)
            row1.label(text='Set Depth:')
            row1.prop(self,'set_depth',text="")
            row1.prop(self.closet.obj_y,'hide_viewport',text="")
            row1.operator('pc_object.select_object',text="",icon='RESTRICT_SELECT_OFF').obj_name = self.closet.obj_y.name

        row1 = col.row(align=True)
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

        # row = box.row()
        # row.label(text='Height from Floor:')
        # row.prop(self.closet.obj_bp,'location',index=2,text="")          

        # props = home_builder_utils.get_scene_props(context.scene)
        # row = box.row()
        # row.alignment = 'LEFT'
        # row.prop(props,'show_cabinet_placement_options',emboss=False,icon='TRIA_DOWN' if props.show_cabinet_tools else 'TRIA_RIGHT')
        # if props.show_cabinet_placement_options:
        #     row = box.row()
        #     row.label(text="TODO: Implement Closet Placement Options")

    def draw_construction_prompts(self,layout,context):
        kick_height = self.closet.get_prompt("Closet Kick Height")
        kick_setback = self.closet.get_prompt("Closet Kick Setback")
        r_bridge = self.closet.get_prompt("Bridge Right")         
        l_bridge = self.closet.get_prompt("Bridge Left")
        r_bridge = self.closet.get_prompt("Bridge Right") 
        l_bridge_width = self.closet.get_prompt("Left Bridge Shelf Width")
        r_bridge_width = self.closet.get_prompt("Right Bridge Shelf Width")       
        l_filler = self.closet.get_prompt("Left Side Wall Filler")
        r_filler = self.closet.get_prompt("Right Side Wall Filler")      
        ctop_oh_front = self.closet.get_prompt("Countertop Overhang Front")       
        ctop_oh_left = self.closet.get_prompt("Countertop Overhang Left")   
        ctop_oh_right = self.closet.get_prompt("Countertop Overhang Right")   
        
        row = layout.row()    
        row.label(text="Toe Kick:")
        row.prop(kick_height,'distance_value',text="Height")    
        row.prop(kick_setback,'distance_value',text="Setback")    

        row = layout.row()   
        row.label(text="Fillers:") 
        row.prop(l_filler,'distance_value',text="Left Width")
        row.prop(r_filler,'distance_value',text="Right Width")

        if ctop_oh_front and ctop_oh_left and ctop_oh_right:
            row = layout.row()   
            row.label(text="Countertop Overhang:") 
            row.prop(ctop_oh_front,'distance_value',text="Front")
            row.prop(ctop_oh_left,'distance_value',text="Left")
            row.prop(ctop_oh_right,'distance_value',text="Right")

        row = layout.row()    
        row.prop(l_bridge,'checkbox_value',text="Bridge Left")
        if l_bridge.get_value():
            row.prop(l_bridge_width,'distance_value',text="Width")
        else:
            row.label(text="")
        row.prop(r_bridge,'checkbox_value',text="Bridge Right")
        if r_bridge.get_value():
            row.prop(r_bridge_width,'distance_value',text="Width")
        else:
            row.label(text="")

        row = layout.row()  
        row.label(text="Remove Bottom")
        for i in range(1,9):
            remove_bottom = self.closet.get_prompt("Remove Bottom " + str(i))
            if remove_bottom:
                row.prop(remove_bottom,'checkbox_value',text=str(i))

        row = layout.row()  
        row.label(text="Double Panel")
        for i in range(1,9):
            double_panel = self.closet.get_prompt("Double Panel " + str(i))
            if double_panel:
                row.prop(double_panel,'checkbox_value',text=str(i))

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
                if self.is_base:
                    row.label(text=str(pc_unit.meter_to_active_unit(depth.distance_value)) + '"')
                else:
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

class home_builder_OT_closet_inside_corner_prompts(bpy.types.Operator):
    bl_idname = "home_builder.closet_inside_corner_prompts"
    bl_label = "Closet Inside Corner Prompts"

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)  

    set_height: bpy.props.EnumProperty(name="Set Height",
                                       items=home_builder_enums.PANEL_HEIGHTS,
                                       default = '2131',
                                       update = update_corner_closet_height)

    closet = None
    
    def check(self, context):
        self.closet.obj_x.location.x = self.width
        self.closet.obj_y.location.y = -self.depth             
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_closet_inside_corner_bp(context.object)
        self.closet = data_closets.Closet_Inside_Corner(bp)
        self.width = self.closet.obj_x.location.x
        self.depth = math.fabs(self.closet.obj_y.location.y)      

    def set_default_heights(self):
        for i in range(1,9):
            opening_height_prompt = self.closet.get_prompt("Opening " + str(i) + " Height")
            if opening_height_prompt:
                opening_height = round(pc_unit.meter_to_millimeter(opening_height_prompt.get_value()),0)
                for index, height in enumerate(home_builder_enums.PANEL_HEIGHTS):
                    if not opening_height >= int(height[0]):
                        exec('self.opening_' + str(i) + '_height = home_builder_enums.PANEL_HEIGHTS[index - 1][0]')                                                                                                                                                                                                        
                        break

    def draw_product_size(self,layout):
        box = layout.box()
        row = box.row()
        
        col = row.column(align=True)
        row1 = col.row(align=True)
        row1.label(text='Width:')
        row1.prop(self,'width',text="")
        row1.prop(self.closet.obj_x,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        row1.label(text='Height:')
        row1.prop(self,'set_height',text="")
        row1.prop(self.closet.obj_z,'hide_viewport',text="")
        
        row1 = col.row(align=True)
        row1.label(text='Depth:')
        row1.prop(self,'depth',text="")
        row1.prop(self.closet.obj_y,'hide_viewport',text="")
            
        col = row.column(align=True)
        col.label(text="Location X:")
        col.label(text="Location Y:")
        col.label(text="Location Z:")
        
        col = row.column(align=True)
        col.prop(self.closet.obj_bp,'location',text="")
        
        is_hanging = self.closet.get_prompt("Is Hanging")
        
        if is_hanging:
            row = box.row()
            # row.label(text="Is Hanging")
            row.prop(is_hanging,'checkbox_value',text="Is Hanging")
            # is_hanging.draw_prompt(row)
            if is_hanging.get_value():
                row.prop(self.closet.obj_z,'location',index=2,text="Hanging Height")
        
        row = box.row()
        row.label(text='Rotation Z:')
        row.prop(self.closet.obj_bp,'rotation_euler',index=2,text="")  

    def draw_construction_prompts(self,layout):
        left_depth = self.closet.get_prompt("Left Depth")
        right_depth = self.closet.get_prompt("Right Depth")
        kick_height = self.closet.get_prompt("Closet Kick Height")
        kick_setback = self.closet.get_prompt("Closet Kick Setback")
        shelf_qty = self.closet.get_prompt("Shelf Quantity")
        back_width = self.closet.get_prompt("Back Width")

        box = layout.box()
        row = box.row()
        row.label(text="Left Depth")
        row.prop(left_depth,'distance_value',text="")
        row.label(text="Right Depth")
        row.prop(right_depth,'distance_value',text="")      

        row = box.row()
        row.label(text="Toe Kick")
        row.prop(kick_height,'distance_value',text="Height")
        row.prop(kick_setback,'distance_value',text="Setback")

        row = box.row()
        row.label(text="Shelf Quantity")
        row.prop(shelf_qty,'quantity_value',text="")

        row = box.row()
        row.label(text="Back Width")
        row.prop(back_width,'distance_value',text="Back Width")

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(layout)
        self.draw_construction_prompts(layout)


class home_builder_OT_closet_door_prompts(bpy.types.Operator):
    bl_idname = "home_builder.closet_door_prompts"
    bl_label = "Closet Door Prompts"

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    door_swing: bpy.props.EnumProperty(name="Door Swing",
                                       items=[('LEFT',"Left","Left Swing Door"),
                                              ('RIGHT',"Right","Right Swing Door"),
                                              ('DOUBLE',"Double","Double Door")])

    opening_1_height: bpy.props.EnumProperty(name="Opening 1 Height",
                                    items=home_builder_enums.PANEL_HEIGHTS,
                                    default = '2131')
    
    insert = None
    calculators = []

    def check(self, context):
        door_swing = self.insert.get_prompt("Door Swing")
        if self.door_swing == 'LEFT':
            door_swing.set_value(0)
        if self.door_swing == 'RIGHT':
            door_swing.set_value(1)
        if self.door_swing == 'DOUBLE':
            door_swing.set_value(2)         
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        door_swing = self.insert.get_prompt("Door Swing")
        if door_swing.get_value() == 0:
            self.door_swing = 'LEFT'
        if door_swing.get_value() == 1:
            self.door_swing = 'RIGHT'
        if door_swing.get_value() == 2:
            self.door_swing = 'DOUBLE'            
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_closet_doors_bp(context.object)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        hot = self.insert.get_prompt("Half Overlay Top")
        hob = self.insert.get_prompt("Half Overlay Bottom")
        hol = self.insert.get_prompt("Half Overlay Left")   
        hor = self.insert.get_prompt("Half Overlay Right")   
        open_door = self.insert.get_prompt("Open Door")  
        door_height = self.insert.get_prompt("Door Height") 
        turn_off_pulls = self.insert.get_prompt("Turn Off Pulls") 
        door_type = self.insert.get_prompt("Door Type")

        box = layout.box()
        row = box.row()
        row.label(text="Door Swing")      
        row.prop(self,'door_swing',expand=True) 
        if door_height:         
            row = box.row()
            row.label(text="Door Height")      
            row.prop(door_height,'distance_value',text="")          
        row = box.row()
        row.label(text="Open Door")      
        row.prop(open_door,'percentage_value',text="")  

        box = layout.box()
        box.label(text="Front Half Overlays")
        row = box.row()
        row.prop(hot,'checkbox_value',text="Top") 
        row.prop(hob,'checkbox_value',text="Bottom") 
        row.prop(hol,'checkbox_value',text="Left") 
        row.prop(hor,'checkbox_value',text="Right") 

        box = layout.box()
        box.label(text="Pulls")
        row = box.row()
        row.label(text="Turn Off Pulls")      
        row.prop(turn_off_pulls,'checkbox_value',text="")    
        if door_type.get_value() == "Base":
            vert_loc = self.insert.get_prompt("Base Pull Vertical Location")  
            row = box.row()
            row.label(text="Pull Location")               
            row.prop(vert_loc,'distance_value',text="")       
        if door_type.get_value() == "Tall":
            vert_loc = self.insert.get_prompt("Tall Pull Vertical Location")   
            row = box.row()
            row.label(text="Pull Location")               
            row.prop(vert_loc,'distance_value',text="")                  
        if door_type.get_value() == "Upper":
            vert_loc = self.insert.get_prompt("Upper Pull Vertical Location")         
            row = box.row()
            row.label(text="Pull Location")               
            row.prop(vert_loc,'distance_value',text="")   


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
        row = layout.row()
        props = row.operator('home_builder.show_hide_closet_opening',text="Show Opening")
        props.insert_obj_bp = self.insert.obj_bp.name
        props.hide = False
        props = row.operator('home_builder.show_hide_closet_opening',text="Hide Opening")
        props.insert_obj_bp = self.insert.obj_bp.name
        props.hide = True


class home_builder_OT_closet_single_shelf_prompts(bpy.types.Operator):
    bl_idname = "home_builder.closet_single_shelf_prompts"
    bl_label = "Closet Single Shelf Prompts"

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
        bp = home_builder_utils.get_single_shelf_bp(context.object)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        shelf_qty = self.insert.get_prompt("Shelf Quantity")
        layout.prop(self.insert.obj_bp,'location',index=2,text="Shelf Location")


class home_builder_OT_closet_cleat_prompts(bpy.types.Operator):
    bl_idname = "home_builder.closet_cleat_prompts"
    bl_label = "Closet Cleat Prompts"

    cleat_width: bpy.props.FloatProperty(name="Width",min=pc_unit.inch(1),unit='LENGTH',precision=4)

    part = None
    calculators = []

    def check(self, context):
        if self.part.obj_y.location.y > 0:
            self.part.obj_y.location.y = self.cleat_width
        else:
            self.part.obj_y.location.y = -self.cleat_width
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_cleat_bp(context.object)
        self.part = pc_types.Assembly(bp)
        self.cleat_width = math.fabs(self.part.obj_y.location.y)

    def draw(self, context):
        layout = self.layout
        inset = self.part.get_prompt("Cleat Inset")
        width = self.part.get_prompt("Cleat Width")
        row = layout.row()
        row.label(text="Cleat Inset")
        row.prop(inset,'distance_value',text="")
        row = layout.row()
        row.label(text="Cleat Width")
        row.prop(self,'cleat_width',text="")


class home_builder_OT_closet_back_prompts(bpy.types.Operator):
    bl_idname = "home_builder.closet_back_prompts"
    bl_label = "Closet Back Prompts"

    part = None
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
        bp = home_builder_utils.get_closet_back_bp(context.object)
        self.part = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        inset = self.part.get_prompt("Back Inset")
        row = layout.row()
        row.label(text="Back Inset")
        row.prop(inset,'distance_value',text="")


class home_builder_OT_hanging_rod_prompts(bpy.types.Operator):
    bl_idname = "home_builder.hanging_rod_prompts"
    bl_label = "Hanging Rod Prompts"

    insert = None

    def check(self, context):
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_hanging_rod_insert_bp(context.object)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        loc_from_top = self.insert.get_prompt("Hanging Rod Location From Top")
        bottom_rod_location = self.insert.get_prompt("Bottom Rod Location From Top")
        setback = self.insert.get_prompt("Hanging Rod Setback")
        if loc_from_top:
            layout.prop(loc_from_top,'distance_value',text="Rod Location From Top")
        if bottom_rod_location:
            layout.prop(bottom_rod_location,'distance_value',text="Bottom Rod Location")
        if setback:
            layout.prop(setback,'distance_value',text="Rod Setback")


class home_builder_OT_closet_wire_baskets_prompts(bpy.types.Operator):
    bl_idname = "home_builder.closet_wire_baskets_prompts"
    bl_label = "Closet Wire Baskets Prompts"

    insert = None

    def check(self, context):
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_closet_wire_baskets_bp(context.object)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        qty = self.insert.get_prompt("Wire Basket Quantity")
        spacing = self.insert.get_prompt("Vertical Spacing")

        box = layout.box()
        row = box.row()
        row.label(text="Wire Basket Quantity")
        row.prop(qty,'quantity_value',text="")

        for i in range(1,7):
            if qty.get_value() > i - 1:
                height = self.insert.get_prompt("Wire Basket " + str(i) + " Height")
                row = box.row()
                row.label(text="Height " + str(i))                
                row.prop(height,'distance_value',text="")

        box = layout.box()
        row = box.row()
        row.label(text="Vertical Spacing")
        row.prop(spacing,'distance_value',text="")

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
        drawer_height = self.insert.get_prompt("Drawer Height")
        remove_top_shelf = self.insert.get_prompt("Remove Top Shelf")
        
        total_drawer_height = 0
        if drawer_height:
            row = box.row()
            row.label(text="Drawer Height")
            row.prop(drawer_height,'distance_value',text="")
            total_drawer_height += drawer_height.get_value()
        if drawer_qty:
            row = box.row()
            row.label(text="Drawer Quantity")            
            row.prop(drawer_qty,'quantity_value',text="")
            for i in range(1,7):
                if drawer_qty.get_value() > i - 1:
                    drawer_height = self.insert.get_prompt("Drawer " + str(i) + " Height")
                    row = box.row()
                    row.label(text="Drawer " + str(i) + " Height")                      
                    row.prop(drawer_height,'distance_value',text="")
                    total_drawer_height += drawer_height.get_value()

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

        box = layout.box()
        row = box.row()
        row.label(text="Remove Top Shelf")
        row.prop(remove_top_shelf,'checkbox_value',text="")
        
        box = layout.box()
        height = round(pc_unit.meter_to_inch(total_drawer_height),2)
        row = box.row()
        row.label(text="Total Drawer Height: ")
        row.label(text=str(height) + '"')


class home_builder_OT_closet_cubby_prompts(bpy.types.Operator):
    bl_idname = "home_builder.closet_cubby_prompts"
    bl_label = "Closet Cubby Prompts"

    cubby_location: bpy.props.EnumProperty(name="Cubby Location",
                                           items=[('BOTTOM',"Bottom","Place on Bottom"),
                                                  ('TOP',"Top","Place on Top"),
                                                  ('FILL',"Fill","Fill Opening")])

    opening_1_height: bpy.props.EnumProperty(name="Opening 1 Height",
                                    items=home_builder_enums.PANEL_HEIGHTS,
                                    default = '2131')
    
    insert = None
    calculators = []

    def check(self, context):
        cubby_placement = self.insert.get_prompt("Cubby Placement")
        if self.cubby_location == 'BOTTOM':
            cubby_placement.set_value(0)
        if self.cubby_location == 'TOP':
            cubby_placement.set_value(1)
        if self.cubby_location == 'FILL':
            cubby_placement.set_value(2)         
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context)
        cubby_placement = self.insert.get_prompt("Cubby Placement")
        if cubby_placement.get_value() == 0:
            self.cubby_location = 'BOTTOM'
        if cubby_placement.get_value() == 1:
            self.cubby_location = 'TOP'
        if cubby_placement.get_value() == 2:
            self.cubby_location = 'FILL'            
        wm = context.window_manager        
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_closet_cubby_bp(context.object)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        layout = self.layout
        h_qty = self.insert.get_prompt("Horizontal Quantity")
        v_qty = self.insert.get_prompt("Vertical Quantity")
        c_height = self.insert.get_prompt("Cubby Height")
        c_setback = self.insert.get_prompt("Cubby Setback")
        row = layout.row()
        row.label(text="Location")
        row.prop(self,'cubby_location',expand=True)
        row = layout.row()
        row.label(text="Shelf Quantity")           
        row.prop(h_qty,'quantity_value',text="")
        row = layout.row()
        row.label(text="Division Quantity")           
        row.prop(v_qty,'quantity_value',text="")        
        row = layout.row()
        row.label(text="Cubby Height")        
        row.prop(c_height,'distance_value',text="")
        row = layout.row()
        row.label(text="Cubby Setback")           
        row.prop(c_setback,'distance_value',text="")


class home_builder_OT_change_closet_openings(bpy.types.Operator):
    bl_idname = "home_builder.change_closet_openings"
    bl_label = "Change Closet Openings"

    quantity: bpy.props.IntProperty(name="Quantity")

    closet = None
    new_closet = None
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

    def set_child_properties(self,obj):
        home_builder_utils.update_id_props(obj,self.new_closet.obj_bp)
        for child in obj.children:
            self.set_child_properties(child)

    def execute(self, context):
        parent = self.closet.obj_bp.parent
        x_loc = self.closet.obj_bp.location.x
        y_loc = self.closet.obj_bp.location.y
        z_loc = self.closet.obj_bp.location.z
        z_rot = self.closet.obj_bp.rotation_euler.z
        length = self.closet.obj_x.location.x
        pc_utils.delete_object_and_children(self.closet.obj_bp)

        self.new_closet = data_closets.Closet_Starter()
        self.new_closet.opening_qty = self.quantity
        self.new_closet.is_base = self.closet.is_base
        self.new_closet.is_hanging = self.closet.is_hanging
        self.new_closet.pre_draw()
        self.new_closet.draw()
        self.new_closet.obj_bp.parent = parent
        self.new_closet.obj_bp.location.x = x_loc
        self.new_closet.obj_bp.location.y = y_loc
        self.new_closet.obj_bp.location.z = z_loc
        self.new_closet.obj_bp.rotation_euler.z = z_rot
        self.new_closet.obj_x.location.x = length
        self.delete_reference_object(self.new_closet.obj_bp)
        self.get_calculators(self.new_closet.obj_bp)
        for calculator in self.calculators:
            calculator.calculate()
        self.new_closet.obj_bp.hide_viewport = True
        self.new_closet.obj_x.hide_viewport = True
        self.new_closet.obj_y.hide_viewport = True
        self.new_closet.obj_z.hide_viewport = True
        self.set_child_properties(self.new_closet.obj_bp)
            
        return {'FINISHED'}


class home_builder_OT_delete_closet_opening(bpy.types.Operator):
    bl_idname = "home_builder.delete_closet_opening"
    bl_label = "Delete Closet Opening"

    insert = None

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        bp = home_builder_utils.get_closet_insert_bp(context.object)
        if bp:
            return True
        else:
            return False

    def execute(self, context):    
        self.get_assemblies(context)
        props = home_builder_utils.get_object_props(self.insert.obj_bp)
        opening_bp = props.insert_opening
        pc_utils.delete_object_and_children(self.insert.obj_bp) 
        del(opening_bp["IS_FILLED"])
        for child in opening_bp.children:
            if child.type == 'MESH':
                child.hide_viewport = False
        return {'FINISHED'}

    def get_assemblies(self,context):
        bp = home_builder_utils.get_closet_insert_bp(context.object)
        self.insert = pc_types.Assembly(bp)


class home_builder_OT_splitter_prompts(bpy.types.Operator):
    bl_idname = "home_builder.splitter_prompts"
    bl_label = "Splitter Prompts"

    opening_1_height: bpy.props.EnumProperty(name="Opening 1 Height",
                                    items=home_builder_enums.PANEL_HEIGHTS,
                                    default = '2131')
    
    insert = None
    calculators = []

    def check(self, context): 
        for calculator in self.calculators:
            calculator.calculate()
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def invoke(self,context,event):
        self.get_assemblies(context) 
        self.get_calculators(self.insert.obj_bp)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_splitter_insert_bp(context.object)
        self.insert = pc_types.Assembly(bp)

    def get_number_of_equal_openings(self,name="Height"):
        number_of_equal_openings = 0
        
        for i in range(1,9):
            size = self.insert.get_prompt("Opening " + str(i) + " " + name)
            if size:
                number_of_equal_openings += 1 if size.equal else 0
            else:
                break
            
        return number_of_equal_openings

    def draw_prompts(self,layout,name="Height"):
        for i in range(1,10):
            opening = self.insert.get_prompt("Opening " + str(i) + " " + name)
            if opening:
                row = layout.row()
                if opening.equal == False:
                    row.prop(opening,'equal',text="")
                else:
                    if self.get_number_of_equal_openings(name=name) != 1:
                        row.prop(opening,'equal',text="")
                    else:
                        row.label(text="",icon='BLANK1')                
                row.label(text="Opening " + str(i) + " " + name + ":")
                if opening.equal:
                    row.label(text=str(pc_unit.meter_to_active_unit(opening.distance_value)) + '"')
                else:
                    row.prop(opening,'distance_value',text="")

    def draw(self, context):
        layout = self.layout
        self.draw_prompts(layout,name="Height")
        self.draw_prompts(layout,name="Width")


classes = (
    home_builder_OT_duplicate_closet_insert,
    home_builder_OT_closet_prompts,
    home_builder_OT_closet_inside_corner_prompts,
    home_builder_OT_closet_shelves_prompts,
    home_builder_OT_closet_cleat_prompts,
    home_builder_OT_closet_back_prompts,
    home_builder_OT_closet_single_shelf_prompts,
    home_builder_OT_hanging_rod_prompts,
    home_builder_OT_closet_door_prompts,
    home_builder_OT_closet_drawer_prompts,
    home_builder_OT_closet_cubby_prompts,
    home_builder_OT_closet_wire_baskets_prompts,
    home_builder_OT_change_closet_openings,
    home_builder_OT_delete_closet_opening,
    home_builder_OT_splitter_prompts,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()            