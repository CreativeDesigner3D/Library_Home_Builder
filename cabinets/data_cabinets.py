import bpy
from os import path
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import common_prompts
from . import data_cabinet_parts
from . import data_cabinet_carcass
from . import data_countertops
from . import cabinet_utils
from .. import home_builder_utils
from .. import home_builder_pointers
from .. import home_builder_paths
import time
import math

def get_sink(category,assembly_name):
    ASSET_DIR = home_builder_paths.get_sink_path()
    if assembly_name == "":
        return path.join(ASSET_DIR,"Generic","Generic Sink.blend")  
    else:
        return path.join(ASSET_DIR, category, assembly_name + ".blend")

def get_faucet(category,assembly_name):
    ASSET_DIR = home_builder_paths.get_faucet_path()
    if assembly_name == "":
        return path.join(ASSET_DIR,"Generic","Generic Faucet.blend")  
    else:
        return path.join(ASSET_DIR, category, assembly_name + ".blend")

def get_cooktop(category,assembly_name):
    ASSET_DIR = home_builder_paths.get_cooktop_path()
    if assembly_name == "":
        return path.join(ASSET_DIR,"Generic","Generic Cooktop.blend")  
    else:
        return path.join(ASSET_DIR, category, assembly_name + ".blend")

def get_range_hood(category,assembly_name):
    ASSET_DIR = home_builder_paths.get_range_hood_path()
    if assembly_name == "":
        return path.join(ASSET_DIR,"Generic","Generic Range Hood.blend")  
    else:
        return path.join(ASSET_DIR, category, assembly_name + ".blend")   

class Cabinet(pc_types.Assembly):

    left_filler = None
    right_filler = None
    countertop = None
    sink_appliance = None
    faucet_appliance = None
    cooktop_appliance = None
    range_hood_appliance = None
    carcasses = []

    def __init__(self,obj_bp=None):
        super().__init__(obj_bp=obj_bp)  
        self.carcasses = []
        if obj_bp:
            for child in obj_bp.children:
                if "IS_LEFT_FILLER_BP" in child:
                    self.left_filler = pc_types.Assembly(child)
                if "IS_RIGHT_FILLER_BP" in child:
                    self.right_filler = pc_types.Assembly(child)     
                if "IS_COUNTERTOP_BP" in child:
                    self.countertop = pc_types.Assembly(child)     
                if "IS_SINK_BP" in child:
                    self.sink_appliance = pc_types.Assembly(child)  
                    for sink_child in self.sink_appliance.obj_bp.children:
                        if "IS_FAUCET_BP" in sink_child:
                            for faucet_child in sink_child.children:
                                self.faucet_appliance = faucet_child
                if "IS_COOKTOP_BP" in child:
                    self.cooktop_appliance = pc_types.Assembly(child)    
                if "IS_RANGE_HOOD_BP" in child:
                    self.range_hood_appliance = pc_types.Assembly(child)                                                                                                   
                if "IS_CARCASS_BP" in child:
                    carcass = data_cabinet_carcass.Carcass(child)
                    self.carcasses.append(carcass)

    def update_range_hood_location(self):
        if self.range_hood_appliance:
            self.range_hood_appliance.obj_bp.location.x = (self.obj_x.location.x/2) - (self.range_hood_appliance.obj_x.location.x)/2
            self.range_hood_appliance.obj_bp.location.z = pc_unit.inch(70)

    def add_sink(self,category="",assembly_name=""):
        self.sink_appliance = pc_types.Assembly(self.add_assembly_from_file(get_sink(category,assembly_name)))
        self.sink_appliance.obj_bp["IS_SINK_BP"] = True

        cabinet_width = self.obj_x.pyclone.get_var('location.x','cabinet_width')
        cabinet_depth = self.obj_y.pyclone.get_var('location.y','cabinet_depth')
        cabinet_height = self.obj_z.pyclone.get_var('location.z','cabinet_height')
        countertop_height = self.countertop.obj_z.pyclone.get_var('location.z','countertop_height')
        sink_width = self.sink_appliance.obj_x.location.x
        sink_depth = self.sink_appliance.obj_y.location.y

        self.sink_appliance.loc_x('(cabinet_width/2)-' + str(sink_width/2),[cabinet_width])
        self.sink_appliance.loc_y('(cabinet_depth/2)-' + str(sink_depth/2),[cabinet_depth])
        self.sink_appliance.loc_z('cabinet_height+countertop_height',[cabinet_height,countertop_height])

        for child in self.sink_appliance.obj_bp.children:
            if child.hide_render:
                child.hide_viewport = True
            if child.type == 'MESH':   
                if 'IS_BOOLEAN' in child and child['IS_BOOLEAN'] == True:   
                    bool_obj = child
                    break

        home_builder_utils.assign_boolean_to_child_assemblies(self.countertop,bool_obj)
        for carcass in self.carcasses:
            home_builder_utils.assign_boolean_to_child_assemblies(carcass,bool_obj)

        home_builder_utils.update_assembly_id_props(self.sink_appliance,self)

    def add_faucet(self,category="",object_name=""):
        if self.sink_appliance:
            self.faucet_appliance = self.add_object_from_file(get_faucet(category,object_name))
            self.faucet_appliance["IS_FAUCET"] = True

            faucet_bp = None

            for child in self.sink_appliance.obj_bp.children:
                if "IS_FAUCET_BP" in child and child["IS_FAUCET_BP"]:
                    faucet_bp = child

            self.faucet_appliance.parent = faucet_bp

    def add_cooktop(self,category="",assembly_name=""):
        self.cooktop_appliance = pc_types.Assembly(self.add_assembly_from_file(get_cooktop(category,assembly_name)))
        self.cooktop_appliance.obj_bp["IS_COOKTOP_BP"] = True

        cabinet_width = self.obj_x.pyclone.get_var('location.x','cabinet_width')
        cabinet_depth = self.obj_y.pyclone.get_var('location.y','cabinet_depth')
        cabinet_height = self.obj_z.pyclone.get_var('location.z','cabinet_height')
        countertop_height = self.countertop.obj_z.pyclone.get_var('location.z','countertop_height')
        cooktop_width = self.cooktop_appliance.obj_x.location.x
        cooktop_depth = self.cooktop_appliance.obj_y.location.y

        self.cooktop_appliance.loc_x('(cabinet_width/2)-' + str(cooktop_width/2),[cabinet_width])
        self.cooktop_appliance.loc_y('(cabinet_depth/2)-' + str(cooktop_depth/2),[cabinet_depth])
        self.cooktop_appliance.loc_z('cabinet_height+countertop_height',[cabinet_height,countertop_height])

        for child in self.cooktop_appliance.obj_bp.children:
            if child.type == 'MESH':   
                if 'IS_BOOLEAN' in child and child['IS_BOOLEAN'] == True:   
                    bool_obj = child
                    break

        home_builder_utils.assign_boolean_to_child_assemblies(self.countertop,bool_obj)
        for carcass in self.carcasses:
            home_builder_utils.assign_boolean_to_child_assemblies(carcass,bool_obj)

        home_builder_utils.update_assembly_id_props(self.cooktop_appliance,self)

    def add_range_hood(self,category="",assembly_name=""):
        self.range_hood_appliance = pc_types.Assembly(self.add_assembly_from_file(get_range_hood(category,assembly_name)))
        self.range_hood_appliance.obj_bp["IS_RANGE_HOOD_BP"] = True
        self.range_hood_appliance.obj_x.empty_display_size = pc_unit.inch(.5)
        self.range_hood_appliance.obj_y.empty_display_size = pc_unit.inch(.5)
        self.range_hood_appliance.obj_z.empty_display_size = pc_unit.inch(.5)

        if not self.range_hood_appliance.obj_x.lock_location[0]:
            width = self.obj_x.pyclone.get_var('location.x','width')
            self.range_hood_appliance.dim_x('width',[width])

        self.update_range_hood_location()

        home_builder_utils.update_assembly_id_props(self.range_hood_appliance,self)

    def add_left_filler(self):
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        left_adjustment_width = self.get_prompt("Left Adjustment Width").get_var("left_adjustment_width")

        self.left_filler = data_cabinet_parts.add_carcass_part(self)
        self.left_filler.obj_bp["IS_LEFT_FILLER_BP"] = True
        self.left_filler.set_name('Left Filler')
        self.left_filler.loc_x(value=0)
        self.left_filler.loc_y(value=0)
        self.left_filler.loc_z(value=0)
        self.left_filler.dim_x('left_adjustment_width',[left_adjustment_width])
        self.left_filler.dim_y('depth',[depth])
        self.left_filler.dim_z('height',[height])
        home_builder_utils.flip_normals(self.left_filler)
        home_builder_pointers.assign_pointer_to_assembly(self.left_filler,"Cabinet Exposed Surfaces")

    def add_right_filler(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        right_adjustment_width = self.get_prompt("Right Adjustment Width").get_var("right_adjustment_width")

        self.right_filler = data_cabinet_parts.add_carcass_part(self)
        self.right_filler.obj_bp["IS_RIGHT_FILLER_BP"] = True
        self.right_filler.set_name('Right Filler')
        self.right_filler.loc_x('width',[width])
        self.right_filler.loc_y(value=0)
        self.right_filler.loc_z(value=0)
        self.right_filler.dim_x('-right_adjustment_width',[right_adjustment_width])
        self.right_filler.dim_y('depth',[depth])
        self.right_filler.dim_z('height',[height])
        home_builder_pointers.assign_pointer_to_assembly(self.right_filler,"Cabinet Exposed Surfaces")

    def add_countertop(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')    
        ctop_front = self.add_prompt("Countertop Overhang Front",'DISTANCE',pc_unit.inch(1))
        ctop_back = self.add_prompt("Countertop Overhang Back",'DISTANCE',pc_unit.inch(0))
        ctop_left = self.add_prompt("Countertop Overhang Left",'DISTANCE',pc_unit.inch(0))
        ctop_right = self.add_prompt("Countertop Overhang Right",'DISTANCE',pc_unit.inch(0))      
        ctop_overhang_front = ctop_front.get_var('ctop_overhang_front')
        ctop_overhang_back = ctop_back.get_var('ctop_overhang_back')
        ctop_overhang_left = ctop_left.get_var('ctop_overhang_left')
        ctop_overhang_right = ctop_right.get_var('ctop_overhang_right')

        self.countertop = self.add_assembly(data_countertops.Countertop())
        self.countertop.set_name('Countertop')
        self.countertop.loc_x('-ctop_overhang_left',[ctop_overhang_left])
        self.countertop.loc_y('ctop_overhang_back',[ctop_overhang_back])
        self.countertop.loc_z('height',[height])
        self.countertop.dim_x('width+ctop_overhang_left+ctop_overhang_right',[width,ctop_overhang_left,ctop_overhang_right])
        self.countertop.dim_y('depth-(ctop_overhang_front+ctop_overhang_back)',[depth,ctop_overhang_front,ctop_overhang_back])


class Standard_Cabinet(Cabinet):
    show_in_library = True
    category_name = "Cabinets"
    
    width = pc_unit.inch(18)
    calculators = []

    # carcass = None
    # interior = None
    # exterior = None
    # splitter = None

    def draw(self):
        start_time = time.time()
        
        self.obj_bp["IS_CABINET_BP"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.cabinet_prompts" 
        self.obj_bp["MENU_ID"] = "HOMEBUILDER_MT_cabinet_menu"
        self.obj_y['IS_MIRROR'] = True

        carcass_type = self.carcass.get_prompt("Carcass Type")
        if self.carcass.interior:
            self.carcass.add_insert(self.carcass.interior)        
        if self.carcass.exterior:
            self.carcass.add_insert(self.carcass.exterior)
        # if self.carcass.splitter:
        #     self.carcass.add_insert(self.carcass.splitter)            

        #BASE CABINET
        if carcass_type.get_value() == 'Base':
            self.add_countertop()
            common_prompts.add_sink_prompts(self)
            common_prompts.add_cooktop_prompts(self)

        print("Cabinet: Draw Time --- %s seconds ---" % (time.time() - start_time))

    def pre_draw(self):
        self.create_assembly()
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        common_prompts.add_cabinet_prompts(self)
        common_prompts.add_filler_prompts(self)
        
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        left_adjment_width = self.get_prompt("Left Adjustment Width").get_var('left_adjment_width')
        right_adjment_width = self.get_prompt("Right Adjustment Width").get_var('right_adjment_width')

        self.carcass = self.add_assembly(self.carcass)
        self.carcass.set_name('Carcass')
        self.carcass.loc_x('left_adjment_width',[left_adjment_width])
        self.carcass.loc_y(value=0)
        self.carcass.loc_z(value=0)
        self.carcass.dim_x('width-left_adjment_width-right_adjment_width',[width,left_adjment_width,right_adjment_width])
        self.carcass.dim_y('depth',[depth])
        self.carcass.dim_z('height',[height])

        carcass_type = self.carcass.get_prompt("Carcass Type")
        self.obj_x.location.x = self.width 
        if carcass_type.get_value() == 'Base':
            self.obj_y.location.y = -props.base_cabinet_depth
            self.obj_z.location.z = props.base_cabinet_height
        if carcass_type.get_value() == 'Tall':
            self.obj_y.location.y = -props.tall_cabinet_depth
            self.obj_z.location.z = props.tall_cabinet_height
        if carcass_type.get_value() == 'Upper':
            self.obj_y.location.y = -props.upper_cabinet_depth
            self.obj_z.location.z = props.upper_cabinet_height
            self.obj_bp.location.z = props.height_above_floor - props.upper_cabinet_height

    def get_calculators(self,obj):
        for cal in obj.pyclone.calculators:
            self.calculators.append(cal)
        for child in obj.children:
            self.get_calculators(child)

    def render(self):
        left_side = None
        right_side = None

        for child in self.carcass.obj_bp.children:
            if "IS_LEFT_SIDE_BP" in child and child["IS_LEFT_SIDE_BP"]:
                left_side = pc_types.Assembly(child)
            if "IS_RIGHT_SIDE_BP" in child and child["IS_RIGHT_SIDE_BP"]:
                right_side = pc_types.Assembly(child)
            if "IS_BACK_BP" in child and child["IS_BACK_BP"]:
                back = pc_types.Assembly(child)

        self.get_calculators(self.obj_bp)

        for cal in self.calculators:
            cal.calculate()


class Stacked_Cabinet(Cabinet):
    show_in_library = True
    category_name = "Cabinets"
    
    width = pc_unit.inch(18)
    height = pc_unit.inch(84)
    depth = pc_unit.inch(25)
    bottom_cabinet_height = pc_unit.inch(50)
    z_loc = 0

    top_carcass = None
    bottom_carcass = None
    # interior = None
    # exterior = None
    # splitter = None

    def draw(self):
        start_time = time.time()
        
        self.obj_bp["IS_CABINET_BP"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.cabinet_prompts" 
        self.obj_bp["MENU_ID"] = "HOMEBUILDER_MT_cabinet_menu"
        self.obj_y['IS_MIRROR'] = True

        # cabinet_type = self.carcass.get_prompt("Cabinet Type")
        if self.top_carcass.exterior:
            self.top_carcass.add_insert(self.top_carcass.exterior)
        if self.top_carcass.interior:
            self.top_carcass.add_insert(self.top_carcass.interior)              

        if self.bottom_carcass.exterior:
            self.bottom_carcass.add_insert(self.bottom_carcass.exterior)
        if self.bottom_carcass.interior:
            self.bottom_carcass.add_insert(self.bottom_carcass.interior)    

        # #BASE CABINET
        # if cabinet_type.get_value() == 'Base':
        #     cabinet_utils.add_countertop(self)
        #     common_prompts.add_sink_prompts(self)
        #     common_prompts.add_cooktop_prompts(self)

        print("Cabinet: Draw Time --- %s seconds ---" % (time.time() - start_time))

    def pre_draw(self):
        self.create_assembly()
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        common_prompts.add_cabinet_prompts(self)
        common_prompts.add_filler_prompts(self)
        common_prompts.add_stacked_cabinet_prompts(self)
        bottom_cabinet_height = self.get_prompt("Bottom Cabinet Height")
        bottom_cabinet_height.set_value(self.bottom_cabinet_height)

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        left_adjment_width = self.get_prompt("Left Adjustment Width").get_var('left_adjment_width')
        right_adjment_width = self.get_prompt("Right Adjustment Width").get_var('right_adjment_width')
        bottom_cabinet_height = bottom_cabinet_height.get_var('bottom_cabinet_height')

        self.bottom_carcass = self.add_assembly(self.bottom_carcass)
        self.bottom_carcass.set_name('Bottom Carcass')
        self.bottom_carcass.loc_x('left_adjment_width',[left_adjment_width])
        self.bottom_carcass.loc_y(value=0)
        self.bottom_carcass.loc_z(value=0)
        self.bottom_carcass.dim_x('width-left_adjment_width-right_adjment_width',[width,left_adjment_width,right_adjment_width])
        self.bottom_carcass.dim_y('depth',[depth])
        self.bottom_carcass.dim_z('bottom_cabinet_height',[bottom_cabinet_height])

        self.top_carcass = self.add_assembly(self.top_carcass)
        self.top_carcass.set_name('Upper Carcass')
        self.top_carcass.loc_x('left_adjment_width',[left_adjment_width])
        self.top_carcass.loc_y(value=0)
        self.top_carcass.loc_z('bottom_cabinet_height',[bottom_cabinet_height])
        self.top_carcass.dim_x('width-left_adjment_width-right_adjment_width',[width,left_adjment_width,right_adjment_width])
        self.top_carcass.dim_y('depth',[depth])
        self.top_carcass.dim_z('height-bottom_cabinet_height',[height,bottom_cabinet_height])

        self.obj_x.location.x = self.width
        self.obj_y.location.y = -self.depth
        self.obj_z.location.z = self.height
        self.obj_bp.location.z = self.z_loc

    def render(self):
        self.pre_draw()
        self.draw()