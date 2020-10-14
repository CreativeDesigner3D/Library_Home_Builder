import bpy
import os
import math
from .pc_lib import pc_types, pc_unit, pc_utils, pc_pointer_utils
from . import home_builder_paths

def get_preferences(context):
    preferences = context.preferences
    return preferences.addons[__name__].preferences

def get_object_props(obj):
    return obj.home_builder

def get_scene_props(scene):
    return scene.home_builder

def get_wm_props(wm):
    return wm.home_builder

def get_wall_bp(obj):
    if not obj:
        return None
    if "IS_WALL_BP" in obj:
        return obj
    elif obj.parent:
        return get_wall_bp(obj.parent)

def get_room_bp(obj):
    if not obj:
        return None    
    if "IS_ROOM_BP" in obj:
        return obj
    elif obj.parent:
        return get_room_bp(obj.parent)

def get_cabinet_bp(obj):
    if not obj:
        return None    
    if "IS_CABINET_BP" in obj:
        return obj
    elif obj.parent:
        return get_cabinet_bp(obj.parent)

def get_carcass_bp(obj):
    if not obj:
        return None    
    if "IS_CARCASS_BP" in obj:
        return obj
    elif obj.parent:
        return get_carcass_bp(obj.parent)

def get_appliance_bp(obj):
    if not obj:
        return None    
    if "IS_APPLIANCE_BP" in obj:
        return obj
    elif obj.parent:
        return get_appliance_bp(obj.parent)

def get_range_bp(obj):
    if not obj:
        return None    
    if "IS_RANGE_BP" in obj:
        return obj
    elif obj.parent:
        return get_range_bp(obj.parent)

def get_door_bp(obj):
    if not obj:
        return None    
    if "IS_DOOR_BP" in obj:
        return obj
    elif obj.parent:
        return get_door_bp(obj.parent)

def get_window_bp(obj):
    if not obj:
        return None    
    if "IS_WINDOW_BP" in obj:
        return obj
    elif obj.parent:
        return get_window_bp(obj.parent)

def get_exterior_bp(obj):
    if not obj:
        return None    
    if "IS_EXTERIOR_BP" in obj:
        return obj
    elif obj.parent:
        return get_exterior_bp(obj.parent)

def get_material(category,material_name):
    if material_name in bpy.data.materials:
        return bpy.data.materials[material_name]

    material_path = os.path.join(home_builder_paths.get_material_path(),category,material_name + ".blend")
    
    if os.path.exists(material_path):

        with bpy.data.libraries.load(material_path, False, False) as (data_from, data_to):
            for mat in data_from.materials:
                if mat == material_name:
                    data_to.materials = [mat]
                    break    
        
        for mat in data_to.materials:
            return mat
            
def get_object(path):
    if os.path.exists(path):

        with bpy.data.libraries.load(path, False, False) as (data_from, data_to):
            data_to.objects = data_from.objects 
        
        for obj in data_to.objects:
            return obj

def flip_normals(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for polygon in child.data.polygons:
                polygon.flip()
            child.data.update()

def apply_hook_modifiers(context,obj):
    context.view_layer.objects.active = obj
    for mod in obj.modifiers:
        if mod.type == 'HOOK':
            bpy.ops.object.modifier_apply(modifier=mod.name)            

def unwrap_obj(context,obj):
    context.view_layer.objects.active = obj
    apply_hook_modifiers(context,obj)       

    mode = obj.mode
    if obj.mode == 'OBJECT':
        bpy.ops.object.editmode_toggle()
        
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0, user_area_weight=0)
    if mode == 'OBJECT':
        bpy.ops.object.editmode_toggle()

    bpy.ops.pc_assembly.connect_meshes_to_hooks_in_assembly(obj_name = obj.name)

def add_bevel(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            bevel = child.modifiers.new('Bevel','BEVEL')    
            bevel.width = .0005

def hide_empties(obj):
    if obj.type == 'EMPTY':
        obj.hide_viewport = True
    for child in obj.children:
        hide_empties(child)    

def update_assembly_id_props(assembly,parent_assembly):
    for child in assembly.obj_bp.children:
        update_id_props(child,parent_assembly.obj_bp)

def update_id_props(obj,parent_obj):
    if "PROMPT_ID" in parent_obj:
        obj["PROMPT_ID"] = parent_obj["PROMPT_ID"]
    if "MENU_ID" in parent_obj:
        obj["MENU_ID"] = parent_obj["MENU_ID"]   

def update_object_and_children_id_props(obj,parent_obj):
    update_id_props(obj,parent_obj)
    for child in obj.children:
        update_object_and_children_id_props(child,obj)        