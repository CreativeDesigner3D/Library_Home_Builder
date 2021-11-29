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


class home_builder_OT_add_bottom_support_cleat(bpy.types.Operator):
    bl_idname = "home_builder.add_bottom_support_cleat"
    bl_label = "Add Bottom Support Cleat"

    part = None

    @classmethod
    def poll(cls, context):
        panels = []
        for obj in context.selected_objects:
            panel_bp = home_builder_utils.get_closet_panel_bp(obj)
            if panel_bp and panel_bp not in panels:
                panels.append(panel_bp) 
        if len(panels) >= 2:
            return True
        else:
            return False

    def get_closet_panels(self,context):
        panels = []
        for obj in context.selected_objects:
            panel_bp = home_builder_utils.get_closet_panel_bp(obj)
            if panel_bp and panel_bp not in panels:
                panels.append(panel_bp)
        panels.sort(key=lambda obj: obj.location.x, reverse=False)  
        return panels

    def set_child_properties(self,obj):
        home_builder_utils.update_id_props(obj,self.part.obj_bp)
        home_builder_utils.assign_current_material_index(obj)      
        for child in obj.children:
            self.set_child_properties(child)

    def add_cleat(self):
        path = os.path.join(home_builder_paths.get_assembly_path(),"Part.blend")
        self.part = pc_types.Assembly(filepath=path)
        self.part.obj_z.location.z = pc_unit.inch(-.75)
        self.part.obj_y.location.y = pc_unit.inch(4)
        self.part.obj_bp.rotation_euler.x = math.radians(-90)
        self.part.add_prompt("Cleat Inset",'DISTANCE',pc_unit.inch(.25))

        # self.exclude_objects.append(part.obj_bp)
        # for obj in part.obj_bp.children:
        #     self.exclude_objects.append(obj)

        self.part.set_name("Bottom Cleat")
        self.part.obj_bp['IS_BOTTOM_SUPPORT_CLEAT_BP'] = True
        self.part.obj_bp['IS_CUTPART_BP'] = True
        self.part.obj_bp['PROMPT_ID'] = 'home_builder.closet_bottom_support_cleat_prompts'
        self.set_child_properties(self.part.obj_bp)
        return self.part

    def execute(self, context):
        panels = self.get_closet_panels(context)
        cleat = self.add_cleat()
        panel1 = pc_types.Assembly(panels[0])
        panel2 = pc_types.Assembly(panels[-1])
        cleat.obj_bp.parent = panel1.obj_bp.parent
        cleat.obj_bp.location.z = max(panel1.obj_bp.location.z,panel2.obj_bp.location.z)
        overlay_left_panel = True
        overlay_right_panel = True
        if panel1.obj_x.location.x > panel2.obj_x.location.x:
            overlay_left_panel = False
        if panel1.obj_x.location.x < panel2.obj_x.location.x:
            overlay_right_panel = False

        if overlay_left_panel:
            cleat.obj_bp.location.x = panel1.obj_bp.location.x
        else:
            cleat.obj_bp.location.x = panel1.obj_bp.location.x + pc_unit.inch(.75)

        if panel2.obj_z.location.z > 0: #IS LAST PANEL
            cleat.obj_x.location.x = panel2.obj_bp.location.x - panel1.obj_bp.location.x
        else:
            cleat.obj_x.location.x = panel2.obj_bp.location.x - panel1.obj_bp.location.x + pc_unit.inch(.75)

        if not overlay_left_panel:
            cleat.obj_x.location.x -= pc_unit.inch(.75)

        if not overlay_right_panel:
            cleat.obj_x.location.x -= pc_unit.inch(.75)

        home_builder_pointers.assign_double_sided_pointers(cleat)
        home_builder_pointers.assign_materials_to_assembly(cleat)    
        cleat.obj_bp.hide_viewport = True    
        cleat.obj_x.hide_viewport = True    
        cleat.obj_y.hide_viewport = True    
        cleat.obj_z.hide_viewport = True    
        home_builder_utils.flip_normals(cleat)
        return {'FINISHED'}


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


class home_builder_OT_move_closet_insert(bpy.types.Operator):
    bl_idname = "home_builder.move_closet_insert"
    bl_label = "Move Closet Insert"

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
        insert = pc_types.Assembly(obj_bp)

        props = home_builder_utils.get_object_props(insert.obj_bp)
        opening_bp = props.insert_opening
        del(opening_bp["IS_FILLED"])
        for child in opening_bp.children:
            if child.type == 'MESH':
                child.hide_viewport = False

        self.select_obj_and_children(insert.obj_bp)
        self.hide_empties(insert.obj_bp)

        insert.obj_bp.parent = None
        self.delete_drivers(insert.obj_bp)
        self.delete_drivers(insert.obj_x)
        self.delete_drivers(insert.obj_y)
        self.delete_drivers(insert.obj_z)

        self.hide_empties(insert.obj_bp)

        bpy.ops.home_builder.place_closet_insert(obj_bp_name=insert.obj_bp.name)

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
    
    kick_height: bpy.props.EnumProperty(name="Kick Height",
                                    items=home_builder_enums.KICK_HEIGHTS,
                                    default = '96')

    closet = None
    calculators = []

    def reset_variables(self):
        #BLENDER CRASHES IF TAB IS SET TO EXTERIOR
        #THIS IS BECAUSE POPUP DIALOGS CANNOT DISPLAY UILISTS ON INVOKE
        self.product_tabs = 'MAIN'
        self.closet = None
        self.calculators = []

    def update_product_size(self,context):
        hb_props = home_builder_utils.get_scene_props(context.scene)
        self.closet.obj_x.location.x = self.width
        if hb_props.use_fixed_closet_heights:
            for i in range(1,9):
                opening_height = self.closet.get_prompt("Opening " + str(i) + " Height")
                if opening_height:
                    height = eval("float(self.opening_" + str(i) + "_height)/1000")
                    opening_height.set_value(height)

            kick_height = self.closet.get_prompt("Closet Kick Height")
            if kick_height:
                kick_height.distance_value = pc_unit.inch(float(self.kick_height) / 25.4)

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
        kick_height = self.closet.get_prompt("Closet Kick Height")
        if kick_height:
            value = round(kick_height.distance_value * 1000,1)
            for index, height in enumerate(home_builder_enums.KICK_HEIGHTS):
                if not value >= float(height[0]):
                    self.kick_height = home_builder_enums.KICK_HEIGHTS[index - 1][0]
                    break

    def check(self, context):
        self.update_product_size(context)
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
        hb_props = home_builder_utils.get_scene_props(context.scene)
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
        lfe = self.closet.get_prompt("Left Finished End")   
        rfe = self.closet.get_prompt("Right Finished End")   
        extend_panels_to_ctop = self.closet.get_prompt("Extend Panels to Countertop")   
        extend_panel_amount = self.closet.get_prompt("Extend Panel Amount") 
        
        row = layout.row()    
        row.label(text="Finished Ends:")
        row.prop(lfe,'checkbox_value',text="Left")    
        row.prop(rfe,'checkbox_value',text="Right")    

        row = layout.row()    
        row.label(text="Top Filler Panels:")
        col_l = row.column()
        col_l.prop(l_bridge,'checkbox_value',text="Left")
        if l_bridge.get_value():
            col_l.prop(l_bridge_width,'distance_value',text="Width")
        col_r = row.column()
        col_r.prop(r_bridge,'checkbox_value',text="Right")
        if r_bridge.get_value():
            col_r.prop(r_bridge_width,'distance_value',text="Width")

        row = layout.row()    
        row.label(text="Toe Kick:")
        if hb_props.use_fixed_closet_heights:
            row.prop(self,'kick_height',text="") 
        else:
            row.prop(kick_height,'distance_value',text="Height")    
        row.prop(kick_setback,'distance_value',text="Setback")    

        row = layout.row()   
        row.label(text="Fillers:") 
        row.prop(l_filler,'distance_value',text="Left Width")
        row.prop(r_filler,'distance_value',text="Right Width")

        row = layout.row()   
        row.label(text="Panels to Countertop:") 
        row.prop(extend_panels_to_ctop,'checkbox_value',text="Extend")
        if extend_panels_to_ctop.checkbox_value:
            row.prop(extend_panel_amount,'distance_value',text="Distance")
        else:
            row.label(text="")

        if ctop_oh_front and ctop_oh_left and ctop_oh_right:
            row = layout.row()   
            row.label(text="Countertop Overhang:") 
            row.prop(ctop_oh_front,'distance_value',text="Front")
            row.prop(ctop_oh_left,'distance_value',text="Left")
            row.prop(ctop_oh_right,'distance_value',text="Right")

        row = layout.row()  
        row.label(text="Remove Bottom:")
        for i in range(1,9):
            remove_bottom = self.closet.get_prompt("Remove Bottom " + str(i))
            if remove_bottom:
                row.prop(remove_bottom,'checkbox_value',text=str(i))

        row = layout.row()  
        row.label(text="Double Panels:")
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
        unit_settings = context.scene.unit_settings
        hb_props = home_builder_utils.get_scene_props(context.scene)

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
                
                if width.equal:
                    value = pc_unit.unit_to_string(unit_settings,width.distance_value)  
                    row.label(text=value)
                else:
                    row.prop(width,'distance_value',text="")
                
                if hb_props.use_fixed_closet_heights:
                    row.prop(self,'opening_' + str(i) + '_height',text="")
                else:
                    row.prop(height,'distance_value',text="")

                if self.is_base:
                    value = pc_unit.unit_to_string(unit_settings,depth.distance_value) 
                    row.label(text=value)
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
        flip_back_support_location = self.closet.get_prompt("Flip Back Support Location")

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
        row.prop(back_width,'distance_value',text="")

        if flip_back_support_location:
            row.prop(flip_back_support_location,'checkbox_value',text="Flip")

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

    door_opening_height: bpy.props.EnumProperty(name="Door Opening Height",
                                    items=home_builder_enums.OPENING_HEIGHTS,
                                    default = '716.95')
    
    insert = None
    calculators = []

    def check(self, context):
        hb_props = home_builder_utils.get_scene_props(context.scene)
        if hb_props.use_fixed_closet_heights:
            insert_height = self.insert.get_prompt("Door Height")
            if insert_height:
                insert_height.distance_value = pc_unit.inch(float(self.door_opening_height) / 25.4)

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

    def set_properties_from_prompts(self):
        hb_props = home_builder_utils.get_scene_props(bpy.context.scene)
        if hb_props.use_fixed_closet_heights:        
            door_height = self.insert.get_prompt("Door Height")
            if door_height:
                value = round(door_height.distance_value * 1000,2)
                for index, height in enumerate(home_builder_enums.OPENING_HEIGHTS):
                    if not value >= float(height[0]):
                        self.door_opening_height = home_builder_enums.OPENING_HEIGHTS[index - 1][0]
                        break
        door_swing = self.insert.get_prompt("Door Swing")
        if door_swing.get_value() == 0:
            self.door_swing = 'LEFT'
        if door_swing.get_value() == 1:
            self.door_swing = 'RIGHT'
        if door_swing.get_value() == 2:
            self.door_swing = 'DOUBLE' 

    def invoke(self,context,event):
        self.get_assemblies(context)
        self.set_properties_from_prompts()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_closet_doors_bp(context.object)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        hb_props = home_builder_utils.get_scene_props(context.scene)
              
        layout = self.layout
        hot = self.insert.get_prompt("Half Overlay Top")
        hob = self.insert.get_prompt("Half Overlay Bottom")
        hol = self.insert.get_prompt("Half Overlay Left")   
        hor = self.insert.get_prompt("Half Overlay Right")   
        open_door = self.insert.get_prompt("Open Door")  
        door_height = self.insert.get_prompt("Door Height") 
        turn_off_pulls = self.insert.get_prompt("Turn Off Pulls") 
        door_type = self.insert.get_prompt("Door Type")
        fill_opening = self.insert.get_prompt("Fill Opening")
        s_qty = self.insert.get_prompt("Shelf Quantity")

        box = layout.box()
        row = box.row()
        row.label(text="Door Swing")      
        row.prop(self,'door_swing',expand=True) 
        if door_height:         
            if fill_opening:
                row = box.row()
                row.label(text="Fill Opening")
                row.prop(fill_opening,'checkbox_value',text="")   

                if fill_opening.get_value() == False:
                    row = box.row()
                    if hb_props.use_fixed_closet_heights:  
                        row.label(text="Door Opening Height")      
                        row.prop(self,'door_opening_height',text="") 
                    else:
                        row.label(text="Door Opening Height")      
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

        box = layout.box()
        row = box.row()
        row.label(text="Shelf Quantity")      
        row.prop(s_qty,'quantity_value',text="")         


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


class home_builder_OT_closet_bottom_support_cleat_prompts(bpy.types.Operator):
    bl_idname = "home_builder.closet_bottom_support_cleat_prompts"
    bl_label = "Closet Bottom Support Cleat Prompts"

    cleat_width: bpy.props.FloatProperty(name="Width",min=pc_unit.inch(1),unit='LENGTH',precision=4)
    cleat_x_location: bpy.props.FloatProperty(name="Cleat X Location",unit='LENGTH',precision=4)
    cleat_length: bpy.props.FloatProperty(name="Cleat Length",unit='LENGTH',precision=4)

    left_overhang: bpy.props.FloatProperty(name="Left Overhang",unit='LENGTH',precision=4)
    right_overhang: bpy.props.FloatProperty(name="Right Overhang",unit='LENGTH',precision=4)

    part = None
    calculators = []

    def check(self, context):
        self.part.obj_bp.location.x = self.cleat_x_location - self.left_overhang
        self.part.obj_x.location.x = self.cleat_length + self.left_overhang + self.right_overhang
        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self,context,event):
        self.left_overhang = 0
        self.right_overhang = 0
        self.get_assemblies(context)
        self.cleat_length = self.part.obj_x.location.x
        self.cleat_x_location = self.part.obj_bp.location.x
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_closet_bottom_support_cleat_bp(context.object)
        self.part = pc_types.Assembly(bp)
        self.cleat_width = math.fabs(self.part.obj_y.location.y)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Left Overhang")
        row.prop(self,'left_overhang',text="")
        row = layout.row()
        row.label(text="Right Overhang")
        row.prop(self,'right_overhang',text="")


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

    top_opening_height: bpy.props.EnumProperty(name="Top Opening Height",
                                    items=home_builder_enums.OPENING_HEIGHTS,
                                    default = '716.95')

    insert = None

    def check(self, context):
        self.insert.obj_prompts.hide_viewport = False
        hb_props = home_builder_utils.get_scene_props(context.scene)
        if hb_props.use_fixed_closet_heights:
            top_opening_height = self.insert.get_prompt("Top Opening Height")
            if top_opening_height:
                top_opening_height.distance_value = pc_unit.inch(float(self.top_opening_height) / 25.4)
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def set_properties_from_prompts(self):
        hb_props = home_builder_utils.get_scene_props(bpy.context.scene)
        if hb_props.use_fixed_closet_heights:        
            top_opening_height = self.insert.get_prompt("Top Opening Height")
            if top_opening_height:
                value = round(top_opening_height.distance_value * 1000,2)
                for index, height in enumerate(home_builder_enums.OPENING_HEIGHTS):
                    if not value >= float(height[0]):
                        self.top_opening_height = home_builder_enums.OPENING_HEIGHTS[index - 1][0]
                        break

    def invoke(self,context,event):
        self.get_assemblies(context)
        self.set_properties_from_prompts()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=230)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_hanging_rod_insert_bp(context.object)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        hb_props = home_builder_utils.get_scene_props(bpy.context.scene)
        layout = self.layout
        loc_from_top = self.insert.get_prompt("Hanging Rod Location From Top")
        top_opening_height = self.insert.get_prompt("Top Opening Height")
        setback = self.insert.get_prompt("Hanging Rod Setback")
        if top_opening_height:
            if hb_props.use_fixed_closet_heights:
                row = layout.row()
                row.label(text="Top Opening Height")
                row.prop(self,'top_opening_height',text="") 
            else:
                layout.prop(top_opening_height,'distance_value',text="Top Opening Height")        
        if loc_from_top:
            layout.prop(loc_from_top,'distance_value',text="Rod Location From Top")
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

    drawer_qty: bpy.props.EnumProperty(name="Drawer Quantity",
                          items=[('1',"1","1 Drawer"),
                                 ('2',"2","2 Drawer"),
                                 ('3',"3","3 Drawer"),
                                 ('4',"4","4 Drawer"),
                                 ('5',"5","5 Drawer"),
                                 ('6',"6","6 Drawer"),
                                 ('7',"7","7 Drawer"),
                                 ('8',"8","8 Drawer")],
                          default='3')

    front_1_height: bpy.props.EnumProperty(name="Front 1 Height",
                                    items=home_builder_enums.FRONT_HEIGHTS,
                                    default = '140.95')

    front_2_height: bpy.props.EnumProperty(name="Front 2 Height",
                                    items=home_builder_enums.FRONT_HEIGHTS,
                                    default = '140.95')

    front_3_height: bpy.props.EnumProperty(name="Front 3 Height",
                                    items=home_builder_enums.FRONT_HEIGHTS,
                                    default = '140.95')

    front_4_height: bpy.props.EnumProperty(name="Front 4 Height",
                                    items=home_builder_enums.FRONT_HEIGHTS,
                                    default = '140.95')

    front_5_height: bpy.props.EnumProperty(name="Front 5 Height",
                                    items=home_builder_enums.FRONT_HEIGHTS,
                                    default = '140.95')

    front_6_height: bpy.props.EnumProperty(name="Front 6 Height",
                                    items=home_builder_enums.FRONT_HEIGHTS,
                                    default = '140.95')      

    front_7_height: bpy.props.EnumProperty(name="Front 7 Height",
                                    items=home_builder_enums.FRONT_HEIGHTS,
                                    default = '140.95')

    front_8_height: bpy.props.EnumProperty(name="Front 8 Height",
                                    items=home_builder_enums.FRONT_HEIGHTS,
                                    default = '140.95')   

    insert = None
    calculators = []

    def check(self, context):
        self.update_front_height_size(context)
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def update_front_height_size(self,context):
        hb_props = home_builder_utils.get_scene_props(context.scene)
        drawer_height = self.insert.get_prompt("Drawer Height")
        if drawer_height:             
            if hb_props.use_fixed_closet_heights:
                height = eval("float(self.front_1_height)/1000")
                drawer_height.set_value(height)
        else:
            drawer_qty = self.insert.get_prompt("Drawer Quantity")
            drawer_qty.set_value(int(self.drawer_qty))             
            if hb_props.use_fixed_closet_heights:
                for i in range(1,9):
                    drawer_height = self.insert.get_prompt("Drawer " + str(i) + " Height")
                    if drawer_height:                        
                        height = eval("float(self.front_" + str(i) + "_height)/1000")
                        drawer_height.set_value(height)

    def set_default_front_size(self):
        drawer_height = self.insert.get_prompt("Drawer Height")
        if drawer_height:
            front_height = round(drawer_height.distance_value * 1000,2)
            for index, height in enumerate(home_builder_enums.FRONT_HEIGHTS):
                if not front_height >= float(height[0]):
                    exec("self.front_1_height = home_builder_enums.FRONT_HEIGHTS[index - 1][0]")
                    break                
        else:
            drawer_qty = self.insert.get_prompt("Drawer Quantity")
            self.drawer_qty = str(drawer_qty.get_value())               
            for i in range(1,9):
                drawer_height_prompt = self.insert.get_prompt("Drawer " + str(i) + " Height")
                if drawer_height_prompt:
                    front_height = round(drawer_height_prompt.distance_value * 1000,2)
                    for index, height in enumerate(home_builder_enums.FRONT_HEIGHTS):
                        if not front_height >= float(height[0]):
                            exec('self.front_' + str(i) + '_height = home_builder_enums.FRONT_HEIGHTS[index - 1][0]')                                                                                                                                                                                                        
                            break

    def invoke(self,context,event):
        self.get_assemblies(context)
        self.set_default_front_size()
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_closet_drawers_bp(context.object)
        self.insert = pc_types.Assembly(bp)

    def draw(self, context):
        hb_props = home_builder_utils.get_scene_props(context.scene)
        layout = self.layout
        box = layout.box()
        open_drawer = self.insert.get_prompt("Open Drawer")
        drawer_qty = self.insert.get_prompt("Drawer Quantity")
        drawer_height = self.insert.get_prompt("Drawer Height")
        remove_top_shelf = self.insert.get_prompt("Remove Top Shelf")
        
        total_drawer_height = 0
        if drawer_height:
            row = box.row()
            row.label(text="Drawer Height")
            if hb_props.use_fixed_closet_heights:
                row.prop(self,'front_1_height',text="")
            else:
                row.prop(drawer_height,'distance_value',text="")
            total_drawer_height += drawer_height.get_value()
        if drawer_qty:
            row = box.row()
            row.label(text="Qty")            
            row.prop(self,'drawer_qty',expand=True)
            for i in range(1,9):
                if drawer_qty.get_value() > i - 1:
                    if hb_props.use_fixed_closet_heights:
                        drawer_height = self.insert.get_prompt("Drawer " + str(i) + " Height")
                        row = box.row()
                        row.label(text="Drawer " + str(i) + " Height")                      
                        row.prop(self,'front_' + str(i) + '_height',text="")
                    else:
                        drawer_height = self.insert.get_prompt("Drawer " + str(i) + " Height")
                        row = box.row()
                        row.label(text="Drawer " + str(i) + " Height")                      
                        row.prop(drawer_height,'distance_value',text="")
                    total_drawer_height += drawer_height.get_value()
            row = box.row()
            row.label(text="Open Drawer")
            row.prop(open_drawer,'percentage_value',text="")

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

    cubby_height: bpy.props.EnumProperty(name="Cubby Height",
                                    items=home_builder_enums.OPENING_HEIGHTS,
                                    default = '716.95')
    
    insert = None
    calculators = []

    def check(self, context):
        self.insert.obj_prompts.hide_viewport = False
        hb_props = home_builder_utils.get_scene_props(context.scene)
        if hb_props.use_fixed_closet_heights:
            cubby_height = self.insert.get_prompt("Cubby Height")
            if cubby_height:
                cubby_height.distance_value = pc_unit.inch(float(self.cubby_height) / 25.4)  

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

    def set_properties_from_prompts(self):
        hb_props = home_builder_utils.get_scene_props(bpy.context.scene)
        if hb_props.use_fixed_closet_heights:        
            cubby_height = self.insert.get_prompt("Cubby Height")
            if cubby_height:
                value = round(cubby_height.distance_value * 1000,2)
                for index, height in enumerate(home_builder_enums.OPENING_HEIGHTS):
                    if not value >= float(height[0]):
                        self.cubby_height = home_builder_enums.OPENING_HEIGHTS[index - 1][0]
                        break

        cubby_placement = self.insert.get_prompt("Cubby Placement")
        if cubby_placement.get_value() == 0:
            self.cubby_location = 'BOTTOM'
        if cubby_placement.get_value() == 1:
            self.cubby_location = 'TOP'
        if cubby_placement.get_value() == 2:
            self.cubby_location = 'FILL'  

    def invoke(self,context,event):
        self.get_assemblies(context)
        self.set_properties_from_prompts()
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
        if self.cubby_location != 'FILL':
            hb_props = home_builder_utils.get_scene_props(bpy.context.scene)
            if hb_props.use_fixed_closet_heights:  
                row = layout.row()
                row.label(text="Cubby Height")        
                row.prop(self,'cubby_height',text="")
            else:
                row = layout.row()
                row.label(text="Cubby Height")        
                row.prop(c_height,'distance_value',text="")
        row = layout.row()
        row.label(text="Shelf Quantity")           
        row.prop(h_qty,'quantity_value',text="")
        row = layout.row()
        row.label(text="Division Quantity")           
        row.prop(v_qty,'quantity_value',text="")        
        row = layout.row()
        row.label(text="Cubby Setback")           
        row.prop(c_setback,'distance_value',text="")


class home_builder_OT_change_closet_openings(bpy.types.Operator):
    bl_idname = "home_builder.change_closet_openings"
    bl_label = "Change Closet Openings"

    change_type: bpy.props.EnumProperty(name="Change Type",
                                        items=[('SET_QUANTITY',"Set Quantity","Set Quantity"),
                                               ('ADD_REMOVE_LAST',"Add/Remove Last Opening","Add/Remove Last Opening")])

    quantity: bpy.props.IntProperty(name="Quantity",min=1,max=8)

    closet = None
    new_closet = None
    calculators = []

    def check(self, context):
        obj = context.object
        closet_bp = home_builder_utils.get_closet_bp(obj)
        self.closet = data_closets.Closet_Starter(closet_bp) 
        return True

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
        row.prop(self,'change_type',expand=True)
        if self.change_type == 'ADD_REMOVE_LAST':
            row = layout.row()
            row.operator('home_builder.delete_closet_opening',text="Delete Last Opening",icon='X')
            row.operator('home_builder.add_closet_opening',text="Add Opening",icon='ADD')            
        else:
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
        if self.change_type == 'SET_QUANTITY' and self.closet.obj_bp:
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

            self.new_closet.obj_bp.hide_viewport = False
            context.view_layer.objects.active = self.new_closet.obj_bp
            self.new_closet.obj_bp.select_set(True)
            
        return {'FINISHED'}


class home_builder_OT_delete_closet_insert(bpy.types.Operator):
    bl_idname = "home_builder.delete_closet_insert"
    bl_label = "Delete Closet insert"

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


class home_builder_OT_add_closet_opening(bpy.types.Operator):
    bl_idname = "home_builder.add_closet_opening"
    bl_label = "Add Closet Opening"

    closet = None

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        bp = home_builder_utils.get_closet_bp(context.object)
        if bp:
            closet = data_closets.Closet_Starter(bp)
            if closet.opening_qty == 1:
                return False
            elif closet.opening_qty == 8:
                return False
            else:
                if closet.obj_prompts:
                    return True
                else:
                    return False
        else:
            return False

    def get_number_of_openings(self):
        for i in range(1,10):
            width = self.closet.get_prompt('Opening ' + str(i) + ' Width')
            if not width:
                return i - 1

    def get_closet_panels(self):
        panels = []
        for child in self.closet.obj_bp.children:
            if 'IS_PANEL_BP' in child:
                panels.append(child)
        panels.sort(key=lambda obj: obj.location.x, reverse=False)        
        return panels

    def get_closet_partitions(self):
        panels = []
        for child in self.closet.obj_bp.children:
            if 'IS_CLOSET_PARTITION_BP' in child:
                panels.append(child)
        panels.sort(key=lambda obj: obj.location.x, reverse=False)        
        return panels

    def get_last_opening_defaults(self):  
        opening_qty = self.closet.opening_qty   
        width = self.closet.get_prompt("Opening " + str(opening_qty) + " Width").get_value()
        height = self.closet.get_prompt("Opening " + str(opening_qty) + " Height").get_value()
        depth = self.closet.get_prompt("Opening " + str(opening_qty) + " Depth").get_value()
        floor = self.closet.get_prompt("Opening " + str(opening_qty) + " Floor Mounted").get_value()
        remove_bottom = self.closet.get_prompt("Remove Bottom " + str(opening_qty)).get_value()
        return [width,height,depth,floor,remove_bottom]

    def add_opening(self,qty):
        props = home_builder_utils.get_scene_props(bpy.context.scene)
        defaults = self.get_last_opening_defaults()
        center_partitions = self.get_closet_partitions()
        panels = self.get_closet_panels()
        self.closet.opening_qty = qty+1
        self.closet.add_opening_prompts(qty+1)
        self.closet.add_prompt("Double Panel " + str(qty),'CHECKBOX',False) 
        new_panel = self.closet.add_panel(qty,pc_types.Assembly(center_partitions[-1]))
        self.closet.add_top_and_bottom_shelf(qty+1,new_panel,pc_types.Assembly(panels[-1]))
        self.closet.add_toe_kick(qty+1,new_panel,pc_types.Assembly(panels[-1]))
        self.closet.add_opening(qty+1,new_panel,pc_types.Assembly(panels[-1]))
        if props.show_closet_panel_drilling:
            self.closet.add_system_holes(qty+1,new_panel,pc_types.Assembly(panels[-1])) 
        self.closet.update_last_panel_formulas(pc_types.Assembly(panels[-1]))  
        width = self.closet.get_prompt("Opening " + str(qty+1) + " Width")
        height = self.closet.get_prompt("Opening " + str(qty+1) + " Height")
        depth = self.closet.get_prompt("Opening " + str(qty+1) + " Depth")
        floor = self.closet.get_prompt("Opening " + str(qty+1) + " Floor Mounted")
        remove_bottom = self.closet.get_prompt("Remove Bottom " + str(qty+1))
        width.set_value(defaults[0])
        height.set_value(defaults[1])
        depth.set_value(defaults[2])
        floor.set_value(defaults[3])
        remove_bottom.set_value(defaults[4])
        self.closet.update_calculator_formula()
        
    def execute(self, context):    
        self.get_assemblies(context)
        number_of_openings = self.get_number_of_openings()
        self.add_opening(number_of_openings)
        return {'FINISHED'}

    def get_assemblies(self,context):
        bp = home_builder_utils.get_closet_bp(context.object)
        self.closet = data_closets.Closet_Starter(bp)


class home_builder_OT_delete_closet_opening(bpy.types.Operator):
    bl_idname = "home_builder.delete_closet_opening"
    bl_label = "Delete Closet Opening"

    closet = None

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        bp = home_builder_utils.get_closet_bp(context.object)
        if bp:
            closet = data_closets.Closet_Starter(bp)
            if closet.opening_qty == 1:
                return False
            else:            
                if closet.obj_prompts:
                    return True
                else:
                    return False
        else:
            return False

    def get_number_of_openings(self):
        if self.closet.obj_prompts:
            for i in range(1,10):
                width = self.closet.get_prompt('Opening ' + str(i) + ' Width')
                if not width:
                    return i - 1

    def get_closet_panels(self):
        panels = []
        for child in self.closet.obj_bp.children:
            if 'IS_PANEL_BP' in child:
                panel = pc_types.Assembly(child)
                hide = panel.get_prompt("Hide").get_value()
                if not hide:
                    panels.append(child)
        panels.sort(key=lambda obj: obj.location.x, reverse=False)        
        return panels

    def get_closet_partitions(self):
        panels = []
        for child in self.closet.obj_bp.children:
            if 'IS_CLOSET_PARTITION_BP' in child:
                panel = pc_types.Assembly(child)
                hide = panel.get_prompt("Hide").get_value()
                if not hide:                
                    panels.append(child)
        panels.sort(key=lambda obj: obj.location.x, reverse=False)        
        return panels

    def delete_opening(self,opening_number):
        calculator = self.closet.get_calculator("Opening Calculator")
        panels = self.get_closet_panels()
        center_panels = self.get_closet_partitions()
        for child in self.closet.obj_bp.children:
            props = home_builder_utils.get_object_props(child)
            if props.opening_number == opening_number:
                pc_utils.delete_object_and_children(child)
        pc_utils.delete_object_and_children(center_panels[-1])
        self.closet.update_last_panel_formulas(pc_types.Assembly(panels[-1])) 
        calculator.prompts.remove(opening_number-1)
        self.closet.obj_prompts.pyclone.delete_prompt("Opening " + str(opening_number) + " Height")
        self.closet.obj_prompts.pyclone.delete_prompt("Opening " + str(opening_number) + " Depth")
        self.closet.obj_prompts.pyclone.delete_prompt("Opening " + str(opening_number) + " Floor Mounted")
        self.closet.obj_prompts.pyclone.delete_prompt("Remove Bottom " + str(opening_number))
        self.closet.obj_prompts.pyclone.delete_prompt("Double Panel " + str(opening_number-1))
        self.closet.update_calculator_formula()

    def execute(self, context):    
        self.get_assemblies(context)
        number_of_openings = self.get_number_of_openings()
        self.closet.opening_qty = number_of_openings - 1
        self.delete_opening(number_of_openings)
        self.closet.obj_bp.hide_viewport = True
        self.closet.obj_bp.select_set(True)
        return {'FINISHED'}

    def get_assemblies(self,context):
        bp = home_builder_utils.get_closet_bp(context.object)
        self.closet = data_closets.Closet_Starter(bp)
        print(self.closet.obj_prompts)


class home_builder_OT_splitter_prompts(bpy.types.Operator):
    bl_idname = "home_builder.splitter_prompts"
    bl_label = "Splitter Prompts"

    opening_1_height: bpy.props.EnumProperty(name="Opening 1 Height",
                                    items=home_builder_enums.OPENING_HEIGHTS,
                                    default = '716.95')
    
    opening_2_height: bpy.props.EnumProperty(name="Opening 2 Height",
                                    items=home_builder_enums.OPENING_HEIGHTS,
                                    default = '716.95')

    opening_3_height: bpy.props.EnumProperty(name="Opening 3 Height",
                                    items=home_builder_enums.OPENING_HEIGHTS,
                                    default = '716.95')

    opening_4_height: bpy.props.EnumProperty(name="Opening 4 Height",
                                    items=home_builder_enums.OPENING_HEIGHTS,
                                    default = '716.95')

    opening_5_height: bpy.props.EnumProperty(name="Opening 5 Height",
                                    items=home_builder_enums.OPENING_HEIGHTS,
                                    default = '716.95')

    insert = None
    calculators = []

    def check(self, context): 
        hb_props = home_builder_utils.get_scene_props(context.scene)
        if hb_props.use_fixed_closet_heights:
            for i in range(1,6):
                opening = self.insert.get_prompt("Opening " + str(i) + " Height")
                if opening:
                    height = eval("float(self.opening_" + str(i) + "_height)/1000")
                    opening.set_value(height)        
        for calculator in self.calculators:
            calculator.calculate()
        return True

    def execute(self, context):                   
        return {'FINISHED'}

    def set_properties_from_prompts(self):
        hb_props = home_builder_utils.get_scene_props(bpy.context.scene)
        if hb_props.use_fixed_closet_heights:        
            for i in range(1,6):
                opening = self.insert.get_prompt("Opening " + str(i) + " Height")
                if opening:
                    value = round(opening.distance_value * 1000,2)
                    for index, height in enumerate(home_builder_enums.OPENING_HEIGHTS):
                        if not value >= float(height[0]):
                            exec("self.opening_" + str(i) + "_height = home_builder_enums.OPENING_HEIGHTS[index - 1][0]")
                            break

    def invoke(self,context,event):
        self.get_assemblies(context) 
        self.get_calculators(self.insert.obj_bp)
        self.set_properties_from_prompts()
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
        hb_props = home_builder_utils.get_scene_props(bpy.context.scene)
        unit_settings = bpy.context.scene.unit_settings
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
                    value = pc_unit.unit_to_string(unit_settings,opening.distance_value)
                    row.label(text=value)
                else:
                    if name == 'Height':
                        if hb_props.use_fixed_closet_heights:
                            row.prop(self,'opening_' + str(i) + '_height',text="")
                        else:
                            row.prop(opening,'distance_value',text="")
                    else:
                        row.prop(opening,'distance_value',text="")

    def draw(self, context):
        layout = self.layout
        self.draw_prompts(layout,name="Height")
        self.draw_prompts(layout,name="Width")


classes = (
    home_builder_OT_add_bottom_support_cleat,
    home_builder_OT_duplicate_closet_insert,
    home_builder_OT_move_closet_insert,
    home_builder_OT_closet_prompts,
    home_builder_OT_closet_inside_corner_prompts,
    home_builder_OT_closet_shelves_prompts,
    home_builder_OT_closet_cleat_prompts,
    home_builder_OT_closet_back_prompts,
    home_builder_OT_closet_bottom_support_cleat_prompts,
    home_builder_OT_closet_single_shelf_prompts,
    home_builder_OT_hanging_rod_prompts,
    home_builder_OT_closet_door_prompts,
    home_builder_OT_closet_drawer_prompts,
    home_builder_OT_closet_cubby_prompts,
    home_builder_OT_closet_wire_baskets_prompts,
    home_builder_OT_change_closet_openings,
    home_builder_OT_delete_closet_insert,
    home_builder_OT_add_closet_opening,
    home_builder_OT_delete_closet_opening,
    home_builder_OT_splitter_prompts,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()            