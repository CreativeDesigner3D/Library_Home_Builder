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
from . import data_cabinet_parts
from .. import home_builder_utils
from .. import home_builder_paths
from .. import home_builder_enums
from .. import home_builder_pointers


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

    position: bpy.props.EnumProperty(name="Position",
                                     items=[('OFF',"Off","Turn off automatic positioning"),
                                            ('LEFT',"Left","Bump Left"),
                                            ('RIGHT',"Right","Bump Right"),
                                            ('FILL',"Fill","Fill Area")])

    default_width = 0
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
                if carcass.design_base_assembly:                                                     
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
        self.default_width = self.cabinet.obj_x.location.x
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

        # props = home_builder_utils.get_scene_props(context.scene)
        # row = box.row()
        # row.alignment = 'LEFT'
        # row.prop(props,'show_cabinet_placement_options',emboss=False,icon='TRIA_DOWN' if props.show_cabinet_placement_options else 'TRIA_RIGHT')
        # if props.show_cabinet_placement_options:
        #     row = box.row()
        #     row.label(text="Anchor X:")
        #     row.prop(self,'anchor_x',expand=True)
        #     row = box.row()
        #     row.label(text="Anchor Z:")
        #     row.prop(self,'anchor_z',expand=True)            

    def draw_carcass_prompts(self,layout,context):
        for carcass in self.cabinet.carcasses:
            left_finished_end = carcass.get_prompt("Left Finished End")
            right_finished_end = carcass.get_prompt("Right Finished End")
            finished_back = carcass.get_prompt("Finished Back")
            finished_top = carcass.get_prompt("Finished Top")
            finished_bottom = carcass.get_prompt("Finished Bottom")
            toe_kick_height = carcass.get_prompt("Toe Kick Height")
            toe_kick_setback = carcass.get_prompt("Toe Kick Setback")
            blind_panel_location = carcass.get_prompt("Blind Panel Location")
            blind_panel_width = carcass.get_prompt("Blind Panel Width")
            blind_panel_reveal = carcass.get_prompt("Blind Panel Reveal")
            # add_bottom_light = carcass.get_prompt("Add Bottom Light")
            # add_top_light = carcass.get_prompt("Add Top Light")
            # add_side_light = carcass.get_prompt("Add Side Light")
  
            col = layout.column(align=True)
            box = col.box()
            row = box.row()
            row.label(text="Carcass - " + carcass.obj_bp.name)

            if blind_panel_location and blind_panel_width and blind_panel_reveal:
                row = box.row()
                blind_panel_location.draw(row,allow_edit=False)  
                row = box.row()
                row.label(text="Blind Options:")  
                row.prop(blind_panel_width,'distance_value',text="Width")
                row.prop(blind_panel_reveal,'distance_value',text="Reveal")  

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


class home_builder_OT_place_wall_cabinet(bpy.types.Operator):
    bl_idname = "home_builder.place_wall_cabinet"
    bl_label = "Place Wall Cabinet"

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name",default="")
    
    allow_fills: bpy.props.BoolProperty(name="Allow Fills",default=True)
    allow_quantities: bpy.props.BoolProperty(name="Allow Quantities",default=True)

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    position: bpy.props.EnumProperty(name="Position",
                                     items=[('SELECTED_POINT',"Selected Point","Turn off automatic positioning"),
                                            ('FILL',"Fill","Fill"),
                                            ('FILL_LEFT',"Fill Left","Fill Left"),
                                            ('LEFT',"Left","Bump Left"),
                                            ('CENTER',"Center","Center"),
                                            ('RIGHT',"Right","Bump Right"),
                                            ('FILL_RIGHT',"Fill Right","Fill Right")],
                                     default='SELECTED_POINT')

    quantity: bpy.props.IntProperty(name="Quantity",default=1)
    left_offset: bpy.props.FloatProperty(name="Left Offset", default=0,subtype='DISTANCE')
    right_offset: bpy.props.FloatProperty(name="Right Offset", default=0,subtype='DISTANCE')

    default_width = 0
    selected_location = 0

    cabinet = None
    qty_cage = None

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        obj_bp = home_builder_utils.get_wall_bp(context.object)
        if obj_bp:
            return True
        else:
            return False

    def reset_variables(self):
        self.quantity = 1
        self.cabinet = None
        self.position = 'SELECTED_POINT'
        self.qty_cage = None

    def set_product_defaults(self):
        self.cabinet.obj_bp.location.x = self.selected_location + self.left_offset
        self.cabinet.obj_x.location.x = self.default_width - (self.left_offset + self.right_offset)

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
    
    def copy_cabinet(self,context,cabinet):
        bpy.ops.object.select_all(action='DESELECT')
        self.select_obj_and_children(cabinet.obj_bp)
        bpy.ops.object.duplicate_move()
        obj = context.active_object
        cabinet_bp = home_builder_utils.get_cabinet_bp(obj)
        return pc_types.Assembly(cabinet_bp)

    def check(self, context):
        # wall_bp = home_builder_utils.get_wall_bp(self.cabinet.obj_bp)
        # if wall_bp:
        left_x = home_builder_utils.get_left_collision_location(self.cabinet)
        right_x = home_builder_utils.get_right_collision_location(self.cabinet)
        offsets = self.left_offset + self.right_offset
        self.set_product_defaults()
        if self.position == 'FILL':
            self.cabinet.obj_bp.location.x = left_x + self.left_offset
            self.cabinet.obj_x.location.x = (right_x - left_x - offsets) / self.quantity
        if self.position == 'FILL_LEFT':
            self.cabinet.obj_bp.location.x = left_x + self.left_offset
            self.cabinet.obj_x.location.x = (self.default_width + (self.selected_location - left_x) - offsets) / self.quantity
        if self.position == 'LEFT':
            # if self.cabinet.obj_bp.mv.placement_type == 'Corner':
            #     self.cabinet.obj_bp.rotation_euler.z = math.radians(0)
            self.cabinet.obj_bp.location.x = left_x + self.left_offset
            self.cabinet.obj_x.location.x = self.width
        if self.position == 'CENTER':
            self.cabinet.obj_x.location.x = self.width
            self.cabinet.obj_bp.location.x = left_x + (right_x - left_x)/2 - ((self.cabinet.obj_x.location.x/2) * self.quantity)
        if self.position == 'RIGHT':
            # if self.cabinet.obj_bp.mv.placement_type == 'Corner':
            #     self.cabinet.obj_bp.rotation_euler.z = math.radians(-90)
            self.cabinet.obj_x.location.x = self.width
            self.cabinet.obj_bp.location.x = (right_x - self.cabinet.obj_x.location.x) - self.right_offset
        if self.position == 'FILL_RIGHT':
            self.cabinet.obj_bp.location.x = self.selected_location + self.left_offset
            self.cabinet.obj_x.location.x = ((right_x - self.selected_location) - offsets) / self.quantity
        self.update_quantity()
        return True

    def create_qty_cage(self):
        width = self.cabinet.obj_x.pyclone.get_var('location.x','width')
        height = self.cabinet.obj_z.pyclone.get_var('location.z','height')
        depth = self.cabinet.obj_y.pyclone.get_var('location.y','depth')

        self.qty_cage = data_cabinet_parts.add_cage(self.cabinet)
        self.qty_cage.obj_bp["IS_REFERENCE"] = True
        self.qty_cage.loc_x(value = 0)
        self.qty_cage.loc_y(value = 0)
        self.qty_cage.loc_z(value = 0)
        self.qty_cage.rot_x(value = 0)
        self.qty_cage.rot_y(value = 0)
        self.qty_cage.rot_z(value = 0)      
        self.qty_cage.dim_x('width',[width])
        self.qty_cage.dim_y('depth',[depth])
        self.qty_cage.dim_z('height',[height])   
    
    def update_quantity(self):
        qty = self.qty_cage.get_prompt("Quantity")
        a_left = self.qty_cage.get_prompt("Array Left")
        qty.set_value(self.quantity)
        if self.position == 'RIGHT':
            a_left.set_value(True)
        else:
            a_left.set_value(False)

    def execute(self, context):        
        new_products = []  
        previous_product = None
        width = self.cabinet.obj_x.location.x 
        pc_utils.delete_object_and_children(self.qty_cage.obj_bp)  
        if self.quantity > 1:
            for i in range(self.quantity - 1):
                if previous_product:
                    new_product = self.copy_cabinet(context,previous_product)
                else:
                    new_product = self.copy_cabinet(context,self.cabinet)
                if self.position == 'RIGHT':
                    new_product.obj_bp.location.x -= width
                else:
                    new_product.obj_bp.location.x += width
                new_products.append(new_product)
                previous_product = new_product

        for new_p in new_products:
            self.hide_empties_and_boolean_meshes(new_p.obj_bp)
            home_builder_utils.show_assembly_xyz(new_p)

        self.hide_empties_and_boolean_meshes(self.cabinet.obj_bp)
        home_builder_utils.show_assembly_xyz(self.cabinet)

        return {'FINISHED'}

    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)

    def invoke(self,context,event):
        self.reset_variables()
        self.get_assemblies(context)
        self.create_qty_cage()
        self.cabinet_name = self.cabinet.obj_bp.name
        self.depth = math.fabs(self.cabinet.obj_y.location.y)
        self.height = math.fabs(self.cabinet.obj_z.location.z)
        self.width = math.fabs(self.cabinet.obj_x.location.x)
        self.selected_location = self.cabinet.obj_bp.location.x
        self.default_width = self.cabinet.obj_x.location.x
        bpy.ops.object.select_all(action='DESELECT')
        for child in self.qty_cage.obj_bp.children:
            if child.type == 'MESH':
                child.select_set(True)          
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def get_assemblies(self,context):
        bp = home_builder_utils.get_cabinet_bp(context.object)
        self.cabinet = data_cabinets.Cabinet(bp)

    def draw(self, context):
        layout = self.layout

        #IF CORNER ALLOW FILLS FALSE

        if self.cabinet.obj_x.lock_location[0]:
            self.allow_fills = False

        box = layout.box()
        row = box.row(align=True)
        row.label(text="Position Options:",icon='EMPTY_ARROWS')
        row = box.row(align=False)
        row.prop_enum(self,'position', 'SELECTED_POINT',icon='RESTRICT_SELECT_OFF',text="Selected Point")
        if self.allow_fills:
            row.prop_enum(self,'position', 'FILL',icon='ARROW_LEFTRIGHT',text="Fill")
        row = box.row(align=True)
        if self.allow_fills:
            row.prop_enum(self, "position", 'FILL_LEFT', icon='REW', text="Fill Left") 
        row.prop_enum(self, "position", 'LEFT', icon='TRIA_LEFT', text="Left") 
        row.prop_enum(self, "position", 'CENTER', icon='TRIA_DOWN', text="Center")
        row.prop_enum(self, "position", 'RIGHT', icon='TRIA_RIGHT', text="Right") 
        if self.allow_fills:  
            row.prop_enum(self, "position", 'FILL_RIGHT', icon='FF', text="Fill Right")
        if self.allow_quantities:
            row = box.row(align=True)
            row.prop(self,'quantity')
        split = box.split(factor=0.5)
        col = split.column(align=True)
        col.label(text="Dimensions:")
        if self.position in {'SELECTED_POINT','LEFT','RIGHT','CENTER'}:
            col.prop(self,"width",text="Width")
        else:
            col.label(text='Width: ' + str(round(pc_unit.meter_to_active_unit(self.cabinet.obj_x.location.x),4)))
        col.prop(self.cabinet.obj_y,"location",index=1,text="Depth")
        col.prop(self.cabinet.obj_z,"location",index=2,text="Height")

        col = split.column(align=True)
        col.label(text="Offset:")
        col.prop(self,"left_offset",text="Left")
        col.prop(self,"right_offset",text="Right")
        col.prop(self.cabinet.obj_bp,"location",index=2,text="Height From Floor")


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
                        cabinet_bp = home_builder_utils.get_cabinet_bp(exterior)
                        cabinet = data_cabinets.Cabinet(cabinet_bp)
                        carcass_bp = home_builder_utils.get_carcass_bp(exterior)
                        carcass = data_cabinet_carcass.Carcass(carcass_bp)
                        new_exterior = data_cabinet_exteriors.get_class_from_name(self.exterior)
                        corner_type = cabinet.get_prompt("Corner Type")
                        if corner_type.get_value() == 'Blind':
                            carcass.add_blind_exterior(new_exterior)
                        else:
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
        remove_carcass = self.product.get_prompt("Remove Cabinet Carcass")
        remove_carcass.draw(box,allow_edit=False)
        carcass_height = self.product.get_prompt("Carcass Height")
        carcass_height.draw(box,allow_edit=False)

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(self.product,layout,context)
        self.draw_refrigerator_prompts(layout,context)
        self.draw_refrigerator_selection(layout,context)


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
        new_obj_bp.constraints.clear()
        self.hide_empties_and_boolean_meshes(new_cabinet.obj_bp)

        bpy.ops.home_builder.place_cabinet(obj_bp_name=new_cabinet.obj_bp.name,snap_cursor_to_cabinet=True)

        return {'FINISHED'}


classes = (
    home_builder_OT_cabinet_prompts,
    home_builder_OT_place_wall_cabinet,
    home_builder_OT_change_cabinet_exterior,
    home_builder_OT_range_prompts,
    home_builder_OT_dishwasher_prompts,
    home_builder_OT_refrigerator_prompts,
    home_builder_OT_delete_cabinet,
    home_builder_OT_delete_part,
    home_builder_OT_part_prompts,
    home_builder_OT_edit_part,
    home_builder_OT_update_cabinet_lighting,
    home_builder_OT_update_prompts,
    home_builder_OT_duplicate_cabinet,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()            