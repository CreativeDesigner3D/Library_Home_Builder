from ..pc_lib import pc_types, pc_unit, pc_utils
from .. import home_builder_utils
from .. import home_builder_pointers
from .. import home_builder_paths
from os import path


def add_closet_part(assembly):
    part_path = path.join(home_builder_paths.get_cabinet_parts_path(),"Cutparts","Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_CUTPART_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    home_builder_utils.add_bevel(part)
    home_builder_pointers.assign_double_sided_pointers(part)
    home_builder_pointers.assign_materials_to_assembly(part)
    return part

def add_closet_array_part(assembly):
    part_path = path.join(home_builder_paths.get_cabinet_parts_path(),"Cutparts","Z Array Part.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_CUTPART_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    home_builder_utils.add_bevel(part)
    home_builder_pointers.assign_double_sided_pointers(part)
    home_builder_pointers.assign_materials_to_assembly(part)
    return part

def add_closet_hangers(assembly):
    part_path = path.join(home_builder_paths.get_cabinet_parts_path(),"Closets","Hangers.blend")
    if path.exists(part_path):
        part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
        part.obj_bp['IS_HANGERS_BP'] = True
        assembly.add_assembly(part)
        part.obj_bp.empty_display_size = .001
        part.obj_x.empty_display_size = .001
        part.obj_y.empty_display_size = .001
        part.obj_z.empty_display_size = .001
        part.obj_prompts.empty_display_size = .001    
        home_builder_utils.add_bevel(part)
        return part    

def add_closet_wire_basket(assembly):
    part_path = path.join(home_builder_paths.get_cabinet_parts_path(),"Closets","Wire Basket.blend")
    if path.exists(part_path):
        part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
        part.obj_bp['IS_WIRE_BASKET_BP'] = True
        assembly.add_assembly(part)
        part.obj_bp.empty_display_size = .001
        part.obj_x.empty_display_size = .001
        part.obj_y.empty_display_size = .001
        part.obj_z.empty_display_size = .001
        part.obj_prompts.empty_display_size = .001    
        # home_builder_utils.add_bevel(part)
        return part    

def add_closet_oval_hanging_rod(assembly):
    part_path = path.join(home_builder_paths.get_cabinet_parts_path(),"Closets","Oval Hanging Rod.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_HANGING_ROD_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    home_builder_utils.add_bevel(part)
    home_builder_pointers.assign_hanging_rods_pointers(part)
    home_builder_pointers.assign_materials_to_assembly(part)
    return part

def add_closet_opening(assembly):
    part_path = path.join(home_builder_paths.get_cabinet_parts_path(),"Opening","Opening.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp['IS_OPENING_BP'] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001  
    for child in part.obj_bp.children:
        if child.type == 'MESH':
            child['IS_OPENING_MESH'] = True
    # home_builder_utils.add_bevel(part)
    return part    

def add_closet_reference(assembly):
    part_path = path.join(home_builder_paths.get_cabinet_parts_path(),"Opening","Opening.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    part.obj_bp["IS_REFERENCE"] = True
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001    
    # home_builder_utils.add_bevel(part)
    return part   

def add_door_part(assembly,pointer):
    part_path = home_builder_paths.get_cabinet_door_panel_path(pointer)
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    assembly.add_assembly(part)
    part.obj_bp["IS_CABINET_DOOR_PANEL"] = True
    part.obj_bp["IS_CUTPART_BP"] = True
    props = home_builder_utils.get_object_props(part.obj_bp)
    props.pointer_name = pointer.name
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001
    home_builder_pointers.assign_materials_to_assembly(part)
    return part    

def add_shelf_holes(assembly):
    part_path = path.join(home_builder_paths.get_cabinet_parts_path(),"Machining","Shelf Holes.blend")
    part = pc_types.Assembly(assembly.add_assembly_from_file(part_path))
    assembly.add_assembly(part)
    part.obj_bp.empty_display_size = .001
    part.obj_x.empty_display_size = .001
    part.obj_y.empty_display_size = .001
    part.obj_z.empty_display_size = .001
    part.obj_prompts.empty_display_size = .001   
    home_builder_pointers.assign_pointer_to_assembly(part,"Shelf Holes")
    return part    