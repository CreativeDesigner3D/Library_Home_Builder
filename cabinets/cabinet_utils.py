import bpy
import math
from os import path
from ..pc_lib import pc_types, pc_unit, pc_utils
from .. import home_builder_utils
from . import data_cabinet_parts
from . import data_cabinet_exteriors
from . import common_prompts
from . import data_countertops

def get_exterior_from_name(name):
    exterior = None
    if name == 'DOORS':
        exterior = data_cabinet_exteriors.Doors()
    elif name == '2_DOOR_2_DRAWER':
        exterior = data_cabinet_exteriors.Doors()             
    elif name == '1_DOOR_1_DRAWER':
        exterior = data_cabinet_exteriors.Doors()           
    elif name == '2_DOOR_1_DRAWER':
        exterior = data_cabinet_exteriors.Doors()       
    elif name == 'SLIDING_DOORS':
        exterior = data_cabinet_exteriors.Doors()                                                   
    elif name == 'DRAWERS':
        exterior = data_cabinet_exteriors.Drawers()
    return exterior

def add_sink(cabinet,carcass,countertop,sink):
    sink = cabinet.add_assembly(sink)
    sink.obj_bp.parent = cabinet.obj_bp

    cabinet_width = cabinet.obj_x.pyclone.get_var('location.x','cabinet_width')
    cabinet_depth = cabinet.obj_y.pyclone.get_var('location.y','cabinet_depth')
    cabinet_height = cabinet.obj_z.pyclone.get_var('location.z','cabinet_height')
    countertop_height = countertop.obj_z.pyclone.get_var('location.z','countertop_height')
    sink_width = sink.obj_x.location.x
    sink_depth = sink.obj_y.location.y

    sink.loc_x('(cabinet_width/2)-' + str(sink_width/2),[cabinet_width])
    sink.loc_y('(cabinet_depth/2)-' + str(sink_depth/2),[cabinet_depth])
    sink.loc_z('cabinet_height+countertop_height',[cabinet_height,countertop_height])

def add_cooktop(cabinet,carcass,countertop,cooktop):
    cooktop = cabinet.add_assembly(cooktop)
    cooktop.obj_bp.parent = cabinet.obj_bp

    cabinet_width = cabinet.obj_x.pyclone.get_var('location.x','cabinet_width')
    cabinet_depth = cabinet.obj_y.pyclone.get_var('location.y','cabinet_depth')
    cabinet_height = cabinet.obj_z.pyclone.get_var('location.z','cabinet_height')
    countertop_height = countertop.obj_z.pyclone.get_var('location.z','countertop_height')
    cooktop_width = cooktop.obj_x.location.x
    cooktop_depth = cooktop.obj_y.location.y

    cooktop.loc_x('(cabinet_width/2)-' + str(cooktop_width/2),[cabinet_width])
    cooktop.loc_y('(cabinet_depth/2)-' + str(cooktop_depth/2),[cabinet_depth])
    cooktop.loc_z('cabinet_height+countertop_height',[cabinet_height,countertop_height])