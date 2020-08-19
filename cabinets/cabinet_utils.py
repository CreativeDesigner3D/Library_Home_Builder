import bpy
import math
from os import path
from ..pc_lib import pc_types, pc_unit, pc_utils
from .. import home_builder_utils
from . import data_cabinet_parts
from . import common_prompts
from . import data_countertops

def update_id_properties(parent,assembly_to_update):
    pass

def add_exterior_to_cabinet(cabinet,carcass,exterior,cabinet_type):
    width = cabinet.obj_x.pyclone.get_var('location.x','width')
    depth = cabinet.obj_y.pyclone.get_var('location.y','depth')
    height = cabinet.obj_z.pyclone.get_var('location.z','height')
    material_thickness = carcass.get_prompt('Material Thickness').get_var('material_thickness')
    
    exterior = cabinet.add_assembly(exterior)
    exterior.loc_x('material_thickness',[material_thickness])
    exterior.loc_y('depth',[depth])
    if cabinet_type == 2: #UPPER CABINET
        exterior.loc_z('material_thickness',[material_thickness])
        exterior.dim_z('height-(material_thickness*2)',[height,material_thickness])
    else:
        toe_kick_height = carcass.get_prompt('Toe Kick Height').get_var('toe_kick_height')
        exterior.loc_z('toe_kick_height+material_thickness',[toe_kick_height,material_thickness])
        exterior.dim_z('height-toe_kick_height-(material_thickness*2)',[height,toe_kick_height,material_thickness])
    
    exterior.dim_x('width-(material_thickness*2)',[width,material_thickness])
    exterior.dim_y('fabs(depth)',[depth])
    exterior.obj_x.empty_display_size = .001
    exterior.obj_y.empty_display_size = .001
    exterior.obj_z.empty_display_size = .001
    exterior.obj_bp.empty_display_size = .001
    exterior.obj_prompts.empty_display_size = .001

    carcass_cabinet_type = carcass.get_prompt("Cabinet Type")
    exterior_cabinet_type = exterior.get_prompt("Cabinet Type")
    exterior_cabinet_type.set_value(carcass_cabinet_type.get_value())

    bpy.context.view_layer.update()

    calculator = exterior.get_calculator('Front Height Calculator')
    if calculator:
        calculator.calculate()

def add_interior_to_cabinet(cabinet,carcass,interior,cabinet_type):
    width = cabinet.obj_x.pyclone.get_var('location.x','width')
    depth = cabinet.obj_y.pyclone.get_var('location.y','depth')
    height = cabinet.obj_z.pyclone.get_var('location.z','height')
    material_thickness = carcass.get_prompt('Material Thickness').get_var('material_thickness')
    
    interior = cabinet.add_assembly(interior)
    interior.loc_x('material_thickness',[material_thickness])
    interior.loc_y('depth',[depth])
    if cabinet_type == 2: #UPPER CABINET
        interior.loc_z('material_thickness',[material_thickness])
        interior.dim_z('height-(material_thickness*2)',[height,material_thickness])
    else:
        toe_kick_height = carcass.get_prompt('Toe Kick Height').get_var('toe_kick_height')
        interior.loc_z('toe_kick_height+material_thickness',[toe_kick_height,material_thickness])
        interior.dim_z('height-toe_kick_height-(material_thickness*2)',[height,toe_kick_height,material_thickness])
    
    interior.dim_x('width-(material_thickness*2)',[width,material_thickness])
    interior.dim_y('fabs(depth)',[depth])
    interior.obj_x.empty_display_size = .001
    interior.obj_y.empty_display_size = .001
    interior.obj_z.empty_display_size = .001
    interior.obj_bp.empty_display_size = .001
    interior.obj_prompts.empty_display_size = .001

    carcass_cabinet_type = carcass.get_prompt("Cabinet Type")
    interior_cabinet_type = interior.get_prompt("Cabinet Type")
    interior_cabinet_type.set_value(carcass_cabinet_type.get_value())

    bpy.context.view_layer.update()

def add_countertop(cabinet):
    width = cabinet.obj_x.pyclone.get_var('location.x','width')
    depth = cabinet.obj_y.pyclone.get_var('location.y','depth')
    height = cabinet.obj_z.pyclone.get_var('location.z','height')    
    ctop_front = cabinet.add_prompt("Countertop Overhang Front",'DISTANCE',pc_unit.inch(1))
    ctop_back = cabinet.add_prompt("Countertop Overhang Back",'DISTANCE',pc_unit.inch(0))
    ctop_left = cabinet.add_prompt("Countertop Overhang Left",'DISTANCE',pc_unit.inch(0))
    ctop_right = cabinet.add_prompt("Countertop Overhang Right",'DISTANCE',pc_unit.inch(0))      
    ctop_overhang_front = ctop_front.get_var('ctop_overhang_front')
    ctop_overhang_back = ctop_back.get_var('ctop_overhang_back')
    ctop_overhang_left = ctop_left.get_var('ctop_overhang_left')
    ctop_overhang_right = ctop_right.get_var('ctop_overhang_right')

    countertop = cabinet.add_assembly(data_countertops.Countertop())
    countertop.set_name('Countertop')
    countertop.loc_x('-ctop_overhang_left',[ctop_overhang_left])
    countertop.loc_y('ctop_overhang_back',[ctop_overhang_back])
    countertop.loc_z('height',[height])
    countertop.dim_x('width+ctop_overhang_left+ctop_overhang_right',[width,ctop_overhang_left,ctop_overhang_right])
    countertop.dim_y('depth-(ctop_overhang_front+ctop_overhang_back)',[depth,ctop_overhang_front,ctop_overhang_back])

def add_sink(cabinet,carcass,countertop,sink):
    sink = cabinet.add_assembly(sink)
    sink.obj_bp.parent = cabinet.obj_bp

    cabinet_width = cabinet.obj_x.pyclone.get_var('location.x','cabinet_width')
    cabinet_depth = cabinet.obj_y.pyclone.get_var('location.y','cabinet_depth')
    cabinet_height = cabinet.obj_z.pyclone.get_var('location.z','cabinet_height')
    countertop_height = countertop.obj_z.pyclone.get_var('location.z','countertop_height')
    sink_width = sink.obj_x.location.x
    sink_depth = sink.obj_y.location.y

    # carcass.assign_boolean(sink)
    # countertop.assign_boolean(sink)

    sink.loc_x('(cabinet_width/2)-' + str(sink_width/2),[cabinet_width])
    sink.loc_y('(cabinet_depth/2)-' + str(sink_depth/2),[cabinet_depth])
    sink.loc_z('cabinet_height+countertop_height',[cabinet_height,countertop_height])