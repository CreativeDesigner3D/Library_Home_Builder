import bpy
import time
import math
from os import path
from ..pc_lib import pc_types, pc_unit, pc_utils

from . import common_prompts
from . import data_closet_parts
from .. import home_builder_utils
from .. import home_builder_pointers
from .. import home_builder_paths

class Shelves(pc_types.Assembly):
    show_in_library = True
    category_name = "CLOSETS"
    subcategory_name = "INSERTS"

    def add_adj_prompts(self):
        self.add_prompt(name="Shelf Qty",
                        prompt_type='QUANTITY',
                        value=5,
                        tab_index=0)

    def add_shelves(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        shelf_qty = self.get_prompt("Shelf Quantity").get_var("shelf_qty")
        shelf_clip_gap = self.get_prompt("Shelf Clip Gap").get_var("shelf_clip_gap")
        shelf_thickness = self.get_prompt("Shelf Thickness").get_var("shelf_thickness")
        
        adj_shelf = data_closet_parts.add_closet_array_part(self)
        is_locked_shelf = adj_shelf.add_prompt("Is Locked Shelf",'CHECKBOX',True)
        is_lock_shelf_var = is_locked_shelf.get_var("is_lock_shelf_var")
        adj_shelf_setback = adj_shelf.add_prompt("Adj Shelf Setback",'DISTANCE',pc_unit.inch(.25))
        adj_shelf_setback_var = adj_shelf_setback.get_var("adj_shelf_setback_var")
        fixed_shelf_setback = adj_shelf.add_prompt("Fixed Shelf Setback",'DISTANCE',pc_unit.inch(.25))
        fixed_shelf_setback_var = fixed_shelf_setback.get_var("fixed_shelf_setback_var")
        
        adj_shelf.loc_x('IF(is_lock_shelf_var,0,shelf_clip_gap)',[shelf_clip_gap,is_lock_shelf_var])
        adj_shelf.loc_y('depth',[depth])
        adj_shelf.loc_z('((height-(shelf_thickness*shelf_qty))/(shelf_qty+1))',[height,shelf_thickness,shelf_qty])
        adj_shelf.rot_x(value = 0)
        adj_shelf.rot_y(value = 0)
        adj_shelf.rot_z(value = 0)
        adj_shelf.dim_x('width-IF(is_lock_shelf_var,0,shelf_clip_gap*2)',[width,is_lock_shelf_var,shelf_clip_gap])
        adj_shelf.dim_y('-depth+IF(is_lock_shelf_var,fixed_shelf_setback_var,adj_shelf_setback_var)',[depth,is_lock_shelf_var,fixed_shelf_setback_var,adj_shelf_setback_var])
        adj_shelf.dim_z('shelf_thickness',[shelf_thickness])
        hide = adj_shelf.get_prompt("Hide")
        z_quantity = adj_shelf.get_prompt("Z Quantity")
        z_offset = adj_shelf.get_prompt("Z Offset")

        hide.set_formula('IF(shelf_qty==0,True,False)',[shelf_qty]) 
        z_quantity.set_formula('shelf_qty',[shelf_qty]) 
        z_offset.set_formula('((height-(shelf_thickness*shelf_qty))/(shelf_qty+1))+shelf_thickness',[height,shelf_thickness,shelf_qty]) 

    def pre_draw(self):
        self.create_assembly()
        self.obj_bp["IS_SHELVES_INSERT"] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.closet_shelves_prompts"
        
        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = data_closet_parts.add_closet_opening(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def draw(self):

        shelf_thickness = self.add_prompt("Shelf Thickness",'DISTANCE',pc_unit.inch(1)) 
        shelf_clip_gap = self.add_prompt("Shelf Clip Gap",'DISTANCE',pc_unit.inch(1)) 
        shelf_qty = self.add_prompt("Shelf Quantity",'QUANTITY',3) 
        
        self.add_shelves()

    def render(self):
        self.pre_draw()
        self.draw()


class Single_Shelf(pc_types.Assembly):
    show_in_library = True
    category_name = "CLOSETS"
    subcategory_name = "CLOSET_PARTS"
    drop_id = ""

    def add_adj_prompts(self):
        self.add_prompt(name="Shelf Qty",
                        prompt_type='QUANTITY',
                        value=5,
                        tab_index=0)

    def add_shelves(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        shelf_qty = self.get_prompt("Shelf Quantity").get_var("shelf_qty")
        shelf_clip_gap = self.get_prompt("Shelf Clip Gap").get_var("shelf_clip_gap")
        shelf_thickness = self.get_prompt("Shelf Thickness").get_var("shelf_thickness")
        
        adj_shelf = data_closet_parts.add_closet_array_part(self)
        is_locked_shelf = adj_shelf.add_prompt("Is Locked Shelf",'CHECKBOX',True)
        is_lock_shelf_var = is_locked_shelf.get_var("is_lock_shelf_var")
        adj_shelf_setback = adj_shelf.add_prompt("Adj Shelf Setback",'DISTANCE',pc_unit.inch(.25))
        adj_shelf_setback_var = adj_shelf_setback.get_var("adj_shelf_setback_var")
        fixed_shelf_setback = adj_shelf.add_prompt("Fixed Shelf Setback",'DISTANCE',pc_unit.inch(.25))
        fixed_shelf_setback_var = fixed_shelf_setback.get_var("fixed_shelf_setback_var")
        
        adj_shelf.loc_x('IF(is_lock_shelf_var,0,shelf_clip_gap)',[shelf_clip_gap,is_lock_shelf_var])
        adj_shelf.loc_y('depth',[depth])
        adj_shelf.loc_z(value = 0)
        adj_shelf.rot_x(value = 0)
        adj_shelf.rot_y(value = 0)
        adj_shelf.rot_z(value = 0)
        adj_shelf.dim_x('width-IF(is_lock_shelf_var,0,shelf_clip_gap*2)',[width,is_lock_shelf_var,shelf_clip_gap])
        adj_shelf.dim_y('-depth+IF(is_lock_shelf_var,fixed_shelf_setback_var,adj_shelf_setback_var)',[depth,is_lock_shelf_var,fixed_shelf_setback_var,adj_shelf_setback_var])
        adj_shelf.dim_z('shelf_thickness',[shelf_thickness])
        # hide = adj_shelf.get_prompt("Hide")
        # z_quantity = adj_shelf.get_prompt("Z Quantity")
        # z_offset = adj_shelf.get_prompt("Z Offset")

        # hide.set_formula('IF(shelf_qty==0,True,False)',[shelf_qty]) 
        # z_quantity.set_formula('shelf_qty',[shelf_qty]) 
        # z_offset.set_formula('((height-(shelf_thickness*shelf_qty))/(shelf_qty+1))+shelf_thickness',[height,shelf_thickness,shelf_qty]) 

    def pre_draw(self):
        self.create_assembly()
        self.obj_bp["IS_SHELVES_INSERT"] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.closet_shelves_prompts"
        
        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(.75)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = data_closet_parts.add_closet_opening(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def draw(self):

        shelf_thickness = self.add_prompt("Shelf Thickness",'DISTANCE',pc_unit.inch(1)) 
        shelf_clip_gap = self.add_prompt("Shelf Clip Gap",'DISTANCE',pc_unit.inch(1)) 
        shelf_qty = self.add_prompt("Shelf Quantity",'QUANTITY',3) 
        
        self.add_shelves()

    def render(self):
        self.pre_draw()
        self.draw()


class Vertical_Splitter(pc_types.Assembly):
    show_in_library = True
    category_name = "CLOSETS"
    subcategory_name = "CLOSET_PARTS"
    drop_id = ""

    splitter_qty = 1

    def add_splitters(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        s_thickness = self.get_prompt("Shelf Thickness").get_var("s_thickness")
        
        previous_splitter = None

        for i in range(1,self.splitter_qty+1):
            opening_height = self.get_prompt('Opening ' + str(i) + ' Height').get_var('Opening Calculator','opening_height')
            splitter = data_closet_parts.add_closet_part(self)
            splitter.loc_x(value = 0)
            splitter.loc_y(value = 0)
            if previous_splitter:
                loc_z = previous_splitter.obj_bp.pyclone.get_var('location.z','loc_z')
                splitter.loc_z('loc_z-opening_height-s_thickness',[loc_z,opening_height,s_thickness])
            else:
                splitter.loc_z('height-opening_height-s_thickness',[height,opening_height,s_thickness])
            splitter.rot_x(value = 0)
            splitter.rot_y(value = 0)
            splitter.rot_z(value = 0)
            splitter.dim_x('width',[width])
            splitter.dim_y('depth',[depth])
            splitter.dim_z('s_thickness',[s_thickness])

            s_loc_z = splitter.obj_bp.pyclone.get_var('location.z','s_loc_z')

            opening = data_closet_parts.add_closet_opening(self)
            opening.set_name('Opening')
            opening.loc_x(value = 0)
            opening.loc_y(value = 0)
            opening.loc_z('s_loc_z+s_thickness',[s_loc_z,s_thickness])
            opening.rot_x(value = 0)
            opening.rot_y(value = 0)
            opening.rot_z(value = 0)
            opening.dim_x('width',[width])
            opening.dim_y('depth',[depth])
            opening.dim_z('opening_height',[opening_height])

            previous_splitter = splitter

        last_opening_height = self.get_prompt('Opening ' + str(self.splitter_qty+1) + ' Height').get_var('Opening Calculator','last_opening_height')

        opening = data_closet_parts.add_closet_opening(self)
        opening.set_name('Opening')
        opening.loc_x(value = 0)
        opening.loc_y(value = 0)
        opening.loc_z(value = 0)
        opening.rot_x(value = 0)
        opening.rot_y(value = 0)
        opening.rot_z(value = 0)
        opening.dim_x('width',[width])
        opening.dim_y('depth',[depth])
        opening.dim_z('last_opening_height',[last_opening_height])

    def pre_draw(self):
        self.create_assembly()
        self.obj_bp["IS_SPLITTER_INSERT"] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.splitter_prompts"
        
        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(.75)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = data_closet_parts.add_closet_opening(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def draw(self):
        shelf_thickness = self.add_prompt("Shelf Thickness",'DISTANCE',pc_unit.inch(1)) 
        
        height = self.obj_z.pyclone.get_var('location.z','height')
        s_thickness = shelf_thickness.get_var('s_thickness')
        calc_distance_obj = self.add_empty('Calc Distance Obj')
        calc_distance_obj.empty_display_size = .001
        opening_calculator = self.obj_prompts.pyclone.add_calculator("Opening Calculator",calc_distance_obj)

        for i in range(1,self.splitter_qty+2):
            opening_calculator.add_calculator_prompt('Opening ' + str(i) + ' Height')

        opening_calculator.set_total_distance('height-s_thickness*' + str(self.splitter_qty),[height,s_thickness])

        self.add_splitters()

        bpy.context.view_layer.update()
        opening_calculator.calculate()

    def render(self):
        self.pre_draw()
        self.draw()


class Horizontal_Splitter(pc_types.Assembly):
    show_in_library = True
    category_name = "CLOSETS"
    subcategory_name = "CLOSET_PARTS"
    drop_id = ""

    splitter_qty = 1

    def add_splitters(self):
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        d_thickness = self.get_prompt("Division Thickness").get_var("d_thickness")
        
        previous_splitter = None

        for i in range(1,self.splitter_qty+1):
            opening_width = self.get_prompt('Opening ' + str(i) + ' Width').get_var('Opening Calculator','opening_width')

            opening = data_closet_parts.add_closet_opening(self)
            opening.set_name('Opening ' + str(i))
            if previous_splitter:
                loc_x = previous_splitter.obj_bp.pyclone.get_var('location.x','loc_x')
                opening.loc_x('loc_x',[loc_x])
            else:
                opening.loc_x(value = 0)
            opening.loc_y(value = 0)
            opening.loc_z(value = 0)
            opening.rot_x(value = 0)
            opening.rot_y(value = 0)
            opening.rot_z(value = 0)
            opening.dim_x('opening_width',[opening_width])
            opening.dim_y('depth',[depth])
            opening.dim_z('height',[height])

            splitter = data_closet_parts.add_closet_part(self)
            splitter.set_name("Division " + str(i))
            if previous_splitter:
                loc_x = previous_splitter.obj_bp.pyclone.get_var('location.x','loc_x')
                splitter.loc_x('loc_x+opening_width+d_thickness',[loc_x,opening_width,d_thickness])
            else:
                splitter.loc_x('opening_width+d_thickness',[opening_width,d_thickness])            
            splitter.loc_y(value = 0)
            splitter.loc_z(value = 0)
            splitter.rot_x(value = 0)
            splitter.rot_y(value = math.radians(-90))
            splitter.rot_z(value = 0)
            splitter.dim_x('height',[height])
            splitter.dim_y('depth',[depth])
            splitter.dim_z('d_thickness',[d_thickness])

            previous_splitter = splitter

        previous_splitter_x = previous_splitter.obj_bp.pyclone.get_var('location.x','previous_splitter_x')
        last_opening_width = self.get_prompt('Opening ' + str(self.splitter_qty+1) + ' Width').get_var('Opening Calculator','last_opening_width')

        last_opening = data_closet_parts.add_closet_opening(self)
        last_opening.set_name('Opening ' + str(self.splitter_qty+1))
        last_opening.loc_x('previous_splitter_x',[previous_splitter_x])
        last_opening.loc_y(value = 0)
        last_opening.loc_z(value = 0)
        last_opening.rot_x(value = 0)
        last_opening.rot_y(value = 0)
        last_opening.rot_z(value = 0)
        last_opening.dim_x('last_opening_width',[last_opening_width])
        last_opening.dim_y('depth',[depth])
        last_opening.dim_z('height',[height])

    def pre_draw(self):
        self.create_assembly()
        self.obj_bp["IS_SPLITTER_INSERT"] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.splitter_prompts"
        
        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(.75)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = data_closet_parts.add_closet_opening(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def draw(self):
        division_thickness = self.add_prompt("Division Thickness",'DISTANCE',pc_unit.inch(1)) 
        
        width = self.obj_x.pyclone.get_var('location.x','width')
        d_thickness = division_thickness.get_var('d_thickness')
        calc_distance_obj = self.add_empty('Calc Distance Obj')
        calc_distance_obj.empty_display_size = .001
        opening_calculator = self.obj_prompts.pyclone.add_calculator("Opening Calculator",calc_distance_obj)

        for i in range(1,self.splitter_qty+2):
            opening_calculator.add_calculator_prompt('Opening ' + str(i) + ' Width')

        opening_calculator.set_total_distance('width-d_thickness*' + str(self.splitter_qty),[width,d_thickness])

        self.add_splitters()

        bpy.context.view_layer.update()
        opening_calculator.calculate()

    def render(self):
        self.pre_draw()
        self.draw()


class Slanted_Shoe_Shelf(pc_types.Assembly):
    show_in_library = True
    category_name = "CLOSETS"
    subcategory_name = "CLOSET_PARTS"
    drop_id = ""

    def pre_draw(self):
        self.create_assembly()
        self.obj_bp["IS_SHELVES_INSERT"] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.closet_shelves_prompts"
        
        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(.75)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = data_closet_parts.add_closet_reference(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def draw(self):

        shelf_thickness = self.add_prompt("Shelf Thickness",'DISTANCE',pc_unit.inch(1)) 
        shelf_clip_gap = self.add_prompt("Shelf Clip Gap",'DISTANCE',pc_unit.inch(1)) 
        shelf_setback = self.add_prompt("Shelf Setback",'DISTANCE',pc_unit.inch(1))
        shelf_lip_width = self.add_prompt("Shelf Lip Width",'DISTANCE',pc_unit.inch(2))
        distance_between_shelves = self.add_prompt("Distance Between Shelves",'DISTANCE',pc_unit.inch(8))
        space_from_bottom = self.add_prompt("Space From Bottom",'DISTANCE',pc_unit.inch(3.5))
        shelf_qty = self.add_prompt("Shelf Quantity",'QUANTITY',3) 
        shelf_angle = self.add_prompt("Shelf Angle",'ANGLE',17.25) 
        
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        qty = shelf_qty.get_var("qty")
        shelf_clip_gap_var = shelf_clip_gap.get_var("shelf_clip_gap")
        lip_width = shelf_lip_width.get_var('lip_width')
        bot_space = space_from_bottom.get_var('bot_space')
        s_thickness = shelf_thickness.get_var("s_thickness")
        angle = shelf_angle.get_var("angle")
        setback = shelf_setback.get_var("setback")
        dim_between_shelves = distance_between_shelves.get_var('dim_between_shelves')
        
        #TOP SHELF
        shelf = data_closet_parts.add_closet_part(self)
        shelf.obj_bp["IS_SHELF_BP"] = True
        shelf.set_name('Top Shelf')
        shelf.loc_x(value = 0)
        shelf.loc_y(value = 0)
        shelf.loc_z('bot_space+dim_between_shelves*qty',[bot_space,dim_between_shelves,qty])
        shelf.rot_y(value = 0)
        shelf.rot_z(value = 0)
        shelf.dim_x('width',[width])
        shelf.dim_y('depth',[depth])
        shelf.dim_z('s_thickness',[s_thickness])

        z_loc = shelf.obj_bp.pyclone.get_var('location.z','z_loc')

        opening = data_closet_parts.add_closet_opening(self)
        opening.set_name('Opening')
        opening.loc_x(value = 0)
        opening.loc_y(value = 0)
        opening.loc_z('z_loc+s_thickness',[z_loc,s_thickness])
        opening.rot_x(value = 0)
        opening.rot_y(value = 0)
        opening.rot_z(value = 0)
        opening.dim_x('width',[width])
        opening.dim_y('depth',[depth])
        opening.dim_z('height-z_loc-s_thickness',[height,z_loc,s_thickness])

        for i in range(1,11):
            slanted_shelf = data_closet_parts.add_closet_array_part(self)
            slanted_shelf.set_name("Slanted Shelf")
            slanted_shelf.loc_x(value = 0)
            slanted_shelf.loc_y('depth',[depth])
            if i == 1:
                slanted_shelf.loc_z('bot_space',[bot_space])
            else:
                slanted_shelf.loc_z('bot_space+dim_between_shelves*' + str(i-1),[bot_space,dim_between_shelves])
            slanted_shelf.rot_x('angle',[angle])
            slanted_shelf.rot_y(value = 0)
            slanted_shelf.rot_z(value = 0)
            slanted_shelf.dim_x('width',[width])
            slanted_shelf.dim_y('-depth+setback',[depth,setback])
            slanted_shelf.dim_z('s_thickness',[s_thickness])
            hide = slanted_shelf.get_prompt('Hide')
            hide.set_formula('IF(' + str(i) + '>qty,True,False)',[qty])
            home_builder_utils.flip_normals(slanted_shelf)

            shelf_depth = slanted_shelf.obj_y.pyclone.get_var('location.y','shelf_depth')
            z_loc = slanted_shelf.obj_bp.pyclone.get_var('location.z','z_loc')

            shelf_lip = data_closet_parts.add_closet_part(self)
            shelf_lip.set_name("Shelf Lip")
            shelf_lip.loc_x(value = 0)
            shelf_lip.loc_y('fabs(depth)-(fabs(shelf_depth)*cos(angle))',[depth,shelf_depth,angle])
            shelf_lip.loc_z('z_loc-(fabs(shelf_depth)*sin(angle))',[z_loc,shelf_depth,angle])
            shelf_lip.rot_x('angle-radians(90)',[angle])
            shelf_lip.rot_y(value = 0)
            shelf_lip.rot_z(value = 0)
            shelf_lip.dim_x('width',[width])
            shelf_lip.dim_y('-lip_width',[lip_width])
            shelf_lip.dim_z('-s_thickness',[s_thickness])
            hide = shelf_lip.get_prompt('Hide')
            hide.set_formula('IF(' + str(i) + '>qty,True,False)',[qty])

    def render(self):
        self.pre_draw()
        self.draw()


class Hanging_Rod(pc_types.Assembly):
    show_in_library = True
    category_name = "CLOSETS"
    subcategory_name = "INSERTS"

    is_double = False

    def add_hanging_rod(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        hanging_rod_location_from_top = self.get_prompt("Hanging Rod Location From Top").get_var("hanging_rod_location_from_top")
        hanging_rod_setback = self.get_prompt("Hanging Rod Setback").get_var("hanging_rod_setback")
        # shelf_clip_gap = self.get_prompt("Shelf Clip Gap").get_var("shelf_clip_gap")
        # shelf_thickness = self.get_prompt("Shelf Thickness").get_var("shelf_thickness")
        
        hanging_rod = data_closet_parts.add_closet_oval_hanging_rod(self)
        hangers = data_closet_parts.add_closet_hangers(self)

        # is_locked_shelf = adj_shelf.add_prompt("Is Locked Shelf",'CHECKBOX',True)
        # is_lock_shelf_var = is_locked_shelf.get_var("is_lock_shelf_var")
        # adj_shelf_setback = adj_shelf.add_prompt("Adj Shelf Setback",'DISTANCE',pc_unit.inch(.25))
        # adj_shelf_setback_var = adj_shelf_setback.get_var("adj_shelf_setback_var")
        # fixed_shelf_setback = adj_shelf.add_prompt("Fixed Shelf Setback",'DISTANCE',pc_unit.inch(.25))
        # fixed_shelf_setback_var = fixed_shelf_setback.get_var("fixed_shelf_setback_var")
        
        hanging_rod.loc_x(value = 0)
        hanging_rod.loc_y('hanging_rod_setback',[hanging_rod_setback])
        # hanging_rod.loc_z('height-hanging_rod_location_from_top',[height,hanging_rod_location_from_top])
        hanging_rod.rot_x(value = 0)
        hanging_rod.rot_y(value = 0)
        hanging_rod.rot_z(value = 0)
        hanging_rod.dim_x('width',[width])
        hanging_rod.dim_y(value = 0)
        hanging_rod.dim_z(value = 0)

        loc_z = hanging_rod.obj_bp.pyclone.get_var('location.z','loc_z')

        if hangers:
            hangers.loc_x(value = 0)
            hangers.loc_y('hanging_rod_setback',[hanging_rod_setback])
            hangers.loc_z('loc_z',[loc_z])
            hangers.rot_x(value = 0)
            hangers.rot_y(value = 0)
            hangers.rot_z(value = 0)
            hangers.dim_x('width',[width])
            hangers.dim_y(value = 0)
            hangers.dim_z(value = 0)  
        return hanging_rod      

    def pre_draw(self):
        self.create_assembly()
        self.obj_bp["IS_HANGING_RODS_BP"] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.hanging_rod_prompts"

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = data_closet_parts.add_closet_opening(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def draw(self):
        top_loc = self.add_prompt("Hanging Rod Location From Top",'DISTANCE',pc_unit.inch(2.145)) 
        shelf_clip_gap = self.add_prompt("Hanging Rod Setback",'DISTANCE',pc_unit.inch(2)) 
        shelf_thickness = self.add_prompt("Shelf Thickness",'DISTANCE',pc_unit.inch(.75)) 

        height = self.obj_z.pyclone.get_var('location.z','height')
        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        hanging_rod_location_from_top = top_loc.get_var("hanging_rod_location_from_top")
        s_thickness = shelf_thickness.get_var("s_thickness")

        rod = self.add_hanging_rod()
        rod.loc_z('height-hanging_rod_location_from_top',[height,hanging_rod_location_from_top])

        if self.is_double:
            bot_loc = self.add_prompt("Bottom Rod Location From Top",'DISTANCE',pc_unit.inch(38)) 
            hanging_rod_location_from_bot = bot_loc.get_var("hanging_rod_location_from_bot")
            rod = self.add_hanging_rod()
            rod.loc_z('height-hanging_rod_location_from_bot-hanging_rod_location_from_top',[height,hanging_rod_location_from_bot,hanging_rod_location_from_top])

            #MID SHELF
            shelf = data_closet_parts.add_closet_part(self)
            shelf.obj_bp["IS_SHELF_BP"] = True
            shelf.set_name('Shelf')
            shelf.loc_x(value = 0)
            shelf.loc_y(value = 0)
            shelf.loc_z('height-hanging_rod_location_from_bot',[height,hanging_rod_location_from_bot,hanging_rod_location_from_top])
            shelf.rot_y(value = 0)
            shelf.rot_z(value = 0)
            shelf.dim_x('x',[x])
            shelf.dim_y('y',[y])
            shelf.dim_z('s_thickness',[s_thickness])
            home_builder_utils.flip_normals(shelf)

            top_opening = data_closet_parts.add_closet_opening(self)
            top_opening.set_name('Top Opening')
            top_opening.loc_x(value = 0)
            top_opening.loc_y(value = 0)
            top_opening.loc_z('height-hanging_rod_location_from_bot+s_thickness',
                              [height,hanging_rod_location_from_bot,s_thickness])
            top_opening.rot_x(value = 0)
            top_opening.rot_y(value = 0)
            top_opening.rot_z(value = 0)
            top_opening.dim_x('x',[x])
            top_opening.dim_y('y',[y])
            top_opening.dim_z('hanging_rod_location_from_bot-s_thickness',
                              [hanging_rod_location_from_bot,s_thickness])            
        
            bot_opening = data_closet_parts.add_closet_opening(self)
            bot_opening.set_name('Bottom Opening')
            bot_opening.loc_x(value = 0)
            bot_opening.loc_y(value = 0)
            bot_opening.loc_z(value = 0)
            bot_opening.rot_x(value = 0)
            bot_opening.rot_y(value = 0)
            bot_opening.rot_z(value = 0)
            bot_opening.dim_x('x',[x])
            bot_opening.dim_y('y',[y])
            bot_opening.dim_z('height-hanging_rod_location_from_bot',
                              [height,hanging_rod_location_from_bot])           
        
        else:
            opening = data_closet_parts.add_closet_opening(self)
            opening.set_name('Opening')
            opening.loc_x(value = 0)
            opening.loc_y(value = 0)
            opening.loc_z(value = 0)
            opening.rot_x(value = 0)
            opening.rot_y(value = 0)
            opening.rot_z(value = 0)
            opening.dim_x('x',[x])
            opening.dim_y('y',[y])
            opening.dim_z('height',[height])

    def render(self):
        self.pre_draw()
        self.draw()        


class Doors(pc_types.Assembly):
    show_in_library = True
    category_name = "CLOSETS"
    subcategory_name = "INSERTS"
    overlay_prompts = None

    def add_overlay_prompts(self):
        hot = self.get_prompt("Half Overlay Top").get_var('hot')
        hob = self.get_prompt("Half Overlay Bottom").get_var('hob')
        hol = self.get_prompt("Half Overlay Left").get_var('hol')
        hor = self.get_prompt("Half Overlay Right").get_var('hor')
        shelf_thickness = self.get_prompt("Shelf Thickness").get_var('shelf_thickness')
        panel_thickness = self.get_prompt("Panel Thickness").get_var('panel_thickness')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        tr = self.get_prompt("Top Reveal").get_var('tr')
        br = self.get_prompt("Bottom Reveal").get_var('br')
        lr = self.get_prompt("Left Reveal").get_var('lr')
        rr = self.get_prompt("Right Reveal").get_var('rr')

        self.overlay_prompts = self.add_empty('Overlay Prompt Obj')
        self.overlay_prompts['OVERLAY_PROMPTS'] = True
        self.overlay_prompts.empty_display_size = .01

        to = self.overlay_prompts.pyclone.add_prompt('DISTANCE',"Top Overlay")
        bo = self.overlay_prompts.pyclone.add_prompt('DISTANCE',"Bottom Overlay")
        lo = self.overlay_prompts.pyclone.add_prompt('DISTANCE',"Left Overlay")
        ro = self.overlay_prompts.pyclone.add_prompt('DISTANCE',"Right Overlay")

        to.set_formula('IF(hot,(shelf_thickness-vertical_gap)/2,shelf_thickness-tr)',[hot,shelf_thickness,vertical_gap,tr])
        bo.set_formula('IF(hob,(shelf_thickness-vertical_gap)/2,shelf_thickness-br)',[hob,shelf_thickness,vertical_gap,br])
        lo.set_formula('IF(hol,(panel_thickness-vertical_gap)/2,panel_thickness-lr)',[hol,panel_thickness,vertical_gap,lr])
        ro.set_formula('IF(hor,(panel_thickness-vertical_gap)/2,panel_thickness-rr)',[hor,panel_thickness,vertical_gap,rr])

        return to, bo, lo, ro

    def pre_draw(self):
        self.create_assembly()
        self.obj_bp["IS_CLOSET_DOORS_BP"] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.closet_door_prompts"

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = data_closet_parts.add_closet_opening(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def add_door_pull(self,front,pointer):
        pull_length = self.get_prompt("Pull Length")  
        if not pull_length:
            return #DON'T ADD PULLS TO APPLIED ENDS

        pull_path = path.join(home_builder_paths.get_pull_path(),pointer.category,pointer.item_name + ".blend")
        pull_obj = home_builder_utils.get_object(pull_path) 
        front.add_object(pull_obj)

        pull_length.set_value(round(pull_obj.dimensions.x,2))

        #VARS
        door_width = front.obj_y.pyclone.get_var('location.y','door_width')
        door_length = front.obj_x.pyclone.get_var('location.x','door_length')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        hide = front.get_prompt("Hide").get_var('hide')
        pull_length_var = pull_length.get_var('pull_length_var')
        base_pull_vertical_location = self.get_prompt("Base Pull Vertical Location").get_var('base_pull_vertical_location')
        tall_pull_vertical_location = self.get_prompt("Tall Pull Vertical Location").get_var('tall_pull_vertical_location')
        upper_pull_vertical_location = self.get_prompt("Upper Pull Vertical Location").get_var('upper_pull_vertical_location')
        pull_horizontal_location = self.get_prompt("Pull Horizontal Location").get_var('pull_horizontal_location')
        turn_off_pulls = self.get_prompt("Turn Off Pulls").get_var('turn_off_pulls')

        #FORMULAS
        pull_obj.pyclone.loc_z('front_thickness',[front_thickness])
        if pointer.name == 'Base Cabinet Pulls':
            pull_obj.pyclone.loc_x('door_length-base_pull_vertical_location-(pull_length_var/2)',
            [door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location,pull_length_var])  
        if pointer.name == 'Tall Cabinet Pulls':
            pull_obj.pyclone.loc_x('tall_pull_vertical_location-(pull_length_var/2)',
            [door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location,pull_length_var])  
        if pointer.name == 'Upper Cabinet Pulls':
            pull_obj.pyclone.loc_x('upper_pull_vertical_location+(pull_length_var/2)',
            [door_length,base_pull_vertical_location,tall_pull_vertical_location,upper_pull_vertical_location,pull_length_var])     
        pull_obj.rotation_euler.x = math.radians(-90)
        pull_obj.pyclone.loc_y('IF(door_width>0,door_width-pull_horizontal_location,door_width+pull_horizontal_location)',[door_width,pull_horizontal_location])
        pull_obj.pyclone.hide('IF(OR(hide,turn_off_pulls),True,False)',[hide,turn_off_pulls])

        pull_obj['IS_CABINET_PULL'] = True
        home_builder_pointers.assign_pointer_to_object(pull_obj,"Cabinet Pull Finish")  
        home_builder_utils.get_object_props(pull_obj).pointer_name = pointer.name

    def add_drawer_pull(self,front,pointer):
        drawer_front_width = front.obj_y.pyclone.get_var('location.y',"drawer_front_width")
        drawer_front_height = front.obj_x.pyclone.get_var('location.x',"drawer_front_height")
        front_thickness = front.obj_z.pyclone.get_var('location.z',"front_thickness")
        turn_off_pulls = self.get_prompt("Turn Off Pulls").get_var('turn_off_pulls')
        hide_drawer_front = front.get_prompt("Hide").get_var('hide_drawer_front')
        center_pull = self.get_prompt("Center Pull On Front").get_var('center_pull')
        vert_loc = self.get_prompt("Drawer Pull Vertical Location").get_var('vert_loc')

        pull_path = path.join(home_builder_paths.get_pull_path(),pointer.category,pointer.item_name + ".blend")
        pull_obj = home_builder_utils.get_object(pull_path)
        pull_obj['IS_CABINET_PULL'] = True
        home_builder_utils.get_object_props(pull_obj).pointer_name = "Drawer Pulls"
        front.add_object(pull_obj)
        pull_obj.parent = front.obj_bp
        pull_obj.pyclone.loc_x('IF(center_pull,(drawer_front_height/2),drawer_front_height-vert_loc)',[drawer_front_height,center_pull,vert_loc])
        pull_obj.pyclone.loc_y('(fabs(drawer_front_width)/2)*-1',[drawer_front_width])
        pull_obj.pyclone.loc_z('front_thickness',[front_thickness])
        pull_obj.rotation_euler.x = math.radians(-90)
        pull_obj.rotation_euler.y = math.radians(0)
        pull_obj.rotation_euler.z = math.radians(90)
        pull_obj.pyclone.hide('IF(turn_off_pulls,True,hide_drawer_front)',[turn_off_pulls,hide_drawer_front])

        home_builder_pointers.assign_pointer_to_object(pull_obj,"Cabinet Pull Finish")

    def add_prompts(self):
        common_prompts.add_door_prompts(self)
        common_prompts.add_front_prompts(self)
        common_prompts.add_pull_prompts(self)
        common_prompts.add_front_overlay_prompts(self)
        common_prompts.add_closet_thickness_prompts(self)

class Base_Doors(Doors):

    def draw(self):
        self.add_prompts()
        door_height = self.add_prompt("Door Height",'DISTANCE',pc_unit.millimeter(716.95))
        door_height_var = door_height.get_var('door_height_var')

        props = home_builder_utils.get_scene_props(bpy.context.scene)
        front_pointer = props.cabinet_door_pointers["Base Cabinet Doors"]
        pull_pointer = props.pull_pointers["Base Cabinet Pulls"]

        door_swing_prompt = self.get_prompt("Door Swing")
        door_swing_prompt.set_value(2)

        door_type_prompt = self.get_prompt("Door Type")
        door_type_prompt.set_value("Base")

        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        z = self.obj_z.pyclone.get_var('location.z','z')        
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        door_swing = door_swing_prompt.get_var('door_swing')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        door_swing = self.get_prompt("Door Swing").get_var('door_swing')
        s_thickness = self.get_prompt("Shelf Thickness").get_var('s_thickness')

        to, bo, lo, ro = self.add_overlay_prompts()

        to_var = to.get_var("to_var")
        bo_var = bo.get_var("bo_var")
        lo_var = lo.get_var("lo_var")
        ro_var = ro.get_var("ro_var")

        opening = data_closet_parts.add_closet_opening(self)
        opening.set_name('Opening')
        opening.loc_x(value = 0)
        opening.loc_y(value = 0)
        opening.loc_z('door_height_var+s_thickness',[door_height_var,s_thickness])
        opening.rot_x(value = 0)
        opening.rot_y(value = 0)
        opening.rot_z(value = 0)
        opening.dim_x('x',[x])
        opening.dim_y('y',[y])
        opening.dim_z('z-door_height_var-s_thickness',[z,door_height_var,s_thickness])

        #TOP SHELF
        shelf = data_closet_parts.add_closet_part(self)
        shelf.obj_bp["IS_SHELF_BP"] = True
        shelf.set_name('Door Shelf')
        shelf.loc_x(value = 0)
        shelf.loc_y(value = 0)
        shelf.loc_z('door_height_var',[door_height_var])
        shelf.rot_y(value = 0)
        shelf.rot_z(value = 0)
        shelf.dim_x('x',[x])
        shelf.dim_y('y',[y])
        shelf.dim_z('s_thickness',[s_thickness])

        #LEFT DOOR
        l_door = data_closet_parts.add_door_part(self,front_pointer)
        l_door.loc_x('-lo_var',[lo_var])
        l_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        l_door.loc_z('-bo_var',[bo_var])
        l_door.rot_x(value = math.radians(90))
        l_door.rot_y(value = math.radians(-90))
        l_door.rot_z('-door_rotation*open_door',[door_rotation,open_door])
        l_door.dim_x('door_height_var+to_var+bo_var',[door_height_var,to_var,bo_var])
        l_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)*-1',[door_swing,x,lo_var,ro_var,vertical_gap])            
        l_door.dim_z('front_thickness',[front_thickness])
        hide = l_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==1,True,False)',[door_swing])
        self.add_door_pull(l_door,pull_pointer)

        #RIGHT DOOR
        r_door = data_closet_parts.add_door_part(self,front_pointer)
        r_door.loc_x('x+ro_var',[x,ro_var])
        r_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        r_door.loc_z('-bo_var',[bo_var])
        r_door.rot_x(value = math.radians(90))
        r_door.rot_y(value = math.radians(-90))
        r_door.rot_z('door_rotation*open_door',[door_rotation,open_door])   
        r_door.dim_x('door_height_var+to_var+bo_var',[door_height_var,to_var,bo_var])
        r_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)',[door_swing,x,lo_var,ro_var,vertical_gap])     
        r_door.dim_z('front_thickness',[front_thickness])
        hide = r_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==0,True,False)',[door_swing])
        self.add_door_pull(r_door,pull_pointer)

    def render(self):
        self.pre_draw()
        self.draw()

class Tall_Doors(Doors):

    def draw(self):
        self.add_prompts()

        props = home_builder_utils.get_scene_props(bpy.context.scene)
        front_pointer = props.cabinet_door_pointers["Tall Cabinet Doors"]
        pull_pointer = props.pull_pointers["Tall Cabinet Pulls"]

        door_swing_prompt = self.get_prompt("Door Swing")
        door_swing_prompt.set_value(2)

        door_type_prompt = self.get_prompt("Door Type")
        door_type_prompt.set_value("Tall")

        x = self.obj_x.pyclone.get_var('location.x','x')
        z = self.obj_z.pyclone.get_var('location.z','z')        
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        door_swing = door_swing_prompt.get_var('door_swing')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        door_swing = self.get_prompt("Door Swing").get_var('door_swing')

        to, bo, lo, ro = self.add_overlay_prompts()

        to_var = to.get_var("to_var")
        bo_var = bo.get_var("bo_var")
        lo_var = lo.get_var("lo_var")
        ro_var = ro.get_var("ro_var")

        #LEFT DOOR
        l_door = data_closet_parts.add_door_part(self,front_pointer)
        l_door.loc_x('-lo_var',[lo_var])
        l_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        l_door.loc_z('-bo_var',[bo_var])
        l_door.rot_x(value = math.radians(90))
        l_door.rot_y(value = math.radians(-90))
        l_door.rot_z('-door_rotation*open_door',[door_rotation,open_door])
        l_door.dim_x('z+to_var+bo_var',[z,to_var,bo_var])
        l_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)*-1',[door_swing,x,lo_var,ro_var,vertical_gap])            
        l_door.dim_z('front_thickness',[front_thickness])
        hide = l_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==1,True,False)',[door_swing])
        self.add_door_pull(l_door,pull_pointer)

        #RIGHT DOOR
        r_door = data_closet_parts.add_door_part(self,front_pointer)
        r_door.loc_x('x+ro_var',[x,ro_var])
        r_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        r_door.loc_z('-bo_var',[bo_var])
        r_door.rot_x(value = math.radians(90))
        r_door.rot_y(value = math.radians(-90))
        r_door.rot_z('door_rotation*open_door',[door_rotation,open_door])   
        r_door.dim_x('z+to_var+bo_var',[z,to_var,bo_var])
        r_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)',[door_swing,x,lo_var,ro_var,vertical_gap])     
        r_door.dim_z('front_thickness',[front_thickness])
        hide = r_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==0,True,False)',[door_swing])
        self.add_door_pull(r_door,pull_pointer)

    def render(self):
        self.pre_draw()
        self.draw()       


class Upper_Doors(Doors):

    def draw(self):
        self.add_prompts()
        door_height = self.add_prompt("Door Height",'DISTANCE',pc_unit.millimeter(716.95))
        door_height_var = door_height.get_var('door_height_var')

        props = home_builder_utils.get_scene_props(bpy.context.scene)
        front_pointer = props.cabinet_door_pointers["Upper Cabinet Doors"]
        pull_pointer = props.pull_pointers["Upper Cabinet Pulls"]

        door_swing_prompt = self.get_prompt("Door Swing")
        door_swing_prompt.set_value(2)

        door_type_prompt = self.get_prompt("Door Type")
        door_type_prompt.set_value("Upper")

        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        z = self.obj_z.pyclone.get_var('location.z','z')        
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        door_swing = door_swing_prompt.get_var('door_swing')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        door_swing = self.get_prompt("Door Swing").get_var('door_swing')
        s_thickness = self.get_prompt("Shelf Thickness").get_var('s_thickness')

        to, bo, lo, ro = self.add_overlay_prompts()

        to_var = to.get_var("to_var")
        bo_var = bo.get_var("bo_var")
        lo_var = lo.get_var("lo_var")
        ro_var = ro.get_var("ro_var")

        opening = data_closet_parts.add_closet_opening(self)
        opening.set_name('Opening')
        opening.loc_x(value = 0)
        opening.loc_y(value = 0)
        opening.loc_z(value = 0)
        opening.rot_x(value = 0)
        opening.rot_y(value = 0)
        opening.rot_z(value = 0)
        opening.dim_x('x',[x])
        opening.dim_y('y',[y])
        opening.dim_z('z-door_height_var-s_thickness',[z,door_height_var,s_thickness])

        #TOP SHELF
        shelf = data_closet_parts.add_closet_part(self)
        shelf.obj_bp["IS_SHELF_BP"] = True
        shelf.set_name('Door Shelf')
        shelf.loc_x(value = 0)
        shelf.loc_y(value = 0)
        shelf.loc_z('z-door_height_var-s_thickness',[z,door_height_var,s_thickness])
        shelf.rot_y(value = 0)
        shelf.rot_z(value = 0)
        shelf.dim_x('x',[x])
        shelf.dim_y('y',[y])
        shelf.dim_z('s_thickness',[s_thickness])

        #LEFT DOOR
        l_door = data_closet_parts.add_door_part(self,front_pointer)
        l_door.loc_x('-lo_var',[lo_var])
        l_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        l_door.loc_z('z-door_height_var-bo_var',[z,door_height_var,bo_var])
        l_door.rot_x(value = math.radians(90))
        l_door.rot_y(value = math.radians(-90))
        l_door.rot_z('-door_rotation*open_door',[door_rotation,open_door])
        l_door.dim_x('door_height_var+to_var+bo_var',[door_height_var,to_var,bo_var])
        l_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)*-1',[door_swing,x,lo_var,ro_var,vertical_gap])            
        l_door.dim_z('front_thickness',[front_thickness])
        hide = l_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==1,True,False)',[door_swing])
        self.add_door_pull(l_door,pull_pointer)

        #RIGHT DOOR
        r_door = data_closet_parts.add_door_part(self,front_pointer)
        r_door.loc_x('x+ro_var',[x,ro_var])
        r_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        r_door.loc_z('z-door_height_var-bo_var',[z,door_height_var,bo_var])
        r_door.rot_x(value = math.radians(90))
        r_door.rot_y(value = math.radians(-90))
        r_door.rot_z('door_rotation*open_door',[door_rotation,open_door])   
        r_door.dim_x('door_height_var+to_var+bo_var',[door_height_var,to_var,bo_var])
        r_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)',[door_swing,x,lo_var,ro_var,vertical_gap])     
        r_door.dim_z('front_thickness',[front_thickness])
        hide = r_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==0,True,False)',[door_swing])
        self.add_door_pull(r_door,pull_pointer)

    def render(self):
        self.pre_draw()
        self.draw()                            


class Drawers(Doors):

    def pre_draw(self):
        self.create_assembly()
        self.obj_bp['IS_CLOSET_DRAWERS_BP'] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp['PROMPT_ID'] = 'home_builder.closet_drawer_prompts'

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = data_closet_parts.add_closet_opening(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def draw(self):
        self.add_prompts()

        drawer_quantity = self.add_prompt("Drawer Quantity",'QUANTITY',3)
        drawer_1_height = self.add_prompt("Drawer 1 Height",'DISTANCE',pc_unit.millimeter(157))
        dh1 = drawer_1_height.get_var('dh1')
        drawer_2_height = self.add_prompt("Drawer 2 Height",'DISTANCE',pc_unit.millimeter(157))
        dh2 = drawer_2_height.get_var('dh2')
        drawer_3_height = self.add_prompt("Drawer 3 Height",'DISTANCE',pc_unit.millimeter(157))
        dh3 = drawer_3_height.get_var('dh3')     
        drawer_4_height = self.add_prompt("Drawer 4 Height",'DISTANCE',pc_unit.millimeter(157))
        dh4 = drawer_4_height.get_var('dh4')  
        drawer_5_height = self.add_prompt("Drawer 5 Height",'DISTANCE',pc_unit.millimeter(157))
        dh5 = drawer_5_height.get_var('dh5')  
        drawer_6_height = self.add_prompt("Drawer 6 Height",'DISTANCE',pc_unit.millimeter(157))
        dh6 = drawer_6_height.get_var('dh6')  

        common_prompts.add_front_prompts(self)
        common_prompts.add_drawer_prompts(self)
        common_prompts.add_drawer_pull_prompts(self)
        common_prompts.add_closet_thickness_prompts(self)

        props = home_builder_utils.get_scene_props(bpy.context.scene)
        front_pointer = props.cabinet_door_pointers["Drawer Fronts"]
        pull_pointer = props.pull_pointers["Drawer Pulls"]

        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        z = self.obj_z.pyclone.get_var('location.z','z')      
        dq = drawer_quantity.get_var('dq') 
        h_gap = self.get_prompt("Horizontal Gap").get_var('h_gap') 
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        open_door = self.get_prompt("Open Door").get_var('open_door')
        s_thickness = self.get_prompt("Shelf Thickness").get_var('s_thickness')

        to, bo, lo, ro = self.add_overlay_prompts()

        to_var = to.get_var("to_var")
        bo_var = bo.get_var("bo_var")
        lo_var = lo.get_var("lo_var")
        ro_var = ro.get_var("ro_var")

        #TOP SHELF
        shelf = data_closet_parts.add_closet_part(self)
        shelf.obj_bp["IS_SHELF_BP"] = True
        shelf.set_name('Door Shelf')
        shelf.loc_x(value = 0)
        shelf.loc_y(value = 0)
        shelf.loc_z('-bo_var-to_var+dh1+IF(dq>1,dh2+h_gap,0)+IF(dq>2,dh3+h_gap,0)+IF(dq>3,dh4+h_gap,0)+IF(dq>4,dh5+h_gap,0)+IF(dq>5,dh6+h_gap,0)',
                    [bo_var,to_var,dq,dh1,dh2,dh3,dh4,dh5,dh6,h_gap])        
        shelf.rot_y(value = 0)
        shelf.rot_z(value = 0)
        shelf.dim_x('x',[x])
        shelf.dim_y('y',[y])
        shelf.dim_z('s_thickness',[s_thickness])

        shelf_z_loc = shelf.obj_bp.pyclone.get_var('location.z','shelf_z_loc')

        opening = data_closet_parts.add_closet_opening(self)
        opening.set_name('Opening')
        opening.loc_x(value = 0)
        opening.loc_y(value = 0)
        opening.loc_z('shelf_z_loc+s_thickness',
                      [shelf_z_loc,s_thickness])
        opening.rot_x(value = 0)
        opening.rot_y(value = 0)
        opening.rot_z(value = 0)
        opening.dim_x('x',[x])
        opening.dim_y('y',[y])
        opening.dim_z('z-shelf_z_loc-s_thickness',
                      [z,shelf_z_loc,s_thickness])

        prev_drawer_empty = None

        for i in range(1,7):
            drawer_height = self.get_prompt('Drawer ' + str(i) + " Height")
            dh = drawer_height.get_var('dh')
            front_empty = self.add_empty('Front Loc ' + str(i))
            if prev_drawer_empty:
                prev_drawer_z_loc = prev_drawer_empty.pyclone.get_var('location.z','prev_drawer_z_loc')
                front_empty.pyclone.loc_z('prev_drawer_z_loc-dh-h_gap',[prev_drawer_z_loc,dh,h_gap])
            else:
                front_empty.pyclone.loc_z('shelf_z_loc+to_var-dh',
                                          [shelf_z_loc,to_var,dh])      

            z_loc = front_empty.pyclone.get_var('location.z','z_loc')

            drawer = data_closet_parts.add_door_part(self,front_pointer)
            drawer.obj_bp['IS_DRAWER_FRONT'] = True
            drawer.loc_x('-lo_var',[lo_var])
            drawer.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
            drawer.loc_z('z_loc',[z_loc])                                                                             
            drawer.rot_x(value = math.radians(90))
            drawer.rot_y(value = math.radians(-90))
            drawer.rot_z('-door_rotation*open_door',[door_rotation,open_door])
            drawer.dim_x('dh',[dh])
            drawer.dim_y('(x+lo_var+ro_var)*-1',[x,lo_var,ro_var])            
            drawer.dim_z('front_thickness',[front_thickness])
            hide = drawer.get_prompt('Hide')
            hide.set_formula('IF(dq>' + str(i-1) + ',False,True)',[dq])
            self.add_drawer_pull(drawer,pull_pointer)

            prev_drawer_empty = front_empty
        
    def render(self):
        self.pre_draw()
        self.draw()          


class Single_Drawer(Doors):

    def pre_draw(self):
        self.create_assembly()
        self.obj_bp['IS_CLOSET_DRAWERS_BP'] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp['PROMPT_ID'] = 'home_builder.closet_drawer_prompts'

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = data_closet_parts.add_closet_opening(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def draw(self):
        self.add_prompts()

        drawer_height = self.add_prompt("Drawer Height",'DISTANCE',pc_unit.millimeter(157))
        dh = drawer_height.get_var('dh')

        common_prompts.add_front_prompts(self)
        common_prompts.add_drawer_prompts(self)
        common_prompts.add_drawer_pull_prompts(self)
        common_prompts.add_closet_thickness_prompts(self)

        props = home_builder_utils.get_scene_props(bpy.context.scene)
        front_pointer = props.cabinet_door_pointers["Drawer Fronts"]
        pull_pointer = props.pull_pointers["Drawer Pulls"]

        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        z = self.obj_z.pyclone.get_var('location.z','z')      
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        s_thickness = self.get_prompt("Shelf Thickness").get_var('s_thickness')

        to, bo, lo, ro = self.add_overlay_prompts()

        to_var = to.get_var("to_var")
        bo_var = bo.get_var("bo_var")
        lo_var = lo.get_var("lo_var")
        ro_var = ro.get_var("ro_var")

        #TOP SHELF
        shelf = data_closet_parts.add_closet_part(self)
        shelf.obj_bp["IS_SHELF_BP"] = True
        shelf.set_name('Door Shelf')
        shelf.loc_x(value = 0)
        shelf.loc_y(value = 0)
        shelf.loc_z('-bo_var-to_var+dh',
                    [bo_var,to_var,dh])        
        shelf.rot_y(value = 0)
        shelf.rot_z(value = 0)
        shelf.dim_x('x',[x])
        shelf.dim_y('y',[y])
        shelf.dim_z('s_thickness',[s_thickness])

        shelf_z_loc = shelf.obj_bp.pyclone.get_var('location.z','shelf_z_loc')

        opening = data_closet_parts.add_closet_opening(self)
        opening.set_name('Opening')
        opening.loc_x(value = 0)
        opening.loc_y(value = 0)
        opening.loc_z('shelf_z_loc+s_thickness',
                      [shelf_z_loc,s_thickness])
        opening.rot_x(value = 0)
        opening.rot_y(value = 0)
        opening.rot_z(value = 0)
        opening.dim_x('x',[x])
        opening.dim_y('y',[y])
        opening.dim_z('z-shelf_z_loc-s_thickness',
                      [z,shelf_z_loc,s_thickness])

        drawer = data_closet_parts.add_door_part(self,front_pointer)
        drawer.obj_bp['IS_DRAWER_FRONT'] = True
        drawer.loc_x('-lo_var',[lo_var])
        drawer.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        drawer.loc_z('-bo_var',[bo_var])                                                                             
        drawer.rot_x(value = math.radians(90))
        drawer.rot_y(value = math.radians(-90))
        drawer.rot_z(value = 0)
        drawer.dim_x('dh',[dh])
        drawer.dim_y('(x+lo_var+ro_var)*-1',[x,lo_var,ro_var])            
        drawer.dim_z('front_thickness',[front_thickness])
        self.add_drawer_pull(drawer,pull_pointer)
        
    def render(self):
        self.pre_draw()
        self.draw()          


class Wire_Baskets(pc_types.Assembly):

    def pre_draw(self):
        self.create_assembly()
        self.obj_bp['IS_WIRE_BASKET_INSERT_BP'] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp['PROMPT_ID'] = 'home_builder.closet_wire_baskets_prompts'

        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(60)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = data_closet_parts.add_closet_opening(self)
        reference.obj_bp["IS_REFERENCE"] = True
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def draw(self):

        wire_basket_quantity = self.add_prompt("Wire Basket Quantity",'QUANTITY',3)
        wire_basket_1_height = self.add_prompt("Wire Basket 1 Height",'DISTANCE',pc_unit.inch(6))
        wbh1 = wire_basket_1_height.get_var('wbh1')
        wire_basket_2_height = self.add_prompt("Wire Basket 2 Height",'DISTANCE',pc_unit.inch(6))
        wbh2 = wire_basket_2_height.get_var('wbh2')
        wire_basket_3_height = self.add_prompt("Wire Basket 3 Height",'DISTANCE',pc_unit.inch(6))
        wbh3 = wire_basket_3_height.get_var('wbh3')     
        wire_basket_4_height = self.add_prompt("Wire Basket 4 Height",'DISTANCE',pc_unit.inch(6))
        wbh4 = wire_basket_4_height.get_var('wbh4')  
        wire_basket_5_height = self.add_prompt("Wire Basket 5 Height",'DISTANCE',pc_unit.inch(6))
        wbh5 = wire_basket_5_height.get_var('wbh5')  
        wire_basket_6_height = self.add_prompt("Wire Basket 6 Height",'DISTANCE',pc_unit.inch(6))
        wbh6 = wire_basket_6_height.get_var('wbh6')  
        vert_spacing = self.add_prompt("Vertical Spacing",'DISTANCE',pc_unit.inch(3))
        v = vert_spacing.get_var('v')

        common_prompts.add_closet_thickness_prompts(self)

        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        z = self.obj_z.pyclone.get_var('location.z','z')      
        qty = wire_basket_quantity.get_var('qty') 
        # h_gap = self.get_prompt("Horizontal Gap").get_var('h_gap') 
        s_thickness = self.get_prompt("Shelf Thickness").get_var('s_thickness')

        #TOP SHELF
        shelf = data_closet_parts.add_closet_part(self)
        shelf.obj_bp["IS_SHELF_BP"] = True
        shelf.set_name('Wire Basket Shelf')
        shelf.loc_x(value = 0)
        shelf.loc_y(value = 0)
        shelf.loc_z('wbh1+v+IF(qty>1,wbh2+v,0)+IF(qty>2,wbh3+v,0)+IF(qty>3,wbh4+v,0)+IF(qty>4,wbh5+v,0)+IF(qty>5,wbh6+v,0)',
                    [qty,wbh1,wbh2,wbh3,wbh4,wbh5,wbh6,v])        
        shelf.rot_y(value = 0)
        shelf.rot_z(value = 0)
        shelf.dim_x('x',[x])
        shelf.dim_y('y',[y])
        shelf.dim_z('s_thickness',[s_thickness])

        shelf_z_loc = shelf.obj_bp.pyclone.get_var('location.z','shelf_z_loc')

        opening = data_closet_parts.add_closet_opening(self)
        opening.set_name('Opening')
        opening.loc_x(value = 0)
        opening.loc_y(value = 0)
        opening.loc_z('shelf_z_loc+s_thickness',
                      [shelf_z_loc,s_thickness])
        opening.rot_x(value = 0)
        opening.rot_y(value = 0)
        opening.rot_z(value = 0)
        opening.dim_x('x',[x])
        opening.dim_y('y',[y])
        opening.dim_z('z-shelf_z_loc-s_thickness',
                      [z,shelf_z_loc,s_thickness])

        prev_wire_basket_empty = None

        for i in range(1,7):
            wire_basket_height = self.get_prompt('Wire Basket ' + str(i) + " Height")
            wbh = wire_basket_height.get_var('wbh')
            wire_basket_empty = self.add_empty('Z Loc ' + str(i))
            if prev_wire_basket_empty:
                prev_z_loc = prev_wire_basket_empty.pyclone.get_var('location.z','prev_z_loc')
                wire_basket_empty.pyclone.loc_z('prev_z_loc-wbh-v',[prev_z_loc,wbh,v])
            else:
                wire_basket_empty.pyclone.loc_z('shelf_z_loc-wbh-v',
                                          [shelf_z_loc,wbh,v])      

            z_loc = wire_basket_empty.pyclone.get_var('location.z','z_loc')

            basket = data_closet_parts.add_closet_wire_basket(self)
            basket.loc_x(value = 0)
            basket.loc_y(value = 0)
            basket.loc_z('z_loc',[z_loc])                                                                             
            basket.rot_x(value = 0)
            basket.rot_y(value = 0)
            basket.rot_z(value = 0)
            basket.dim_x('x',[x])
            basket.dim_y('y',[y])            
            basket.dim_z('wbh',[wbh])
            hide = basket.get_prompt('Hide')
            hide.set_formula('IF(qty>' + str(i-1) + ',False,True)',[qty])
            home_builder_pointers.assign_pointer_to_assembly(basket,"Wire Baskets")
            home_builder_pointers.assign_materials_to_assembly(basket)

            prev_wire_basket_empty = wire_basket_empty
        
    def render(self):
        self.pre_draw()
        self.draw()          


class Cubbies(pc_types.Assembly):
    show_in_library = True
    category_name = "CLOSETS"
    subcategory_name = "CLOSET_INSERTS"
    drop_id = ""

    def pre_draw(self):
        self.create_assembly()
        self.obj_bp["IS_CUBBY_INSERT"] = True
        self.obj_bp["IS_CLOSET_INSERT"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.closet_cubby_prompts"
        
        self.obj_x.location.x = pc_unit.inch(20)
        self.obj_y.location.y = pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.inch(.75)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = data_closet_parts.add_closet_reference(self)
        reference.loc_x(value = 0)
        reference.loc_y(value = 0)
        reference.loc_z(value = 0)
        reference.rot_x(value = 0)
        reference.rot_y(value = 0)
        reference.rot_z(value = 0)      
        reference.dim_x('width',[width])
        reference.dim_y('depth',[depth])
        reference.dim_z('height',[height])  

    def draw(self):
        cubby_placement = self.add_prompt("Cubby Placement",'COMBOBOX',0,["Bottom","Top","Fill"])
        shelf_thickness = self.add_prompt("Shelf Thickness",'DISTANCE',pc_unit.inch(1)) 
        divider_thickness = self.add_prompt("Divider Thickness",'DISTANCE',pc_unit.inch(1)) 
        horizontal_qty = self.add_prompt("Horizontal Quantity",'QUANTITY',2) 
        vertical_qty = self.add_prompt("Vertical Quantity",'QUANTITY',2) 
        cubby_setback = self.add_prompt("Cubby Setback",'DISTANCE',pc_unit.inch(.25)) 
        cubby_height = self.add_prompt("Cubby Height",'DISTANCE',pc_unit.millimeter(556.95)) 
        
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        placement = cubby_placement.get_var('placement')
        c_height = cubby_height.get_var('c_height')
        s_thickness = shelf_thickness.get_var('s_thickness')
        d_thickness = divider_thickness.get_var('d_thickness')
        h_qty = horizontal_qty.get_var('h_qty')
        v_qty = vertical_qty.get_var('v_qty')
        setback = cubby_setback.get_var('setback')

        #TOP SHELF
        shelf = data_closet_parts.add_closet_part(self)
        shelf.obj_bp["IS_SHELF_BP"] = True
        shelf.set_name('Cubby Shelf')
        shelf.loc_x(value = 0)
        shelf.loc_y(value = 0)
        shelf.loc_z('IF(placement==0,c_height+s_thickness,height-c_height)',[placement,c_height,height,s_thickness])
        shelf.rot_y(value = 0)
        shelf.rot_z(value = 0)
        shelf.dim_x('width',[width])
        shelf.dim_y('depth',[depth])
        shelf.dim_z('-s_thickness',[s_thickness])
        hide = shelf.get_prompt('Hide')
        hide.set_formula('IF(placement==2,True,False)',[placement])
        home_builder_utils.flip_normals(shelf)

        opening = data_closet_parts.add_closet_opening(self)
        opening.loc_x(value = 0)
        opening.loc_y(value = 0)
        opening.loc_z('IF(placement==0,c_height+s_thickness,0)',[placement,c_height,s_thickness])
        opening.rot_x(value = 0)
        opening.rot_y(value = 0)
        opening.rot_z(value = 0)
        opening.dim_x('IF(placement==2,0,width)',[placement,width])
        opening.dim_y('IF(placement==2,0,depth)',[placement,depth])
        opening.dim_z('IF(placement==2,0,height-c_height-s_thickness)',[placement,height,c_height,s_thickness])

        v_cubby = data_closet_parts.add_closet_array_part(self)
        v_cubby.loc_x('((width-(d_thickness*v_qty))/(v_qty+1))',[width,d_thickness,v_qty])
        v_cubby.loc_y('setback',[setback])
        v_cubby.loc_z('IF(placement==1,height-c_height,0)',[placement,height,c_height,s_thickness])
        v_cubby.rot_x(value = 0)
        v_cubby.rot_y(value = math.radians(-90))
        v_cubby.rot_z(value = 0)
        v_cubby.dim_x('IF(placement==2,height,c_height)',[placement,height,c_height])
        v_cubby.dim_y('depth-setback',[depth,setback])
        v_cubby.dim_z('-d_thickness',[d_thickness])
        qty = v_cubby.get_prompt('Z Quantity')
        offset = v_cubby.get_prompt('Z Offset')
        qty.set_formula('v_qty',[v_qty])
        offset.set_formula('-(((width-(d_thickness*v_qty))/(v_qty+1))+d_thickness)',[width,d_thickness,v_qty])
        home_builder_utils.flip_normals(v_cubby)

        start_placement = 'IF(placement==1,height-c_height,0)'
        v_spacing = '((IF(placement==2,height,c_height)-(s_thickness*h_qty))/(h_qty+1))'

        h_cubby = data_closet_parts.add_closet_array_part(self)
        h_cubby.loc_x(value = 0)
        h_cubby.loc_y('setback',[setback])
        h_cubby.loc_z(start_placement + '+(' + v_spacing + ')',[placement,height,c_height,h_qty,s_thickness])
        h_cubby.rot_x(value = 0)
        h_cubby.rot_y(value = 0)
        h_cubby.rot_z(value = 0)
        h_cubby.dim_x('width',[width])
        h_cubby.dim_y('depth-setback',[depth,setback])
        h_cubby.dim_z('s_thickness',[s_thickness])
        qty = h_cubby.get_prompt('Z Quantity')
        offset = h_cubby.get_prompt('Z Offset')
        qty.set_formula('h_qty',[h_qty])
        offset.set_formula(v_spacing + '+s_thickness',[placement,height,c_height,h_qty,s_thickness])

    def render(self):
        self.pre_draw()
        self.draw()