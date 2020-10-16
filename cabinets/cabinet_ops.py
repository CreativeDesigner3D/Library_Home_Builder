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
from .. import home_builder_utils
from .. import home_builder_paths
from .. import home_builder_enums
from .. import home_builder_pointers
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

class home_builder_OT_place_cabinet(bpy.types.Operator):
    bl_idname = "home_builder.place_cabinet"
    bl_label = "Place Cabinet"
    
    filepath: bpy.props.StringProperty(name="Filepath",default="Error")

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    
    cabinet = None
    selected_cabinet = None

    calculators = []

    drawing_plane = None

    next_wall = None
    current_wall = None
    previous_wall = None

    starting_point = ()
    placement = ''

    assembly = None
    obj = None
    exclude_objects = []

    class_name = ""

    def reset_selection(self):
        self.current_wall = None
        self.selected_cabinet = None    
        self.next_wall = None
        self.previous_wall = None  
        self.placement = ''  

    def reset_properties(self):
        self.cabinet = None
        self.selected_cabinet = None
        self.calculators = []
        self.drawing_plane = None
        self.next_wall = None
        self.current_wall = None
        self.previous_wall = None
        self.starting_point = ()
        self.placement = ''
        self.assembly = None
        self.obj = None
        self.exclude_objects = []
        self.class_name = ""

    def execute(self, context):
        self.reset_properties()
        self.create_drawing_plane(context)
        self.get_cabinet(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def position_cabinet(self,mouse_location,selected_obj):
        cabinet_bp = home_builder_utils.get_cabinet_bp(selected_obj)
        if not cabinet_bp:
            cabinet_bp = home_builder_utils.get_appliance_bp(selected_obj)

        wall_bp = home_builder_utils.get_wall_bp(selected_obj)
        if cabinet_bp:
            self.selected_cabinet = pc_types.Assembly(cabinet_bp)

            sel_cabinet_world_loc = (self.selected_cabinet.obj_bp.matrix_world[0][3],
                                     self.selected_cabinet.obj_bp.matrix_world[1][3],
                                     self.selected_cabinet.obj_bp.matrix_world[2][3])
            
            sel_cabinet_x_world_loc = (self.selected_cabinet.obj_x.matrix_world[0][3],
                                       self.selected_cabinet.obj_x.matrix_world[1][3],
                                       self.selected_cabinet.obj_x.matrix_world[2][3])

            dist_to_bp = pc_utils.calc_distance(mouse_location,sel_cabinet_world_loc)
            dist_to_x = pc_utils.calc_distance(mouse_location,sel_cabinet_x_world_loc)
            rot = self.selected_cabinet.obj_bp.rotation_euler.z
            x_loc = 0
            y_loc = 0
            if wall_bp:
                self.current_wall = pc_types.Assembly(wall_bp)
                rot += self.current_wall.obj_bp.rotation_euler.z      

            if dist_to_bp < dist_to_x:
                self.placement = 'LEFT'
                add_x_loc = 0
                add_y_loc = 0
                # if sel_product.obj_bp.mv.placement_type == 'Corner':
                #     rot += math.radians(90)
                #     add_x_loc = math.cos(rot) * sel_product.obj_y.location.y
                #     add_y_loc = math.sin(rot) * sel_product.obj_y.location.y
                x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] - math.cos(rot) * self.cabinet.obj_x.location.x + add_x_loc
                y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] - math.sin(rot) * self.cabinet.obj_x.location.x + add_y_loc

            else:
                self.placement = 'RIGHT'
                x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] + math.cos(rot) * self.selected_cabinet.obj_x.location.x
                y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] + math.sin(rot) * self.selected_cabinet.obj_x.location.x

            self.cabinet.obj_bp.rotation_euler.z = rot
            self.cabinet.obj_bp.location.x = x_loc
            self.cabinet.obj_bp.location.y = y_loc

        elif wall_bp:
            self.placement = 'WALL'
            self.current_wall = pc_types.Assembly(wall_bp)
            self.cabinet.obj_bp.rotation_euler = self.current_wall.obj_bp.rotation_euler
            self.cabinet.obj_bp.location.x = mouse_location[0]
            self.cabinet.obj_bp.location.y = mouse_location[1]

        else:
            self.cabinet.obj_bp.location.x = mouse_location[0]
            self.cabinet.obj_bp.location.y = mouse_location[1]

    def get_cabinet(self,context):
        directory, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)   

        wm_props = home_builder_utils.get_wm_props(context.window_manager)
        self.cabinet = wm_props.get_asset(self.filepath)
        if hasattr(self.cabinet,'pre_draw'):
            self.cabinet.pre_draw()
        else:
            self.cabinet.draw()
        self.cabinet.set_name(filename)
        self.set_child_properties(self.cabinet.obj_bp)

    def set_child_properties(self,obj):
        if "IS_DRAWERS_BP" in obj and obj["IS_DRAWERS_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Front Height Calculator')
            if calculator:
                calculator.calculate()
                self.calculators.append(calculator)

        if "IS_VERTICAL_SPLITTER_BP" in obj and obj["IS_VERTICAL_SPLITTER_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Opening Height Calculator')
            if calculator:
                calculator.calculate()
                self.calculators.append(calculator)

        home_builder_utils.update_id_props(obj,self.cabinet.obj_bp)
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
        for child in obj.children:
            self.set_placed_properties(child) 

    def create_drawing_plane(self,context):
        bpy.ops.mesh.primitive_plane_add()
        plane = context.active_object
        plane.location = (0,0,0)
        self.drawing_plane = context.active_object
        self.drawing_plane.display_type = 'WIRE'
        self.drawing_plane.dimensions = (100,100,1)

    def confirm_placement(self,context):
        if self.current_wall:
            x_loc = pc_utils.calc_distance((self.cabinet.obj_bp.location.x,self.cabinet.obj_bp.location.y,0),
                                           (self.current_wall.obj_bp.matrix_local[0][3],self.current_wall.obj_bp.matrix_local[1][3],0))

            self.cabinet.obj_bp.location = (0,0,self.cabinet.obj_bp.location.z)
            self.cabinet.obj_bp.rotation_euler = (0,0,0)
            self.cabinet.obj_bp.parent = self.current_wall.obj_bp
            self.cabinet.obj_bp.location.x = x_loc

        if self.placement == 'LEFT':
            self.cabinet.obj_bp.parent = self.selected_cabinet.obj_bp.parent
            constraint_obj = self.cabinet.obj_x
            constraint = self.selected_cabinet.obj_bp.constraints.new('COPY_LOCATION')
            constraint.target = constraint_obj
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = False

        if self.placement == 'RIGHT':
            self.cabinet.obj_bp.parent = self.selected_cabinet.obj_bp.parent
            constraint_obj = self.selected_cabinet.obj_x
            constraint = self.cabinet.obj_bp.constraints.new('COPY_LOCATION')
            constraint.target = constraint_obj
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = False

        if hasattr(self.cabinet,'pre_draw'):
            self.cabinet.draw()
        self.set_child_properties(self.cabinet.obj_bp)
        for cal in self.calculators:
            cal.calculate()
        self.refresh_data(False)  

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        context.area.tag_redraw()

        for calculator in self.calculators:
            calculator.calculate()

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.reset_selection()

        selected_point, selected_obj = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        self.position_cabinet(selected_point,selected_obj)

        if self.event_is_place_first_point(event):
            self.confirm_placement(context)
            return self.finish(context)
            
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

    def position_object(self,selected_point,selected_obj):
        self.cabinet.obj_bp.location = selected_point

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.cabinet.obj_bp)
        pc_utils.delete_object_and_children(self.drawing_plane)
        return {'CANCELLED'}

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.cabinet.obj_x.hide_viewport = hide
        self.cabinet.obj_y.hide_viewport = hide
        self.cabinet.obj_z.hide_viewport = hide
        self.cabinet.obj_x.empty_display_size = .001
        self.cabinet.obj_y.empty_display_size = .001
        self.cabinet.obj_z.empty_display_size = .001
 
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        self.set_placed_properties(self.cabinet.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        return {'FINISHED'}


class home_builder_OT_move_cabinet(bpy.types.Operator):
    bl_idname = "home_builder.move_cabinet"
    bl_label = "Move Cabinet"
    
    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")
    
    cabinet = None
    selected_cabinet = None

    calculators = []

    drawing_plane = None

    next_wall = None
    current_wall = None
    previous_wall = None

    starting_point = ()
    placement = ''

    assembly = None
    obj = None
    exclude_objects = []

    class_name = ""

    def reset_selection(self):
        self.current_wall = None
        self.selected_cabinet = None    
        self.next_wall = None
        self.previous_wall = None  
        self.placement = ''  

    def reset_properties(self):
        self.cabinet = None
        self.selected_cabinet = None
        self.calculators = []
        self.drawing_plane = None
        self.next_wall = None
        self.current_wall = None
        self.previous_wall = None
        self.starting_point = ()
        self.placement = ''
        self.assembly = None
        self.obj = None
        self.exclude_objects = []
        self.class_name = ""

    # def invoke(self,context,event):
    def execute(self, context):
        self.reset_properties()
        self.create_drawing_plane(context)
        self.get_cabinet(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def position_cabinet(self,mouse_location,selected_obj):
        cabinet_bp = home_builder_utils.get_cabinet_bp(selected_obj)
        if not cabinet_bp:
            cabinet_bp = home_builder_utils.get_appliance_bp(selected_obj)

        wall_bp = home_builder_utils.get_wall_bp(selected_obj)
        if cabinet_bp:
            self.selected_cabinet = pc_types.Assembly(cabinet_bp)

            sel_cabinet_world_loc = (self.selected_cabinet.obj_bp.matrix_world[0][3],
                                     self.selected_cabinet.obj_bp.matrix_world[1][3],
                                     self.selected_cabinet.obj_bp.matrix_world[2][3])
            
            sel_cabinet_x_world_loc = (self.selected_cabinet.obj_x.matrix_world[0][3],
                                       self.selected_cabinet.obj_x.matrix_world[1][3],
                                       self.selected_cabinet.obj_x.matrix_world[2][3])

            dist_to_bp = pc_utils.calc_distance(mouse_location,sel_cabinet_world_loc)
            dist_to_x = pc_utils.calc_distance(mouse_location,sel_cabinet_x_world_loc)
            rot = self.selected_cabinet.obj_bp.rotation_euler.z
            x_loc = 0
            y_loc = 0
            if wall_bp:
                self.current_wall = pc_types.Assembly(wall_bp)
                rot += self.current_wall.obj_bp.rotation_euler.z      

            if dist_to_bp < dist_to_x:
                self.placement = 'LEFT'
                add_x_loc = 0
                add_y_loc = 0
                # if sel_product.obj_bp.mv.placement_type == 'Corner':
                #     rot += math.radians(90)
                #     add_x_loc = math.cos(rot) * sel_product.obj_y.location.y
                #     add_y_loc = math.sin(rot) * sel_product.obj_y.location.y
                x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] - math.cos(rot) * self.cabinet.obj_x.location.x + add_x_loc
                y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] - math.sin(rot) * self.cabinet.obj_x.location.x + add_y_loc

            else:
                self.placement = 'RIGHT'
                x_loc = self.selected_cabinet.obj_bp.matrix_world[0][3] + math.cos(rot) * self.selected_cabinet.obj_x.location.x
                y_loc = self.selected_cabinet.obj_bp.matrix_world[1][3] + math.sin(rot) * self.selected_cabinet.obj_x.location.x

            self.cabinet.obj_bp.rotation_euler.z = rot
            self.cabinet.obj_bp.location.x = x_loc
            self.cabinet.obj_bp.location.y = y_loc

        elif wall_bp:
            self.placement = 'WALL'
            self.current_wall = pc_types.Assembly(wall_bp)
            self.cabinet.obj_bp.rotation_euler = self.current_wall.obj_bp.rotation_euler
            self.cabinet.obj_bp.location.x = mouse_location[0]
            self.cabinet.obj_bp.location.y = mouse_location[1]

        else:
            self.cabinet.obj_bp.location.x = mouse_location[0]
            self.cabinet.obj_bp.location.y = mouse_location[1]

    def get_cabinet(self,context):
        obj = bpy.data.objects[self.obj_bp_name]
        obj_bp = home_builder_utils.get_cabinet_bp(obj)
        self.cabinet = pc_types.Assembly(obj_bp)
        self.cabinet.obj_bp.constraints.clear()
        self.cabinet.obj_bp.parent = None
        self.set_child_properties(self.cabinet.obj_bp)

    def set_child_properties(self,obj):
        if obj.name != self.drawing_plane.name:
            self.exclude_objects.append(obj)            
        if obj.type == 'MESH':
            obj.display_type = 'WIRE'          
        for child in obj.children:
            self.set_child_properties(child)         

    def set_placed_properties(self,obj):
        if obj.type == 'MESH':
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

    def confirm_placement(self,context):
        if self.current_wall:
            x_loc = pc_utils.calc_distance((self.cabinet.obj_bp.location.x,self.cabinet.obj_bp.location.y,0),
                                           (self.current_wall.obj_bp.matrix_local[0][3],self.current_wall.obj_bp.matrix_local[1][3],0))

            self.cabinet.obj_bp.location = (0,0,self.cabinet.obj_bp.location.z)
            self.cabinet.obj_bp.rotation_euler = (0,0,0)
            self.cabinet.obj_bp.parent = self.current_wall.obj_bp
            self.cabinet.obj_bp.location.x = x_loc

        if self.placement == 'LEFT':
            self.cabinet.obj_bp.parent = self.selected_cabinet.obj_bp.parent
            constraint_obj = self.cabinet.obj_x
            constraint = self.selected_cabinet.obj_bp.constraints.new('COPY_LOCATION')
            constraint.target = constraint_obj
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = False

        if self.placement == 'RIGHT':
            self.cabinet.obj_bp.parent = self.selected_cabinet.obj_bp.parent
            constraint_obj = self.selected_cabinet.obj_x
            constraint = self.cabinet.obj_bp.constraints.new('COPY_LOCATION')
            constraint.target = constraint_obj
            constraint.use_x = True
            constraint.use_y = True
            constraint.use_z = False

        if hasattr(self.cabinet,'pre_draw'):
            self.cabinet.draw()
        self.set_child_properties(self.cabinet.obj_bp)
        self.refresh_data(False)  

    def modal(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        context.area.tag_redraw()

        for calculator in self.calculators:
            calculator.calculate()

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        self.reset_selection()

        selected_point, selected_obj = pc_utils.get_selection_point(context,event,exclude_objects=self.exclude_objects)

        self.position_cabinet(selected_point,selected_obj)

        if self.event_is_place_first_point(event):
            self.confirm_placement(context)
            return self.finish(context)
            
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

    def position_object(self,selected_point,selected_obj):
        self.cabinet.obj_bp.location = selected_point

    def cancel_drop(self,context):
        pc_utils.delete_object_and_children(self.drawing_plane)
        return {'CANCELLED'}

    def refresh_data(self,hide=True):
        ''' For some reason matrix world doesn't evaluate correctly
            when placing cabinets next to this if object is hidden
            For now set x, y, z object to not be hidden.
        '''
        self.cabinet.obj_x.hide_viewport = hide
        self.cabinet.obj_y.hide_viewport = hide
        self.cabinet.obj_z.hide_viewport = hide
        self.cabinet.obj_x.empty_display_size = .001
        self.cabinet.obj_y.empty_display_size = .001
        self.cabinet.obj_z.empty_display_size = .001
 
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        if self.drawing_plane:
            pc_utils.delete_obj_list([self.drawing_plane])
        self.set_placed_properties(self.cabinet.obj_bp) 
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()
        return {'FINISHED'}


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

    cabinet = None

    def reset_variables(self):
        #BLENDER CRASHES IF TAB IS SET TO EXTERIOR
        #THIS IS BECAUSE POPUP DIALOGS CANNOT DISPLAY UILISTS ON INVOKE
        self.product_tabs = 'MAIN'
        self.cabinet = None

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
        for carcass in self.cabinet.carcasses:
            left_finished_end = carcass.get_prompt("Left Finished End")
            right_finished_end = carcass.get_prompt("Right Finished End")
            finished_back = carcass.get_prompt("Finished Back")
            finished_top = carcass.get_prompt("Finished Top")
            finished_bottom = carcass.get_prompt("Finished Bottom")
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

    def check(self, context):
        self.update_product_size()
        self.update_fillers(context)
        self.update_materials(context)
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
        bp = home_builder_utils.get_cabinet_bp(context.object)
        if not bp:
            bp = home_builder_utils.get_appliance_bp(context.object)
        self.cabinet = data_cabinets.Cabinet(bp)
        self.cabinet_name = self.cabinet.obj_bp.name
        self.depth = math.fabs(self.cabinet.obj_y.location.y)
        self.height = math.fabs(self.cabinet.obj_z.location.z)
        self.width = math.fabs(self.cabinet.obj_x.location.x)
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
        for carcass in self.cabinet.carcasses:
            left_finished_end = carcass.get_prompt("Left Finished End")
            right_finished_end = carcass.get_prompt("Right Finished End")
            finished_back = carcass.get_prompt("Finished Back")
            finished_top = carcass.get_prompt("Finished Top")
            finished_bottom = carcass.get_prompt("Finished Bottom")
            toe_kick_height = carcass.get_prompt("Toe Kick Height")
            toe_kick_setback = carcass.get_prompt("Toe Kick Setback")
            add_bottom_light = carcass.get_prompt("Add Bottom Light")
            add_top_light = carcass.get_prompt("Add Top Light")
            add_side_light = carcass.get_prompt("Add Side Light")
  
            col = layout.column(align=True)
            box = col.box()
            row = box.row()
            row.label(text="Carcass - " + carcass.obj_bp.name)

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

            if add_bottom_light and add_top_light and add_side_light:
                row = box.row()
                row.label(text="Cabinet Lighting:")   
                row.prop(add_bottom_light,'checkbox_value',text="Bottom")
                row.prop(add_top_light,'checkbox_value',text="Top")
                row.prop(add_side_light,'checkbox_value',text="Side")  

    def draw_cabinet_prompts(self,layout,context):
        bottom_cabinet_height = self.cabinet.get_prompt("Bottom Cabinet Height")    
        left_adjustment_width = self.cabinet.get_prompt("Left Adjustment Width")       
        right_adjustment_width = self.cabinet.get_prompt("Right Adjustment Width")    
        add_sink = self.cabinet.get_prompt("Add Sink")
        add_cooktop = self.cabinet.get_prompt("Add Cooktop")
        ctop_front = self.cabinet.get_prompt("Countertop Overhang Front")
        ctop_back = self.cabinet.get_prompt("Countertop Overhang Back")
        ctop_left = self.cabinet.get_prompt("Countertop Overhang Left")
        ctop_right = self.cabinet.get_prompt("Countertop Overhang Right")
        ctop_left = self.cabinet.get_prompt("Countertop Overhang Left")   

        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.label(text="Cabinet - " + self.cabinet.obj_bp.name)

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

        if add_sink or add_cooktop:
            box = layout.box()
            box.operator_context = 'INVOKE_AREA'
            row = box.row()
            row.label(text="Cabinet Appliances:")  

            if add_sink:
                row.operator('home_builder.cabinet_sink_options',text="Sink Options")
            if add_cooktop:
                row.operator('home_builder.cabinet_cooktop_options',text="Cooktop Options")

    def draw(self, context):
        layout = self.layout
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


def update_exterior(self,context):
    self.exterior_changed = True


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
                        carcass_bp = home_builder_utils.get_carcass_bp(exterior)
                        carcass = data_cabinet_carcass.Carcass(carcass_bp)
                        new_exterior = data_cabinet_exteriors.get_class_from_name(self.exterior)
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


class home_builder_OT_cabinet_sink_options(bpy.types.Operator):
    bl_idname = "home_builder.cabinet_sink_options"
    bl_label = "Cabinet Sink Options"

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name",default="")

    sink_category: bpy.props.EnumProperty(name="Sink Category",
        items=home_builder_enums.enum_sink_categories,
        update=home_builder_enums.update_sink_category)
    sink_name: bpy.props.EnumProperty(name="Sink Name",
        items=home_builder_enums.enum_sink_names)

    faucet_category: bpy.props.EnumProperty(name="Faucet Category",
        items=home_builder_enums.enum_faucet_categories,
        update=home_builder_enums.update_faucet_category)
    faucet_name: bpy.props.EnumProperty(name="Faucet Name",
        items=home_builder_enums.enum_faucet_names)

    add_sink = False
    add_faucet = False
    cabinet = None
    carcass = None
    countertop = None
    previous_sink = None
    sink = None
    faucet = None

    def reset_variables(self):
        self.cabinet = None
        self.carcass = None
        self.countertop = None
        self.sink = None
        self.faucet = None

    def check(self, context):
        return True

    def assign_boolean_to_child_assemblies(self,context,assembly,bool_obj):
        for child in assembly.obj_bp.children:
            for nchild in child.children:
                if nchild.type == 'MESH':       
                    mod = nchild.modifiers.new(bool_obj.name,'BOOLEAN')
                    mod.object = bool_obj
                    mod.operation = 'DIFFERENCE'      

    def assign_boolean_modifiers(self,context):
        bool_obj = None

        for child in self.sink.obj_bp.children:
            if child.type == 'MESH':   
                if 'IS_BOOLEAN' in child and child['IS_BOOLEAN'] == True:   
                    bool_obj = child  
                    bool_obj.hide_viewport = True
                    bool_obj.display_type = 'WIRE'                        

        if bool_obj:
            self.assign_boolean_to_child_assemblies(context,self.countertop,bool_obj)
            self.assign_boolean_to_child_assemblies(context,self.carcass,bool_obj)                

    def delete_previous_sink(self,context):
        if not self.previous_sink:
            return

        pc_utils.delete_object_and_children(self.previous_sink.obj_bp)

    def execute(self, context):
        self.delete_previous_sink(context)
        if self.add_sink:
            cabinet_utils.add_sink(self.cabinet,self.carcass,self.countertop,self.get_sink(context))
            self.assign_boolean_modifiers(context)
            self.sink.obj_bp.hide_viewport = True
            self.sink.obj_x.hide_viewport = True
            self.sink.obj_y.hide_viewport = True
            self.sink.obj_z.hide_viewport = True
            if self.add_faucet:
                self.get_faucet(context)
        return {'FINISHED'}

    def get_faucet_bp(self):
        for child in self.sink.obj_bp.children:
            if "IS_FAUCET_BP" in child and child["IS_FAUCET_BP"]:
                return child

    def get_faucet(self,context):
        root_path = home_builder_paths.get_faucet_path()
        sink_path = os.path.join(root_path,self.faucet_category,self.faucet_name + ".blend")

        with bpy.data.libraries.load(sink_path, False, False) as (data_from, data_to):
            data_to.objects = data_from.objects

        for obj in data_to.objects:
            home_builder_utils.update_id_props(obj,self.cabinet.obj_bp)
            self.faucet = obj

        self.sink.add_object(self.faucet)
        obj_bp = self.get_faucet_bp()
        if obj_bp:
            self.faucet.parent = obj_bp
        return self.faucet

    def get_sink(self,context):
        root_path = home_builder_paths.get_sink_path()
        sink_path = os.path.join(root_path,self.sink_category,self.sink_name + ".blend")
        self.sink = pc_types.Assembly(filepath=sink_path)
        self.sink.obj_bp["IS_SINK_BP"] = True
        home_builder_utils.update_assembly_id_props(self.sink,self.cabinet)
        return self.sink

    def get_assemblies(self,context):
        self.carcass = None
        self.countertop = None

        for child in self.cabinet.obj_bp.children:
            if "IS_CARCASS_BP" in child and child["IS_CARCASS_BP"]:
                self.carcass = pc_types.Assembly(child)      
            if "IS_COUNTERTOP_BP" in child and child["IS_COUNTERTOP_BP"]:
                self.countertop = pc_types.Assembly(child)   
            if "IS_SINK_BP" in child and child["IS_SINK_BP"]:
                self.previous_sink = pc_types.Assembly(child)   

    def invoke(self,context,event):
        self.reset_variables()
        bp = home_builder_utils.get_cabinet_bp(context.object)
        self.cabinet = pc_types.Assembly(bp)
        self.cabinet_name = self.cabinet.obj_bp.name
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def draw_sink_prompts(self,layout,context):
        add_sink = self.cabinet.get_prompt("Add Sink")

        if not add_sink:
            return False

        add_sink.draw(layout)
        self.add_sink = add_sink.get_value()
        if self.add_sink:
            layout.prop(self,'sink_category',text="",icon='FILE_FOLDER')  
            if len(self.sink_name) > 0:
                layout.template_icon_view(self,"sink_name",show_labels=True)  

    def draw_faucet_prompts(self,layout,context):
        add_faucet = self.cabinet.get_prompt("Add Faucet")

        if not add_faucet:
            return False

        add_faucet.draw(layout)
        self.add_faucet = add_faucet.get_value()
        if self.add_faucet:
            layout.prop(self,'faucet_category',text="",icon='FILE_FOLDER')  
            if len(self.sink_name) > 0:
                layout.template_icon_view(self,"faucet_name",show_labels=True)  

    def draw(self, context):
        layout = self.layout

        split = layout.split()

        self.draw_sink_prompts(split.box(),context)
        self.draw_faucet_prompts(split.box(),context)


class home_builder_OT_cabinet_cooktop_options(bpy.types.Operator):
    bl_idname = "home_builder.cabinet_cooktop_options"
    bl_label = "Cabinet Cooktop Options"

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name",default="")

    cooktop_category: bpy.props.EnumProperty(name="Cooktop Category",
        items=home_builder_enums.enum_cooktop_categories,
        update=home_builder_enums.update_cooktop_category)
    cooktop_name: bpy.props.EnumProperty(name="Cooktop Name",
        items=home_builder_enums.enum_cooktop_names)

    range_hood_category: bpy.props.EnumProperty(name="Range Hood Category",
        items=home_builder_enums.enum_range_hood_categories,
        update=home_builder_enums.update_range_hood_category)
    range_hood_name: bpy.props.EnumProperty(name="Range Hood Name",
        items=home_builder_enums.enum_range_hood_names)

    add_cooktop = False
    add_range_hood = False
    cabinet = None
    carcass = None
    countertop = None
    previous_cooktop = None
    previous_range_hood = None
    cooktop = None
    range_hood = None

    def reset_variables(self):
        self.cabinet = None
        self.carcass = None
        self.countertop = None
        self.cooktop = None
        self.range_hood = None

    def check(self, context):
        return True

    def assign_boolean_to_child_assemblies(self,context,assembly,bool_obj):
        for child in assembly.obj_bp.children:
            for nchild in child.children:
                if nchild.type == 'MESH':       
                    mod = nchild.modifiers.new(bool_obj.name,'BOOLEAN')
                    mod.object = bool_obj
                    mod.operation = 'DIFFERENCE'      

    def assign_boolean_modifiers(self,context):
        bool_obj = None

        for child in self.cooktop.obj_bp.children:
            if child.type == 'MESH':   
                if 'IS_BOOLEAN' in child and child['IS_BOOLEAN'] == True:   
                    bool_obj = child  
                    bool_obj.hide_viewport = True
                    bool_obj.hide_render = True
                    bool_obj.display_type = 'WIRE'                        

        if bool_obj:
            self.assign_boolean_to_child_assemblies(context,self.countertop,bool_obj)
            self.assign_boolean_to_child_assemblies(context,self.carcass,bool_obj)                

    def delete_previous_cooktop(self,context):
        if not self.previous_cooktop:
            return

        pc_utils.delete_object_and_children(self.previous_cooktop.obj_bp)

    def execute(self, context):
        self.delete_previous_cooktop(context)
        if self.add_cooktop:
            cabinet_utils.add_cooktop(self.cabinet,self.carcass,self.countertop,self.get_cooktop(context))
            self.assign_boolean_modifiers(context)
            self.cooktop.obj_bp.hide_viewport = True
            self.cooktop.obj_x.hide_viewport = True
            self.cooktop.obj_y.hide_viewport = True
            self.cooktop.obj_z.hide_viewport = True
            if self.add_range_hood:
                self.get_range_hood(context)
        return {'FINISHED'}

    def get_cooktop(self,context):
        root_path = home_builder_paths.get_cooktop_path()
        cooktop_path = os.path.join(root_path,self.cooktop_category,self.cooktop_name + ".blend")
        self.cooktop = pc_types.Assembly(filepath=cooktop_path)
        self.cooktop.obj_bp["IS_COOKTOP_BP"] = True
        home_builder_utils.update_assembly_id_props(self.cooktop,self.cabinet)
        return self.cooktop

    def get_range_hood(self,context):
        root_path = home_builder_paths.get_range_hood_path()
        range_hood_path = os.path.join(root_path,self.range_hood_category,self.range_hood_name + ".blend")
        self.range_hood = pc_types.Assembly(self.cabinet.add_assembly_from_file(filepath=range_hood_path))
        self.range_hood.obj_bp["IS_RANGE_HOOD_BP"] = True
        home_builder_utils.update_assembly_id_props(self.range_hood,self.cabinet)
        return self.range_hood

    def get_assemblies(self,context):
        self.carcass = None
        self.countertop = None
        self.previous_cooktop = None
        self.previous_range_hood = None

        for child in self.cabinet.obj_bp.children:
            if "IS_CARCASS_BP" in child and child["IS_CARCASS_BP"]:
                self.carcass = pc_types.Assembly(child)      
            if "IS_COUNTERTOP_BP" in child and child["IS_COUNTERTOP_BP"]:
                self.countertop = pc_types.Assembly(child)   
            if "IS_COOKTOP_BP" in child and child["IS_COOKTOP_BP"]:
                self.previous_cooktop = pc_types.Assembly(child)   
            if "IS_RANGE_HOOD_BP" in child and child["IS_RANGE_HOOD_BP"]:
                self.previous_range_hood = pc_types.Assembly(child)   

    def invoke(self,context,event):
        self.reset_variables()
        bp = home_builder_utils.get_cabinet_bp(context.object)
        self.cabinet = pc_types.Assembly(bp)
        self.cabinet_name = self.cabinet.obj_bp.name
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def draw_cooktop_prompts(self,layout,context):
        add_cooktop = self.cabinet.get_prompt("Add Cooktop")

        if not add_cooktop:
            return False

        add_cooktop.draw(layout)
        self.add_cooktop = add_cooktop.get_value()
        if self.add_cooktop:
            layout.prop(self,'cooktop_category',text="",icon='FILE_FOLDER')
            layout.template_icon_view(self,"cooktop_name",show_labels=True)

    def draw_range_hood_prompts(self,layout,context):
        add_range_hood = self.cabinet.get_prompt("Add Range Hood")

        if not add_range_hood:
            return False

        add_range_hood.draw(layout)
        self.add_range_hood = add_range_hood.get_value()
        if self.add_range_hood:
            layout.prop(self,'range_hood_category',text="",icon='FILE_FOLDER')  
            layout.template_icon_view(self,"range_hood_name",show_labels=True)  

    def draw(self, context):
        layout = self.layout

        split = layout.split()

        self.draw_cooktop_prompts(split.box(),context)
        self.draw_range_hood_prompts(split.box(),context)


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


def update_range(self,context):
    self.range_changed = True

def update_range_hood(self,context):
    self.range_hood_changed = True

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
            home_builder_utils.hide_empties(self.product.obj_bp)
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
                home_builder_utils.hide_empties(self.product.obj_bp)
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

def update_dishwasher(self,context):
    self.dishwasher_changed = True


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


def update_refrigerator(self,context):
    self.refrigerator_changed = True


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

    def draw_refrigerator_prompts(self,layout,context):
        layout.label(text="")
        box = layout.box()
        box.prop(self,'refrigerator_category',text="",icon='FILE_FOLDER')  
        box.template_icon_view(self,"refrigerator_name",show_labels=True)          

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(self.product,layout,context)
        split = layout.split()
        self.draw_refrigerator_prompts(split.column(),context)


class home_builder_MT_cabinet_menu(bpy.types.Menu):
    bl_label = "Cabinet Commands"

    def draw(self, context):
        layout = self.layout
        obj_bp = pc_utils.get_assembly_bp(context.object)
        cabinet_bp = home_builder_utils.get_cabinet_bp(context.object)
        appliance_bp = home_builder_utils.get_appliance_bp(context.object)
        exterior_bp = home_builder_utils.get_exterior_bp(context.object)

        layout.operator_context = 'INVOKE_DEFAULT'

        if cabinet_bp:
            layout.operator('home_builder.move_cabinet',text="Move Cabinet - " + cabinet_bp.name,icon='OBJECT_ORIGIN').obj_bp_name = cabinet_bp.name
            layout.operator('home_builder.free_move_cabinet',text="Grab Cabinet - " + cabinet_bp.name,icon='VIEW_PAN').obj_bp_name = cabinet_bp.name
            layout.operator('home_builder.duplicate_cabinet',text="Duplicate Cabinet - " + cabinet_bp.name,icon='DUPLICATE').obj_bp_name = cabinet_bp.name
            layout.separator()
            
        if exterior_bp:
            layout.operator('home_builder.change_cabinet_exterior',text="Change Cabinet Exterior",icon='FILE_REFRESH')
            layout.separator()

        layout.operator('home_builder.part_prompts',text="Part Prompts - " + obj_bp.name,icon='WINDOW')
        layout.operator('home_builder.hardlock_part_size',icon='FILE_REFRESH')
        layout.separator()
        layout.operator('home_builder.delete_cabinet',icon='X')


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


class home_builder_OT_hardlock_part_size(bpy.types.Operator):
    bl_idname = "home_builder.hardlock_part_size"
    bl_label = "Hardlock Part Size"

    @classmethod
    def poll(cls, context):
        obj_bp = pc_utils.get_assembly_bp(context.object)
        for child in obj_bp.children:
            if child.type == 'MESH':
                for mod in child.modifiers:
                    if mod.type == 'HOOK':
                        return  True      
        return False

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
        self.hide_empties_and_boolean_meshes(new_cabinet.obj_bp)

        bpy.ops.home_builder.move_cabinet(obj_bp_name=new_cabinet.obj_bp.name)

        return {'FINISHED'}


class home_builder_OT_free_move_cabinet(bpy.types.Operator):
    bl_idname = "home_builder.free_move_cabinet"
    bl_label = "Free Move Cabinet"

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    @classmethod
    def poll(cls, context):
        obj_bp = home_builder_utils.get_cabinet_bp(context.object)
        if obj_bp:
            return True
        else:
            return False

    def execute(self, context):
        obj = context.object
        obj_bp = home_builder_utils.get_cabinet_bp(obj)
        cabinet = pc_types.Assembly(obj_bp)
        bpy.ops.object.select_all(action='DESELECT')

        cabinet.obj_bp.hide_viewport = False
        cabinet.obj_bp.select_set(True)

        region = context.region
        co = location_3d_to_region_2d(region,context.region_data,cabinet.obj_bp.matrix_world.translation)
        region_offset = Vector((region.x,region.y))
        context.window.cursor_warp(*(co + region_offset))
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(home_builder_OT_place_cabinet)  
    bpy.utils.register_class(home_builder_OT_cabinet_prompts)  
    bpy.utils.register_class(home_builder_OT_change_cabinet_exterior)  
    bpy.utils.register_class(home_builder_OT_cabinet_sink_options)  
    bpy.utils.register_class(home_builder_OT_cabinet_cooktop_options)   
    bpy.utils.register_class(home_builder_OT_range_prompts)  
    bpy.utils.register_class(home_builder_OT_dishwasher_prompts)  
    bpy.utils.register_class(home_builder_OT_refrigerator_prompts)  
    bpy.utils.register_class(home_builder_MT_cabinet_menu)     
    bpy.utils.register_class(home_builder_OT_delete_cabinet)    
    bpy.utils.register_class(home_builder_OT_delete_part)    
    bpy.utils.register_class(home_builder_OT_part_prompts)    
    bpy.utils.register_class(home_builder_OT_hardlock_part_size)  
    bpy.utils.register_class(home_builder_OT_update_cabinet_lighting)  
    bpy.utils.register_class(home_builder_OT_update_prompts)  
    bpy.utils.register_class(home_builder_OT_move_cabinet)  
    bpy.utils.register_class(home_builder_OT_duplicate_cabinet)  
    bpy.utils.register_class(home_builder_OT_free_move_cabinet)  
    

def unregister():
    bpy.utils.unregister_class(home_builder_OT_place_cabinet)  
    bpy.utils.unregister_class(home_builder_OT_cabinet_prompts)   
    bpy.utils.unregister_class(home_builder_OT_change_cabinet_exterior)  
    bpy.utils.unregister_class(home_builder_OT_cabinet_sink_options)   
    bpy.utils.unregister_class(home_builder_OT_cabinet_cooktop_options)   
    bpy.utils.unregister_class(home_builder_OT_range_prompts) 
    bpy.utils.unregister_class(home_builder_OT_dishwasher_prompts)  
    bpy.utils.unregister_class(home_builder_OT_refrigerator_prompts)  
    bpy.utils.unregister_class(home_builder_MT_cabinet_menu)       
    bpy.utils.unregister_class(home_builder_OT_delete_cabinet)        
    bpy.utils.unregister_class(home_builder_OT_delete_part)      
    bpy.utils.unregister_class(home_builder_OT_part_prompts) 
    bpy.utils.unregister_class(home_builder_OT_hardlock_part_size)   
    bpy.utils.unregister_class(home_builder_OT_update_cabinet_lighting)  
    bpy.utils.unregister_class(home_builder_OT_update_prompts)  
    bpy.utils.unregister_class(home_builder_OT_move_cabinet)  
    bpy.utils.unregister_class(home_builder_OT_duplicate_cabinet)  
    bpy.utils.unregister_class(home_builder_OT_free_move_cabinet)
