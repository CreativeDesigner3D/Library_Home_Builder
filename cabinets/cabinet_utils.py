import bpy
import math
from os import path
from ..pc_lib import pc_types, pc_unit, pc_utils
from .. import home_builder_utils
from . import data_cabinet_parts
from . import common_prompts

def update_id_properties(parent,assembly_to_update):
    pass

def add_exterior_to_cabinet(cabinet,carcass,exterior):
    width = cabinet.obj_x.pyclone.get_var('location.x','width')
    depth = cabinet.obj_y.pyclone.get_var('location.y','depth')
    height = cabinet.obj_z.pyclone.get_var('location.z','height')

    material_thickness = carcass.get_prompt('Material Thickness').get_var('material_thickness')
    toe_kick_height = carcass.get_prompt('Toe Kick Height').get_var('toe_kick_height')

    exterior = cabinet.add_assembly(exterior)
    exterior.loc_x('material_thickness',[material_thickness])
    exterior.loc_y('depth',[depth])
    exterior.loc_z('toe_kick_height+material_thickness',[toe_kick_height,material_thickness])
    exterior.dim_x('width-(material_thickness*2)',[width,material_thickness])
    exterior.dim_y('fabs(depth)',[depth])
    exterior.dim_z('height-toe_kick_height-(material_thickness*2)',[height,toe_kick_height,material_thickness])
    exterior.obj_x.empty_display_size = .001
    exterior.obj_y.empty_display_size = .001
    exterior.obj_z.empty_display_size = .001
    exterior.obj_bp.empty_display_size = .001
    exterior.obj_prompts.empty_display_size = .001

    bpy.context.view_layer.update()

    calculator = exterior.get_calculator('Front Height Calculator')
    if calculator:
        calculator.calculate()