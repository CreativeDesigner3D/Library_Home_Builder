import bpy,os,inspect
import math
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
from .walls import library_walls
from .cabinets import cabinet_library
from . import home_builder_utils

class room_builder_OT_activate(Operator):
    bl_idname = "room_builder.activate"
    bl_label = "Activate Room Builder"
    bl_description = "This activates the room builder"
    bl_options = {'UNDO'}
    
    library_name: StringProperty(name='Library Name')

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        library_path = home_builder_utils.get_library_path()
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

        if props.active_category == 'Walls':
            if 'Archipack' in self.filepath and hasattr(bpy.types,'ARCHIPACK_OT_wall2_draw'):
                bpy.ops.archipack.wall2_draw('INVOKE_DEFAULT')
            else:
                bpy.ops.home_builder.draw_multiple_walls(filepath=self.filepath)

        if props.active_category == 'Cabinets':
            bpy.ops.home_builder.place_cabinet(filepath=self.filepath)

        if props.active_category == 'Fences':
            pass

        if props.active_category == 'Doors':
            bpy.ops.home_builder.place_door(filepath=self.filepath)

        if props.active_category == 'Windows':
            pass

        return {'FINISHED'}


class home_builder_OT_change_library_category(bpy.types.Operator):
    bl_idname = "home_builder.change_library_category"
    bl_label = "Change Library Category"
    bl_description = "This changes the active library category"

    category: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        props = home_builder_utils.get_scene_props(context.scene)
        props.active_category = self.category
        path = os.path.join(home_builder_utils.get_library_path(),self.category)
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
        home_builder_utils.assign_floor_pointers(obj_plane)
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
        return {'FINISHED'}


class home_builder_OT_update_material_pointer(bpy.types.Operator):
    bl_idname = "home_builder.update_material_pointer"
    bl_label = "Update Material Pointer"
    
    pointer_name: bpy.props.StringProperty(name="Pointer Name")

    def execute(self, context):
        return {'FINISHED'}


class home_builder_OT_update_scene_pulls(bpy.types.Operator):
    bl_idname = "home_builder.update_scene_pulls"
    bl_label = "Update Scene Pulls"
    
    def execute(self, context):
        return {'FINISHED'}


class home_builder_OT_update_pull_pointer(bpy.types.Operator):
    bl_idname = "home_builder.update_pull_pointer"
    bl_label = "Update Pull Pointer"
    
    pointer_name: bpy.props.StringProperty(name="Pointer Name")

    def execute(self, context):
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
    home_builder_OT_update_pull_pointer,
    home_builder_OT_auto_add_molding,
    home_builder_OT_generate_2d_views,
    home_builder_OT_toggle_dimensions,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
