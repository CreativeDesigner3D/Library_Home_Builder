import bpy
import os
import math
from ..pc_lib import pc_utils, pc_types, pc_unit
from .. import home_builder_utils
from .. import home_builder_enums
from . import data_doors_windows

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
        home_builder_utils.update_id_props(obj,self.assembly.obj_bp)
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

def update_door_panel(self,context):
    self.door_panel_changed = True

def update_door_frame(self,context):
    self.door_frame_changed = True

def update_door_handle(self,context):
    self.door_handle_changed = True

class home_builder_OT_door_prompts(bpy.types.Operator):
    bl_idname = "home_builder.door_prompts"
    bl_label = "Entry Door Prompts"

    assembly_name: bpy.props.StringProperty(name="Window Name",default="")
    door_panel_changed: bpy.props.BoolProperty(name="Door Panel Changed")
    door_frame_changed: bpy.props.BoolProperty(name="Door Frame Changed")
    door_handle_changed: bpy.props.BoolProperty(name="Door Handle Changed")

    entry_door_tabs: bpy.props.EnumProperty(name="Entry Door Tabs",
                                         items=[('PANEL',"Panel","Panel Options"),
                                                ('FRAME',"Frame","Frame Options"),
                                                ('HANDLE',"Handle","Handle Options")])

    door_swing: bpy.props.EnumProperty(name="Door Swing",
                                       items=[('LEFT',"Left","Left Swing Door"),
                                              ('RIGHT',"Right","Right Swing Door"),
                                              ('DOUBLE',"Double","Double Doors")])

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    entry_door_panel_category: bpy.props.EnumProperty(name="Entry Door Panel Category",
        items=home_builder_enums.enum_entry_door_panel_categories,
        update=home_builder_enums.update_entry_door_panel_category)
    entry_door_panel: bpy.props.EnumProperty(name="Entry Door Panel",
        items=home_builder_enums.enum_entry_door_panels_names,
        update=update_door_panel)

    entry_door_frame_category: bpy.props.EnumProperty(name="Entry Door Frame Category",
        items=home_builder_enums.enum_entry_door_frame_categories,
        update=home_builder_enums.update_entry_door_frame_category)
    entry_door_frame: bpy.props.EnumProperty(name="Entry Door Frame",
        items=home_builder_enums.enum_entry_door_frame_names,
        update=update_door_frame)

    entry_door_handle_category: bpy.props.EnumProperty(name="Entry Door Handle Category",
        items=home_builder_enums.enum_entry_door_handle_categories,
        update=home_builder_enums.update_entry_door_handle_category)
    entry_door_handle: bpy.props.EnumProperty(name="Entry Door Handle",
        items=home_builder_enums.enum_entry_door_handle_names,
        update=update_door_handle)

    assembly = None
    door_panels = []
    door_frames = []
    door_handles = []

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

    def update_door_panel(self,context):
        if self.door_panel_changed:
            for door_panel in self.door_panels:
                pc_utils.delete_object_and_children(door_panel)

            if hasattr(self.assembly,'add_doors'):
                self.assembly.add_doors(door_panel_category=self.entry_door_panel_category,
                                        door_panel_name=self.entry_door_panel,
                                        door_handle_category=self.entry_door_handle_category,
                                        door_handle_name=self.entry_door_handle)
                
                home_builder_utils.hide_empties(self.assembly.obj_bp)

            self.door_panel_changed = False
            self.get_assemblies_and_set_prompts(context)

    def update_door_frame(self,context):
        if self.door_frame_changed:
            for door_frame in self.door_frames:
                pc_utils.delete_object_and_children(door_frame)

            if hasattr(self.assembly,'add_frame'):
                self.assembly.add_frame(door_frame_category=self.entry_door_frame_category,
                                        door_frame_name=self.entry_door_frame)
                
                home_builder_utils.hide_empties(self.assembly.obj_bp)

            self.door_frame_changed = False
            self.get_assemblies_and_set_prompts(context)

    def update_door_handle(self,context):
        if self.door_handle_changed:
            for door_handle in self.door_handles:
                pc_utils.delete_object_and_children(door_handle)

            for door_panel_bp in self.door_panels:
                door_panel = pc_types.Assembly(door_panel_bp)
                if hasattr(self.assembly,'add_door_handle'):
                    self.assembly.add_door_handle(door_panel=door_panel,
                                                  door_handle_category=self.entry_door_handle_category,
                                                  door_handle_name=self.entry_door_handle)
                
                home_builder_utils.hide_empties(self.assembly.obj_bp)

            self.door_handle_changed = False
            self.get_assemblies_and_set_prompts(context)

    def check(self, context):
        self.update_product_size()
        self.update_door_panel(context)
        self.update_door_frame(context)
        self.update_door_handle(context)
        entry_door_swing = self.assembly.get_prompt("Entry Door Swing")
        if entry_door_swing:
            if self.door_swing == 'LEFT':
                entry_door_swing.set_value(0)
            if self.door_swing == 'RIGHT':
                entry_door_swing.set_value(1)
            if self.door_swing == 'DOUBLE':
                entry_door_swing.set_value(2)                        
        return True

    def execute(self, context):
        return {'FINISHED'}

    def get_assemblies_and_set_prompts(self,context):
        self.door_panels = []
        self.door_frames = []
        self.door_handles = []
        
        bp_window = home_builder_utils.get_window_bp(context.object)
        if bp_window:
            self.assembly = data_doors_windows.Standard_Window(bp_window)
        bp_door = home_builder_utils.get_door_bp(context.object)  
        if bp_door:
            self.assembly = data_doors_windows.Standard_Door(bp_door)
        for child in self.assembly.obj_bp.children:
            if "IS_ENTRY_DOOR_PANEL" in child:
                self.door_panels.append(child)
                for nchild in child.children:
                    if "IS_ENTRY_DOOR_HANDLE" in nchild:
                        self.door_handles.append(nchild)
        for child in self.assembly.obj_bp.children:
            if "IS_ENTRY_DOOR_FRAME" in child:
                self.door_frames.append(child)

        entry_door_swing = self.assembly.get_prompt("Entry Door Swing")
        if entry_door_swing:
            if entry_door_swing.get_value() == 0:
                self.door_swing = 'LEFT'
            if entry_door_swing.get_value() == 1:
                self.door_swing = 'RIGHT'
            if entry_door_swing.get_value() == 2:
                self.door_swing = 'DOUBLE'

    def invoke(self,context,event):
        self.get_assemblies_and_set_prompts(context)
        self.depth = math.fabs(self.assembly.obj_y.location.y)
        self.height = math.fabs(self.assembly.obj_z.location.z)
        self.width = math.fabs(self.assembly.obj_x.location.x)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

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

        row = box.row()    
        row.label(text="Location:")
        row.prop(self.assembly.obj_bp,'location',index=0,text="X")
        row.prop(self.assembly.obj_bp,'location',index=2,text="Z")

    def draw_prompts(self,layout,context):
        # door_reveal = self.assembly.get_prompt("Door Reveal")
        handle_vertical_location = self.assembly.get_prompt("Handle Vertical Location")
        handle_location_from_edge = self.assembly.get_prompt("Handle Location From Edge")
        entry_door_swing = self.assembly.get_prompt("Entry Door Swing")
        outswing = self.assembly.get_prompt("Outswing")
        open_door = self.assembly.get_prompt("Open Door")

        if open_door and outswing and entry_door_swing:
            box = layout.box()
            box.label(text="Door Swing")
            row = box.row()
            open_door.draw(row,allow_edit=False)
            row = box.row(align=True)
            row.label(text="Door Swing")
            row.prop_enum(self, "door_swing", 'LEFT') 
            row.prop_enum(self, "door_swing", 'RIGHT') 
            row.prop_enum(self, "door_swing", 'DOUBLE')
            outswing.draw(row,allow_edit=False)     

        if handle_vertical_location and handle_location_from_edge:
            box = layout.box()
            box.label(text="Door Hardware")
            row = box.row()
            row.label(text="Pull Location:")
            row.prop(handle_vertical_location,'distance_value',text="Vertical")  
            row.prop(handle_location_from_edge,'distance_value',text="From Edge")  

    def draw_door_panel(self,layout,context):
        layout.prop(self,'entry_door_panel_category',text="")
        layout.template_icon_view(self,"entry_door_panel",show_labels=True)          

    def draw_door_frame(self,layout,context):
        layout.prop(self,'entry_door_frame_category',text="")
        layout.template_icon_view(self,"entry_door_frame",show_labels=True)      

    def draw_door_handle(self,layout,context):
        layout.prop(self,'entry_door_handle_category',text="")
        layout.template_icon_view(self,"entry_door_handle",show_labels=True)      

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(layout,context)
        self.draw_prompts(layout,context)
        box = layout.box()
        row = box.row(align=True)
        row.prop(self,'entry_door_tabs',expand=True)
        if self.entry_door_tabs == 'PANEL':
            self.draw_door_panel(box,context)
        if self.entry_door_tabs == 'FRAME':
            self.draw_door_frame(box,context)
        if self.entry_door_tabs == 'HANDLE':
            self.draw_door_handle(box,context)                        


class home_builder_OT_window_prompts(bpy.types.Operator):
    bl_idname = "home_builder.window_prompts"
    bl_label = "Window Prompts"

    assembly_name: bpy.props.StringProperty(name="Window Name",default="")
    door_panel_changed: bpy.props.BoolProperty(name="Door Panel Changed")
    door_frame_changed: bpy.props.BoolProperty(name="Door Frame Changed")
    door_handle_changed: bpy.props.BoolProperty(name="Door Handle Changed")

    entry_door_tabs: bpy.props.EnumProperty(name="Entry Door Tabs",
                                         items=[('PANEL',"Panel","Panel Options"),
                                                ('FRAME',"Frame","Frame Options"),
                                                ('HANDLE',"Handle","Handle Options")])

    door_swing: bpy.props.EnumProperty(name="Door Swing",
                                       items=[('LEFT',"Left","Left Swing Door"),
                                              ('RIGHT',"Right","Right Swing Door"),
                                              ('DOUBLE',"Double","Double Doors")])

    width: bpy.props.FloatProperty(name="Width",unit='LENGTH',precision=4)
    height: bpy.props.FloatProperty(name="Height",unit='LENGTH',precision=4)
    depth: bpy.props.FloatProperty(name="Depth",unit='LENGTH',precision=4)

    entry_door_panel_category: bpy.props.EnumProperty(name="Entry Door Panel Category",
        items=home_builder_enums.enum_entry_door_panel_categories,
        update=home_builder_enums.update_entry_door_panel_category)
    entry_door_panel: bpy.props.EnumProperty(name="Entry Door Panel",
        items=home_builder_enums.enum_entry_door_panels_names,
        update=update_door_panel)

    entry_door_frame_category: bpy.props.EnumProperty(name="Entry Door Frame Category",
        items=home_builder_enums.enum_entry_door_frame_categories,
        update=home_builder_enums.update_entry_door_frame_category)
    entry_door_frame: bpy.props.EnumProperty(name="Entry Door Frame",
        items=home_builder_enums.enum_entry_door_frame_names,
        update=update_door_frame)

    entry_door_handle_category: bpy.props.EnumProperty(name="Entry Door Handle Category",
        items=home_builder_enums.enum_entry_door_handle_categories,
        update=home_builder_enums.update_entry_door_handle_category)
    entry_door_handle: bpy.props.EnumProperty(name="Entry Door Handle",
        items=home_builder_enums.enum_entry_door_handle_names,
        update=update_door_handle)

    assembly = None
    door_panels = []
    door_frames = []
    door_handles = []

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

    def update_door_panel(self,context):
        if self.door_panel_changed:
            for door_panel in self.door_panels:
                pc_utils.delete_object_and_children(door_panel)

            if hasattr(self.assembly,'add_doors'):
                self.assembly.add_doors(door_panel_category=self.entry_door_panel_category,
                                        door_panel_name=self.entry_door_panel)
                
                home_builder_utils.hide_empties(self.assembly.obj_bp)

            self.door_panel_changed = False
            self.get_assemblies_and_set_prompts(context)

    def update_door_frame(self,context):
        if self.door_frame_changed:
            for door_frame in self.door_frames:
                pc_utils.delete_object_and_children(door_frame)

            if hasattr(self.assembly,'add_frame'):
                print('add frame',self.assembly)
                self.assembly.add_frame(door_frame_category=self.entry_door_frame_category,
                                        door_frame_name=self.entry_door_frame)
                
                home_builder_utils.hide_empties(self.assembly.obj_bp)

            self.door_frame_changed = False
            self.get_assemblies_and_set_prompts(context)

    def update_door_handle(self,context):
        pass

    def check(self, context):
        self.update_product_size()
        self.update_door_panel(context)
        self.update_door_frame(context)
        entry_door_swing = self.assembly.get_prompt("Entry Door Swing")
        if entry_door_swing:
            if self.door_swing == 'LEFT':
                entry_door_swing.set_value(0)
            if self.door_swing == 'RIGHT':
                entry_door_swing.set_value(1)
            if self.door_swing == 'DOUBLE':
                entry_door_swing.set_value(2)                        
        return True

    def execute(self, context):
        return {'FINISHED'}

    def get_assemblies_and_set_prompts(self,context):
        self.door_panels = []
        self.door_frames = []
        self.door_handles = []
        
        bp_window = home_builder_utils.get_window_bp(context.object)
        if bp_window:
            self.assembly = data_doors_windows.Standard_Window(bp_window)
        bp_door = home_builder_utils.get_door_bp(context.object)  
        if bp_door:
            self.assembly = data_doors_windows.Standard_Door(bp_door)
        for child in self.assembly.obj_bp.children:
            if "IS_ENTRY_DOOR_PANEL" in child:
                self.door_panels.append(child)
        for child in self.assembly.obj_bp.children:
            if "IS_ENTRY_DOOR_FRAME" in child:
                self.door_frames.append(child)

        entry_door_swing = self.assembly.get_prompt("Entry Door Swing")
        if entry_door_swing:
            if entry_door_swing.get_value() == 0:
                self.door_swing = 'LEFT'
            if entry_door_swing.get_value() == 1:
                self.door_swing = 'RIGHT'
            if entry_door_swing.get_value() == 2:
                self.door_swing = 'DOUBLE'

    def invoke(self,context,event):
        self.get_assemblies_and_set_prompts(context)
        self.depth = math.fabs(self.assembly.obj_y.location.y)
        self.height = math.fabs(self.assembly.obj_z.location.z)
        self.width = math.fabs(self.assembly.obj_x.location.x)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

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

        row = box.row()    
        row.label(text="Location:")
        row.prop(self.assembly.obj_bp,'location',index=0,text="X")
        row.prop(self.assembly.obj_bp,'location',index=2,text="Z")

    def draw_prompts(self,layout,context):
        # door_reveal = self.assembly.get_prompt("Door Reveal")
        handle_vertical_location = self.assembly.get_prompt("Handle Vertical Location")
        handle_location_from_edge = self.assembly.get_prompt("Handle Location From Edge")
        entry_door_swing = self.assembly.get_prompt("Entry Door Swing")
        outswing = self.assembly.get_prompt("Outswing")
        open_door = self.assembly.get_prompt("Open Door")

        if open_door and outswing and entry_door_swing:
            box = layout.box()
            box.label(text="Door Swing")
            row = box.row()
            open_door.draw(row,allow_edit=False)
            row = box.row(align=True)
            row.label(text="Door Swing")
            row.prop_enum(self, "door_swing", 'LEFT') 
            row.prop_enum(self, "door_swing", 'RIGHT') 
            row.prop_enum(self, "door_swing", 'DOUBLE')
            outswing.draw(row,allow_edit=False)     

        if handle_vertical_location and handle_location_from_edge:
            box = layout.box()
            box.label(text="Door Hardware")
            row = box.row()
            row.label(text="Pull Location:")
            row.prop(handle_vertical_location,'distance_value',text="Vertical")  
            row.prop(handle_location_from_edge,'distance_value',text="From Edge")  

    def draw_door_panel(self,layout,context):
        layout.prop(self,'entry_door_panel_category',text="")
        layout.template_icon_view(self,"entry_door_panel",show_labels=True)          

    def draw_door_frame(self,layout,context):
        layout.prop(self,'entry_door_frame_category',text="")
        layout.template_icon_view(self,"entry_door_frame",show_labels=True)      

    def draw_door_handle(self,layout,context):
        layout.prop(self,'entry_door_handle_category',text="")
        layout.template_icon_view(self,"entry_door_handle",show_labels=True)      

    def draw(self, context):
        layout = self.layout
        self.draw_product_size(layout,context)
        self.draw_prompts(layout,context)
        box = layout.box()
        row = box.row(align=True)
        row.prop(self,'entry_door_tabs',expand=True)
        if self.entry_door_tabs == 'PANEL':
            self.draw_door_panel(box,context)
        if self.entry_door_tabs == 'FRAME':
            self.draw_door_frame(box,context)
        if self.entry_door_tabs == 'HANDLE':
            self.draw_door_handle(box,context)              

classes = (
    home_builder_OT_place_door_window,
    home_builder_OT_door_prompts,
    home_builder_OT_window_prompts,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()