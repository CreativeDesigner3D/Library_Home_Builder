import bpy
import os
import math
from .pc_lib import pc_types, pc_unit, pc_utils
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

def get_closet_bp(obj):
    if not obj:
        return None    
    if "IS_CLOSET_BP" in obj:
        return obj
    elif obj.parent:
        return get_closet_bp(obj.parent)

def get_opening_bp(obj):
    if not obj:
        return None    
    if "IS_OPENING_BP" in obj:
        return obj
    elif obj.parent:
        return get_opening_bp(obj.parent)

def get_closet_shelves_bp(obj):
    if not obj:
        return None    
    if "IS_SHELVES_INSERT" in obj:
        return obj
    elif obj.parent:
        return get_closet_shelves_bp(obj.parent)

def get_closet_doors_bp(obj):
    if not obj:
        return None    
    if "IS_CLOSET_DOORS_BP" in obj:
        return obj
    elif obj.parent:
        return get_closet_doors_bp(obj.parent)

def get_closet_drawers_bp(obj):
    if not obj:
        return None    
    if "IS_CLOSET_DRAWERS_BP" in obj:
        return obj
    elif obj.parent:
        return get_closet_drawers_bp(obj.parent)

def get_closet_cubby_bp(obj):
    if not obj:
        return None    
    if "IS_CUBBY_INSERT" in obj:
        return obj
    elif obj.parent:
        return get_closet_cubby_bp(obj.parent)

def get_closet_wire_baskets_bp(obj):
    if not obj:
        return None    
    if "IS_WIRE_BASKET_INSERT_BP" in obj:
        return obj
    elif obj.parent:
        return get_closet_wire_baskets_bp(obj.parent)

def get_hanging_rod_insert_bp(obj):
    if not obj:
        return None    
    if "IS_HANGING_RODS_BP" in obj:
        return obj
    elif obj.parent:
        return get_hanging_rod_insert_bp(obj.parent)

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

def get_cabinet_door_bp(obj):
    if not obj:
        return None    
    if "IS_CABINET_DOOR_PANEL" in obj:
        return obj
    elif obj.parent:
        return get_cabinet_door_bp(obj.parent)

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
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0)
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

def assign_current_material_index(obj):
    props = get_scene_props(bpy.context.scene)
    obj_props = get_object_props(obj)
    obj_props.material_group_index = props.material_group_index
    
def update_object_and_children_id_props(obj,parent_obj):
    update_id_props(obj,parent_obj)
    for child in obj.children:
        update_object_and_children_id_props(child,obj)        

def assign_boolean_to_child_assemblies(assembly,bool_obj):
    #TODO: DELETE OLD BOOLEAN MODIFIERS
    bool_obj.hide_viewport = True
    bool_obj.hide_render = True
    bool_obj.display_type = 'WIRE'  
    for child in assembly.obj_bp.children:
        for nchild in child.children:
            if nchild.type == 'MESH':       
                mod = nchild.modifiers.new(bool_obj.name,'BOOLEAN')
                mod.solver ='FAST'
                mod.object = bool_obj
                mod.operation = 'DIFFERENCE'

def replace_assembly(old_assembly,new_assembly):
    copy_drivers(old_assembly.obj_bp,new_assembly.obj_bp)
    copy_drivers(old_assembly.obj_x,new_assembly.obj_x)
    copy_drivers(old_assembly.obj_y,new_assembly.obj_y)
    copy_drivers(old_assembly.obj_z,new_assembly.obj_z)
    copy_drivers(old_assembly.obj_prompts,new_assembly.obj_prompts)
    pc_utils.delete_object_and_children(old_assembly.obj_bp)

def copy_drivers(old_obj,new_obj):
    new_obj.location = old_obj.location
    new_obj.rotation_euler = old_obj.rotation_euler
    if old_obj.animation_data:
        for driver in old_obj.animation_data.drivers:
            newdriver = None
            try:
                newdriver = new_obj.driver_add(driver.data_path,driver.array_index)
            except Exception:
                try:
                    newdriver = new_obj.driver_add(driver.data_path)
                except Exception:
                    print("Unable to Copy Prompt Driver", driver.data_path)
            if newdriver:
                newdriver.driver.expression = driver.driver.expression
                newdriver.driver.type = driver.driver.type
                for var in driver.driver.variables:
                    if var.name not in newdriver.driver.variables:
                        newvar = newdriver.driver.variables.new()
                        newvar.name = var.name
                        newvar.type = var.type
                        for index, target in enumerate(var.targets):
                            newtarget = newvar.targets[index]
                            if target.id is old_obj:
                                newtarget.id = new_obj #CHECK SELF REFERENCE FOR PROMPTS
                            else:
                                newtarget.id = target.id
                            newtarget.transform_space = target.transform_space
                            newtarget.transform_type = target.transform_type
                            newtarget.data_path = target.data_path