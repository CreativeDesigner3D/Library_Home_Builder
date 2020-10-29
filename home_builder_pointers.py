import bpy
import os
from .pc_lib import pc_types, pc_unit, pc_utils, pc_pointer_utils
from . import home_builder_utils

def get_default_material_pointers():
    pointers = []
    #CABINETS
    pointers.append(("Cabinet Unfinished Surfaces","_Sample","Particle Board"))
    pointers.append(("Cabinet Unfinished Edges","_Sample","Particle Board"))
    pointers.append(("Cabinet Exposed Surfaces","_Sample","Dark Wood"))
    pointers.append(("Cabinet Exposed Edges","_Sample","Dark Wood"))
    pointers.append(("Cabinet Interior Surfaces","_Sample","Dark Wood"))
    pointers.append(("Cabinet Interior Edges","_Sample","Dark Wood"))
    pointers.append(("Cabinet Door Surfaces","_Sample","Dark Wood"))
    pointers.append(("Cabinet Door Edges","_Sample","Dark Wood"))
    pointers.append(("Cabinet Pull Finish","_Sample","Polished Chrome"))
    pointers.append(("Countertop Surface","_Sample","Midnight Granite"))

    #MISC
    pointers.append(("Glass","_Sample","Glass"))
    pointers.append(("Shelf Holes","_Sample","Machining"))

    #WALLS FLOOR
    pointers.append(("Walls","_Sample","Wall Paint"))
    pointers.append(("Lumber","_Sample","Plywood"))
    pointers.append(("Bricks","_Sample","Red Brick"))
    pointers.append(("Morter","_Sample","Concrete"))
    pointers.append(("Floor","_Sample","Provincial Oak Hardwood"))

    #DOORS WINDOWS
    pointers.append(("Entry Door Frame","_Sample","Painted Wood White"))
    pointers.append(("Entry Door Panels","_Sample","Painted Wood White"))
    pointers.append(("Entry Door Handle","_Sample","Polished Chrome"))
    pointers.append(("Window Metal Frame","_Sample","Polished Chrome"))

    return pointers

def get_default_pull_pointers():
    pointers = []
    pointers.append(("Base Cabinet Pulls","_Sample","Pull 8in (203mm) Bar"))
    pointers.append(("Tall Cabinet Pulls","_Sample","Pull 8in (203mm) Bar"))
    pointers.append(("Upper Cabinet Pulls","_Sample","Pull 8in (203mm) Bar"))
    pointers.append(("Drawer Pulls","_Sample","Pull 8in (203mm) Bar"))
    return pointers

def get_default_cabinet_door_pointers():
    pointers = []
    pointers.append(("Base Cabinet Doors","_Sample","Slab"))
    pointers.append(("Tall Cabinet Doors","_Sample","Slab"))
    pointers.append(("Upper Cabinet Doors","_Sample","Slab"))
    pointers.append(("Drawer Fronts","_Sample","Slab"))
    return pointers

def get_material_pointer_xml_path():
    path = os.path.join(os.path.dirname(__file__),'pointers')
    return os.path.join(path,"material_pointers.xml")

def get_pull_pointer_xml_path():
    path = os.path.join(os.path.dirname(__file__),'pointers')
    return os.path.join(path,"pull_pointers.xml")

def get_cabinet_door_pointer_xml_path():
    path = os.path.join(os.path.dirname(__file__),'pointers')
    return os.path.join(path,"cabinet_door_pointers.xml")

def write_pointer_files():
    pc_pointer_utils.write_xml_file(get_material_pointer_xml_path(),
                                    get_default_material_pointers())
    pc_pointer_utils.write_xml_file(get_pull_pointer_xml_path(),
                                    get_default_pull_pointers())
    pc_pointer_utils.write_xml_file(get_cabinet_door_pointer_xml_path(),
                                    get_default_cabinet_door_pointers())

def update_pointer_properties():
    props = home_builder_utils.get_scene_props(bpy.context.scene)
    pc_pointer_utils.update_props_from_xml_file(get_material_pointer_xml_path(),
                                                props.material_pointers)
    pc_pointer_utils.update_props_from_xml_file(get_pull_pointer_xml_path(),
                                                props.pull_pointers)    
    pc_pointer_utils.update_props_from_xml_file(get_cabinet_door_pointer_xml_path(),
                                                props.cabinet_door_pointers)                                                    

def assign_pointer_to_object(obj,pointer_name):
    if len(obj.pyclone.pointers) == 0:
        bpy.ops.pc_material.add_material_slot(object_name=obj.name)    
    for index, pointer in enumerate(obj.pyclone.pointers):  
        pointer.pointer_name = pointer_name  
    assign_materials_to_object(obj)  

def assign_pointer_to_assembly(assembly,pointer_name):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            assign_pointer_to_object(child,pointer_name)

def assign_materials_to_object(obj):
    props = home_builder_utils.get_scene_props(bpy.context.scene)
    for index, pointer in enumerate(obj.pyclone.pointers):
        if index + 1 <= len(obj.material_slots) and pointer.pointer_name in props.material_pointers:
            p = props.material_pointers[pointer.pointer_name]
            slot = obj.material_slots[index]
            slot.material = home_builder_utils.get_material(p.category,p.item_name)
            
def assign_materials_to_assembly(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            assign_materials_to_object(child)

def update_side_material(assembly,is_finished_end,is_finished_back,is_finished_top,is_finished_bottom):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Bottom':
                    if is_finished_end:
                        pointer.pointer_name = "Cabinet Exposed Surfaces" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces"
                if pointer.name == 'L1':
                    if is_finished_back:
                        pointer.pointer_name = "Cabinet Exposed Edges" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Edges"          
                if pointer.name == 'W1':
                    if is_finished_bottom:
                        pointer.pointer_name = "Cabinet Exposed Edges" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Edges"     
                if pointer.name == 'W2':
                    if is_finished_top:
                        pointer.pointer_name = "Cabinet Exposed Edges" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Edges"    
    assign_materials_to_assembly(assembly)

def update_top_material(assembly,is_finished_back,is_finished_top):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Bottom':
                    if is_finished_top:
                        pointer.pointer_name = "Cabinet Exposed Surfaces" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces"
                if pointer.name == 'L1':
                    if is_finished_back:
                        pointer.pointer_name = "Cabinet Exposed Edges" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Edges"           
    assign_materials_to_assembly(assembly)

def update_bottom_material(assembly,is_finished_back,is_finished_bottom):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Bottom':
                    if is_finished_bottom:
                        pointer.pointer_name = "Cabinet Exposed Surfaces" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces"
                if pointer.name == 'L1':
                    if is_finished_back:
                        pointer.pointer_name = "Cabinet Exposed Edges" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Edges"           
    assign_materials_to_assembly(assembly)

def update_cabinet_back_material(assembly,is_finished_back):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Bottom':
                    if is_finished_back:
                        pointer.pointer_name = "Cabinet Exposed Surfaces" 
                    else:
                        pointer.pointer_name = "Cabinet Unfinished Surfaces"
                    break
    assign_materials_to_assembly(assembly)

def assign_carcass_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Cabinet Interior Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Cabinet Unfinished Surfaces"
                if pointer.name == 'L1':
                    pointer.pointer_name = "Cabinet Unfinished Edges"
                if pointer.name == 'L2':
                    pointer.pointer_name = "Cabinet Exposed Edges"
                if pointer.name == 'W1':
                    pointer.pointer_name = "Cabinet Unfinished Edges"
                if pointer.name == 'W2':
                    pointer.pointer_name = "Cabinet Unfinished Edges"     

def assign_carcass_bottom_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Cabinet Interior Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"
                if pointer.name == 'L1':
                    pointer.pointer_name = "Cabinet Unfinished Edges"
                if pointer.name == 'L2':
                    pointer.pointer_name = "Cabinet Exposed Edges"
                if pointer.name == 'W1':
                    pointer.pointer_name = "Cabinet Unfinished Edges"
                if pointer.name == 'W2':
                    pointer.pointer_name = "Cabinet Unfinished Edges"    

def assign_door_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Cabinet Door Surface"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Cabinet Door Surface"
                if pointer.name == 'L1':
                    pointer.pointer_name = "Cabinet Door Edge"
                if pointer.name == 'L2':
                    pointer.pointer_name = "Cabinet Door Edge"
                if pointer.name == 'W1':
                    pointer.pointer_name = "Cabinet Door Edge"
                if pointer.name == 'W2':
                    pointer.pointer_name = "Cabinet Door Edge"

def assign_cabinet_shelf_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Cabinet Interior Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Cabinet Interior Surfaces"
                if pointer.name == 'L1':
                    pointer.pointer_name = "Cabinet Interior Edges"
                if pointer.name == 'L2':
                    pointer.pointer_name = "Cabinet Interior Edges"
                if pointer.name == 'W1':
                    pointer.pointer_name = "Cabinet Interior Edges"
                if pointer.name == 'W2':
                    pointer.pointer_name = "Cabinet Interior Edges"         

def assign_double_sided_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Cabinet Exposed Surfaces"
                if pointer.name == 'L1':
                    pointer.pointer_name = "Cabinet Exposed Edges"
                if pointer.name == 'L2':
                    pointer.pointer_name = "Cabinet Exposed Edges"
                if pointer.name == 'W1':
                    pointer.pointer_name = "Cabinet Exposed Edges"
                if pointer.name == 'W2':
                    pointer.pointer_name = "Cabinet Exposed Edges"