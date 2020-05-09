import bpy
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinet_parts
from . import data_cabinet_carcass
from . import data_countertops
from . import data_cabinet_doors
from .. import home_builder_utils
import time
import math

class Standard_Cabinet(pc_types.Assembly):
    show_in_library = True
    category_name = "Cabinets"
    prompt_id = "kitchen.cabinet_prompts"
    placement_id = "kitchen.place_cabinet"

    carcass = None
    interior = None
    exterior = None
    splitter = None

    def draw(self):
        start_time = time.time()
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly()
        self.obj_bp["IS_CABINET_BP"] = True
        self.obj_y['IS_MIRROR'] = True
        self.obj_x.location.x = pc_unit.inch(18) 
        self.obj_y.location.y = -props.base_cabinet_depth
        self.obj_z.location.z = props.base_cabinet_height

        ctop_front = self.add_prompt("Countertop Overhang Front",'DISTANCE',pc_unit.inch(1))
        ctop_back = self.add_prompt("Countertop Overhang Back",'DISTANCE',pc_unit.inch(0))
        ctop_left = self.add_prompt("Countertop Overhang Left",'DISTANCE',pc_unit.inch(0))
        ctop_right = self.add_prompt("Countertop Overhang Right",'DISTANCE',pc_unit.inch(0))        

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        ctop_overhang_front = ctop_front.get_var('ctop_overhang_front')
        ctop_overhang_back = ctop_back.get_var('ctop_overhang_back')
        ctop_overhang_left = ctop_left.get_var('ctop_overhang_left')
        ctop_overhang_right = ctop_right.get_var('ctop_overhang_right')

        carcass = self.add_assembly(self.carcass)
        carcass.set_name('Carcass')
        carcass.loc_x(value=0)
        carcass.loc_y(value=0)
        carcass.loc_z(value=0)
        carcass.dim_x('width',[width])
        carcass.dim_y('depth',[depth])
        carcass.dim_z('height',[height])       

        material_thickness = carcass.get_prompt('Material Thickness').get_var('material_thickness')
        toe_kick_height = carcass.get_prompt('Toe Kick Height').get_var('toe_kick_height')

        if carcass.carcass_type in {'Base','Suspended','Sink'}:
            countertop = self.add_assembly(data_countertops.Countertop())
            countertop.set_name('Countertop')
            countertop.loc_x('-ctop_overhang_left',[ctop_overhang_left])
            countertop.loc_y('ctop_overhang_back',[ctop_overhang_back])
            countertop.loc_z('height',[height])
            countertop.dim_x('width+ctop_overhang_left+ctop_overhang_right',[width,ctop_overhang_left,ctop_overhang_right])
            countertop.dim_y('depth-(ctop_overhang_front+ctop_overhang_back)',[depth,ctop_overhang_front,ctop_overhang_back])
            countertop.dim_z(value=.1)

        if self.exterior:
            exterior = self.add_assembly(self.exterior)
            exterior.loc_x('material_thickness',[material_thickness])
            exterior.loc_y('depth',[depth])
            exterior.loc_z('toe_kick_height+material_thickness',[toe_kick_height,material_thickness])
            exterior.dim_x('width-(material_thickness*2)',[width,material_thickness])
            exterior.dim_y('depth',[depth])
            exterior.dim_z('height-toe_kick_height-(material_thickness*2)',[height,toe_kick_height,material_thickness])

        if self.interior:
            exterior = self.add_assembly(self.interior)
            exterior.loc_x('material_thickness',[material_thickness])
            exterior.loc_y('depth',[depth])
            exterior.loc_z('toe_kick_height+material_thickness',[toe_kick_height,material_thickness])
            exterior.dim_x('width-(material_thickness*2)',[width,material_thickness])
            exterior.dim_y('depth',[depth])
            exterior.dim_z('height-toe_kick_height-(material_thickness*2)',[height,toe_kick_height,material_thickness])

        print("Test_Cabinet: Draw Time --- %s seconds ---" % (time.time() - start_time))