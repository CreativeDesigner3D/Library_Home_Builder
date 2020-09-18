import bpy,os,inspect
import math
import subprocess
import codecs
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
from .cabinets import cabinet_utils
from . import home_builder_pointers
from . import home_builder_utils
from . import home_builder_paths

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
                    new_pull = home_builder_utils.get_pull(pointer.category,pointer.item_name)
                    new_pull_props = home_builder_utils.get_object_props(new_pull)
                    new_pull_props.pointer_name = pointer.name
                    new_pull.parent = pull.parent
                    new_pull["IS_CABINET_PULL"] = True
                    context.view_layer.active_layer_collection.collection.objects.link(new_pull)
                    home_builder_pointers.assign_pointer_to_object(new_pull,"Pull Finish")
                    if exterior_bp:
                        exterior = pc_types.Assembly(exterior_bp)
                        pull_length = exterior.get_prompt("Pull Length")    
                        if pull_length:
                            pull_length.set_value(round(new_pull.dimensions.x,2))  
                        exterior_bp.location = exterior_bp.location 

        pc_utils.delete_obj_list(pull_objs)
        return {'FINISHED'}


class home_builder_OT_update_cabinet_doors(bpy.types.Operator):
    bl_idname = "home_builder.update_cabinet_doors"
    bl_label = "Update Cabinet Doors"
    
    def run_calculators(self,context,assembly):
        for calculator in assembly.obj_prompts.pyclone.calculators:
            calculator.calculate()

    def execute(self, context):
        exterior_bp_objs = []

        for obj in bpy.data.objects:
            if "IS_EXTERIOR_BP" in obj and obj["IS_EXTERIOR_BP"]:
                exterior_bp_objs.append(obj)

        for exterior_bp in exterior_bp_objs:
            cabinet_bp = home_builder_utils.get_cabinet_bp(exterior_bp)
            carcass = None
            for child in cabinet_bp.children:
                carcass_bp = home_builder_utils.get_carcass_bp(child)
                if carcass_bp:
                    carcass = data_cabinet_carcass.Carcass(child) 
                    break

            if carcass:
                cabinet = pc_types.Assembly(cabinet_bp)
                old_exterior = pc_types.Assembly(exterior_bp)

                exterior_prompt_dict = old_exterior.get_prompt_dict()
                exterior = cabinet_utils.get_exterior_from_name(exterior_bp["EXTERIOR_NAME"])
                exterior.prompts = exterior_prompt_dict
                new_exterior = carcass.add_insert(cabinet,exterior)
                self.run_calculators(context,exterior)
                

            pc_utils.delete_object_and_children(exterior_bp)

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

        #CLEAR FILE
        file.write("for mat in bpy.data.materials:\n")
        file.write("    bpy.data.materials.remove(mat,do_unlink=True)\n")
        file.write("for obj in bpy.data.objects:\n")
        file.write("    bpy.data.objects.remove(obj,do_unlink=True)\n")   

        #DRAW ASSET
        file.write("item = eval('Library_Home_Builder." + asset.package_name + "." + asset.module_name + "." + asset.class_name + "()')" + "\n")
        file.write("if hasattr(item,'draw'):\n")
        file.write("    item.draw()\n")
        file.write("if hasattr(item,'draw_door'):\n")
        file.write("    item.draw_door()\n")      
        file.write("if hasattr(item,'draw_wall'):\n")
        file.write("    item.draw_wall()\n")          
        file.write("if hasattr(item,'render'):\n")
        file.write("    item.render()\n")

        #ADD CAMERA
        file.write("if bpy.context.scene.camera is None:\n")
        file.write("    bpy.ops.object.camera_add()\n")
        file.write("bpy.context.scene.camera = bpy.context.object\n")
        file.write("bpy.context.scene.camera.rotation_euler = (1.1093,0,.8149)\n")

        file.write("bpy.ops.object.select_all(action='DESELECT')\n")
        file.write("select_objects()\n")
        file.write("bpy.ops.view3d.camera_to_view_selected()\n")

        #ADD LIGHTING
        file.write("bpy.ops.object.light_add(type='SUN')\n")
        file.write("bpy.context.object.data.energy = 1.5\n")
        file.write("bpy.context.object.rotation_euler = (1.1093,0,.8149)\n")

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

    def execute(self, context):
        wm_props = home_builder_utils.get_wm_props(context.window_manager)
        for asset in wm_props.assets:
            if asset.is_selected:
                script = self.create_item_thumbnail_script(asset)
                subprocess.call(bpy.app.binary_path + ' -b --python "' + script + '"') 
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
        layout.operator('The Archipack add-on is not enabled.')
        layout.operator('Check the box and try again.')
        layout.prop(self,'enable_archipack')

    def execute(self, context):
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
    home_builder_OT_update_cabinet_doors,
    home_builder_OT_update_pull_pointer,
    home_builder_OT_update_cabinet_door_pointer,
    home_builder_OT_auto_add_molding,
    home_builder_OT_generate_2d_views,
    home_builder_OT_toggle_dimensions,
    home_builder_OT_render_asset_thumbnails,
    home_builder_OT_message,
    home_builder_OT_archipack_not_enabled,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
