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
    home_builder_utils.add_bevel(part)
    return part    