import bpy,os,inspect, sys
import math
import subprocess
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
from .cabinets import data_cabinet_carcass
from .cabinets import data_cabinet_parts
from .cabinets import cabinet_utils
from . import home_builder_pointers
from . import home_builder_utils
from . import home_builder_paths

try:
    import reportlab
except ModuleNotFoundError:
    PATH = os.path.join(os.path.dirname(__file__),"python_libs")
    sys.path.append(PATH)

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import legal,letter,inch,cm
from reportlab.platypus import Image
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Frame, Spacer, PageTemplate, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, A4, landscape, portrait
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus.flowables import HRFlowable

class room_builder_OT_activate(Operator):
    bl_idname = "room_builder.activate"
    bl_label = "Activate Room Builder"
    bl_description = "This activates the room builder"
    bl_options = {'UNDO'}
    
    library_name: StringProperty(name='Library Name')

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        library_path = home_builder_paths.get_library_path()
        dirs = os.listdir(library_path)

        if props.active_category in dirs:
            path = os.path.join(library_path,props.active_category)
        else:
            props.active_category = dirs[0]
            path = os.path.join(library_path,props.active_category)

        if len(props.material_pointers) == 0:
            home_builder_pointers.update_pointer_properties()

        pc_utils.update_file_browser_path(context,path)
        return {'FINISHED'}


class room_builder_OT_drop(Operator):
    bl_idname = "room_builder.drop"
    bl_label = "Activate Room Builder"
    bl_description = "This is called when an asset is dropped from the home builder library"
    bl_options = {'UNDO'}
    
    filepath: StringProperty(name='Library Name')

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)

        directory, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)

        if props.active_category == 'Archipack':
            if not hasattr(bpy.types,'ARCHIPACK_OT_wall2_draw'):
                bpy.ops.home_builder.archipack_not_enabled('INVOKE_DEFAULT')
                return {'FINISHED'}
            if 'Wall' in filename:
                bpy.ops.archipack.wall2_draw('INVOKE_DEFAULT')
            if 'Door' in filename:
                bpy.ops.archipack.door_draw('INVOKE_DEFAULT')
            if 'Window' in filename:
                bpy.ops.archipack.window_draw('INVOKE_DEFAULT')
            if 'Fence' in filename:
                bpy.ops.archipack.fence('INVOKE_DEFAULT')
            if 'Stairs' in filename:
                bpy.ops.archipack.stair('INVOKE_DEFAULT')

        if props.active_category == 'Appliances':
            bpy.ops.home_builder.place_cabinet(filepath=self.filepath)

        if props.active_category == 'Doors and Windows':
            bpy.ops.home_builder.place_door_window(filepath=self.filepath)

        if props.active_category == 'Cabinets':
            bpy.ops.home_builder.place_cabinet(filepath=self.filepath)

        if props.active_category == 'Walls':
            bpy.ops.home_builder.draw_multiple_walls(filepath=self.filepath)

        return {'FINISHED'}


class home_builder_OT_change_library_category(bpy.types.Operator):
    bl_idname = "home_builder.change_library_category"
    bl_label = "Change Library Category"
    bl_description = "This changes the active library category"

    category: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        props.active_category = self.category
        path = os.path.join(home_builder_paths.get_library_path(),self.category)
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
        obj_lamp.data.energy = max(pc_unit.meter_to_active_unit(largest_x),pc_unit.meter_to_active_unit(largest_y))/4
        obj_lamp["PROMPT_ID"] = "home_builder.light_prompts"
        return {'FINISHED'}


class home_builder_OT_update_pointers(bpy.types.Operator):
    bl_idname = "home_builder.update_pointers"
    bl_label = "Update Scene Materials"
    
    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        for pointer in props.material_pointers:
            props.material_pointers.remove(0)
        for pointer in props.pull_pointers:
            props.pull_pointers.remove(0)   
        home_builder_utils.write_pointer_files()
        home_builder_utils.update_pointer_properties()   
        return {'FINISHED'}


class home_builder_OT_update_scene_materials(bpy.types.Operator):
    bl_idname = "home_builder.update_scene_materials"
    bl_label = "Update Scene Materials"
    
    def execute(self, context):
        for obj in context.visible_objects:
            if obj.type == 'MESH':
                home_builder_pointers.assign_materials_to_object(obj)
        return {'FINISHED'}


class home_builder_OT_update_material_pointer(bpy.types.Operator):
    bl_idname = "home_builder.update_material_pointer"
    bl_label = "Update Material Pointer"
    
    pointer_name: bpy.props.StringProperty(name="Pointer Name")

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        for pointer in props.material_pointers:
            if pointer.name == self.pointer_name:
                pointer.category = props.material_category
                pointer.item_name = props.material_name  
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
            for pointer in pull_pointers:
                if pointer.name == props.pointer_name:
                    pull_path = os.path.join(home_builder_paths.get_pull_path(),pointer.category,pointer.item_name + ".blend")
                    new_pull = home_builder_utils.get_object(pull_path)
                    new_pull_props = home_builder_utils.get_object_props(new_pull)
                    new_pull_props.pointer_name = pointer.name
                    new_pull.parent = pull.parent
                    new_pull["IS_CABINET_PULL"] = True
                    context.view_layer.active_layer_collection.collection.objects.link(new_pull)
                    home_builder_pointers.assign_pointer_to_object(new_pull,"Cabinet Pull Finish")
                    if exterior_bp:
                        exterior = pc_types.Assembly(exterior_bp)
                        pull_length = exterior.get_prompt("Pull Length")    
                        if pull_length:
                            pull_length.set_value(round(new_pull.dimensions.x,2))  
                        exterior_bp.location = exterior_bp.location 

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
            pull_path = os.path.join(home_builder_paths.get_pull_path(),pointer.category,pointer.item_name + ".blend")
            new_pull = home_builder_utils.get_object(pull_path)
            new_pull_props = home_builder_utils.get_object_props(new_pull)
            new_pull_props.pointer_name = pointer.name
            new_pull.parent = pull.parent
            new_pull["IS_CABINET_PULL"] = True
            context.view_layer.active_layer_collection.collection.objects.link(new_pull)
            home_builder_pointers.assign_pointer_to_object(new_pull,"Cabinet Pull Finish")
            if exterior_bp:
                exterior = pc_types.Assembly(exterior_bp)
                pull_length = exterior.get_prompt("Pull Length")    
                if pull_length:
                    pull_length.set_value(round(new_pull.dimensions.x,2))  
                exterior_bp.location = exterior_bp.location 

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
            old_door_panel_parent = pc_types.Assembly(door_panel_bp.parent)
            new_door = data_cabinet_parts.add_door_part(old_door_panel_parent,pointer)

            home_builder_utils.update_assembly_id_props(new_door,old_door_panel_parent)
            home_builder_utils.replace_assembly(old_door_panel,new_door)
            home_builder_utils.hide_empties(new_door.obj_bp)

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
            old_door_panel_parent = pc_types.Assembly(door_panel_bp.parent)
            new_door = data_cabinet_parts.add_door_part(old_door_panel_parent,pointer)

            home_builder_utils.update_assembly_id_props(new_door,old_door_panel_parent)
            home_builder_utils.replace_assembly(old_door_panel,new_door)
            home_builder_utils.hide_empties(new_door.obj_bp)

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


class home_builder_OT_auto_add_molding(bpy.types.Operator):
    bl_idname = "home_builder.auto_add_molding"
    bl_label = "Auto Add Molding"
    
    molding_type: bpy.props.StringProperty(name="Molding Type")

    def execute(self, context):
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
        file.write("import Library_Home_Builder\n")

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
        file.write("item = eval('Library_Home_Builder." + asset.package_name + "." + asset.module_name + "." + asset.class_name + "()')" + "\n")
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

        #RENDER
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
        return os.path.join(home_builder_paths.get_library_path(),"thumbnail.blend")

    def execute(self, context):
        wm_props = home_builder_utils.get_wm_props(context.window_manager)
        for asset in wm_props.assets:
            if asset.is_selected:
                script = self.create_item_thumbnail_script(asset)
                subprocess.call(bpy.app.binary_path + ' "' + self.get_thumbnail_path() + '" -b --python "' + script + '"',shell=True) 
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

    def create_item_thumbnail_script(self,asset):
        file = codecs.open(os.path.join(bpy.app.tempdir,"thumb_temp.py"),'w',encoding='utf-8')
        file.write("import bpy\n")
        file.write("import os\n")
        file.write("import sys\n")
        file.write("import Library_Home_Builder\n")

        file.write("path = r'" + os.path.join(os.path.dirname(asset.asset_path),asset.name)  + "'\n")

        file.write("bpy.ops.object.select_all(action='DESELECT')\n")

        file.write("with bpy.data.libraries.load(r'" + asset.asset_path + "', False, True) as (data_from, data_to):\n")
        file.write("    data_to.objects = data_from.objects\n")

        file.write("for obj in data_to.objects:\n")
        file.write("    bpy.context.view_layer.active_layer_collection.collection.objects.link(obj)\n")
        file.write("    Library_Home_Builder.home_builder_pointers.assign_materials_to_object(obj)\n")
        file.write("    obj.select_set(True)\n")

        file.write("bpy.ops.view3d.camera_to_view_selected()\n")

        #RENDER
        file.write("render = bpy.context.scene.render\n")    
        file.write("render.use_file_extension = True\n")
        file.write("render.filepath = path\n")
        file.write("bpy.ops.render.render(write_still=True)\n")
        file.close()
        return os.path.join(bpy.app.tempdir,'thumb_temp.py')

    def create_item_material_thumbnail_script(self,asset):
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
        file.write("    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0, area_weight=0)\n")
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

    def get_thumbnail_path(self,asset):
        return os.path.join(os.path.dirname(os.path.dirname(asset.asset_path)),"thumbnail.blend")

    def execute(self, context):
        scene_props = home_builder_utils.get_scene_props(context.scene)
        for asset in scene_props.active_asset_collection:
            if asset.is_selected:
                if scene_props.asset_tabs == 'MATERIALS':
                    script = self.create_item_material_thumbnail_script(asset)
                else:
                    script = self.create_item_thumbnail_script(asset)
                subprocess.call(bpy.app.binary_path + ' "' + self.get_thumbnail_path(asset) + '" -b --python "' + script + '"',shell=True) 
                # subprocess.call(bpy.app.binary_path + ' -b --python "' + script + '"',shell=True) 
        scene_props.asset_tabs = scene_props.asset_tabs
        return {'FINISHED'}


class home_builder_OT_save_asset_to_library(Operator):
    bl_idname = "home_builder.save_asset_to_library"
    bl_label = "Save Current Asset to Library"
    bl_description = "This will save the current file to the active library"
    bl_options = {'UNDO'}
    
    object_libraries = {'CABINET_PULLS','ENTRY_DOOR_HANDLES','FAUCETS'}
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
        file.write("    data_to.objects = data_from.objects\n")
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
        file.write("    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0, area_weight=0)\n")
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
            subprocess.call(bpy.app.binary_path + ' -b --python "' + save_script_path + '"',shell=True)

        if scene_props.asset_tabs in self.assembly_libraries:
            save_script_path = self.create_save_object_script(path, self.get_asset(context))
            subprocess.call(bpy.app.binary_path + ' -b --python "' + save_script_path + '"',shell=True)

        if scene_props.asset_tabs in self.material_libraries:
            save_script_path = self.create_save_material_script(path, self.get_asset(context))
            subprocess.call(bpy.app.binary_path + ' -b --python "' + save_script_path + '"',shell=True)

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
        layout.label(text="This will set Material, Door Fronts, and Hardware")
        layout.label(text="pointers back to the default.")

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        for pointer in props.material_pointers:
            props.material_pointers.remove(0)

        for pointer in props.pull_pointers:
            props.pull_pointers.remove(0)

        for pointer in props.cabinet_door_pointers:
            props.cabinet_door_pointers.remove(0)   

        home_builder_pointers.write_pointer_files()
        home_builder_pointers.update_pointer_properties()                                    
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
            if os.path.isdir(library_path) and ".git" not in library_folder:
                self.create_header(library_folder, font_size=20)
                for category_folder in os.listdir(library_path):
                    category_path = os.path.join(file_path,library_folder,category_folder)
                    if os.path.isdir(category_path):
                        self.create_header(category_folder, font_size=10)
                        self.create_img_table(category_path)

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

    def create_elevation_layout(self,context,wall):
        for scene in bpy.data.scenes:
            if not scene.pyclone.is_view_scene:
                context.window.scene = scene
                break
        collection = wall.create_assembly_collection(wall.obj_bp.name)

        bpy.ops.scene.new(type='EMPTY')
        layout = pc_types.Assembly_Layout(context.scene)
        layout.setup_assembly_layout()
        wall_view = layout.add_assembly_view(collection)
        # wall_view.location = (0.048988,0,0.05597)
        wall_view.rotation_euler.z = wall.obj_bp.rotation_euler.z *-1
        wall_view.location.x = wall.obj_bp.location.x *-1
        wall_view.location.y = wall.obj_bp.location.y *-1
        wall_view.location.z = wall.obj_bp.location.z *-1
        layout.add_layout_camera()   
        layout.scene.world = self.model_scene.world

        context.scene.pyclone.fit_to_paper = False
        context.scene.pyclone.page_scale_unit_type = 'METRIC'
        context.scene.pyclone.metric_page_scale = '1:30'    

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
        today = date.today()
        # props = bpy.context.scene.fullbloom
        # if props.original_date == "":
        #     props.original_date = today.strftime("%m/%d/%Y")

        # if props.revision_date == "":
        #     props.revision_date = today.strftime("%m/%d/%Y")

        # if props.revision_number == "":
        #     props.revision_number = "-"

        title_block = pc_types.Title_Block()
        title_block.create_title_block(layout)
        title_block.obj_bp.rotation_euler.x = math.radians(90)
        # title_block.obj_drawing_title.data.body = "Title"
        # title_block.obj_description.data.body = description
        # title_block.obj_scale.data.body = "1 : 30"
        # title_block.obj_drawing_number.data.body = number
        # title_block.obj_original_date.data.body = props.original_date
        # title_block.obj_revision_date.data.body = props.revision_date
        # title_block.obj_revision_number.data.body = props.revision_number
        # title_block.obj_drawn_by.data.body = props.drawn_by

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


classes = (
    room_builder_OT_activate,
    room_builder_OT_drop,
    home_builder_OT_change_library_category,
    home_builder_OT_disconnect_constraint,
    home_builder_OT_draw_floor_plane,
    home_builder_OT_add_room_light,
    home_builder_OT_update_pointers,
    home_builder_OT_update_scene_materials,
    home_builder_OT_update_material_pointer,
    home_builder_OT_update_scene_pulls,
    home_builder_OT_update_selected_pulls,
    home_builder_OT_update_all_cabinet_doors,
    home_builder_OT_update_selected_cabinet_doors,
    home_builder_OT_update_pull_pointer,
    home_builder_OT_update_cabinet_door_pointer,
    home_builder_OT_auto_add_molding,
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
    # home_builder_OT_create_library_pdf,
    home_builder_OT_create_2d_views,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
