import bpy
import os
from .pc_lib import pc_types, pc_unit, pc_utils, pc_pointer_utils
from . import home_builder_utils

def get_default_material_pointers():
    pointers = []
    #CABINETS
    pointers.append(("Wood Core Surfaces","Wood","PB Small"))
    pointers.append(("Wood Core Edges","Wood","PB Small"))
    pointers.append(("Exposed Cabinet Surfaces","Wood","Autumn Leaves"))
    pointers.append(("Exposed Cabinet Edges","Wood","Autumn Leaves"))
    pointers.append(("Interior Cabinet Surfaces","Wood","Autumn Leaves"))
    pointers.append(("Interior Cabinet Edges","Wood","Autumn Leaves"))
    pointers.append(("Cabinet Lighting","Lighting","Under Cabinet Lighting"))
    pointers.append(("Door Surface","Wood","Autumn Leaves"))
    pointers.append(("Door Edge","Wood","Autumn Leaves"))
    pointers.append(("Countertop Surface","Stone","Midnight Granite"))
    pointers.append(("Drawer Box Surface","Wood","Autumn Leaves"))
    pointers.append(("Drawer Box Edge","Wood","Autumn Leaves"))
    pointers.append(("Pull Finish","Metal","Polished Chrome"))
    pointers.append(("Molding","Wood","Autumn Leaves"))

    #MISC
    pointers.append(("Glass","Misc","Glass"))
    pointers.append(("Shelf Holes","Misc","Machining"))

    #WALLS FLOOR
    pointers.append(("Walls","Wall Paint","Textured Paint Cream"))
    pointers.append(("Lumber","Wood","Wooden Fine Light 2"))
    pointers.append(("Bricks","Stone","Red Brick"))
    pointers.append(("Morter","Concrete","Concrete Plain Ground 2"))
    pointers.append(("Floor","Wood Flooring","Provincial Oak Hardwood"))

    #DOORS
    pointers.append(("Entry Doors","Wood","Painted Wood White"))
    pointers.append(("Entry Door Frame","Wood","Painted Wood White"))
    pointers.append(("Entry Door Panels","Wood","Painted Wood White"))
    pointers.append(("Entry Door Handle","Metal","Polished Chrome"))

    return pointers

def get_default_pull_pointers():
    pointers = []
    pointers.append(("Base Cabinet Pulls","Decorative Pulls","Americana Handle"))
    pointers.append(("Tall Cabinet Pulls","Decorative Pulls","Americana Handle"))
    pointers.append(("Upper Cabinet Pulls","Decorative Pulls","Americana Handle"))
    pointers.append(("Drawer Pulls","Decorative Pulls","Americana Handle"))
    return pointers

def get_default_cabinet_door_pointers():
    pointers = []
    pointers.append(("Base Cabinet Doors","Generic","Slab"))
    pointers.append(("Tall Cabinet Doors","Generic","Slab"))
    pointers.append(("Upper Cabinet Doors","Generic","Slab"))
    pointers.append(("Drawer Fronts","Generic","Slab"))
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
        if index <= len(obj.material_slots) and pointer.pointer_name in props.material_pointers:
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
                        pointer.pointer_name = "Exposed Cabinet Surfaces" 
                    else:
                        pointer.pointer_name = "Wood Core Surfaces"
                if pointer.name == 'L1':
                    if is_finished_back:
                        pointer.pointer_name = "Exposed Cabinet Edges" 
                    else:
                        pointer.pointer_name = "Wood Core Edges"          
                if pointer.name == 'W1':
                    if is_finished_bottom:
                        pointer.pointer_name = "Exposed Cabinet Edges" 
                    else:
                        pointer.pointer_name = "Wood Core Edges"     
                if pointer.name == 'W2':
                    if is_finished_top:
                        pointer.pointer_name = "Exposed Cabinet Edges" 
                    else:
                        pointer.pointer_name = "Wood Core Edges"    
    assign_materials_to_assembly(assembly)

def update_top_material(assembly,is_finished_back,is_finished_top):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Bottom':
                    if is_finished_top:
                        pointer.pointer_name = "Exposed Cabinet Surfaces" 
                    else:
                        pointer.pointer_name = "Wood Core Surfaces"
                if pointer.name == 'L1':
                    if is_finished_back:
                        pointer.pointer_name = "Exposed Cabinet Edges" 
                    else:
                        pointer.pointer_name = "Wood Core Edges"           
    assign_materials_to_assembly(assembly)

def update_bottom_material(assembly,is_finished_back,is_finished_bottom):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Bottom':
                    if is_finished_bottom:
                        pointer.pointer_name = "Exposed Cabinet Surfaces" 
                    else:
                        pointer.pointer_name = "Wood Core Surfaces"
                if pointer.name == 'L1':
                    if is_finished_back:
                        pointer.pointer_name = "Exposed Cabinet Edges" 
                    else:
                        pointer.pointer_name = "Wood Core Edges"           
    assign_materials_to_assembly(assembly)

def update_cabinet_back_material(assembly,is_finished_back):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Bottom':
                    if is_finished_back:
                        pointer.pointer_name = "Exposed Cabinet Surfaces" 
                    else:
                        pointer.pointer_name = "Wood Core Surfaces"
                    break
    assign_materials_to_assembly(assembly)

def assign_carcass_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Interior Cabinet Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Wood Core Surfaces"
                if pointer.name == 'L1':
                    pointer.pointer_name = "Wood Core Edges"
                if pointer.name == 'L2':
                    pointer.pointer_name = "Exposed Cabinet Edges"
                if pointer.name == 'W1':
                    pointer.pointer_name = "Wood Core Edges"
                if pointer.name == 'W2':
                    pointer.pointer_name = "Wood Core Edges"     

def assign_carcass_bottom_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Interior Cabinet Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Exposed Cabinet Surfaces"
                if pointer.name == 'L1':
                    pointer.pointer_name = "Wood Core Edges"
                if pointer.name == 'L2':
                    pointer.pointer_name = "Exposed Cabinet Edges"
                if pointer.name == 'W1':
                    pointer.pointer_name = "Wood Core Edges"
                if pointer.name == 'W2':
                    pointer.pointer_name = "Wood Core Edges"    

def assign_door_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Door Surface"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Door Surface"
                if pointer.name == 'L1':
                    pointer.pointer_name = "Door Edge"
                if pointer.name == 'L2':
                    pointer.pointer_name = "Door Edge"
                if pointer.name == 'W1':
                    pointer.pointer_name = "Door Edge"
                if pointer.name == 'W2':
                    pointer.pointer_name = "Door Edge"

def assign_cabinet_shelf_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Interior Cabinet Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Interior Cabinet Surfaces"
                if pointer.name == 'L1':
                    pointer.pointer_name = "Interior Cabinet Edges"
                if pointer.name == 'L2':
                    pointer.pointer_name = "Interior Cabinet Edges"
                if pointer.name == 'W1':
                    pointer.pointer_name = "Interior Cabinet Edges"
                if pointer.name == 'W2':
                    pointer.pointer_name = "Interior Cabinet Edges"         

def assign_double_sided_pointers(assembly):
    for child in assembly.obj_bp.children:
        if child.type == 'MESH':
            for pointer in child.pyclone.pointers:
                if pointer.name == 'Top':
                    pointer.pointer_name = "Exposed Cabinet Surfaces"
                if pointer.name == 'Bottom':
                    pointer.pointer_name = "Exposed Cabinet Surfaces"
                if pointer.name == 'L1':
                    pointer.pointer_name = "Exposed Cabinet Edges"
                if pointer.name == 'L2':
                    pointer.pointer_name = "Exposed Cabinet Edges"
                if pointer.name == 'W1':
                    pointer.pointer_name = "Exposed Cabinet Edges"
                if pointer.name == 'W2':
                    pointer.pointer_name = "Exposed Cabinet Edges"