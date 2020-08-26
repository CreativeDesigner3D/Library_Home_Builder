import bpy
import os
import math
import inspect
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import cabinet_library
from . import cabinet_utils
from . import data_appliances
from . import data_cabinet_doors
from .. import home_builder_utils
from .. import home_builder_paths
from .. import home_builder_enums

def update_cabinet_id_props(obj):
    obj["PROMPT_ID"] = "home_builder.cabinet_prompts"   
    obj["MENU_ID"] = "home_builder_MT_cabinet_menu"       

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
        for name, obj in inspect.getmembers(cabinet_library):
            if name == filename.replace(" ","_"):
                self.cabinet = obj()
                self.cabinet.draw()
                self.cabinet.set_name(filename.replace("_"," "))
                self.set_child_properties(self.cabinet.obj_bp)
                self.refresh_data(False)  

        if not self.cabinet:
            directory, file = os.path.split(self.filepath)
            filename, ext = os.path.splitext(file)        
            for name, obj in inspect.getmembers(data_appliances):
                if name == filename.replace(" ","_"):
                    self.cabinet = obj()
                    self.cabinet.draw()
                    self.cabinet.set_name(filename.replace("_"," "))
                    self.set_child_properties(self.cabinet.obj_bp)
                    self.refresh_data(False)  

        # self.cabinet.obj_bp.hide_viewport = False
        # self.cabinet.obj_bp.location = self.cabinet.obj_bp.location
        # for calculator in self.calculators:
        #     print('CALC')
        #     calculator.calculate()

    def set_child_properties(self,obj):
        if "IS_DRAWERS_BP" in obj and obj["IS_DRAWERS_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Front Height Calculator')
            calculator.calculate()
            self.calculators.append(calculator)

        if "IS_VERTICAL_SPLITTER_BP" in obj and obj["IS_VERTICAL_SPLITTER_BP"]:
            assembly = pc_types.Assembly(obj)
            calculator = assembly.get_calculator('Opening Height Calculator')
            calculator.calculate()
            self.calculators.append(calculator)

        update_cabinet_id_props(obj)
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

    def modal(self, context, event):
        
        bpy.ops.object.select_all(action='DESELECT')
        context.area.tag_redraw()

        for calculator in self.calculators:
            calculator.calculate()

        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y

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

def update_child_props(obj):
    update_cabinet_id_props(obj)
    for child in obj.children:
        update_child_props(child)

def update_exterior(self,context):
    if self.cabinet_name not in bpy.data.objects:
        return

    obj = bpy.data.objects[self.cabinet_name]
    bp = home_builder_utils.get_cabinet_bp(obj)

    cabinet = pc_types.Assembly(bp)    
    carcass = None
    exterior_assembly = None
    # drawers = None
    # doors = None

    for child in cabinet.obj_bp.children:
        if "IS_CARCASS_BP" in child and child["IS_CARCASS_BP"]:
            carcass = pc_types.Assembly(child)        
        if "IS_EXTERIOR_BP" in child and child["IS_EXTERIOR_BP"]:
            exterior_assembly = pc_types.Assembly(child)            
        # if "IS_DRAWERS_BP" in child and child["IS_DRAWERS_BP"]:
        #     drawers = pc_types.Assembly(child)   
        # if "IS_DOORS_BP" in child and child["IS_DOORS_BP"]:
        #     doors = pc_types.Assembly(child)          

    if exterior_assembly:
        pc_utils.delete_object_and_children(exterior_assembly.obj_bp)
        exterior = None
        if self.exterior == 'DOOR':
            exterior = data_cabinet_doors.Door()
        elif self.exterior == '2_DOOR_2_DRAWER':
            exterior = data_cabinet_doors.Door()             
        elif self.exterior == '1_DOOR_1_DRAWER':
            exterior = data_cabinet_doors.Door()           
        elif self.exterior == '2_DOOR_1_DRAWER':
            exterior = data_cabinet_doors.Door()       
        elif self.exterior == 'SLIDING_DOORS':
            exterior = data_cabinet_doors.Door()                                                   
        elif self.exterior == 'DRAWERS':
            exterior = data_cabinet_doors.Drawers()
        if exterior:
            cabinet_type = carcass.get_prompt("Cabinet Type")
            cabinet_utils.add_exterior_to_cabinet(cabinet,carcass,exterior,cabinet_type.get_value())
            update_child_props(exterior.obj_bp)

def update_interior(self,context):
    print(self.interior_assembly)
    if self.interior_assembly:
        print(self.interior_assembly.obj_bp)

class home_builder_OT_cabinet_prompts(bpy.types.Operator):
    bl_idname = "home_builder.cabinet_prompts"
    bl_label = "Cabinet Prompts"

    cabinet_name: bpy.props.StringProperty(name="Cabinet Name",default="")

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    product_tabs: bpy.props.EnumProperty(name="Product Tabs",
                                         items=[('CARCASS',"Carcass","Carcass Options"),
                                                ('EXTERIOR',"Exterior","Exterior Options"),
                                                ('INTERIOR',"Interior","Interior Options"),
                                                ('SPLITTER',"Openings","Openings Options")])

    exterior: bpy.props.EnumProperty(name="Exterior",
                                     items=[('OPEN',"Open","Open"),
                                            ('DOOR',"Door","Door"),
                                            ('2_DOOR_2_DRAWER',"2 Door 2 Drawer","2 Door 2 Drawer"),
                                            ('1_DOOR_1_DRAWER',"1 Door 1 Drawer","1 Door 1 Drawer"),
                                            ('2_DOOR_1_DRAWER',"2 Door 1 Drawer","2 Door 1 Drawer"),
                                            ('SLIDING_DOORS',"Sliding Doors","Sliding Doors"),
                                            ('DRAWERS',"Drawers","Drawers")],
                                    update=update_exterior)

    interior: bpy.props.EnumProperty(name="Interior",
                                     items=[('OPEN',"Open","Open"),
                                            ('SHELVES',"Shelves","Shelves"),
                                            ('ROLLOUTS',"Rollouts","Rollouts"),
                                            ('DIVISIONS',"Divisions","Divisions"),
                                            ('CUBBIES',"Cubbies","Cubbies")],
                                     update=update_interior)

    door_swing: bpy.props.EnumProperty(name="Door Swing",
                                       items=[('LEFT',"Left Swing","Left Swing"),
                                              ('RIGHT',"Right Swing","Right Swing"),
                                              ('TOP',"Top Swing","Top Swing")])

    drawer_qty: bpy.props.EnumProperty(name="Drawer Quantity",
                                       items=[('1',"1","1"),
                                              ('2',"2","2"),
                                              ('3',"3","3"),
                                              ('4',"4","4"),
                                              ('5',"5","5"),
                                              ('6',"6","6")])

    # sink_category: bpy.props.EnumProperty(name="Sink Category",
    #     items=home_builder_enums.enum_sink_categories,
    #     update=home_builder_enums.update_sink_category)
    # sink_name: bpy.props.EnumProperty(name="Sink Name",
    #     items=home_builder_enums.enum_sink_names)

    calculators = []

    left_side = None
    right_side = None

    cabinet = None
    carcass = None
    countertop = None
    doors = None
    drawers = None
    interior_assembly = None
    exterior_assembly = None
    splitter = None

    def reset_variables(self):
        #BLENDER CRASHES IF TAB IS SET TO EXTERIOR
        self.product_tabs = 'CARCASS'

        self.calculators = []

        self.left_side = None
        self.right_side = None

        self.cabinet = None
        self.carcass = None
        self.countertop = None
        self.doors = None
        self.drawers = None
        self.interior_assembly = None
        self.exterior_assembly = None       
        self.splitter = None     

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

        for calculator in self.calculators:
            if calculator.distance_obj:
                calculator.calculate()

        self.update_materials(context)
        return True

    def execute(self, context):
        return {'FINISHED'}

    def get_assemblies(self,context):
        self.carcass = None
        self.interior_assembly = None
        self.exterior_assembly = None
        self.countertop = None
        self.drawers = None
        self.drawer_calculator = None
        self.doors = None
        self.left_side = None
        self.right_side = None

        for child in self.cabinet.obj_bp.children:
            if "IS_CARCASS_BP" in child and child["IS_CARCASS_BP"]:
                self.carcass = pc_types.Assembly(child)      
            if "IS_INTERIOR_BP" in child and child["IS_INTERIOR_BP"]:
                self.interior_assembly = pc_types.Assembly(child)              
            if "IS_EXTERIOR_BP" in child and child["IS_EXTERIOR_BP"]:
                self.exterior_assembly = pc_types.Assembly(child)
            if "IS_COUNTERTOP_BP" in child and child["IS_COUNTERTOP_BP"]:
                self.countertop = pc_types.Assembly(child)   
            if "IS_DRAWERS_BP" in child and child["IS_DRAWERS_BP"]:
                self.drawers = pc_types.Assembly(child)   
                self.calculators.append(self.drawers.get_calculator('Front Height Calculator'))
            if "IS_DOORS_BP" in child and child["IS_DOORS_BP"]:
                self.doors = pc_types.Assembly(child)
            if "IS_VERTICAL_SPLITTER_BP" in child and child["IS_VERTICAL_SPLITTER_BP"]:
                self.splitter = pc_types.Assembly(child)   
                self.calculators.append(self.splitter.get_calculator('Opening Height Calculator'))

        for child in self.carcass.obj_bp.children:
            if "IS_LEFT_SIDE_BP" in child and child["IS_LEFT_SIDE_BP"]:
                self.left_side = pc_types.Assembly(child)
            if "IS_RIGHT_SIDE_BP" in child and child["IS_RIGHT_SIDE_BP"]:
                self.right_side = pc_types.Assembly(child)  

    def invoke(self,context,event):
        self.reset_variables()
        bp = home_builder_utils.get_cabinet_bp(context.object)
        self.cabinet = pc_types.Assembly(bp)
        self.cabinet_name = self.cabinet.obj_bp.name
        self.depth = math.fabs(self.cabinet.obj_y.location.y)
        self.height = math.fabs(self.cabinet.obj_z.location.z)
        self.width = math.fabs(self.cabinet.obj_x.location.x)
        self.get_assemblies(context)
        if self.drawer_calculator:
            self.drawer_calculator.calculate()
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
        add_bottom_light = self.carcass.get_prompt("Add Bottom Light")
        add_top_light = self.carcass.get_prompt("Add Top Light")
        add_side_light = self.carcass.get_prompt("Add Side Light")
        add_sink = self.carcass.get_prompt("Add Sink")

        left_finished_end.draw(layout)
        right_finished_end.draw(layout)
        if toe_kick_height:
            toe_kick_height.draw(layout)
        if toe_kick_setback:
            toe_kick_setback.draw(layout)
        if add_bottom_light:
            add_bottom_light.draw(layout)      
        if add_top_light:
            add_top_light.draw(layout)                   
        if add_side_light:
            add_side_light.draw(layout)    

    def draw_sink_prompts(self,layout,context):
        add_sink = self.cabinet.get_prompt("Add Sink")

        if not add_sink:
            return False

        layout.operator_context = 'INVOKE_AREA'
        layout.operator('home_builder.cabinet_sink_options',text="Sink Options")
        # add_sink.draw(layout)

        # if add_sink.get_value():
        #     layout.prop(self,'sink_category',text="",icon='FILE_FOLDER')  
        #     if len(self.sink_name) > 0:
        #         layout.template_icon_view(self,"sink_name",show_labels=True)  

    def draw_countertop_prompts(self,layout,context):
        ctop_front = self.cabinet.get_prompt("Countertop Overhang Front")
        ctop_back = self.cabinet.get_prompt("Countertop Overhang Back")
        ctop_left = self.cabinet.get_prompt("Countertop Overhang Left")
        ctop_right = self.cabinet.get_prompt("Countertop Overhang Right")

        if ctop_front:
            ctop_front.draw(layout)
        if ctop_back:
            ctop_back.draw(layout)     
        if ctop_left:  
            ctop_left.draw(layout)  
        if ctop_right:
            ctop_right.draw(layout)         

    def check_for_stale_data(self,context,assembly,prompt_name):
        '''
        After removing assemblies some data doesn't evaluate correctly
        This is use to make sure the current assemblies are loaded.
        TODO: Find a better way to reload current assemblies
        '''
        try:
            prompt = assembly.get_prompt(prompt_name)
        except:
            self.get_assemblies(context)

    def draw_door_prompts(self,layout,context):
        self.check_for_stale_data(context,self.doors,"Open Door")

        if self.doors:
            open_door = self.doors.get_prompt("Open Door")
            open_door.draw(layout)

            door_swing = self.doors.get_prompt("Door Swing")
            door_swing.draw(layout,allow_edit=False)

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
            self.draw_sink_prompts(prompt_box,context)

        if self.product_tabs == 'EXTERIOR':
            prompt_box.prop(self,'exterior')
            if self.doors:
                self.draw_door_prompts(prompt_box,context)
            if self.drawer_calculator:
                self.draw_drawer_prompts(prompt_box,context)

        if self.product_tabs == 'INTERIOR':
            prompt_box.prop(self,'interior')
            # TODO: Draw interior options


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
            update_cabinet_id_props(obj)
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
        for child in self.sink.obj_bp.children:
            update_cabinet_id_props(child)
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

def update_range(self,context):
    if self.appliance_bp_name not in bpy.data.objects:
        return

    obj = bpy.data.objects[self.appliance_bp_name]
    bp = home_builder_utils.get_appliance_bp(obj)

    appliance = pc_types.Assembly(bp)    
    range_assembly = None

    for child in appliance.obj_bp.children:
        if "IS_RANGE_BP" in child and child["IS_RANGE_BP"]:
            range_assembly = pc_types.Assembly(child)               

    root_path = home_builder_paths.get_range_path()
    range_path = os.path.join(root_path,self.range_category,self.range_name + ".blend")
    range_bp = appliance.add_assembly_from_file(range_path)

    new_range_assembly = pc_types.Assembly(range_bp)
    new_range_assembly.obj_bp["IS_RANGE_BP"] = True

    appliance.dim_x(value=new_range_assembly.obj_x.location.x)
    appliance.dim_y(value=new_range_assembly.obj_y.location.y)
    appliance.dim_z(value=new_range_assembly.obj_z.location.z)

    if range_assembly:
        pc_utils.delete_object_and_children(range_assembly.obj_bp)

def update_range_hood(self,context):
    if self.appliance_bp_name not in bpy.data.objects:
        return

    obj = bpy.data.objects[self.appliance_bp_name]
    bp = home_builder_utils.get_appliance_bp(obj)

    appliance = pc_types.Assembly(bp)    
    range_hood_assembly = None

    for child in appliance.obj_bp.children:
        if "IS_RANGE_HOOD_BP" in child and child["IS_RANGE_HOOD_BP"]:
            range_hood_assembly = pc_types.Assembly(child)

    if self.add_range_hood:
        root_path = home_builder_paths.get_range_hood_path()
        range_path = os.path.join(root_path,self.range_hood_category,self.range_hood_name + ".blend")
        range_bp = appliance.add_assembly_from_file(range_path)

        new_range_hood_assembly = pc_types.Assembly(range_bp)
        new_range_hood_assembly.obj_bp["IS_RANGE_HOOD_BP"] = True
        

        a_width = appliance.obj_x.location.x
        a_height = appliance.obj_z.location.z

        rh_width = new_range_hood_assembly.obj_x.location.x
        print('HOOD',(a_width/2)-(rh_width/2))
        new_range_hood_assembly.loc_x(value = (a_width/2)-(rh_width/2))
        new_range_hood_assembly.loc_z(value = a_height+pc_unit.inch(36))

    if range_hood_assembly:
        pc_utils.delete_object_and_children(range_hood_assembly.obj_bp)

class home_builder_OT_range_options(bpy.types.Operator):
    bl_idname = "home_builder.range_options"
    bl_label = "Range Options"

    appliance_bp_name: bpy.props.StringProperty(name="Appliance BP Name",default="")
    add_range_hood: bpy.props.BoolProperty(name="Add Range Hood",default=False,update=update_range_hood)

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
    range_appliance = None
    range_hood_appliance = None
    previous_range_appliance = None
    previous_range_hood_appliance = None

    def reset_variables(self):
        self.product = None
        self.range_appliance = None
        self.range_hood_appliance = None

    def check(self, context):
        
        return True             

    def execute(self, context):
        return {'FINISHED'}

    def get_assemblies(self,context):
        self.carcass = None
        self.countertop = None

        for child in self.product.obj_bp.children:
            if "IS_RANGE_BP" in child and child["IS_RANGE_BP"]:
                self.range_appliance = pc_types.Assembly(child)

    def invoke(self,context,event):
        self.reset_variables()
        bp = home_builder_utils.get_appliance_bp(context.object)
        self.product = pc_types.Assembly(bp)
        self.appliance_bp_name = self.product.obj_bp.name
        self.get_assemblies(context)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=500)

    def draw_range_prompts(self,layout,context):
        layout.label(text="")
        box = layout.box()
        box.prop(self,'range_category',text="",icon='FILE_FOLDER')  
        if len(self.range_name) > 0:
            box.template_icon_view(self,"range_name",show_labels=True)  

    def draw_range_hood_prompts(self,layout,context):
        layout.prop(self,'add_range_hood')
        
        if not self.add_range_hood:
            return False

        if self.add_range_hood:
            box = layout.box()
            box.prop(self,'range_hood_category',text="",icon='FILE_FOLDER')  
            if len(self.range_hood_name) > 0:
                box.template_icon_view(self,"range_hood_name",show_labels=True)  

    def draw(self, context):
        layout = self.layout

        split = layout.split()
        self.draw_range_prompts(split.column(),context)
        self.draw_range_hood_prompts(split.column(),context)


class home_builder_MT_cabinet_menu(bpy.types.Menu):
    bl_label = "Cabinet Commands"

    def draw(self, context):
        layout = self.layout
        obj_bp = pc_utils.get_assembly_bp(context.object)
        cabinet_bp = home_builder_utils.get_cabinet_bp(context.object)
        appliance_bp = home_builder_utils.get_appliance_bp(context.object)
        layout.operator_context = 'INVOKE_AREA'

        if cabinet_bp:
            cabinet = pc_types.Assembly(cabinet_bp)  
            add_sink = cabinet.get_prompt("Add Sink")
            if add_sink:
                layout.operator('home_builder.cabinet_sink_options',text="Cabinet Sink Options",icon='WINDOW')

        if appliance_bp:
            range_bp = home_builder_utils.get_range_bp(context.object)
            if range_bp:
                layout.operator('home_builder.range_options',text="Range Options",icon='WINDOW')

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
        obj_bp = pc_utils.get_assembly_bp(context.object)
        for child in obj_bp.children:
            if child.type == 'MESH':
                home_builder_utils.apply_hook_modifiers(context,child)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(home_builder_OT_place_cabinet)  
    bpy.utils.register_class(home_builder_OT_cabinet_prompts)  
    bpy.utils.register_class(home_builder_OT_cabinet_sink_options)  
    bpy.utils.register_class(home_builder_OT_range_options)  
    bpy.utils.register_class(home_builder_MT_cabinet_menu)     
    bpy.utils.register_class(home_builder_OT_delete_cabinet)    
    bpy.utils.register_class(home_builder_OT_delete_part)    
    bpy.utils.register_class(home_builder_OT_part_prompts)    
    bpy.utils.register_class(home_builder_OT_hardlock_part_size)  

def unregister():
    bpy.utils.unregister_class(home_builder_OT_place_cabinet)  
    bpy.utils.unregister_class(home_builder_OT_cabinet_prompts)   
    bpy.utils.unregister_class(home_builder_OT_cabinet_sink_options)   
    bpy.utils.unregister_class(home_builder_OT_range_options) 
    bpy.utils.unregister_class(home_builder_MT_cabinet_menu)       
    bpy.utils.unregister_class(home_builder_OT_delete_cabinet)        
    bpy.utils.unregister_class(home_builder_OT_delete_part)      
    bpy.utils.unregister_class(home_builder_OT_part_prompts) 
    bpy.utils.unregister_class(home_builder_OT_hardlock_part_size)    