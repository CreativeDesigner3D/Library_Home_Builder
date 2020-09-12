import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinet_parts
from .. import home_builder_utils
from .. import home_builder_pointers
from . import common_prompts
from os import path

def add_cabinet_shelf(assembly):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    height = assembly.obj_z.pyclone.get_var('location.z','height')
    depth = assembly.obj_y.pyclone.get_var('location.y','depth')
    material_thickness = assembly.get_prompt("Material Thickness").get_var("material_thickness")
    shelf_qty = assembly.get_prompt("Shelf Quantity").get_var("shelf_qty")
    shelf_clip_gap = assembly.get_prompt("Shelf Clip Gap").get_var("shelf_clip_gap")
    shelf_setback = assembly.get_prompt("Shelf Setback").get_var("shelf_setback")

    shelf = data_cabinet_parts.add_cabinet_shelf(assembly)
    shelf.set_name('Shelf')
    shelf.loc_x('shelf_clip_gap',[shelf_clip_gap])
    shelf.loc_y('shelf_setback',[shelf_setback])
    shelf.loc_z('(height-(material_thickness*shelf_qty))/(shelf_qty+1)',[height,material_thickness,shelf_qty])
    shelf.dim_x('width-(shelf_clip_gap*2)',[width,shelf_clip_gap])
    shelf.dim_y('depth-shelf_setback',[depth,shelf_setback])
    shelf.dim_z('material_thickness',[material_thickness])
    z_quantity = shelf.get_prompt("Z Quantity")
    z_offset = shelf.get_prompt("Z Offset")
    z_quantity.set_formula('shelf_qty',[shelf_qty])
    z_offset.set_formula('((height-(material_thickness*shelf_qty))/(shelf_qty+1))+material_thickness',[height,material_thickness,shelf_qty])
    return shelf

def add_shelf_holes(assembly):
    width = assembly.obj_x.pyclone.get_var('location.x','width')
    height = assembly.obj_z.pyclone.get_var('location.z','height')
    depth = assembly.obj_y.pyclone.get_var('location.y','depth')

    holes = data_cabinet_parts.add_shelf_holes(assembly)
    holes.dim_x('width',[width])
    holes.dim_y('depth',[depth])
    holes.dim_z('height',[height])    


class Shelves(pc_types.Assembly):

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)    

        self.create_assembly("Shelves")
        self.obj_bp["IS_SHELVES_BP"] = True
        self.obj_bp["IS_INTERIOR_BP"] = True        

        common_prompts.add_cabinet_prompts(self)
        common_prompts.add_thickness_prompts(self)
        common_prompts.add_interior_shelf_prompts(self)

        add_cabinet_shelf(self)
        add_shelf_holes(self)