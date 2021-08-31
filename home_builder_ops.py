import bpy,os,inspect, sys
import math
import subprocess
import datetime
import codecs
from datetime import date
from bpy.types import (Header, 
                       Menu, 
                       Panel, 
                       Operator,
                       PropertyGroup)

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       PointerProperty,
                       EnumProperty,
                       CollectionProperty)

from .pc_lib import pc_unit, pc_utils, pc_types
from .cabinets import data_cabinets
from .cabinets import data_cabinet_carcass
from .cabinets import data_cabinet_exteriors
from .cabinets import data_cabinet_parts
from .cabinets import data_drawer_box
from .cabinets import cabinet_utils
from . import home_builder_pointers
from . import home_builder_utils
from . import home_builder_paths
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector

try:
    import reportlab
except ModuleNotFoundError:
    PATH = os.path.join(os.path.dirname(__file__),"python_libs")
    sys.path.append(PATH)

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import legal,letter,inch
from reportlab.platypus import Image
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Frame, Spacer, PageTemplate, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, A4, landscape, portrait
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus.flowables import HRFlowable

def event_is_place_asset(event):
    if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
        return True
    elif event.type == 'NUMPAD_ENTER' and event.value == 'PRESS':
        return True
    elif event.type == 'RET' and event.value == 'PRESS':
        return True
    else:
        return False

def event_is_cancel_command(event):
    if event.type in {'RIGHTMOUSE', 'ESC'}:
        return True
    else:
        return False

def event_is_pass_through(event):
    if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
        return True
    else:
        return False

class home_builder_OT_activate(Operator):
    bl_idname = "home_builder.activate"
    bl_label = "Activate Room Builder"
    bl_description = "This activates the room builder"
    bl_options = {'UNDO'}
    
    library_name: StringProperty(name='Library Name')

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)

        root_path = props.get_current_catalog_path()
        path = os.path.join(root_path,props.get_active_catalog_name())

        if len(props.material_pointer_groups) == 0:
            home_builder_pointers.update_pointer_properties()

        pc_utils.update_file_browser_path(context,path)
        return {'FINISHED'}


class home_builder_OT_change_library_category(bpy.types.Operator):
    bl_idname = "home_builder.change_library_category"
    bl_label = "Change Library Category"
    bl_description = "This changes the active library category"

    category: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        root_path = props.get_current_catalog_path()
        path = os.path.join(root_path,self.category)
        if os.path.exists(path):
            if props.library_tabs == 'ROOMS':
                if props.room_tabs == 'WALLS':
                    props.active_wall_catalog = self.category
                if props.room_tabs == 'DOORS':
                    props.active_door_catalog = self.category
                if props.room_tabs == 'WINDOWS':
                    props.active_window_catalog = self.category
                if props.room_tabs == 'OBSTACLES':
                    props.active_obstacle_catalog = self.category               
                if props.room_tabs == 'DECORATIONS':
                    props.active_room_decoration_catalog = self.category  

            if props.library_tabs == 'KITCHENS':
                if props.kitchen_tabs == 'RANGES':
                    props.active_range_catalog = self.category
                if props.kitchen_tabs == 'REFRIGERATORS':
                    props.active_regfrigerator_catalog = self.category
                if props.kitchen_tabs == 'DISHWASHERS':
                    props.active_dishwasher_catalog = self.category                                        
                if props.kitchen_tabs == 'CABINETS':
                    props.active_cabinet_catalog = self.category    
                if props.kitchen_tabs == 'PARTS':
                    props.active_cabinet_part_catalog = self.category    
                if props.kitchen_tabs == 'CUSTOM_CABINETS':
                    props.active_custom_cabinet_catalog = self.category   
                if props.kitchen_tabs == 'DECORATIONS':
                    props.active_kitchen_decoration_catalog = self.category 

            if props.library_tabs == 'BATHS':
                if props.bath_tabs == 'TOILETS':
                    props.active_toilet_catalog = self.category 
                if props.bath_tabs == 'BATHS':
                    props.active_bath_catalog = self.category               
                if props.bath_tabs == 'VANITIES':
                    props.active_vanity_catalog = self.category 
                if props.bath_tabs == 'DECORATIONS':
                    props.active_bath_decoration_catalog = self.category                   

            if props.library_tabs == 'CLOSETS':
                if props.closet_tabs == 'STARTERS':
                    props.active_closet_starter_catalog = self.category   
                if props.closet_tabs == 'INSERTS':
                    props.active_closet_insert_catalog = self.category  
                if props.closet_tabs == 'SPLITTERS':
                    props.active_closet_splitter_catalog = self.category  
                if props.closet_tabs == 'CLOSET_PARTS':
                    props.active_closet_part_catalog = self.category                             
                if props.closet_tabs == 'DECORATIONS':
                    props.active_closet_decoration_catalog = self.category            
                
            pc_utils.update_file_browser_path(context,path)        

        return {'FINISHED'}

#REMOVE
class home_builder_OT_change_closet_category(bpy.types.Operator):
    bl_idname = "home_builder.change_closet_category"
    bl_label = "Change Closet Category"
    bl_description = "This changes the closet category"

    category: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        props.active_subcategory = self.category
        path = os.path.join(home_builder_paths.get_library_path(),"Closets",self.category)
        if os.path.exists(path):
            pc_utils.update_file_browser_path(context,path)
        return {'FINISHED'}


class home_builder_OT_disconnect_constraint(bpy.types.Operator):
    bl_idname = "home_builder.disconnect_constraint"
    bl_label = "Disconnect Constraint"
    
    obj_name: bpy.props.StringProperty(name="Base Point Name")

    def execute(self, context):
        obj = bpy.data.objects[self.obj_name]
        obj.constraints.clear()
        return {'FINISHED'}


class home_builder_OT_draw_floor_plane(bpy.types.Operator):
    bl_idname = "home_builder.draw_floor_plane"
    bl_label = "Draw Floor Plane"
    bl_options = {'UNDO'}
    
    def create_floor_mesh(self,name,size):
        
        verts = [(0.0, 0.0, 0.0),
                (0.0, size[1], 0.0),
                (size[0], size[1], 0.0),
                (size[0], 0.0, 0.0),
                ]

        faces = [(0, 1, 2, 3),
                ]

        return pc_utils.create_object_from_verts_and_faces(verts,faces,name)

    def execute(self, context):
        largest_x = 0
        largest_y = 0
        smallest_x = 0
        smallest_y = 0
        overhang = pc_unit.inch(6)
        wall_assemblies = []
        wall_bps = []
        for obj in context.visible_objects:
            if obj.parent and 'IS_WALL_BP' in obj.parent and obj.parent not in wall_bps:
                wall_bps.append(obj.parent)
                wall_assemblies.append(pc_types.Assembly(obj.parent))
            
        for assembly in wall_assemblies:
            start_point = (assembly.obj_bp.matrix_world[0][3],assembly.obj_bp.matrix_world[1][3],0)
            end_point = (assembly.obj_x.matrix_world[0][3],assembly.obj_x.matrix_world[1][3],0)

            if start_point[0] > largest_x:
                largest_x = start_point[0]
            if start_point[1] > largest_y:
                largest_y = start_point[1]
            if start_point[0] < smallest_x:
                smallest_x = start_point[0]
            if start_point[1] < smallest_y:
                smallest_y = start_point[1]
            if end_point[0] > largest_x:
                largest_x = end_point[0]
            if end_point[1] > largest_y:
                largest_y = end_point[1]
            if end_point[0] < smallest_x:
                smallest_x = end_point[0]
            if end_point[1] < smallest_y:
                smallest_y = end_point[1]

        loc = (smallest_x - overhang, smallest_y - overhang,0)
        width = math.fabs(smallest_y) + math.fabs(largest_y) + (overhang*2)
        length = math.fabs(largest_x) + math.fabs(smallest_x) + (overhang*2)
        if width == 0:
            width = pc_unit.inch(-48)
        if length == 0:
            length = pc_unit.inch(-48)
        obj_plane = self.create_floor_mesh('Floor',(length,width,0.0))
        context.view_layer.active_layer_collection.collection.objects.link(obj_plane)
        obj_plane.location = loc
        home_builder_utils.unwrap_obj(context,obj_plane)
        home_builder_pointers.assign_pointer_to_object(obj_plane,"Floor")
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.flip_normals()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.select_all(action='DESELECT')
        obj_plane["PROMPT_ID"] = "home_builder.floor_prompts"

        #SET CONTEXT
        context.view_layer.objects.active = obj_plane
        
        return {'FINISHED'}


class home_builder_OT_add_room_light(bpy.types.Operator):
    bl_idname = "home_builder.add_room_light"
    bl_label = "Add Room Light"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        largest_x = 0
        largest_y = 0
        smallest_x = 0
        smallest_y = 0
        wall_groups = []
        height = 0

        wall_assemblies = []
        wall_bps = []
        for obj in context.visible_objects:
            if obj.parent and 'IS_WALL_BP' in obj.parent and obj.parent not in wall_bps:
                wall_bps.append(obj.parent)
                wall_assemblies.append(pc_types.Assembly(obj.parent))

        for assembly in wall_assemblies:
            start_point = (assembly.obj_bp.matrix_world[0][3],assembly.obj_bp.matrix_world[1][3],0)
            end_point = (assembly.obj_x.matrix_world[0][3],assembly.obj_x.matrix_world[1][3],0)
            height = assembly.obj_z.location.z
            
            if start_point[0] > largest_x:
                largest_x = start_point[0]
            if start_point[1] > largest_y:
                largest_y = start_point[1]
            if start_point[0] < smallest_x:
                smallest_x = start_point[0]
            if start_point[1] < smallest_y:
                smallest_y = start_point[1]
            if end_point[0] > largest_x:
                largest_x = end_point[0]
            if end_point[1] > largest_y:
                largest_y = end_point[1]
            if end_point[0] < smallest_x:
                smallest_x = end_point[0]
            if end_point[1] < smallest_y:
                smallest_y = end_point[1]

        x = (math.fabs(largest_x) - math.fabs(smallest_x))/2
        y = (math.fabs(largest_y) - math.fabs(smallest_y))/2
        z = height - pc_unit.inch(.01)
        
        width = math.fabs(smallest_y) + math.fabs(largest_y)
        length = math.fabs(largest_x) + math.fabs(smallest_x)
        if width == 0:
            width = pc_unit.inch(-48)
        if length == 0:
            length = pc_unit.inch(-48)

        bpy.ops.object.light_add(type = 'AREA')
        obj_lamp = context.active_object
        obj_lamp.location.x = x
        obj_lamp.location.y = y
        obj_lamp.location.z = z
        obj_lamp.data.shape = 'RECTANGLE'
        obj_lamp.data.size = length + pc_unit.inch(20)
        obj_lamp.data.size_y = math.fabs(width) + pc_unit.inch(20)
        obj_lamp.data.energy = 120
        obj_lamp["PROMPT_ID"] = "home_builder.light_prompts"
        return {'FINISHED'}


class home_builder_OT_update_scene_materials(bpy.types.Operator):
    bl_idname = "home_builder.update_scene_materials"
    bl_label = "Update Scene Materials"
    
    def execute(self, context):
        for obj in context.visible_objects:
            if obj.type in {'MESH','CURVE'}:
                home_builder_pointers.assign_materials_to_object(obj)
        return {'FINISHED'}


class home_builder_OT_update_material_pointer(bpy.types.Operator):
    bl_idname = "home_builder.update_material_pointer"
    bl_label = "Update Material Pointer"
    
    pointer_name: bpy.props.StringProperty(name="Pointer Name")
    refresh: bpy.props.BoolProperty(name="Refresh",default=False)

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        group = props.material_pointer_groups[props.material_group_index]
        for pointer in group.pointers:
            if pointer.name == self.pointer_name:
                pointer.category = props.material_category
                pointer.item_name = props.material_name  

        if self.refresh:
            bpy.ops.home_builder.update_scene_materials()
        return {'FINISHED'}


class home_builder_OT_update_scene_pulls(bpy.types.Operator):
    bl_idname = "home_builder.update_scene_pulls"
    bl_label = "Update Scene Pulls"
    
    def execute(self, context):
        pull_objs = []
        pull_pointers = home_builder_utils.get_scene_props(context.scene).pull_pointers

        for obj in context.visible_objects:
            if "IS_CABINET_PULL" in obj and obj["IS_CABINET_PULL"]:
                pull_objs.append(obj)

        for pull in pull_objs:
            props = home_builder_utils.get_object_props(pull)
            exterior_bp = home_builder_utils.get_exterior_bp(pull)
            exterior = data_cabinet_exteriors.Cabinet_Exterior(exterior_bp)
            front_bp = home_builder_utils.get_cabinet_door_bp(pull)
            front = pc_types.Assembly(front_bp)
            pointer = pull_pointers[props.pointer_name]
            if "Drawer" in pointer.name:
                exterior.add_drawer_pull(front,pointer)
            else:
                exterior.add_door_pull(front,pointer)

        pc_utils.delete_obj_list(pull_objs)
        return {'FINISHED'}


class home_builder_OT_update_selected_pulls(bpy.types.Operator):
    bl_idname = "home_builder.update_selected_pulls"
    bl_label = "Update Selected Pulls"
    
    def execute(self, context):
        pull_objs = []
        scene_props = home_builder_utils.get_scene_props(context.scene) 

        for obj in context.selected_objects:
            if "IS_CABINET_PULL" in obj and obj["IS_CABINET_PULL"]:
                pull_objs.append(obj)

        for pull in pull_objs:
            props = home_builder_utils.get_object_props(pull)

            exterior_bp = home_builder_utils.get_exterior_bp(pull)

            pointer = TempPointer()
            pointer.name = props.pointer_name
            pointer.category = scene_props.pull_category
            pointer.item_name = scene_props.pull_name   

            front_bp = home_builder_utils.get_cabinet_door_bp(pull)
            front = pc_types.Assembly(front_bp)
            exterior = data_cabinet_exteriors.Cabinet_Exterior(exterior_bp)
            if "Drawer" in pointer.name:
                exterior.add_drawer_pull(front,pointer)
            else:
                exterior.add_door_pull(front,pointer)

        pc_utils.delete_obj_list(pull_objs)
        return {'FINISHED'}


class home_builder_OT_update_all_cabinet_doors(bpy.types.Operator):
    bl_idname = "home_builder.update_all_cabinet_doors"
    bl_label = "Update All Cabinet Doors"

    def execute(self, context):
        door_panel_bps = []
        scene_props = home_builder_utils.get_scene_props(context.scene)

        for obj in bpy.data.objects:
            if "IS_CABINET_DOOR_PANEL" in obj and obj["IS_CABINET_DOOR_PANEL"]:
                door_panel_bps.append(obj)

        for door_panel_bp in door_panel_bps:
            props = home_builder_utils.get_object_props(door_panel_bp)
            pointer = scene_props.cabinet_door_pointers[props.pointer_name]

            old_door_panel = pc_types.Assembly(door_panel_bp)
            exterior = data_cabinet_exteriors.Cabinet_Exterior(door_panel_bp.parent)
            exterior.replace_front(old_door_panel,pointer)
        return {'FINISHED'}


# This is used in home_builder.update_selected_cabinet_doors
# since you cannot create an instance of a blender PropertyGroup
# this is used to store the default properties for the pointer
# for the cabinet door front
class TempPointer():
    name = ""
    category = ""
    item_name = ""

class home_builder_OT_update_selected_cabinet_doors(bpy.types.Operator):
    bl_idname = "home_builder.update_selected_cabinet_doors"
    bl_label = "Update Selected Cabinet Doors"

    def execute(self, context):
        door_panel_bps = []
        scene_props = home_builder_utils.get_scene_props(context.scene)

        for obj in context.selected_objects:
            door_bp = home_builder_utils.get_cabinet_door_bp(obj)
            if door_bp and door_bp not in door_panel_bps:
                door_panel_bps.append(door_bp)

        for door_panel_bp in door_panel_bps:
            props = home_builder_utils.get_object_props(door_panel_bp)
            pointer = TempPointer()
            pointer.name = props.pointer_name
            pointer.category = scene_props.cabinet_door_category
            pointer.item_name = scene_props.cabinet_door_name

            old_door_panel = pc_types.Assembly(door_panel_bp)

            exterior = data_cabinet_exteriors.Cabinet_Exterior(door_panel_bp.parent)

            exterior.replace_front(old_door_panel,pointer)

        return {'FINISHED'}


class home_builder_OT_add_drawer(bpy.types.Operator):
    bl_idname = "home_builder.add_drawer"
    bl_label = "Add Drawer"

    def execute(self, context):
        door_panel_bps = []
        scene_props = home_builder_utils.get_scene_props(context.scene)

        for obj in context.selected_objects:
            door_bp = home_builder_utils.get_cabinet_door_bp(obj)
            if door_bp and door_bp not in door_panel_bps:
                door_panel_bps.append(door_bp)

        for door_panel_bp in door_panel_bps:
            exterior = data_cabinet_exteriors.Cabinet_Exterior(door_panel_bp.parent)
            exterior.add_drawer_box(pc_types.Assembly(door_panel_bp))

        return {'FINISHED'}


class home_builder_OT_update_pull_pointer(bpy.types.Operator):
    bl_idname = "home_builder.update_pull_pointer"
    bl_label = "Update Pull Pointer"
    
    pointer_name: bpy.props.StringProperty(name="Pointer Name")

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        for pointer in props.pull_pointers:
            if pointer.name == self.pointer_name:
                pointer.category = props.pull_category
                pointer.item_name = props.pull_name      
        return {'FINISHED'}


class home_builder_OT_update_molding_pointer(bpy.types.Operator):
    bl_idname = "home_builder.update_molding_pointer"
    bl_label = "Update Molding Pointer"
    
    pointer_name: bpy.props.StringProperty(name="Pointer Name")

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        for pointer in props.molding_pointers:
            if pointer.name == self.pointer_name:
                pointer.category = props.molding_category
                pointer.item_name = props.molding_name      
        return {'FINISHED'}


class home_builder_OT_update_cabinet_door_pointer(bpy.types.Operator):
    bl_idname = "home_builder.update_cabinet_door_pointer"
    bl_label = "Update Cabinet Door Pointer"
    
    pointer_name: bpy.props.StringProperty(name="Pointer Name")

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        for pointer in props.cabinet_door_pointers:
            if pointer.name == self.pointer_name:
                pointer.category = props.cabinet_door_category
                pointer.item_name = props.cabinet_door_name      
        return {'FINISHED'}

class home_builder_OT_generate_2d_views(bpy.types.Operator):
    bl_idname = "home_builder.generate_2d_views"
    bl_label = "Generate 2D Views"
    
    def execute(self, context):
        return {'FINISHED'}


class home_builder_OT_toggle_dimensions(bpy.types.Operator):
    bl_idname = "home_builder.toggle_dimensions"
    bl_label = "Toggle Dimensions"
    
    def execute(self, context):
        return {'FINISHED'}        


class home_builder_OT_render_asset_thumbnails(Operator):
    bl_idname = "home_builder.render_asset_thumbnails"
    bl_label = "Render Asset Thumbnails"
    bl_description = "This will open a dialog and allow you to register assets found in the library"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return True

    def reset_variables(self):
        pass

    def create_item_thumbnail_script(self,asset):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("import sys\n")
        file.write("import " + __package__ + "\n")
        file.write("bpy.ops.home_builder.reload_pointers()\n")
        
        #CREATE DIR
        file.write("dir_path = r'" + asset.library_path + "'\n")
        file.write("path = os.path.join(dir_path,'" + asset.name.replace("_"," ") + "')\n")
        file.write("if not os.path.exists(dir_path):\n")
        file.write("    os.makedirs(dir_path)\n")

        #SELECT ALL OBJECTS FUNCTION
        file.write("def select_objects():\n")
        file.write("    for obj in bpy.data.objects:\n")
        file.write("        if obj.type == 'MESH':\n")
        file.write("            obj.select_set(True)\n")

        #DRAW ASSET
        file.write("item = eval('" + __package__ + "." + asset.package_name + "." + asset.module_name + "." + asset.class_name + "()')" + "\n")
        # file.write("if hasattr(item,'pre_draw'):\n")
        # file.write("    item.pre_draw()\n")        
        # file.write("if hasattr(item,'draw'):\n")
        # file.write("    item.draw()\n")
        # file.write("if hasattr(item,'draw_door'):\n")
        # file.write("    item.draw_door()\n")      
        # file.write("if hasattr(item,'draw_wall'):\n")
        # file.write("    item.draw_wall()\n")          
        file.write("if hasattr(item,'render'):\n")
        file.write("    item.render()\n")

        #VIEW ASSET
        file.write("bpy.ops.object.select_all(action='DESELECT')\n")
        file.write("select_objects()\n")
        file.write("bpy.ops.view3d.camera_to_view_selected()\n")

        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")

        #RENDER
        file.write("bpy.context.scene.camera.data.lens = 40\n")
        file.write("bpy.context.scene.camera.location.z += .05\n")
        file.write("render = bpy.context.scene.render\n")
        file.write("render.resolution_x = 540\n")
        file.write("render.resolution_y = 540\n")
        file.write("render.engine = 'BLENDER_EEVEE'\n")
        file.write("bpy.context.scene.eevee.use_gtao = True\n")
        file.write("bpy.context.scene.eevee.use_ssr = True\n")
        file.write("render.film_transparent = True\n")        
        file.write("render.use_file_extension = True\n")
        file.write("render.filepath = path\n")
        file.write("bpy.ops.render.render(write_still=True)\n")        
        file.close()
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')

    def get_thumbnail_path(self):
        return os.path.join(home_builder_paths.get_asset_folder_path(),"thumbnail.blend")

    def execute(self, context):
        wm_props = home_builder_utils.get_wm_props(context.window_manager)
        for asset in wm_props.assets:
            if asset.is_selected:
                script = self.create_item_thumbnail_script(asset)
                command = [bpy.app.binary_path,self.get_thumbnail_path(),"-b","--python",script]
                subprocess.call(command) 
                # subprocess.call(bpy.app.binary_path + ' "' + self.get_thumbnail_path() + '" -b --python "' + script + '"',shell=True) 
        return {'FINISHED'}

class home_builder_OT_save_custom_cabinet(Operator):
    bl_idname = "home_builder.save_custom_cabinet"
    bl_label = "Save Custom Cabinet"
    bl_description = "This will save the assembly to the custom cabinet library"
    bl_options = {'UNDO'}

    assembly_bp_name: bpy.props.StringProperty(name="Collection Name")

    assembly = None
    assembly_name = ""

    @classmethod
    def poll(cls, context):
        assembly_bp = pc_utils.get_assembly_bp(context.object)
        if assembly_bp:
            return True
        else:
            return False

    def check(self, context):    
        return True

    def invoke(self,context,event):
        assembly_bp = pc_utils.get_assembly_bp(context.object)
        self.assembly = pc_types.Assembly(assembly_bp)
        self.assembly_name = self.assembly.obj_bp.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout

        path = self.get_path(context)
        files = os.listdir(path) if os.path.exists(path) else []

        layout.label(text="Assembly Name: " + self.assembly_name)

        if self.assembly_name + ".blend" in files or self.assembly_name + ".png" in files:
            layout.label(text="File already exists",icon="ERROR")

    def select_assembly_objects(self,coll):
        for obj in coll.objects:
            obj.select_set(True)
        for child in coll.children:
            self.select_collection_objects(child)

    def get_path(self,context):
        props = home_builder_utils.get_scene_props(context.scene)
        if props.library_tabs == 'KITCHENS':
            cat = props.active_custom_cabinet_catalog
            return os.path.join(home_builder_paths.get_custom_cabinet_library_path(),cat)
        else:
            cat = props.active_vanity_catalog
            return os.path.join(home_builder_paths.get_vanity_library_path(),cat)

    def create_assembly_thumbnail_script(self,source_dir,source_file,assembly_name,obj_list):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    data_to.objects = " + str(obj_list) + "\n")    

        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")
        file.write("    obj.select_set(True)\n")
        
        file.write("bpy.ops.view3d.camera_to_view_selected()\n")

        file.write("render = bpy.context.scene.render\n")
        file.write("render.use_file_extension = True\n")
        file.write("render.filepath = r'" + os.path.join(source_dir,assembly_name) + "'\n")
        file.write("bpy.ops.render.render(write_still=True)\n")
        file.close()

        return os.path.join(bpy.app.tempdir,'thumb_temp.py')
        
    def create_assembly_save_script(self,source_dir,source_file,assembly_name,obj_list):
        file = codecs.open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")

        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")               
        file.write("bpy.context.preferences.filepaths.save_version = 0\n")
        
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    data_to.objects = " + str(obj_list) + "\n")        

        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")

        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(source_dir,assembly_name) + ".blend')\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'save_temp.py')

    def get_children_list(self,obj_bp,obj_list):
        obj_list.append(obj_bp.name)
        for obj in obj_bp.children:
            self.get_children_list(obj,obj_list)
        return obj_list

    def get_thumbnail_path(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)
        return os.path.join(home_builder_paths.get_asset_folder_path(),props.library_tabs,"thumbnail.blend")

    def execute(self, context):
        if bpy.data.filepath == "":
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(bpy.app.tempdir,"temp_blend.blend"))
                    
        directory_to_save_to = self.get_path(context)

        obj_list = []
        obj_list = self.get_children_list(self.assembly.obj_bp,obj_list)

        thumbnail_script_path = self.create_assembly_thumbnail_script(directory_to_save_to, bpy.data.filepath, self.assembly_name, obj_list)
        save_script_path = self.create_assembly_save_script(directory_to_save_to, bpy.data.filepath, self.assembly_name, obj_list)

#         subprocess.Popen(r'explorer ' + bpy.app.tempdir)
        
        tn_command = [bpy.app.binary_path,self.get_thumbnail_path(),"-b","--python",thumbnail_script_path]
        save_command = [bpy.app.binary_path,"-b","--python",save_script_path]

        subprocess.call(tn_command)
        subprocess.call(save_command)

        # subprocess.call(bpy.app.binary_path + ' "' + self.get_thumbnail_path() + '" -b --python "' + thumbnail_script_path + '"')
        # subprocess.call(bpy.app.binary_path + ' -b --python "' + save_script_path + '"')
        
        os.remove(thumbnail_script_path)
        os.remove(save_script_path)
        
        bpy.ops.file.refresh()
        
        return {'FINISHED'}


class home_builder_OT_save_decoration_to_library(Operator):
    bl_idname = "home_builder.save_decoration_to_library"
    bl_label = "Save Decoration to Library"
    bl_description = "This will save the selected object and it's children to the library"
    bl_options = {'UNDO'}

    obj_name = ""

    @classmethod
    def poll(cls, context):
        if context.object:
            return True
        else:
            return False

    def check(self, context):    
        return True

    def invoke(self,context,event):
        self.obj_name = context.object.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        obj = context.object
        obj_list = []
        obj_list = self.get_children_list(obj,obj_list)

        path = self.get_path(context)
        files = os.listdir(path) if os.path.exists(path) else []

        layout.label(text="Object Name: " + obj.name)
        if len(obj_list) > 1:
            layout.label(text=str(len(obj_list) - 1) + " child objects will also be saved.")

        if self.obj_name + ".blend" in files or self.obj_name + ".png" in files:
            layout.label(text="File already exists",icon="ERROR")

    def select_assembly_objects(self,coll):
        for obj in coll.objects:
            obj.select_set(True)
        for child in coll.children:
            self.select_collection_objects(child)

    def get_path(self,context):
        return home_builder_utils.get_file_browser_path(context)

    def create_thumbnail_script(self,source_dir,source_file,assembly_name,obj_list):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    data_to.objects = " + str(obj_list) + "\n")    

        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")
        file.write("    obj.select_set(True)\n")
        
        file.write("bpy.ops.view3d.camera_to_view_selected()\n")

        file.write("render = bpy.context.scene.render\n")
        file.write("render.use_file_extension = True\n")
        file.write("render.filepath = r'" + os.path.join(source_dir,assembly_name) + "'\n")
        file.write("bpy.ops.render.render(write_still=True)\n")
        file.close()

        return os.path.join(bpy.app.tempdir,'thumb_temp.py')
        
    def create_save_script(self,source_dir,source_file,assembly_name,obj_list):
        file = codecs.open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")

        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")               
        file.write("bpy.context.preferences.filepaths.save_version = 0\n")
        
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    data_to.objects = " + str(obj_list) + "\n")        

        file.write("parent_obj = None\n")
        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")
        file.write("    if obj.parent == None:\n")
        file.write("        parent_obj = obj\n")

        file.write("parent_obj.location = (0,0,0)\n")
        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(source_dir,assembly_name) + ".blend')\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'save_temp.py')

    def get_children_list(self,obj_bp,obj_list):
        obj_list.append(obj_bp.name)
        for obj in obj_bp.children:
            self.get_children_list(obj,obj_list)
        return obj_list

    def get_thumbnail_path(self):
        return os.path.join(home_builder_paths.get_asset_folder_path(),"thumbnail.blend")

    def execute(self, context):
        if bpy.data.filepath == "":
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(bpy.app.tempdir,"temp_blend.blend"))
                    
        directory_to_save_to = self.get_path(context)

        obj_list = []
        obj_list = self.get_children_list(context.object,obj_list)

        thumbnail_script_path = self.create_thumbnail_script(directory_to_save_to, bpy.data.filepath, self.obj_name, obj_list)
        save_script_path = self.create_save_script(directory_to_save_to, bpy.data.filepath, self.obj_name, obj_list)

        tn_command = [bpy.app.binary_path,self.get_thumbnail_path(),"-b","--python",thumbnail_script_path]
        save_command = [bpy.app.binary_path,"-b","--python",save_script_path]

        subprocess.call(tn_command)
        subprocess.call(save_command)

        os.remove(thumbnail_script_path)
        os.remove(save_script_path)
        
        bpy.ops.file.refresh()
        
        return {'FINISHED'}


class home_builder_OT_message(bpy.types.Operator):
    bl_idname = "home_builder.message"
    bl_label = "Message"
    
    message: bpy.props.StringProperty(name="Message",description="Message to Display")

    def check(self, context):
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)
        
    def draw(self, context):
        layout = self.layout
        layout.label(text=self.message)

    def execute(self, context):
        return {'FINISHED'}

def update_enable_archipack(self,context):
    if self.enable_archipack:
        bpy.ops.preferences.addon_enable(module="archipack")
    else:
        bpy.ops.preferences.addon_disable(module="archipack")

class home_builder_OT_archipack_not_enabled(bpy.types.Operator):
    bl_idname = "home_builder.archipack_not_enabled"
    bl_label = "Archipack Not Enabled"
    
    enable_archipack: bpy.props.BoolProperty(
        name="Enable Archipack",
        description="Check this to enable Archipack",
        update=update_enable_archipack)

    def check(self, context):
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)
        
    def draw(self, context):
        layout = self.layout
        layout.label(text='The Archipack add-on is not enabled.')
        layout.label(text='Check the box and try again.')
        layout.prop(self,'enable_archipack')

    def execute(self, context):
        return {'FINISHED'}


class home_builder_OT_create_thumbnails_for_selected_assets(Operator):
    bl_idname = "home_builder.create_thumbnails_for_selected_assets"
    bl_label = "Create Thumbnails for Selected Assets"
    bl_description = "This will create thumbnails for the selected assets"
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return True

    def reset_variables(self):
        pass

    def create_thumbnail_script(self,asset):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("import sys\n")
        file.write("import " + __package__ + "\n")

        file.write("path = r'" + os.path.join(os.path.dirname(asset.asset_path),asset.name)  + "'\n")

        file.write("bpy.ops.object.select_all(action='DESELECT')\n")

        file.write("with bpy.data.libraries.load(r'" + asset.asset_path + "', False, True) as (data_from, data_to):\n")
        file.write("    data_to.objects = data_from.objects\n")

        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")
        file.write("    " + __package__ + ".home_builder_pointers.assign_materials_to_object(obj)\n")
        file.write("    obj.select_set(True)\n")

        file.write("bpy.ops.view3d.camera_to_view_selected()\n")

        #RENDER
        file.write("render = bpy.context.scene.render\n")    
        file.write("render.use_file_extension = True\n")
        file.write("render.filepath = path\n")
        file.write("bpy.ops.render.render(write_still=True)\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')

    def create_material_thumbnail_script(self,asset):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("import sys\n")

        file.write("path = r'" + os.path.join(os.path.dirname(asset.asset_path),asset.name)  + "'\n")

        file.write("bpy.ops.object.select_all(action='DESELECT')\n")

        file.write("with bpy.data.libraries.load(r'" + asset.asset_path + "', False, True) as (data_from, data_to):\n")
        file.write("    for mat in data_from.materials:\n")
        file.write("        if mat == '" + asset.name + "':\n")
        file.write("            data_to.materials = [mat]\n")
        file.write("            break\n")
        file.write("for mat in data_to.materials:\n")
        file.write("    bpy.ops.mesh.primitive_cube_add()\n")
        file.write("    obj = bpy.context.view_layer.objects.active\n")
        file.write("    bpy.ops.object.shade_smooth()\n")
        file.write("    obj.dimensions = (2,2,2)\n")
        file.write("    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)\n")
        file.write("    mod = obj.modifiers.new('bevel','BEVEL')\n")
        file.write("    mod.segments = 5\n")
        file.write("    mod.width = .05\n")
        file.write("    bpy.ops.object.modifier_apply(modifier='bevel')\n")
        file.write("    bpy.ops.object.editmode_toggle()\n")
        file.write("    bpy.ops.mesh.select_all(action='SELECT')\n")
        file.write("    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)\n")
        file.write("    bpy.ops.object.editmode_toggle()\n")
        file.write("    bpy.ops.object.material_slot_add()\n")
        file.write("    for slot in obj.material_slots:\n")
        file.write("        slot.material = mat\n")

        file.write("bpy.ops.view3d.camera_to_view_selected()\n")

        #RENDER
        file.write("render = bpy.context.scene.render\n")
        file.write("render.use_file_extension = True\n")
        file.write("render.filepath = path\n")
        file.write("bpy.ops.render.render(write_still=True)\n")        
        file.close()
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')    

    def create_molding_thumbnail_script(self,asset):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("import sys\n")

        file.write("path = r'" + os.path.join(os.path.dirname(asset.asset_path),asset.name)  + "'\n")

        file.write("bpy.ops.object.select_all(action='DESELECT')\n")

        file.write("with bpy.data.libraries.load(r'" + asset.asset_path + "', False, True) as (data_from, data_to):\n")
        file.write("    data_to.objects = data_from.objects\n")

        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")
        file.write("    obj.select_set(True)\n")
        file.write("    if obj.type == 'CURVE':\n")
        file.write("        bpy.context.scene.camera.rotation_euler = (0,0,0)\n")
        file.write("        obj.data.dimensions = '2D'\n")        

        file.write("bpy.ops.view3d.camera_to_view_selected()\n")

        #RENDER
        file.write("render = bpy.context.scene.render\n")    
        file.write("render.use_file_extension = True\n")
        file.write("render.filepath = path\n")
        file.write("bpy.ops.render.render(write_still=True)\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')

    def get_thumbnail_path(self,asset):
        return os.path.join(os.path.dirname(os.path.dirname(asset.asset_path)),"thumbnail.blend")

    def execute(self, context):
        scene_props = home_builder_utils.get_scene_props(context.scene)
        for asset in scene_props.active_asset_collection:
            if asset.is_selected:
                if scene_props.asset_tabs == 'MATERIALS':
                    script = self.create_material_thumbnail_script(asset)
                elif scene_props.asset_tabs == 'MOLDINGS':
                    script = self.create_molding_thumbnail_script(asset)                    
                else:
                    script = self.create_thumbnail_script(asset)
                command = [bpy.app.binary_path,self.get_thumbnail_path(asset),"-b","--python",script]
                subprocess.call(command) 
                # subprocess.call(bpy.app.binary_path + ' "' + self.get_thumbnail_path(asset) + '" -b --python "' + script + '"',shell=True) 

        scene_props.asset_tabs = scene_props.asset_tabs
        return {'FINISHED'}


class home_builder_OT_save_asset_to_library(Operator):
    bl_idname = "home_builder.save_asset_to_library"
    bl_label = "Save Current Asset to Library"
    bl_description = "This will save the current file to the active library"
    bl_options = {'UNDO'}
    
    object_libraries = {'CABINET_PULLS','ENTRY_DOOR_HANDLES','FAUCETS','MOLDINGS'}
    assembly_libraries = {'BUILT_IN_APPLIANCES','CABINET_DOORS','CABINET_PARTS',
                          'COOKTOPS','DISHWASHERS','ENTRY_DOOR_FRAMES','ENTRY_DOOR_PANELS',
                          'RANGE_HOODS','RANGES','REFRIGERATORS','SINKS','WINDOW_FRAMES',
                          'WINDOW_INSERTS'}
    material_libraries = {'MATERIALS'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def create_save_object_script(self,save_dir,asset):
        source_file = bpy.data.filepath
        file = codecs.open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")        
        file.write("bpy.context.preferences.filepaths.save_version = 0\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    data_to.objects = ['" + asset.name + "']\n")
        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")
        # file.write("    obj.select_set(True)\n")
        # file.write("    if obj.type == 'CURVE':\n")
        # file.write("        bpy.context.scene.camera.rotation_euler = (0,0,0)\n")
        # file.write("        obj.data.dimensions = '2D'\n")
        # file.write("    bpy.context.view_layer.objects.active = obj\n")
        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(save_dir,asset.name) + ".blend')\n")
        file.close()

        return os.path.join(bpy.app.tempdir,'save_temp.py')

    def create_save_material_script(self,save_dir,material):
        source_file = bpy.data.filepath
        file = codecs.open(os.path.join(bpy.app.tempdir,"save_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")        
        file.write("bpy.context.preferences.filepaths.save_version = 0\n")
        file.write("with bpy.data.libraries.load(r'" + source_file + "', False, True) as (data_from, data_to):\n")
        file.write("    for mat in data_from.materials:\n")
        file.write("        if mat == '" + material.name + "':\n")
        file.write("            data_to.materials = [mat]\n")
        file.write("            break\n")
        file.write("for mat in data_to.materials:\n")
        file.write("    bpy.ops.mesh.primitive_cube_add()\n")
        file.write("    obj = bpy.context.view_layer.objects.active\n")
        file.write("    bpy.ops.object.shade_smooth()\n")
        file.write("    obj.dimensions = (2,2,2)\n")
        file.write("    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)\n")
        file.write("    mod = obj.modifiers.new('bevel','BEVEL')\n")
        file.write("    mod.segments = 5\n")
        file.write("    mod.width = .05\n")
        file.write("    bpy.ops.object.modifier_apply(modifier='bevel')\n")
        file.write("    bpy.ops.object.editmode_toggle()\n")
        file.write("    bpy.ops.mesh.select_all(action='SELECT')\n")
        file.write("    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)\n")
        file.write("    bpy.ops.object.editmode_toggle()\n")
        file.write("    bpy.ops.object.material_slot_add()\n")
        file.write("    for slot in obj.material_slots:\n")
        file.write("        slot.material = mat\n")
        file.write("    bpy.context.view_layer.objects.active = obj\n")
        file.write("bpy.ops.wm.save_as_mainfile(filepath=r'" + os.path.join(save_dir,material.name) + ".blend')\n")
        file.close()

        return os.path.join(bpy.app.tempdir,'save_temp.py')

    def execute(self, context):     
        if bpy.data.filepath == "":
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(bpy.app.tempdir,"temp_blend.blend"))

        scene_props = home_builder_utils.get_scene_props(context.scene)
        path = os.path.join(scene_props.get_active_category_path(),scene_props.active_asset_category)

        if scene_props.asset_tabs in self.object_libraries:
            save_script_path = self.create_save_object_script(path, self.get_asset(context))
            command = [bpy.app.binary_path,"-b","--python",save_script_path]
            subprocess.call(command)
            # subprocess.call(bpy.app.binary_path + ' -b --python "' + save_script_path + '"',shell=True)

        if scene_props.asset_tabs in self.assembly_libraries:
            save_script_path = self.create_save_object_script(path, self.get_asset(context))
            command = [bpy.app.binary_path,"-b","--python",save_script_path]
            subprocess.call(command)            
            # subprocess.call(bpy.app.binary_path + ' -b --python "' + save_script_path + '"',shell=True)

        if scene_props.asset_tabs in self.material_libraries:
            save_script_path = self.create_save_material_script(path, self.get_asset(context))
            command = [bpy.app.binary_path,"-b","--python",save_script_path]
            subprocess.call(command)            
            # subprocess.call(bpy.app.binary_path + ' -b --python "' + save_script_path + '"',shell=True)

        file_path = os.path.join(path,self.get_asset(context).name + ".blend")

        for asset in scene_props.active_asset_collection:
            scene_props.active_asset_collection.remove(0)

        asset = scene_props.active_asset_collection.add()
        asset.is_selected = True
        asset.name = self.get_asset(context).name
        asset.asset_path = file_path

        bpy.ops.home_builder.create_thumbnails_for_selected_assets()
        return {'FINISHED'}

    def get_asset(self,context):
        scene_props = home_builder_utils.get_scene_props(context.scene)
        if scene_props.asset_tabs in self.object_libraries:
            return context.object
        if scene_props.asset_tabs in self.assembly_libraries:
            return pc_utils.get_assembly_bp(context.object)
        if scene_props.asset_tabs in self.material_libraries:
            return context.object.active_material     

    def draw(self, context):
        layout = self.layout
        scene_props = home_builder_utils.get_scene_props(context.scene)

        path = os.path.join(scene_props.get_active_category_path(),scene_props.active_asset_category)
        files = os.listdir(path) if os.path.exists(path) else []
        
        asset_name = self.get_asset(context).name

        layout.label(text="Asset Name: " + asset_name)
        
        if asset_name + ".blend" in files or asset_name + ".png" in files:
            layout.label(text="File already exists",icon="ERROR")     


class home_builder_OT_open_browser_window(bpy.types.Operator):
    bl_idname = "home_builder.open_browser_window"
    bl_label = "Open Browser Window"
    bl_description = "This will open a path in your OS file browser"

    path: bpy.props.StringProperty(name="Path",description="Path to Open")

    def execute(self, context):
        import subprocess
        if 'Windows' in str(bpy.app.build_platform):
            subprocess.Popen(r'explorer ' + self.path)
        elif 'Darwin' in str(bpy.app.build_platform):
            subprocess.Popen(['open' , os.path.normpath(self.path)])
        else:
            subprocess.Popen(['xdg-open' , os.path.normpath(self.path)])
        return {'FINISHED'}


class home_builder_OT_create_new_asset(bpy.types.Operator):
    bl_idname = "home_builder.create_new_asset"
    bl_label = "Create New Asset"
    bl_description = "This will create a new asset of the specified type"

    asset_type: bpy.props.StringProperty(name="Asset Type",description="Type of Asset to Create")

    def execute(self, context):
        scene_props = home_builder_utils.get_scene_props(context.scene)

        if scene_props.asset_tabs == 'BUILT_IN_APPLIANCES':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Built In Appliance")
            assembly.obj_x.location.x = pc_unit.inch(30)
            assembly.obj_y.location.y = pc_unit.inch(20)
            assembly.obj_z.location.z = pc_unit.inch(30)
            assembly.obj_bp.select_set(True)
            context.view_layer.objects.active = assembly.obj_bp   

        if scene_props.asset_tabs == 'CABINET_DOORS':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Cabinet Door")
            assembly.obj_x.location.x = pc_unit.inch(30)
            assembly.obj_y.location.y = pc_unit.inch(18)
            assembly.obj_z.location.z = pc_unit.inch(.75)
            assembly.obj_bp.select_set(True)
            assembly.add_prompt("Hide",'CHECKBOX',False)
            dim_y = assembly.obj_y.pyclone.get_var('location.y','dim_y')
            y1 = assembly.add_empty('Y1')
            y1.empty_display_size = .01
            y1.pyclone.loc_y('IF(dim_y>0,0,dim_y)',[dim_y])
            y2 = assembly.add_empty('Y2')
            y2.empty_display_size = .01
            y2.pyclone.loc_y('IF(dim_y>0,dim_y,0)',[dim_y])            
            context.view_layer.objects.active = assembly.obj_bp

        if scene_props.asset_tabs == 'CABINET_PARTS':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Cabinet Part")
            assembly.obj_x.location.x = pc_unit.inch(30)
            assembly.obj_y.location.y = pc_unit.inch(20)
            assembly.obj_z.location.z = pc_unit.inch(.75)
            assembly.obj_bp.select_set(True)
            context.view_layer.objects.active = assembly.obj_bp  

        if scene_props.asset_tabs == 'CABINET_PULLS':
            pass #OBJ

        if scene_props.asset_tabs == 'COOKTOPS':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Cooktop")
            assembly.obj_x.location.x = pc_unit.inch(30)
            assembly.obj_y.location.y = -pc_unit.inch(20)
            assembly.obj_z.location.z = -pc_unit.inch(10)
            assembly.obj_bp.select_set(True)
            context.view_layer.objects.active = assembly.obj_bp  

        if scene_props.asset_tabs == 'DISHWASHERS':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Dishwasher")
            assembly.obj_x.location.x = pc_unit.inch(24)
            assembly.obj_y.location.y = -pc_unit.inch(23)
            assembly.obj_z.location.z = pc_unit.inch(34)
            assembly.obj_bp.select_set(True)
            context.view_layer.objects.active = assembly.obj_bp

        if scene_props.asset_tabs == 'ENTRY_DOOR_FRAMES':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Entry Door Frame")
            assembly.obj_x.location.x = pc_unit.inch(36)
            assembly.obj_y.location.y = pc_unit.inch(6)
            assembly.obj_z.location.z = pc_unit.inch(90)
            assembly.obj_bp.select_set(True)
            assembly.add_prompt("Door Frame Width",'DISTANCE',pc_unit.inch(3))
            context.view_layer.objects.active = assembly.obj_bp

        if scene_props.asset_tabs == 'ENTRY_DOOR_HANDLES':
            pass #OBJ

        if scene_props.asset_tabs == 'ENTRY_DOOR_PANELS':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Entry Door Panel")
            assembly.obj_x.location.x = pc_unit.inch(36)
            assembly.obj_y.location.y = pc_unit.inch(1.5)
            assembly.obj_z.location.z = pc_unit.inch(90)
            assembly.obj_bp.select_set(True)
            assembly.add_prompt("Hide",'CHECKBOX',False)
            dim_x = assembly.obj_x.pyclone.get_var('location.x','dim_x')
            x1 = assembly.add_empty('X1')
            x1.empty_display_size = .01
            x1.pyclone.loc_x('IF(dim_x>0,0,dim_x)',[dim_x])
            x2 = assembly.add_empty('X2')
            x2.empty_display_size = .01
            x2.pyclone.loc_x('IF(dim_x>0,dim_x,0)',[dim_x])                
            context.view_layer.objects.active = assembly.obj_bp

        if scene_props.asset_tabs == 'FAUCETS':
            pass #OBJ

        if scene_props.asset_tabs == 'MATERIALS':
            pass #MATERIAL

        if scene_props.asset_tabs == 'RANGE_HOODS':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Range Hoods")
            assembly.obj_x.location.x = pc_unit.inch(30)
            assembly.obj_y.location.y = -pc_unit.inch(14)
            assembly.obj_z.location.z = pc_unit.inch(20)
            # assembly.obj_bp.location.z = pc_unit.inch(70)
            assembly.obj_bp.select_set(True)
            context.view_layer.objects.active = assembly.obj_bp   

        if scene_props.asset_tabs == 'RANGES':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Range")
            assembly.obj_x.location.x = pc_unit.inch(30)
            assembly.obj_y.location.y = -pc_unit.inch(14)
            assembly.obj_z.location.z = pc_unit.inch(20)
            assembly.obj_bp.select_set(True)
            context.view_layer.objects.active = assembly.obj_bp     
               
        if scene_props.asset_tabs == 'REFRIGERATORS':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Refrigerator")
            assembly.obj_x.location.x = pc_unit.inch(36)
            assembly.obj_y.location.y = -pc_unit.inch(25)
            assembly.obj_z.location.z = pc_unit.inch(84)
            assembly.obj_bp.select_set(True)
            context.view_layer.objects.active = assembly.obj_bp  

        if scene_props.asset_tabs == 'SINKS':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Sinks")
            assembly.obj_x.location.x = pc_unit.inch(30)
            assembly.obj_y.location.y = -pc_unit.inch(20)
            assembly.obj_z.location.z = -pc_unit.inch(10)
            assembly.obj_bp.select_set(True)
            faucet_bp = assembly.add_empty('Faucet BP')
            faucet_bp.empty_display_size = .01    
            faucet_bp["IS_FAUCET_BP"] = True        
            context.view_layer.objects.active = assembly.obj_bp  

        if scene_props.asset_tabs == 'WINDOW_FRAMES':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Window Frame")      
            # assembly.obj_bp.location.z = pc_unit.inch(48)
            assembly.obj_x.location.x = pc_unit.inch(36)
            assembly.obj_y.location.y = pc_unit.inch(6)
            assembly.obj_z.location.z = pc_unit.inch(48)
            assembly.obj_bp.select_set(True)                  
            assembly.add_prompt("Left Window Frame Width",'DISTANCE',pc_unit.inch(3))
            assembly.add_prompt("Right Window Frame Width",'DISTANCE',pc_unit.inch(3))
            assembly.add_prompt("Top Window Frame Width",'DISTANCE',pc_unit.inch(3))
            assembly.add_prompt("Bottom Window Frame Width",'DISTANCE',pc_unit.inch(3))  
            context.view_layer.objects.active = assembly.obj_bp         

        if scene_props.asset_tabs == 'WINDOW_INSERTS':
            assembly = pc_types.Assembly()
            assembly.create_assembly("Window Insert")      
            # assembly.obj_bp.location.z = pc_unit.inch(48)
            assembly.obj_x.location.x = pc_unit.inch(36)
            assembly.obj_y.location.y = pc_unit.inch(6)
            assembly.obj_z.location.z = pc_unit.inch(48)
            assembly.obj_bp.select_set(True)               

        return {'FINISHED'}


class home_builder_OT_light_prompts(bpy.types.Operator):
    bl_idname = "home_builder.light_prompts"
    bl_label = "Light Prompts"
    
    def check(self, context):
        return True

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)
        
    def draw(self, context):
        layout = self.layout
        obj = context.object
        light = obj.data
        box = layout.box()
        row = box.row()
        row.prop(light, "type",expand=True)
        row = box.row()
        row.label(text="Color")
        row.prop(light, "color",text="")
        row = box.row()
        row.label(text="Energy")
        row.prop(light, "energy",text="")
        row = box.row()
        row.label(text="Specular")
        row.prop(light, "specular_factor", text="")
        row = box.row()
        row.prop(light, "use_custom_distance", text="Use Custom Distance")
        if light.use_custom_distance:
            row.prop(light,"cutoff_distance",text="Distance")

        if light.type in {'POINT', 'SPOT', 'SUN'}:
            row = box.row()
            row.label(text="Radius")            
            row.prop(light, "shadow_soft_size", text="")
        elif light.type == 'AREA':
            box = layout.box()
            row = box.row()
            row.label(text="Shape:")
            row.prop(light, "shape",expand=True)

            sub = box.column(align=True)

            if light.shape in {'SQUARE', 'DISK'}:
                row = sub.row(align=True)
                row.label(text="Size:")     
                row.prop(light, "size",text="")
            elif light.shape in {'RECTANGLE', 'ELLIPSE'}:
                row = sub.row(align=True)
                row.label(text="Size:")

                row.prop(light, "size", text="X")
                row.prop(light, "size_y", text="Y")
        
        if light.type == 'SPOT':
            box = layout.box()
            row = box.row()        
            row.label(text="Spot Size:")    
            row.prop(light, "spot_size", text="")
            row = box.row()        
            row.label(text="Spot Blend:")                
            row.prop(light, "spot_blend", text="", slider=True)

            box.prop(light, "show_cone")            

        box = layout.box()
        box.prop(light, "use_shadow", text="Use Shadows")
        box.active = light.use_shadow

        col = box.column()
        row = col.row(align=True)
        row.label(text="Clip:")
        row.prop(light, "shadow_buffer_clip_start", text="Start")
        if light.type == 'SUN':
            row.prop(light, "shadow_buffer_clip_end", text="End")

        # row = col.row(align=True)
        # row.label(text="Softness:")
        # row.prop(light, "shadow_buffer_soft", text="")

        # col.separator()

        # row = col.row(align=True)
        # row.label(text="Bias:")
        # row.prop(light, "shadow_buffer_bias", text="")
        # row = col.row(align=True)
        # row.label(text="Bleed Bias:")        
        # row.prop(light, "shadow_buffer_bleed_bias", text="")        
        # row = col.row(align=True)
        # row.label(text="Exponent:")        
        # row.prop(light, "shadow_buffer_exp", text="")

        # col.separator()

        # col.prop(light, "use_contact_shadow", text="Use Contact Shadows")
        # if light.use_shadow and light.use_contact_shadow:
        #     col = box.column()
        #     row = col.row(align=True)
        #     row.label(text="Distance:")  
        #     row.prop(light, "contact_shadow_distance", text="")
        #     row = col.row(align=True)
        #     row.label(text="Softness:")  
        #     row.prop(light, "contact_shadow_soft_size", text="")
        #     row = col.row(align=True)
        #     row.label(text="Bias:")          
        #     row.prop(light, "contact_shadow_bias", text="")
        #     row = col.row(align=True)
        #     row.label(text="Thickness:")          
        #     row.prop(light, "contact_shadow_thickness", text="")

        # if light.type == 'SUN' and light.use_shadow:
        #     box = layout.box()
        #     box.label(text="Sun Shadow Settings")
        #     row = box.row(align=True)
        #     row.label(text="Cascade Count:")                
        #     row.prop(light, "shadow_cascade_count", text="")
        #     row = box.row(align=True)
        #     row.label(text="Fade:")                 
        #     row.prop(light, "shadow_cascade_fade", text="")

        #     row = box.row(align=True)
        #     row.label(text="Max Distance:")      
        #     row.prop(light, "shadow_cascade_max_distance", text="")
        #     row = box.row(align=True)
        #     row.label(text="Distribution:")                  
        #     row.prop(light, "shadow_cascade_exponent", text="")

    def execute(self, context):
        return {'FINISHED'}


class home_builder_OT_floor_prompts(bpy.types.Operator):
    bl_idname = "home_builder.floor_prompts"
    bl_label = "Floor Prompts"
    
    mapping_node = None

    def check(self, context):
        return True

    def invoke(self,context,event):
        self.mapping_node = None
        floor = context.object
        for slot in floor.material_slots:
            mat = slot.material
            if mat:
                for node in mat.node_tree.nodes:
                    if node.type == 'MAPPING':
                        self.mapping_node = node

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=150)
        
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column()
        if self.mapping_node:
            col.label(text="Texture Mapping")
            col.prop(self.mapping_node.inputs[1],'default_value',text="Location")
            col.prop(self.mapping_node.inputs[2],'default_value',text="Rotation")
            col.prop(self.mapping_node.inputs[3],'default_value',text="Scale")
        else:
            col.label(text="No Material Found")

    def execute(self, context):
        return {'FINISHED'}


class home_builder_OT_delete_assembly(bpy.types.Operator):
    bl_idname = "home_builder.delete_assembly"
    bl_label = "Delete Assembly"
    
    obj_name: StringProperty(name="Object Name")

    def execute(self, context):
        obj_bp = bpy.data.objects[self.obj_name]
        pc_utils.delete_object_and_children(obj_bp)
        return {'FINISHED'}


class home_builder_OT_reload_pointers(bpy.types.Operator):
    bl_idname = "home_builder.reload_pointers"
    bl_label = "Reload Pointers"
    
    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Are you sure you want to reload the pointer files?")
        layout.label(text="This will set Material, Molding, Door Fronts, and Hardware")
        layout.label(text="pointers back to the default.")

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        for pointer in props.material_pointer_groups:
            props.material_pointer_groups.remove(0)

        for pointer in props.pull_pointers:
            props.pull_pointers.remove(0)

        for pointer in props.cabinet_door_pointers:
            props.cabinet_door_pointers.remove(0)   

        for pointer in props.molding_pointers:
            props.molding_pointers.remove(0)  

        home_builder_pointers.update_pointer_properties()
        props.material_group_index = 0                                    
        return {'FINISHED'}

    
class home_builder_OT_create_library_pdf(bpy.types.Operator):
    bl_idname = "home_builder.create_library_pdf"
    bl_label = "Create Library PDF"
    bl_description = "This will create a PDF with all of the items that are available in the library"
    
    elements = []
    package = None
    
    def create_header(self, name, font_size):
        header_style = TableStyle([('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                                ('TOPPADDING', (0, 0), (-1, -1), 15),
                                ('FONTSIZE', (0, 0), (-1, -1), 8),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                                # ('LINEBELOW', (0, 0), (-1, -1), 2, colors.black),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.white)])        
        
        name_p = Paragraph(name, ParagraphStyle("Category name style", fontSize=font_size))
        header_tbl = Table([[name_p]], colWidths = 500, rowHeights = None, repeatRows = 1)
        header_tbl.setStyle(header_style)
        self.elements.append(header_tbl)
        
    def create_img_table(self, dir):
        item_tbl_data = []
        item_tbl_row = []

        if os.path.isdir(dir):
            for i, file in enumerate(os.listdir(dir)):
                last_item = len(os.listdir(dir)) - 1
                if ".png" in file or ".jpg" in file:
                    img = Image(os.path.join(dir, file), inch, inch)
                    img_name = file.replace(".png", "")
                                
                    if len(item_tbl_row) == 4:
                        item_tbl_data.append(item_tbl_row)
                        item_tbl_row = []
                    elif i == last_item:
                        item_tbl_data.append(item_tbl_row)
                        
                    i_tbl = Table([[img], [Paragraph(img_name, ParagraphStyle("item name style", fontSize=8, wordWrap='CJK'))]])
                    item_tbl_row.append(i_tbl)    

            if len(item_tbl_data) > 0:
                item_tbl = Table(item_tbl_data, colWidths=125)
                self.elements.append(item_tbl)
                # self.elements.append(Spacer(1, inch * 0.5))
          
    def get_number_of_assets_in_category(self,path):
        qty = 0
        for file in os.listdir(path):
            filepath = os.path.join(path,file)
            filename, ext = os.path.splitext(file)
            if os.path.isfile(filepath) and ext in {".png",".jpg"}:
                qty += 1
        return qty

    def execute(self, context):
        file_path = home_builder_paths.get_asset_folder_path()
        file_name = "Library.pdf"
        
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        
        doc = SimpleDocTemplate(os.path.join(file_path, file_name), 
                                pagesize = A4,
                                leftMargin = 0.25 * inch,
                                rightMargin = 0.25 * inch,
                                topMargin = 0.25 * inch,
                                bottomMargin = 0.25 * inch)      
        
        for library_folder in os.listdir(file_path):
            library_path = os.path.join(file_path,library_folder)
            if os.path.isdir(library_path) and ".git" not in library_folder and "ASSEMBLIES" not in library_folder:
                self.create_header(library_folder, font_size=20)
                for category_folder in os.listdir(library_path):
                    category_path = os.path.join(file_path,library_folder,category_folder)
                    if os.path.isdir(category_path):
                        qty = self.get_number_of_assets_in_category(category_path)
                        header_name = category_folder
                        if qty != 0:
                            header_name += " (" + str(qty) + ")"
                        self.create_header(header_name, font_size=10)
                        self.create_img_table(category_path)

                        for nested_folder in os.listdir(category_path):
                            nested_path = os.path.join(file_path,library_folder,category_folder,nested_folder)
                            if os.path.isdir(nested_path):
                                qty = self.get_number_of_assets_in_category(nested_path)
                                header_name = category_folder
                                if qty != 0:
                                    header_name += " (" + str(qty) + ")"                                
                                self.create_header(header_name, font_size=8)
                                self.create_img_table(nested_path)

        doc.build(self.elements)
        return {'FINISHED'}


class home_builder_OT_create_2d_views(bpy.types.Operator):
    bl_idname = "home_builder.create_2d_views"
    bl_label = "Create 2D Views"
    
    model_scene = None

    def get_wall_assemblies(self):
        walls = []
        for obj in bpy.data.objects:
            wall_bp = home_builder_utils.get_wall_bp(obj)
            if wall_bp and wall_bp not in walls:
                walls.append(wall_bp)
        return walls

    def link_children_with_collection(self,obj,collection):
        collection.objects.link(obj)
        for child in obj.children:
            self.link_children_with_collection(child,collection)

    def create_elevation_layout(self,context,wall):
        for scene in bpy.data.scenes:
            if not scene.pyclone.is_view_scene:
                context.window.scene = scene
                break
        collection = wall.create_assembly_collection(wall.obj_bp.name)
        left_wall =  home_builder_utils.get_connected_left_wall(wall)
        right_wall =  home_builder_utils.get_connected_right_wall(wall)

        if left_wall:
            for child in left_wall.obj_bp.children:
                if 'IS_ASSEMBLY_BP' in child:
                    assembly = pc_types.Assembly(child)
                    if child.location.x >= (left_wall.obj_x.location.x - assembly.obj_x.location.x - pc_unit.inch(10)):
                        self.link_children_with_collection(child,collection)

        if right_wall:
            for child in right_wall.obj_bp.children:
                if 'IS_ASSEMBLY_BP' in child:
                    if child.location.x <= pc_unit.inch(10):
                        self.link_children_with_collection(child,collection)

        bpy.ops.scene.new(type='EMPTY')
        layout = pc_types.Assembly_Layout(context.scene)
        layout.setup_assembly_layout()
        layout.scene.name = wall.obj_bp.name
        wall_view = layout.add_assembly_view(collection)
        
        layout.add_layout_camera()   
        layout.scene.world = self.model_scene.world
        layout.camera.parent = wall.obj_bp

        layout.scene.world.node_tree.nodes['Background'].inputs[1].default_value = 15
        layout.scene.render.film_transparent = True

        dim = pc_types.Dimension()
        dim.create_dimension(layout)
        dim.obj_bp.rotation_euler.x = math.radians(-90)
        dim.obj_bp.rotation_euler.y = 0
        dim.obj_y.location.y = .2
        dim.obj_bp.parent = wall_view
        dim.obj_bp.location = wall.obj_bp.matrix_world.translation
        dim.obj_bp.rotation_euler.z = wall.obj_bp.rotation_euler.z
        dim.obj_x.location.x = wall.obj_x.location.x
        dim.flip_y()
        dim.update_dim_text()

        context.scene.pyclone.fit_to_paper = False
        context.scene.pyclone.page_scale_unit_type = 'METRIC'
        context.scene.pyclone.metric_page_scale = '1:20'    

        bpy.ops.object.select_all(action='DESELECT')
        wall_view.select_set(True)
        context.view_layer.objects.active = wall_view
        bpy.ops.view3d.camera_to_view_selected()

        #NEEDED TO REFRESH CAMERA ORTHO SCALE AFTER VIEW SELECTED
        context.scene.pyclone.metric_page_scale = '1:20'   

        self.add_title_block(layout,"Wall","1")    

    def render_scene(self,context,scene):
        context.window.scene = scene
        filepath = os.path.join(bpy.app.tempdir,scene.name + " View")
        render = bpy.context.scene.render
        render.use_file_extension = True
        render.filepath = filepath
        bpy.ops.render.render(write_still=True)
        return filepath

    def add_title_block(self,layout,description,number):
        title_block = pc_types.Title_Block()
        title_block.create_title_block(layout)

    def create_pdf(self,context,images):
        width, height = landscape(letter)
        filepath = os.path.join(bpy.app.tempdir,"2D Views.PDF")
        filename = "2D Views.PDF"
        c = canvas.Canvas(filepath, pagesize=landscape(letter))

        for image in images:
            c.drawImage(image,0,0,width=width, height=height, mask='auto',preserveAspectRatio=True)  
            c.showPage()
        c.save()

        os.system('start "Title" /D "' + bpy.app.tempdir + '" "' + filename + '"')

    def execute(self, context):
        self.model_scene = context.scene
        walls = self.get_wall_assemblies()
        for wall in walls:
            self.create_elevation_layout(context,pc_types.Assembly(wall))
        context.window_manager.pyclone.scene_index = len(bpy.data.scenes) - 1
        # images = []
        # for scene in bpy.data.scenes:
        #     if scene.pyclone.is_view_scene:
        #         file_path = self.render_scene(context,scene)
        #         images.append(file_path + ".png")

        # self.create_pdf(context,images)

        return {'FINISHED'}


class home_builder_OT_create_2d_cabinet_views(bpy.types.Operator):
    bl_idname = "home_builder.create_2d_cabinet_views"
    bl_label = "Create 2D Cabinet Views"
    
    model_scene = None

    def get_cabinet_assemblies(self):
        cabinets = []
        for obj in bpy.data.objects:
            cabinet_bp = home_builder_utils.get_cabinet_bp(obj)
            if cabinet_bp and cabinet_bp not in cabinets:
                cabinets.append(cabinet_bp)
        return cabinets

    def create_cabinet_layout(self,context,cabinet):
        for scene in bpy.data.scenes:
            if not scene.pyclone.is_view_scene:
                context.window.scene = scene
                break
        collection = cabinet.create_assembly_collection(cabinet.obj_bp.name)

        bpy.ops.scene.new(type='EMPTY')
        context.scene.name = cabinet.obj_bp.name
        layout = pc_types.Assembly_Layout(context.scene)
        layout.setup_assembly_layout()
        cabinet_view = layout.add_assembly_view(collection)

        layout.add_layout_camera()
        layout.scene.world = self.model_scene.world
        layout.camera.parent = cabinet.obj_bp

        self.add_title_block(layout,"Wall","1")    

        context.scene.pyclone.fit_to_paper = False
        context.scene.pyclone.page_scale_unit_type = 'METRIC'
        context.scene.pyclone.metric_page_scale = '1:30'    

        bpy.ops.object.select_all(action='DESELECT')
        cabinet_view.select_set(True)
        context.view_layer.objects.active = cabinet_view
        bpy.ops.view3d.camera_to_view_selected()

        #NEEDED TO REFRESH CAMERA ORTHO SCALE AFTER VIEW SELECTED
        context.scene.pyclone.metric_page_scale = '1:30'   

    def render_scene(self,context,scene):
        context.window.scene = scene
        filepath = os.path.join(bpy.app.tempdir,scene.name + " View")
        render = bpy.context.scene.render
        render.use_file_extension = True
        render.filepath = filepath
        bpy.ops.render.render(write_still=True)
        return filepath

    def add_title_block(self,layout,description,number):
        title_block = pc_types.Title_Block()
        title_block.create_title_block(layout)

    def create_pdf(self,context,images):
        width, height = landscape(letter)
        filepath = os.path.join(bpy.app.tempdir,"2D Views.PDF")
        filename = "2D Views.PDF"
        c = canvas.Canvas(filepath, pagesize=landscape(letter))

        for image in images:
            c.drawImage(image,0,0,width=width, height=height, mask='auto',preserveAspectRatio=True)  
            c.showPage()
        c.save()

        os.system('start "Title" /D "' + bpy.app.tempdir + '" "' + filename + '"')

    def execute(self, context):
        self.model_scene = context.scene
        walls = self.get_cabinet_assemblies()
        for wall in walls:
            self.create_cabinet_layout(context,pc_types.Assembly(wall))
        context.window_manager.pyclone.scene_index = len(bpy.data.scenes) - 1
        # images = []
        # for scene in bpy.data.scenes:
        #     if scene.pyclone.is_view_scene:
        #         file_path = self.render_scene(context,scene)
        #         images.append(file_path + ".png")

        # self.create_pdf(context,images)

        return {'FINISHED'}


class home_builder_OT_create_cabinet_list_report(bpy.types.Operator):
    bl_idname = "home_builder.create_cabinet_list_report"
    bl_label = "Create Cabinet List Report"
    
    def get_cabinet_assemblies(self):
        cabinets = []
        for obj in bpy.data.objects:
            cabinet_bp = home_builder_utils.get_cabinet_bp(obj)
            if cabinet_bp and cabinet_bp not in cabinets:
                cabinets.append(cabinet_bp)
        return cabinets

    def set_part_table_style(self,data):
        obj_table = Table(data, colWidths=(100,200,50,50,50,120), repeatRows=1)
        obj_table.hAlign = 'CENTER'
        tblStyle = TableStyle([('TEXTCOLOR',(0,0),(-1,-1),colors.black),
                               ('FONTSIZE',(0,0),(-1,-1),8),
                               ('VALIGN',(0,0),(-1,-1),'TOP'),
                               ('ALIGN',(0,0),(-1,-1),'CENTER'),
                               ('LINEBELOW',(0,0),(-1,0),2,colors.black),
                               ('LINEBELOW',(0,1),(-1,-2),1,colors.lightgrey),
                               ('BACKGROUND',(0,1),(-1,-1),colors.white)])        

        obj_table.setStyle(tblStyle)
        return obj_table

    def draw_cabinets(self,cabinets):
        data = [["CABINETS (" + str(len(cabinets)) + ")" ,"Name","Width","Height","Depth","Material"]]
        for i, cab in enumerate(cabinets):
            cabinet = pc_types.Assembly(cab)
            if bpy.context.scene.unit_settings.system == 'METRIC':
                ext = "mm"
            else:
                ext = '"'
            depth = int(pc_unit.meter_to_active_unit(math.fabs(cabinet.obj_y.location.y)))
            width = int(pc_unit.meter_to_active_unit(math.fabs(cabinet.obj_x.location.x)))
            height = int(pc_unit.meter_to_active_unit(math.fabs(cabinet.obj_z.location.z)))
            material_group_index = home_builder_utils.get_object_props(cabinet.obj_bp).material_group_index
            material_groups = home_builder_utils.get_scene_props(bpy.context.scene).material_pointer_groups
            material_group = material_groups[material_group_index]
            data.append([str(i+1),cabinet.obj_bp.name,str(width) + ext,str(height) + ext,str(depth) + ext,material_group.name])
        
        return self.set_part_table_style(data)

    def draw_report_header(self,elements,report_name):  
        if bpy.data.filepath == "":
            room_name = ""
        else:
            filename = os.path.basename(bpy.data.filepath)
            room_name, ext = os.path.splitext(filename)
        
        styles=getSampleStyleSheet()  
        elements.append(Paragraph(report_name,styles["Title"]))
        elements.append(Paragraph("Room Name: " + room_name,styles["Normal"]))
        elements.append(Paragraph("Date: " + datetime.date.today().strftime("%m/%d/%y"),styles["Normal"]))
        elements.append(Spacer(1,0.2*inch))

    def execute(self, context):
        self.model_scene = context.scene
        cabinets = self.get_cabinet_assemblies()
        width, height = landscape(letter)
        filename = "Cabinet Product List.PDF"
        filepath = os.path.join(bpy.app.tempdir,filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4,leftMargin=.25*inch,rightMargin=.25*inch,topMargin=.25*inch,bottomMargin=.25*inch)        
        
        elements = []
        self.draw_report_header(elements, "Cabinet List Report")
        elements.append(self.draw_cabinets(cabinets))
        doc.build(elements)     
        os.system('start "Title" /D "' + bpy.app.tempdir + '" "' + filename + '"')
        return {'FINISHED'}


class home_builder_OT_assign_material(bpy.types.Operator):
    bl_idname = "home_builder.assign_material"
    bl_label = "Assign Material"

    mat = None
    
    @classmethod
    def poll(cls, context):  
        if context.object and context.object.mode != 'OBJECT':
            return False
        return True
        
    def execute(self, context):
        self.mat = self.get_material(context)
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}
        
    def get_material(self,context):
        props = home_builder_utils.get_scene_props(context.scene)
        return home_builder_utils.get_material(props.material_category,props.material_name)

    def modal(self, context, event):
        context.window.cursor_set('PAINT_BRUSH')
        context.area.tag_redraw()
        self.mouse_x = event.mouse_x
        self.mouse_y = event.mouse_y
        selected_point, selected_obj, selected_normal = pc_utils.get_selection_point(context,event)
        bpy.ops.object.select_all(action='DESELECT')
        if selected_obj:
            selected_obj.select_set(True)
            context.view_layer.objects.active = selected_obj
        
            if event_is_place_asset(event):
                if hasattr(selected_obj.data,'uv_layers') and len(selected_obj.data.uv_layers) == 0:
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.select_all(action='SELECT') 
                    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)  
                    bpy.ops.object.editmode_toggle()

                if len(selected_obj.material_slots) == 0:
                    bpy.ops.object.material_slot_add()

                if len(selected_obj.pyclone.pointers) > 0:
                    print(self.mat,selected_obj)
                    bpy.ops.home_builder.assign_material_dialog('INVOKE_DEFAULT',material_name = self.mat.name, object_name = selected_obj.name)
                    return self.finish(context)
                else:
                    for slot in selected_obj.material_slots:
                        slot.material = self.mat
                        
                return self.finish(context)

        if event_is_cancel_command(event):
            return self.cancel_drop(context)
        
        if event_is_pass_through(event):
            return {'PASS_THROUGH'}        
        
        return {'RUNNING_MODAL'}

    def cancel_drop(self,context):
        context.window.cursor_set('DEFAULT')
        return {'CANCELLED'}
    
    def finish(self,context):
        context.window.cursor_set('DEFAULT')
        context.area.tag_redraw()
        return {'FINISHED'}


class home_builder_OT_assign_material_dialog(bpy.types.Operator):
    bl_idname = "home_builder.assign_material_dialog"
    bl_label = "Assign Material Dialog"
    bl_description = "This is a dialog to assign materials to Home Builder objects"
    bl_options = {'UNDO'}
    
    #READONLY
    material_name: bpy.props.StringProperty(name="Material Name")
    object_name: bpy.props.StringProperty(name="Object Name")
    
    obj = None
    material = None
    
    def check(self, context):
        return True
    
    def invoke(self, context, event):
        self.material = bpy.data.materials[self.material_name]
        self.obj = bpy.data.objects[self.object_name]
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=480)
        
    def draw(self,context):
        scene_props = home_builder_utils.get_scene_props(context.scene)
        obj_props = home_builder_utils.get_object_props(self.obj)
        layout = self.layout
        box = layout.box()
        box.label(text=self.obj.name,icon='OBJECT_DATA')
        pointer_list = []

        if len(scene_props.material_pointer_groups) - 1 >= obj_props.material_group_index:
            mat_group = scene_props.material_pointer_groups[obj_props.material_group_index]
        else:
            mat_group = scene_props.material_pointer_groups[0]

        for index, mat_slot in enumerate(self.obj.material_slots):
            row = box.split(factor=.80)
            pointer = None

            if index + 1 <= len(self.obj.pyclone.pointers):
                pointer = self.obj.pyclone.pointers[index]

            if mat_slot.name == "":
                row.label(text='No Material')
            else:
                if pointer:
                    row.prop(mat_slot,"name",text=pointer.name,icon='MATERIAL')
                else:
                    row.prop(mat_slot,"name",text=" ",icon='MATERIAL')

            if pointer and pointer.pointer_name not in pointer_list and pointer.pointer_name != "":
                pointer_list.append(pointer.pointer_name)

            props = row.operator('home_builder.assign_material_to_slot',text="Override",icon='BACK')
            props.object_name = self.obj.name
            props.material_name = self.material.name
            props.index = index

        if len(pointer_list) > 0:
            box = layout.box()
            row = box.row()
            row.label(text="Update Material Pointers",icon='MATERIAL')
            row.label(text="Material Group: " + mat_group.name,icon='COLOR')
            for pointer in pointer_list:
                row = box.split(factor=.80)
                mat_pointer = mat_group.pointers[pointer] 
                row.label(text=pointer + ": " + mat_pointer.category + "/" + mat_pointer.item_name)    
                props = row.operator('home_builder.update_material_pointer',text="Update All",icon='FILE_REFRESH')
                props.pointer_name = pointer
                props.refresh = True
        
    def execute(self,context):
        return {'FINISHED'}        


class home_builder_OT_assign_material_to_slot(bpy.types.Operator):
    bl_idname = "home_builder.assign_material_to_slot"
    bl_label = "Assign Material to Slot"
    bl_description = "This will assign a material to a material slot"
    bl_options = {'UNDO'}
    
    #READONLY
    material_name: bpy.props.StringProperty(name="Material Name")
    object_name: bpy.props.StringProperty(name="Object Name")
    
    index: bpy.props.IntProperty(name="Index")
    
    def execute(self,context):
        obj = bpy.data.objects[self.object_name]
        mat = bpy.data.materials[self.material_name]
        obj.material_slots[self.index].material = mat
        return {'FINISHED'}


class home_builder_OT_add_material_pointer_group(bpy.types.Operator):
    bl_idname = "home_builder.add_material_pointer_group"
    bl_label = "Add Material Pointer Group"
    bl_description = "This will add a new material pointer group"
    bl_options = {'UNDO'}
    
    #READONLY
    material_group_name: bpy.props.StringProperty(name="Material Group Name",default="New Material Group")

    def execute(self,context):
        scene_props = home_builder_utils.get_scene_props(context.scene)
        mat_group = scene_props.material_pointer_groups.add()
        mat_group.name = self.material_group_name
        home_builder_pointers.add_pointers_from_list(home_builder_pointers.get_default_material_pointers(),
                                                     mat_group.pointers)        

        scene_props.material_group_index = len(scene_props.material_pointer_groups) - 1
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)
        
    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.label(text="Material Group Name")
        layout.prop(self,'material_group_name',text="")


class home_builder_OT_change_global_material_pointer_group(bpy.types.Operator):
    bl_idname = "home_builder.change_global_material_pointer_group"
    bl_label = "Change Global Material Pointer Group"
    bl_description = "This change the global material pointer group"
    bl_options = {'UNDO'}
    
    material_index: bpy.props.IntProperty(name="Index")

    def execute(self,context):
        scene_props = home_builder_utils.get_scene_props(context.scene)
        scene_props.material_group_index = self.material_index
        return {'FINISHED'}


class home_builder_OT_change_product_material_pointer_group(bpy.types.Operator):
    bl_idname = "home_builder.change_product_material_pointer_group"
    bl_label = "Change Product Material Pointer Group"
    bl_description = "This change the product material pointer group"
    bl_options = {'UNDO'}
    
    object_name: bpy.props.StringProperty(name="Object Name")
    material_index: bpy.props.IntProperty(name="Index")

    def execute(self,context):
        obj = bpy.data.objects[self.object_name]
        obj_props = home_builder_utils.get_object_props(obj)
        obj_props.material_group_index = self.material_index
        return {'FINISHED'}


class home_builder_OT_update_product_material_group(bpy.types.Operator):
    bl_idname = "home_builder.update_product_material_group"
    bl_label = "Update Product Material Group"
    
    object_name: bpy.props.StringProperty(name="Object Name")

    def update_children(self,obj,index):
        obj_props = home_builder_utils.get_object_props(obj)
        obj_props.material_group_index = index
        for child in obj.children:
            self.update_children(child,index)

    def execute(self, context):
        obj = bpy.data.objects[self.object_name]
        obj_props = home_builder_utils.get_object_props(obj)
        index = obj_props.material_group_index
        self.update_children(obj,index)
        return {'FINISHED'}


class home_builder_OT_add_material_pointer(bpy.types.Operator):
    bl_idname = "home_builder.add_material_pointer"
    bl_label = "Add Material Pointer"
    bl_description = "This will add a new material pointer to the active group"
    bl_options = {'UNDO'}
    
    #READONLY
    material_pointer_name: bpy.props.StringProperty(name="Material Pointer Name",default="New Pointer")

    def execute(self,context):
        scene_props = home_builder_utils.get_scene_props(context.scene)
        mat_group = scene_props.material_pointer_groups[scene_props.material_group_index]
        pointer = mat_group.pointers.add()
        pointer.name = self.material_pointer_name
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=350)
        
    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.label(text="Material Pointer Name")
        layout.prop(self,'material_pointer_name',text="")


class home_builder_OT_update_object_materials(bpy.types.Operator):
    bl_idname = "home_builder.update_object_materials"
    bl_label = "Update Object Materials"
    bl_description = "This updates the object materials from the assigned pointers"
    bl_options = {'UNDO'}
    
    object_name: bpy.props.StringProperty(name="Object Name")

    def execute(self,context):
        obj = bpy.data.objects[self.object_name]
        home_builder_pointers.assign_materials_to_object(obj)
        return {'FINISHED'}


class home_builder_OT_reload_library(bpy.types.Operator):
    bl_idname = "home_builder.reload_library"
    bl_label = "Reload Library"
    bl_description = "This updates the library path"
    bl_options = {'UNDO'}
    
    object_name: bpy.props.StringProperty(name="Object Name")

    def execute(self,context):
        props = home_builder_utils.get_scene_props(context.scene)
        props.library_tabs = 'ROOMS'
        props.room_tabs = 'WALLS'
        return {'FINISHED'}


class home_builder_OT_add_part(bpy.types.Operator):
    bl_idname = "home_builder.add_part"
    bl_label = "Add Part"
    bl_description = "This adds a part to the selected assembly"
    bl_options = {'UNDO'}
    
    #READONLY
    object_name: bpy.props.StringProperty(name="Object Name")

    #APPLIED PANEL
    carcass_type: bpy.props.EnumProperty(name="Carcass Type",
                                items=[('BASE',"Base","Use Base Pointer"),
                                       ('TALL',"Tall","Use Tall Pointer"),
                                       ('UPPER',"Upper","Use Upper Pointer")],
                                default='BASE')  
    add_left_panel: bpy.props.BoolProperty(name="Add Left Panel")
    add_right_panel: bpy.props.BoolProperty(name="Add Right Panel")
    add_back_panel: bpy.props.BoolProperty(name="Add Back Panel")
    applied_panel_front_overlay: bpy.props.FloatProperty(name="Applied Panel Front Overlay",subtype='DISTANCE')
    applied_panel_rear_overlay: bpy.props.FloatProperty(name="Applied Panel Rear Overlay",subtype='DISTANCE')
    applied_panel_left_overlay: bpy.props.FloatProperty(name="Applied Panel Left Overlay",subtype='DISTANCE')
    applied_panel_right_overlay: bpy.props.FloatProperty(name="Applied Panel Right Overlay",subtype='DISTANCE')

    #COUNTERTOP
    countertop_front_overlay: bpy.props.FloatProperty(name="Countertop Front Overlay",subtype='DISTANCE')
    countertop_rear_overlay: bpy.props.FloatProperty(name="Countertop Rear Overlay",subtype='DISTANCE')
    countertop_left_overlay: bpy.props.FloatProperty(name="Countertop Left Overlay",subtype='DISTANCE')
    countertop_right_overlay: bpy.props.FloatProperty(name="Countertop Right Overlay",subtype='DISTANCE')    

    #MOLDING
    left_return: bpy.props.BoolProperty(name="Left Return")
    right_return: bpy.props.BoolProperty(name="Right Return")    

    def check(self, context):
        return True
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
        
    def draw(self,context):
        layout = self.layout
        props = home_builder_utils.get_scene_props(context.scene)
        if props.selected_part == 'APPLIED_PANEL':
            layout.prop(self,'carcass_type')
            layout.prop(self,'add_left_panel')
            layout.prop(self,'add_right_panel')
            layout.prop(self,'add_back_panel')
            if self.add_left_panel or self.add_right_panel:
                layout.prop(self,'applied_panel_front_overlay')
                layout.prop(self,'applied_panel_rear_overlay')
            if self.add_back_panel:
                layout.prop(self,'applied_panel_left_overlay')
                layout.prop(self,'applied_panel_right_overlay')

        if props.selected_part == 'COUNTERTOP':
            layout.prop(self,'countertop_front_overlay')
            layout.prop(self,'countertop_rear_overlay')
            layout.prop(self,'countertop_left_overlay')
            layout.prop(self,'countertop_right_overlay')

        if props.selected_part == 'MOLDING_BASE':
            layout.prop(self,'left_return')
            layout.prop(self,'right_return')

        if props.selected_part == 'MOLDING_CROWN':
            layout.prop(self,'left_return')
            layout.prop(self,'right_return')

        if props.selected_part == 'MOLDING_LIGHT':
            layout.prop(self,'left_return')
            layout.prop(self,'right_return')                      

    def add_applied_panel(self,props,sel_assembly):
        pointer = None
        if self.carcass_type == 'BASE':
            pointer = props.cabinet_door_pointers["Base Cabinet Doors"]
        if self.carcass_type == 'TALL':
            pointer = props.cabinet_door_pointers["Tall Cabinet Doors"]
        if self.carcass_type == 'UPPER':
            pointer = props.cabinet_door_pointers["Upper Cabinet Doors"]

        if self.add_left_panel:
            door = data_cabinet_parts.add_door_part(sel_assembly,pointer)
            door.set_name("Applied Panel")
            door.loc_x(value=0)
            door.loc_y(value=sel_assembly.obj_y.location.y-self.applied_panel_front_overlay)
            door.loc_z(value=0)
            door.rot_x(value=0)
            door.rot_y(value=math.radians(-90))
            door.rot_z(value=0)
            door.dim_x(value=sel_assembly.obj_z.location.z)
            door.dim_y(value=math.fabs(sel_assembly.obj_y.location.y)+self.applied_panel_front_overlay+self.applied_panel_rear_overlay)
            door.dim_z(value=pc_unit.inch(.75))      

        if self.add_right_panel:
            door = data_cabinet_parts.add_door_part(sel_assembly,pointer)
            door.set_name("Applied Panel")
            door.loc_x(value=sel_assembly.obj_x.location.x)
            door.loc_y(value=-self.applied_panel_rear_overlay)
            door.loc_z(value=0)
            door.rot_x(value=0)
            door.rot_y(value=math.radians(-90))
            door.rot_z(value=math.radians(180))
            door.dim_x(value=sel_assembly.obj_z.location.z)
            door.dim_y(value=math.fabs(sel_assembly.obj_y.location.y)+self.applied_panel_front_overlay+self.applied_panel_rear_overlay)
            door.dim_z(value=pc_unit.inch(.75))  

        if self.add_back_panel:
            door = data_cabinet_parts.add_door_part(sel_assembly,pointer)
            door.set_name("Applied Back Panel")
            door.loc_x(value=-self.applied_panel_left_overlay)
            door.loc_y(value=0)
            door.loc_z(value=0)
            door.rot_x(value=0)
            door.rot_y(value=math.radians(-90))
            door.rot_z(value=math.radians(-90))
            door.dim_x(value=sel_assembly.obj_z.location.z)
            door.dim_y(value=sel_assembly.obj_x.location.x+self.applied_panel_left_overlay+self.applied_panel_right_overlay)
            door.dim_z(value=pc_unit.inch(.75)) 

    def add_countertop(self,props,sel_assembly):
        ctop = data_cabinet_parts.add_countertop_part(sel_assembly)
        ctop.set_name("Countertop")
        ctop.loc_x(value=-self.countertop_left_overlay)
        ctop.loc_y(value=self.countertop_rear_overlay)
        ctop.loc_z(value=sel_assembly.obj_z.location.z)
        ctop.rot_x(value=0)
        ctop.rot_y(value=0)
        ctop.rot_z(value=0)
        ctop.dim_x(value=sel_assembly.obj_x.location.x+self.countertop_left_overlay+self.countertop_right_overlay)
        ctop.dim_y(value=sel_assembly.obj_y.location.y-self.countertop_front_overlay-self.countertop_rear_overlay)
        ctop.dim_z(value=pc_unit.inch(1.5)) 
        home_builder_utils.flip_normals(ctop)
        ctop.obj_bp.hide_viewport = False
        ctop.obj_x.hide_viewport = False
        ctop.obj_y.hide_viewport = False
        ctop.obj_z.hide_viewport = False

    def add_base_molding(self,props,sel_assembly):
        pointer = props.molding_pointers["Base Molding"]
        molding_path = home_builder_paths.get_molding_path()
        path = os.path.join(molding_path,pointer.category,pointer.item_name + ".blend")
        profile = home_builder_utils.get_object(path)

        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=False)
        obj_curve = bpy.context.active_object
        obj_curve.name = "Base Molding"
        obj_curve.parent = sel_assembly.obj_bp
        obj_curve.modifiers.new("Edge Split",type='EDGE_SPLIT')     
        obj_curve.data.splines.clear()   
        obj_curve.data.bevel_mode = 'OBJECT'
        obj_curve.data.bevel_object = profile
        obj_curve.location = (0,0,0)
        
        spline = obj_curve.data.splines.new('BEZIER')

        if self.left_return:
            spline.bezier_points.add(count=2)   
            spline.bezier_points[0].co = (0,0,0)
            spline.bezier_points[1].co = (0,sel_assembly.obj_y.location.y,0)
            spline.bezier_points[2].co = (sel_assembly.obj_x.location.x,sel_assembly.obj_y.location.y,0)
        else:
            spline.bezier_points.add(count=1)   
            spline.bezier_points[0].co = (0,sel_assembly.obj_y.location.y,0)
            spline.bezier_points[1].co = (sel_assembly.obj_x.location.x,sel_assembly.obj_y.location.y,0)

        if self.right_return:
            spline.bezier_points.add(count=1) 
            if self.left_return:
                spline.bezier_points[3].co = (sel_assembly.obj_x.location.x,0,0)
            else:
                spline.bezier_points[2].co = (sel_assembly.obj_x.location.x,0,0)

        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.handle_type_set(type='VECTOR')
        bpy.ops.object.editmode_toggle()

        home_builder_pointers.assign_pointer_to_object(obj_curve,"Molding")
        home_builder_pointers.assign_materials_to_object(obj_curve)

    def add_crown_molding(self,props,sel_assembly):
        pointer = props.molding_pointers["Crown Molding"]
        molding_path = home_builder_paths.get_molding_path()
        path = os.path.join(molding_path,pointer.category,pointer.item_name + ".blend")
        profile = home_builder_utils.get_object(path)
        
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=False)
        obj_curve = bpy.context.active_object
        obj_curve.name = "Crown Molding"
        obj_curve.parent = sel_assembly.obj_bp
        obj_curve.modifiers.new("Edge Split",type='EDGE_SPLIT')     
        obj_curve.data.splines.clear()   
        obj_curve.data.bevel_mode = 'OBJECT'
        obj_curve.data.bevel_object = profile
        obj_curve.location = (0,0,0)
        spline = obj_curve.data.splines.new('BEZIER')

        if self.left_return:
            spline.bezier_points.add(count=2)   
            spline.bezier_points[0].co = (0,0,sel_assembly.obj_z.location.z)
            spline.bezier_points[1].co = (0,sel_assembly.obj_y.location.y,sel_assembly.obj_z.location.z)
            spline.bezier_points[2].co = (sel_assembly.obj_x.location.x,sel_assembly.obj_y.location.y,sel_assembly.obj_z.location.z)
        else:
            spline.bezier_points.add(count=1)   
            spline.bezier_points[0].co = (0,sel_assembly.obj_y.location.y,sel_assembly.obj_z.location.z)
            spline.bezier_points[1].co = (sel_assembly.obj_x.location.x,sel_assembly.obj_y.location.y,sel_assembly.obj_z.location.z)

        if self.right_return:
            spline.bezier_points.add(count=1) 
            if self.left_return:
                spline.bezier_points[3].co = (sel_assembly.obj_x.location.x,0,sel_assembly.obj_z.location.z)
            else:
                spline.bezier_points[2].co = (sel_assembly.obj_x.location.x,0,sel_assembly.obj_z.location.z)

        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.handle_type_set(type='VECTOR')
        bpy.ops.object.editmode_toggle()

        home_builder_pointers.assign_pointer_to_object(obj_curve,"Molding")
        home_builder_pointers.assign_materials_to_object(obj_curve)

    def add_light_molding(self,props,sel_assembly):
        pointer = props.molding_pointers["Light Rail Molding"]
        molding_path = home_builder_paths.get_molding_path()
        path = os.path.join(molding_path,pointer.category,pointer.item_name + ".blend")
        profile = home_builder_utils.get_object(path)
        
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=False)
        obj_curve = bpy.context.active_object
        obj_curve.name = "Light Molding"
        obj_curve.parent = sel_assembly.obj_bp
        obj_curve.modifiers.new("Edge Split",type='EDGE_SPLIT')     
        obj_curve.data.splines.clear()   
        obj_curve.data.bevel_mode = 'OBJECT'
        obj_curve.data.bevel_object = profile
        obj_curve.location = (0,0,0)
        spline = obj_curve.data.splines.new('BEZIER')

        if self.left_return:
            spline.bezier_points.add(count=2)   
            spline.bezier_points[0].co = (0,0,0)
            spline.bezier_points[1].co = (0,sel_assembly.obj_y.location.y,0)
            spline.bezier_points[2].co = (sel_assembly.obj_x.location.x,sel_assembly.obj_y.location.y,0)
        else:
            spline.bezier_points.add(count=1)   
            spline.bezier_points[0].co = (0,sel_assembly.obj_y.location.y,0)
            spline.bezier_points[1].co = (sel_assembly.obj_x.location.x,sel_assembly.obj_y.location.y,0)

        if self.right_return:
            spline.bezier_points.add(count=1) 
            if self.left_return:
                spline.bezier_points[3].co = (sel_assembly.obj_x.location.x,0,0)
            else:
                spline.bezier_points[2].co = (sel_assembly.obj_x.location.x,0,0)

        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.handle_type_set(type='VECTOR')
        bpy.ops.object.editmode_toggle()

        home_builder_pointers.assign_pointer_to_object(obj_curve,"Molding")
        home_builder_pointers.assign_materials_to_object(obj_curve)
        
    def execute(self,context):
        obj = bpy.data.objects[self.object_name]
        obj_bp = pc_utils.get_assembly_bp(obj)
        sel_assembly = pc_types.Assembly(obj_bp)
        props = home_builder_utils.get_scene_props(context.scene)

        if props.selected_part == 'APPLIED_PANEL':
            self.add_applied_panel(props,sel_assembly)
        if props.selected_part == 'COUNTERTOP':
            self.add_countertop(props,sel_assembly)
        if props.selected_part == 'MOLDING_BASE':
            self.add_base_molding(props,sel_assembly)
        if props.selected_part == 'MOLDING_CROWN':
            self.add_crown_molding(props,sel_assembly)
        if props.selected_part == 'MOLDING_LIGHT':
            self.add_light_molding(props,sel_assembly)                        
                           
        return {'FINISHED'}    


class home_builder_OT_delete_room_molding(bpy.types.Operator):
    bl_idname = "home_builder.delete_room_molding"
    bl_label = "Delete Room Molding"
    bl_description = "This removes the molding in the room"
    bl_options = {'UNDO'}

    def check(self, context):
        return True
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)    

    def execute(self,context):
        #COLLECT DATA
        cabinet_base_molding = []
        cabinet_crown_molding = []
        cabinet_light_rail_molding = []
        wall_crown_molding = []
        wall_base_molding = []

        for obj in bpy.data.objects:
            if "IS_CABINET_BASE_MOLDING" in obj and obj not in cabinet_base_molding:
                cabinet_base_molding.append(obj)
            if "IS_CABINET_CROWN_MOLDING" in obj and obj not in cabinet_crown_molding:
                cabinet_crown_molding.append(obj)  
            if "IS_CABINET_LIGHT_MOLDING" in obj and obj not in cabinet_light_rail_molding:
                cabinet_light_rail_molding.append(obj)                  
            if "IS_WALL_CROWN_MOLDING" in obj and obj not in wall_crown_molding:
                wall_crown_molding.append(obj)
            if "IS_WALL_BASE_MOLDING" in obj and obj not in wall_base_molding:
                wall_base_molding.append(obj)

        #DELETE CURVES
        pc_utils.delete_obj_list(cabinet_base_molding)
        pc_utils.delete_obj_list(cabinet_crown_molding)
        pc_utils.delete_obj_list(cabinet_light_rail_molding)
        pc_utils.delete_obj_list(wall_crown_molding)
        pc_utils.delete_obj_list(wall_base_molding)    

        return {'FINISHED'}   

    def draw(self,context):
        layout = self.layout
        layout.label(text="Are you sure you want to delete the room molding?")


class home_builder_OT_auto_add_molding(bpy.types.Operator):
    bl_idname = "home_builder.auto_add_molding"
    bl_label = "Auto Add Molding"
    bl_description = "This adds automatically adds molding to the products in the current scene"
    bl_options = {'UNDO'}
    
    add_base_molding: bpy.props.BoolProperty(name="Add Base Molding")
    add_crown_molding: bpy.props.BoolProperty(name="Add Crown Molding")
    add_light_rail_molding: bpy.props.BoolProperty(name="Add Light Rail Molding")
    add_wall_crown_molding: bpy.props.BoolProperty(name="Add Wall Crown Molding")
    add_wall_base_molding: bpy.props.BoolProperty(name="Add Wall Base Molding")

    base_profile = None
    light_profile = None        
    base_profile = None
    crown_profile = None
    wall_crown_profile = None

    def check(self, context):
        return True
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
        
    def draw(self,context):
        layout = self.layout
        props = home_builder_utils.get_scene_props(context.scene)
        layout.prop(self,'add_base_molding')     
        layout.prop(self,'add_crown_molding')   
        layout.prop(self,'add_light_rail_molding')   
        layout.prop(self,'add_wall_crown_molding')   
        layout.prop(self,'add_wall_base_molding')                

    def create_curve(self):
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=False)
        obj_curve = bpy.context.active_object
        obj_curve.modifiers.new("Edge Split",type='EDGE_SPLIT')     
        obj_curve.data.splines.clear()   
        obj_curve.data.bevel_mode = 'OBJECT'
        obj_curve.location = (0,0,0)
        obj_curve.data.dimensions = '2D'
        return obj_curve

    def assign_active_curve_properties(self,obj_curve):
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.handle_type_set(type='VECTOR')
        bpy.ops.object.editmode_toggle()

        home_builder_pointers.assign_pointer_to_object(obj_curve,"Molding")
        home_builder_pointers.assign_materials_to_object(obj_curve)

    def add_base_molding_to_wall(self,sel_assembly):
        obj_curve = self.create_curve()
        obj_curve["IS_WALL_BASE_MOLDING"] = True
        obj_curve.name = "Base Wall Molding"
        obj_curve.parent = sel_assembly.obj_bp
        obj_curve.data.bevel_object = self.base_profile
        
        spline = obj_curve.data.splines.new('BEZIER')

        spline.bezier_points.add(count=1)   
        spline.bezier_points[0].co = (0,0,0)
        spline.bezier_points[1].co = (sel_assembly.obj_x.location.x,0,0)

        self.assign_active_curve_properties(obj_curve)

    def add_crown_molding_to_wall(self,sel_assembly):
        width = sel_assembly.obj_x.location.x
        height = sel_assembly.obj_z.location.z

        obj_curve = self.create_curve()
        obj_curve["IS_WALL_CROWN_MOLDING"] = True
        obj_curve.name = "Crown Wall Molding"
        obj_curve.parent = sel_assembly.obj_bp
        obj_curve.data.bevel_object = self.wall_crown_profile
        obj_curve.location.z = height

        spline = obj_curve.data.splines.new('BEZIER')
        spline.bezier_points.add(count=1)   
        spline.bezier_points[0].co = (0,0,0)
        spline.bezier_points[1].co = (width,0,0)

        self.assign_active_curve_properties(obj_curve)

    def add_base_molding_to_cabinet(self,sel_assembly):
        for carcass in sel_assembly.carcasses:
            carcass_type = carcass.get_prompt("Carcass Type").get_value()
            if carcass_type not in ("Base","Tall"):
                return None            
            toe_kick_setback = carcass.get_prompt("Toe Kick Setback").get_value()
            lfe = carcass.get_prompt("Left Finished End").get_value()
            rfe = carcass.get_prompt("Right Finished End").get_value()

            obj_curve = self.create_curve()
            obj_curve["IS_CABINET_BASE_MOLDING"] = True
            obj_curve.name = "Base Cabinet Molding"
            obj_curve.parent = sel_assembly.obj_bp
            obj_curve.data.bevel_object = self.base_profile

            spline = obj_curve.data.splines.new('BEZIER')

            width = sel_assembly.obj_x.location.x
            depth = sel_assembly.obj_y.location.y
            if lfe:
                spline.bezier_points.add(count=2)   
                spline.bezier_points[0].co = (0,0,0)
                spline.bezier_points[1].co = (0,depth+toe_kick_setback,0)
                spline.bezier_points[2].co = (width,depth+toe_kick_setback,0)
            else:
                spline.bezier_points.add(count=1)   
                spline.bezier_points[0].co = (0,depth+toe_kick_setback,0)
                spline.bezier_points[1].co = (width,depth+toe_kick_setback,0)

            if rfe:
                spline.bezier_points.add(count=1) 
                if lfe:
                    spline.bezier_points[3].co = (width,0,0)
                else:
                    spline.bezier_points[2].co = (width,0,0)

            self.assign_active_curve_properties(obj_curve)

    def add_crown_molding_to_cabinet(self,sel_assembly):
        width = sel_assembly.obj_x.location.x
        height = sel_assembly.obj_z.location.z
        depth = sel_assembly.obj_y.location.y
        cabinet_type = sel_assembly.get_prompt("Cabinet Type").get_value()
        lfe = None
        rfe = None
        for carcass in sel_assembly.carcasses:
            lfe = carcass.get_prompt("Left Finished End").get_value()
            rfe = carcass.get_prompt("Right Finished End").get_value()
            break

        if cabinet_type not in ("Upper","Tall"):
            return None

        obj_curve = self.create_curve()
        obj_curve["IS_CABINET_CROWN_MOLDING"] = True
        obj_curve.name = "Crown Cabinet Molding"
        obj_curve.parent = sel_assembly.obj_bp
        obj_curve.data.bevel_object = self.crown_profile
        obj_curve.location.z = height
        spline = obj_curve.data.splines.new('BEZIER')

        if lfe:
            spline.bezier_points.add(count=2)   
            spline.bezier_points[0].co = (0,0,0)
            spline.bezier_points[1].co = (0,depth,0)
            spline.bezier_points[2].co = (width,depth,0)
        else:
            spline.bezier_points.add(count=1)   
            spline.bezier_points[0].co = (0,depth,0)
            spline.bezier_points[1].co = (width,depth,0)

        if rfe:
            spline.bezier_points.add(count=1) 
            if lfe:
                spline.bezier_points[3].co = (width,0,0)
            else:
                spline.bezier_points[2].co = (width,0,0)

        self.assign_active_curve_properties(obj_curve)

    def add_light_rail_molding_to_cabinet(self,sel_assembly):
        width = sel_assembly.obj_x.location.x
        height = sel_assembly.obj_z.location.z
        depth = sel_assembly.obj_y.location.y
        cabinet_type = sel_assembly.get_prompt("Cabinet Type").get_value()
        lfe = None
        rfe = None

        for carcass in sel_assembly.carcasses:
            lfe = carcass.get_prompt("Left Finished End").get_value()
            rfe = carcass.get_prompt("Right Finished End").get_value()
            break

        if cabinet_type not in ("Upper"):
            return None

        obj_curve = self.create_curve()
        obj_curve["IS_CABINET_LIGHT_MOLDING"] = True
        obj_curve.name = "Light Rail Cabinet Molding"
        obj_curve.parent = sel_assembly.obj_bp
        obj_curve.data.bevel_object = self.light_profile
        spline = obj_curve.data.splines.new('BEZIER')

        if lfe:
            spline.bezier_points.add(count=2)   
            spline.bezier_points[0].co = (0,0,0)
            spline.bezier_points[1].co = (0,depth,0)
            spline.bezier_points[2].co = (width,depth,0)
        else:
            spline.bezier_points.add(count=1)   
            spline.bezier_points[0].co = (0,depth,0)
            spline.bezier_points[1].co = (width,depth,0)

        if rfe:
            spline.bezier_points.add(count=1) 
            if lfe:
                spline.bezier_points[3].co = (width,0,0)
            else:
                spline.bezier_points[2].co = (width,0,0)

        self.assign_active_curve_properties(obj_curve)

    def add_base_molding_to_closet(self,closet):
        pt = closet.get_prompt("Panel Thickness").get_value()
        start_x = 0
        for i in range(1,10):
            width_p = closet.get_prompt("Opening " + str(i) + " Width")
            if width_p:
                width = width_p.get_value()
                floor = closet.get_prompt("Opening " + str(i) + " Floor Mounted").get_value()
                if not floor:
                    start_x += width + pt
                    continue #DONT ADD MOLDING TO HANGING UNITS

                obj_curve = self.create_curve()
                obj_curve["IS_CABINET_BASE_MOLDING"] = True
                obj_curve.name = "Base Closet Molding"
                obj_curve.parent = closet.obj_bp
                obj_curve.data.bevel_object = self.base_profile
                obj_curve.data.dimensions = '2D'
                spline = obj_curve.data.splines.new('BEZIER')
            
                next_width_p = closet.get_prompt("Opening " + str(i + 1) + " Width")
                next_depth_p = closet.get_prompt("Opening " + str(i + 1) + " Depth")
                next_floor = closet.get_prompt("Opening " + str(i + 1) + " Floor Mounted")  
                prev_floor = closet.get_prompt("Opening " + str(i - 1) + " Floor Mounted") 
                prev_depth_p = closet.get_prompt("Opening " + str(i - 1) + " Depth")       
                
                depth = closet.get_prompt("Opening " + str(i) + " Depth").get_value()
                
                current_index = 0

                no_back_left_point = False
                #BACK LEFT
                if prev_depth_p:
                    if not prev_floor.get_value():
                        spline.bezier_points[current_index].co = (start_x,0,0)  
                    else:
                        prev_depth = prev_depth_p.get_value()
                        if prev_depth >= depth:
                            no_back_left_point = True
                        else:
                            spline.bezier_points[current_index].co = (start_x,-prev_depth,0)  
                else:
                    spline.bezier_points[current_index].co = (start_x,0,0)  

                #FRONT LEFT
                if not no_back_left_point:
                    spline.bezier_points.add(count=1)
                    current_index += 1    
                spline.bezier_points[current_index].co = (start_x,-depth,0)  

                #FRONT RIGHT
                spline.bezier_points.add(count=1)  
                current_index += 1  
                spline.bezier_points[current_index].co = (start_x+width+(pt*2),-depth,0)  

                #BACK RIGHT
                if next_width_p:
                    next_depth = next_depth_p.get_value()
                    if not next_floor.get_value():
                        spline.bezier_points.add(count=1)  
                        current_index += 1                        
                        spline.bezier_points[current_index].co = (start_x+width+(pt*2),0,0)  
                    else:
                        if next_depth >= depth:
                            pass
                        else:
                            spline.bezier_points.add(count=1)  
                            current_index += 1 
                            spline.bezier_points[current_index].co = (start_x+width+(pt*2),-next_depth,0)  
                else:
                    #LAST RETURN
                    spline.bezier_points.add(count=1)  
                    current_index += 1
                    spline.bezier_points[current_index].co = (start_x+width+(pt*2),0,0)  

                start_x += width + pt

            self.assign_active_curve_properties(obj_curve)    

    def add_crown_molding_to_closet(self,closet):
        pt = closet.get_prompt("Panel Thickness").get_value()
        start_x = 0
        hanging_height = closet.obj_z.location.z
        for i in range(1,10):
            obj_curve = self.create_curve()
            obj_curve["IS_CABINET_CROWN_MOLDING"] = True
            obj_curve.name = "Crown Closet Molding"
            obj_curve.parent = closet.obj_bp
            obj_curve.data.bevel_object = self.crown_profile
            spline = obj_curve.data.splines.new('BEZIER')
            width_p = closet.get_prompt("Opening " + str(i) + " Width")

            if width_p:
                
                next_width_p = closet.get_prompt("Opening " + str(i + 1) + " Width")
                next_height_p = closet.get_prompt("Opening " + str(i + 1) + " Height")
                next_depth_p = closet.get_prompt("Opening " + str(i + 1) + " Depth")
                prev_height_p = closet.get_prompt("Opening " + str(i - 1) + " Height")
                prev_depth_p = closet.get_prompt("Opening " + str(i - 1) + " Depth")                
                width = width_p.get_value()
                height = closet.get_prompt("Opening " + str(i) + " Height").get_value()
                depth = closet.get_prompt("Opening " + str(i) + " Depth").get_value()
                floor = closet.get_prompt("Opening " + str(i) + " Floor Mounted").get_value()
                if floor:
                    obj_curve.location.z = height
                else:
                    obj_curve.location.z = hanging_height
                current_index = 0

                no_back_left_point = False
                #BACK LEFT
                if prev_depth_p:
                    prev_depth = prev_depth_p.get_value()
                    prev_height = prev_height_p.get_value()
                    if prev_depth >= depth:
                        no_back_left_point = True
                    else:
                        if prev_height < height:
                            spline.bezier_points[current_index].co = (start_x,0,0)  
                        else:
                            spline.bezier_points[current_index].co = (start_x,-prev_depth,0)  
                else:
                    spline.bezier_points[current_index].co = (start_x,0,0)  

                #FRONT LEFT
                if not no_back_left_point:
                    spline.bezier_points.add(count=1)
                    current_index += 1    
                spline.bezier_points[current_index].co = (start_x,-depth,0)  

                #FRONT RIGHT
                spline.bezier_points.add(count=1)  
                current_index += 1  
                spline.bezier_points[current_index].co = (start_x+width+(pt*2),-depth,0)  

                #BACK RIGHT
                if next_width_p:
                    next_depth = next_depth_p.get_value()
                    next_height = next_height_p.get_value()
                    if next_depth >= depth:
                        pass
                    else:
                        spline.bezier_points.add(count=1)  
                        current_index += 1 
                        if next_height < height:
                            spline.bezier_points[current_index].co = (start_x+width+(pt*2),0,0)  
                        else:
                            spline.bezier_points[current_index].co = (start_x+width+(pt*2),-next_depth,0) 
                else:
                    #LAST RETURN
                    spline.bezier_points.add(count=1)  
                    current_index += 1
                    spline.bezier_points[current_index].co = (start_x+width+(pt*2),0,0)  

                start_x += width + pt

            self.assign_active_curve_properties(obj_curve)    

    def execute(self,context):
        #LOAD PROFILES
        props = home_builder_utils.get_scene_props(context.scene)  
        light_pointer = props.molding_pointers["Light Rail Molding"]
        base_pointer = props.molding_pointers["Base Molding"]
        crown_pointer = props.molding_pointers["Crown Molding"]
        wall_crown_pointer = props.molding_pointers["Wall Crown Molding"]
        molding_path = home_builder_paths.get_molding_path()
        base_path = os.path.join(molding_path,base_pointer.category,base_pointer.item_name + ".blend")
        light_path = os.path.join(molding_path,light_pointer.category,light_pointer.item_name + ".blend")
        crown_path = os.path.join(molding_path,crown_pointer.category,crown_pointer.item_name + ".blend")
        wall_crown_path = os.path.join(molding_path,wall_crown_pointer.category,wall_crown_pointer.item_name + ".blend")
        self.light_profile = home_builder_utils.get_object(light_path)        
        self.base_profile = home_builder_utils.get_object(base_path)
        self.crown_profile = home_builder_utils.get_object(crown_path)
        self.wall_crown_profile = home_builder_utils.get_object(wall_crown_path)
        self.light_profile.use_fake_user = True
        self.base_profile.use_fake_user = True
        self.crown_profile.use_fake_user = True
        self.wall_crown_profile.use_fake_user = True

        #COLLECT DATA
        cabinet_base_molding = []
        cabinet_crown_molding = []
        cabinet_light_rail_molding = []
        wall_crown_molding = []
        wall_base_molding = []
        walls = []
        cabinets = []
        closets = []

        for obj in bpy.data.objects:
            if "IS_CABINET_BASE_MOLDING" in obj and obj not in cabinet_base_molding:
                cabinet_base_molding.append(obj)
            if "IS_CABINET_CROWN_MOLDING" in obj and obj not in cabinet_crown_molding:
                cabinet_crown_molding.append(obj)  
            if "IS_CABINET_LIGHT_MOLDING" in obj and obj not in cabinet_light_rail_molding:
                cabinet_light_rail_molding.append(obj)                  
            if "IS_WALL_CROWN_MOLDING" in obj and obj not in wall_crown_molding:
                wall_crown_molding.append(obj)
            if "IS_WALL_BASE_MOLDING" in obj and obj not in wall_base_molding:
                wall_base_molding.append(obj)

            cabinet_bp = home_builder_utils.get_cabinet_bp(obj)
            closet_bp = home_builder_utils.get_closet_bp(obj)
            wall_bp = home_builder_utils.get_wall_bp(obj)
            if cabinet_bp and cabinet_bp not in cabinets:
                cabinets.append(cabinet_bp)
            if wall_bp and wall_bp not in walls:
                walls.append(wall_bp)
            if closet_bp and closet_bp not in closets:
                closets.append(closet_bp)

        #DELETE OLD CURVES
        if self.add_base_molding:
            pc_utils.delete_obj_list(cabinet_base_molding)
        if self.add_crown_molding:
            pc_utils.delete_obj_list(cabinet_crown_molding)
        if self.add_light_rail_molding:
            pc_utils.delete_obj_list(cabinet_light_rail_molding)
        if self.add_wall_crown_molding:
            pc_utils.delete_obj_list(wall_crown_molding)
        if self.add_wall_base_molding:
            pc_utils.delete_obj_list(wall_base_molding)      

        #CREATE NEW CURVES
        for wall_bp in walls:
            wall = pc_types.Assembly(wall_bp)
            if self.add_wall_base_molding:
                self.add_base_molding_to_wall(wall)
            if self.add_wall_crown_molding:
                self.add_crown_molding_to_wall(wall)                
        for cabinet_bp in cabinets:
            cabinet = data_cabinets.Cabinet(cabinet_bp)
            if self.add_base_molding:
                self.add_base_molding_to_cabinet(cabinet)
            if self.add_crown_molding:
                self.add_crown_molding_to_cabinet(cabinet)
            if self.add_light_rail_molding:
                self.add_light_rail_molding_to_cabinet(cabinet)
        for closet_bp in closets:
            closet = pc_types.Assembly(closet_bp)
            if self.add_base_molding:
                self.add_base_molding_to_closet(closet)
            if self.add_crown_molding:
                self.add_crown_molding_to_closet(closet)

        return {'FINISHED'}    


class home_builder_OT_change_closet_offsets(bpy.types.Operator):
    bl_idname = "home_builder.change_closet_offsets"
    bl_label = "Change Closet Offsets"
    bl_description = "This allows you to easily adjust the closets left and right offset"
    bl_options = {'UNDO'}
    
    anchor_type: EnumProperty(name="Anchor Type",
                             items=[('SET_OFFSETS',"Set Offsets","Set Offsets"),
                                    ('LEFT',"Left","Left"),
                                    ('RIGHT',"Right","Right"),
                                    ('CENTER','Center','Center')],
                             default='SET_OFFSETS')

    left_offset: FloatProperty(name="Left Offset",subtype='DISTANCE')
    right_offset: FloatProperty(name="Right Offset",subtype='DISTANCE')
    start_x: FloatProperty(name="Start X",subtype='DISTANCE')
    start_width: FloatProperty(name="Start Width",subtype='DISTANCE')
    change_width: FloatProperty(name="Change Width",subtype='DISTANCE')

    closet = None
    calculators = []

    def check(self, context):
        if self.anchor_type == 'SET_OFFSETS':
            self.closet.obj_bp.location.x = self.start_x + self.left_offset
            self.closet.obj_x.location.x = self.start_width - self.left_offset - self.right_offset
        if self.anchor_type == 'LEFT':
            self.closet.obj_x.location.x = self.change_width
        if self.anchor_type == 'RIGHT':
            self.closet.obj_bp.location.x = self.start_x + (self.start_width - self.change_width)
            self.closet.obj_x.location.x = self.change_width
        if self.anchor_type == 'CENTER':
            self.closet.obj_bp.location.x = self.start_x + (self.start_width - self.change_width)/2
            self.closet.obj_x.location.x = self.change_width     
        for calculator in self.calculators:
            calculator.calculate()
        return True
    
    def invoke(self, context, event):
        self.closet = None
        self.calculators = []
        self.left_offset = 0
        self.right_offset = 0
        closet_bp = home_builder_utils.get_closet_bp(context.object)
        if closet_bp:
            self.closet = pc_types.Assembly(closet_bp)
            self.start_x = self.closet.obj_bp.location.x
            self.start_width = self.closet.obj_x.location.x
            self.change_width = self.closet.obj_x.location.x
            self.get_calculators(self.closet.obj_bp)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
        
    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)        

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.prop(self,'anchor_type',expand=True)
        if self.anchor_type == 'SET_OFFSETS':
            row = layout.row()
            row.label(text="Offsets:")
            row.prop(self,'left_offset',text="Left")
            row.prop(self,'right_offset',text="Right")
            row = layout.row()
            row.label(text="Closet Width")
            row.label(text=str(round(pc_unit.meter_to_inch(self.closet.obj_x.location.x),3)) + '"')
        else:
            row = layout.row()
            row.label(text="Closet Width:")
            row.prop(self,'change_width',text="")

    def execute(self,context):
        return {'FINISHED'}    


class home_builder_OT_collect_walls(bpy.types.Operator):
    bl_idname = "home_builder.collect_walls"
    bl_label = "Collect Walls"
    bl_description = "This collects all of the walls in the current scene"
    bl_options = {'UNDO'}

    def execute(self,context):
        props = home_builder_utils.get_scene_props(context.scene)
        for wall in props.walls:
            props.walls.remove(0)
        for obj in context.scene.objects:
            if 'IS_WALL_BP' in obj:
                wall = props.walls.add()
                wall.obj_bp = obj
                for child in wall.obj_bp.children:
                    if child.type == 'MESH':
                        wall.wall_mesh = child

        return {'FINISHED'}    


class home_builder_OT_show_hide_walls(bpy.types.Operator):
    bl_idname = "home_builder.show_hide_walls"
    bl_label = "Show Hide Walls"
    bl_description = "This toggles the walls visibility"
    bl_options = {'UNDO'}

    wall_obj_bp: bpy.props.StringProperty(name="Wall Base Point Name")

    def hide_children(self,obj,context):
        if obj.name in context.view_layer.objects:
            if obj.type in {'MESH','CURVE'}:
                if obj.hide_get():
                    obj.hide_set(False)
                else:
                    obj.hide_set(True)
        for child in obj.children:
            self.hide_children(child,context)

    def execute(self,context):
        wall_bp = bpy.data.objects[self.wall_obj_bp]
        self.hide_children(wall_bp,context)
        return {'FINISHED'}    


class home_builder_OT_show_hide_closet_opening(bpy.types.Operator):
    bl_idname = "home_builder.show_hide_closet_opening"
    bl_label = "Show Hide Closet Opening"
    bl_description = "This toggles the closet opening visibility"
    bl_options = {'UNDO'}

    insert_obj_bp: bpy.props.StringProperty(name="Insert Base Point Name")
    hide: bpy.props.BoolProperty(name="Hide")

    def execute(self,context):
        insert_bp = bpy.data.objects[self.insert_obj_bp]

        props = home_builder_utils.get_object_props(insert_bp)
        if props.insert_opening:
            for child in props.insert_opening.children:
                if child.type == 'MESH':
                    child.hide_viewport = self.hide
        return {'FINISHED'}   


class home_builder_OT_free_move_object(bpy.types.Operator):
    bl_idname = "home_builder.free_move_object"
    bl_label = "Free Move Object"

    obj_bp_name: bpy.props.StringProperty(name="Obj Base Point Name")

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')

        obj = bpy.data.objects[self.obj_bp_name]
        loc = obj.matrix_world
        obj.constraints.clear()
        obj.hide_viewport = False
        obj.select_set(True)
        obj.matrix_world = loc
        
        region = context.region
        co = location_3d_to_region_2d(region,context.region_data,obj.matrix_world.translation)
        region_offset = Vector((region.x,region.y))
        context.window.cursor_warp(*(co + region_offset))
        bpy.ops.transform.translate('INVOKE_DEFAULT')
        
        return {'FINISHED'}


class home_builder_OT_update_distance_prompt_in_scene(bpy.types.Operator):
    bl_idname = "home_builder.update_distance_prompt_in_scene"
    bl_label = "Update Distance Prompt in Scene"

    prompt_name: bpy.props.StringProperty(name="Prompt Name")
    prompt_value: bpy.props.FloatProperty(name="Prompt Value",subtype='DISTANCE')

    def execute(self, context):
        for obj in bpy.data.objects:
            if 'IS_ASSEMBLY_BP' in obj:
                assembly = pc_types.Assembly(obj)
                prompt = assembly.get_prompt(self.prompt_name)
                if prompt:
                    prompt.set_value(self.prompt_value)
        return {'FINISHED'}

class home_builder_OT_update_checkbox_prompt_in_scene(bpy.types.Operator):
    bl_idname = "home_builder.update_checkbox_prompt_in_scene"
    bl_label = "Update Distance Prompt in Scene"

    prompt_name: bpy.props.StringProperty(name="Prompt Name")
    prompt_value: bpy.props.BoolProperty(name="Prompt Value")

    def execute(self, context):
        for obj in bpy.data.objects:
            if 'IS_ASSEMBLY_BP' in obj:
                assembly = pc_types.Assembly(obj)
                prompt = assembly.get_prompt(self.prompt_name)
                if prompt:
                    prompt.set_value(self.prompt_value)
        return {'FINISHED'}

classes = (
    home_builder_OT_activate,
    home_builder_OT_change_library_category,
    home_builder_OT_change_closet_category,
    home_builder_OT_disconnect_constraint,
    home_builder_OT_draw_floor_plane,
    home_builder_OT_add_room_light,
    home_builder_OT_update_scene_materials,
    home_builder_OT_update_material_pointer,
    home_builder_OT_update_scene_pulls,
    home_builder_OT_update_selected_pulls,
    home_builder_OT_update_all_cabinet_doors,
    home_builder_OT_update_selected_cabinet_doors,
    home_builder_OT_add_drawer,
    home_builder_OT_update_pull_pointer,
    home_builder_OT_update_molding_pointer,
    home_builder_OT_update_cabinet_door_pointer,
    home_builder_OT_generate_2d_views,
    home_builder_OT_toggle_dimensions,
    home_builder_OT_render_asset_thumbnails,
    home_builder_OT_message,
    home_builder_OT_archipack_not_enabled,
    home_builder_OT_save_asset_to_library,
    home_builder_OT_create_thumbnails_for_selected_assets,
    home_builder_OT_open_browser_window,
    home_builder_OT_create_new_asset,
    home_builder_OT_light_prompts,
    home_builder_OT_floor_prompts,
    home_builder_OT_delete_assembly,
    home_builder_OT_reload_pointers,
    home_builder_OT_create_library_pdf,
    home_builder_OT_create_2d_views,
    home_builder_OT_create_2d_cabinet_views,
    home_builder_OT_save_custom_cabinet,
    home_builder_OT_save_decoration_to_library,
    home_builder_OT_assign_material,
    home_builder_OT_assign_material_dialog,
    home_builder_OT_assign_material_to_slot,
    home_builder_OT_add_material_pointer_group,
    home_builder_OT_change_global_material_pointer_group,
    home_builder_OT_change_product_material_pointer_group,
    home_builder_OT_update_product_material_group,
    home_builder_OT_add_material_pointer,
    home_builder_OT_update_object_materials,
    home_builder_OT_create_cabinet_list_report,
    home_builder_OT_add_part,
    home_builder_OT_reload_library,
    home_builder_OT_delete_room_molding,
    home_builder_OT_auto_add_molding,
    home_builder_OT_change_closet_offsets,
    home_builder_OT_collect_walls,
    home_builder_OT_show_hide_walls,
    home_builder_OT_show_hide_closet_opening,
    home_builder_OT_free_move_object,
    home_builder_OT_update_distance_prompt_in_scene,
    home_builder_OT_update_checkbox_prompt_in_scene,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
