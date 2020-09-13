import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinet_parts
from .. import home_builder_utils
from . import common_prompts
from os import path

class Vertical_Splitter(pc_types.Assembly):

    vertical_openings = 2 #2-10

    opening_1_height = 0
    opening_2_height = 0
    opening_3_height = 0
    opening_4_height = 0
    opening_5_height = 0
    opening_6_height = 0
    opening_7_height = 0
    opening_8_height = 0
    opening_9_height = 0
    opening_10_height = 0
    
    remove_splitter_1 = False
    remove_splitter_2 = False
    remove_splitter_3 = False
    remove_splitter_4 = False
    remove_splitter_5 = False
    remove_splitter_6 = False
    remove_splitter_7 = False
    remove_splitter_8 = False
    remove_splitter_9 = False
    
    interior_1 = None
    exterior_1 = None
    interior_2 = None
    exterior_2 = None
    interior_3 = None
    exterior_3 = None
    interior_4 = None
    exterior_4 = None
    interior_5 = None
    exterior_5 = None
    interior_6 = None
    exterior_6 = None
    interior_7 = None
    exterior_7 = None
    interior_8 = None
    exterior_8 = None
    interior_9 = None
    exterior_9 = None
    interior_10 = None
    exterior_10 = None
    interior_11 = None
    exterior_11 = None

    def add_insert(self,assembly,index,z_loc_expression="",z_loc_vars=[]):
        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')

        calculator = self.get_calculator("Opening Height Calculator")
        prompt = calculator.get_calculator_prompt("Opening " + str(index) + " Height")
        opening_height_var = prompt.get_var(calculator.name,"opening_" + str(index) + "_height")
        z_dim_expression = "opening_" + str(index) + "_height"

        if assembly:
            assembly = self.add_assembly(assembly)
            assembly.loc_x(value = 0)
            assembly.loc_y(value = 0)
            if index == self.vertical_openings:
                assembly.loc_z(value = 0)
            else:
                assembly.loc_z(z_loc_expression,z_loc_vars)
            assembly.rot_x(value = 0)
            assembly.rot_y(value = 0)
            assembly.rot_z(value = 0)
            assembly.dim_x('width',[width])
            assembly.dim_y('depth',[depth])
            assembly.dim_z(z_dim_expression,[opening_height_var])

            # calculator = assembly.get_calculator('Front Height Calculator')
            # if calculator:
            #     calculator.calculate()

            # if index == 1:
            #     # ALLOW DOOR TO EXTEND TO TOP OF VALANCE
            #     extend_top_amount = assembly.get_prompt("Extend Top Amount")
            #     if extend_top_amount:
            #         Extend_Top_Amount = self.get_var("Extend Top Amount")
            #         assembly.prompt('Extend Top Amount','Extend_Top_Amount',[Extend_Top_Amount])
            
            # if index == self.vertical_openings:
            #     # ALLOW DOOR TO EXTEND TO BOTTOM OF VALANCE
            #     extend_bottom_amount = assembly.get_prompt("Extend Bottom Amount")
            #     if extend_bottom_amount:
            #         Extend_Bottom_Amount = self.get_var("Extend Bottom Amount")
            #         assembly.prompt('Extend Bottom Amount','Extend_Bottom_Amount',[Extend_Bottom_Amount])

    def add_splitters(self):
        thickness = self.get_prompt('Thickness').get_var("thickness")
        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        previous_splitter = None

        calculator = self.get_calculator("Opening Height Calculator")

        for i in range(1,self.vertical_openings):
            prompt = eval("calculator.get_calculator_prompt('Opening " + str(i) + " Height')")

            z_loc_vars = []
            open_var = eval("prompt.get_var(calculator.name,'opening_" + str(i) + "_height')")
            z_loc_vars.append(open_var)
            
            if previous_splitter:
                z_loc = previous_splitter.obj_bp.pyclone.get_var("location.z","splitter_z_loc")
                z_loc_vars.append(z_loc)

            splitter = data_cabinet_parts.add_carcass_part(self)
            splitter.set_name("Splitter " + str(i))
            splitter.loc_x(value = 0)
            splitter.loc_y(value = 0)
            if previous_splitter:
                z_loc_vars.append(thickness)
                splitter.loc_z('splitter_z_loc-opening_' + str(i) + '_height-thickness',z_loc_vars)
            else:
                z_loc_vars.append(height)
                splitter.loc_z('height-opening_' + str(i) + '_height',z_loc_vars)
            splitter.rot_x(value = 0)
            splitter.rot_y(value = 0)
            splitter.rot_z(value = 0)
            splitter.dim_x('width',[width])
            splitter.dim_y('depth',[depth])
            splitter.dim_z('-thickness',[thickness])
            remove_splitter = eval("self.remove_splitter_" + str(i))
            if remove_splitter:
                hide = self.get_prompt('Hide')
                hide.set_value(True)
            
            previous_splitter = splitter

            opening_z_loc_vars = []
            opening_z_loc = splitter.obj_bp.pyclone.get_var("location.z","splitter_z_loc")
            opening_z_loc_vars.append(opening_z_loc)

            exterior = eval('self.exterior_' + str(i))
            self.add_insert(exterior, i, "splitter_z_loc", opening_z_loc_vars)            

        #LAST EXTERIOR
        exterior = eval('self.exterior_' + str(self.vertical_openings))
        self.add_insert(exterior, self.vertical_openings, "splitter_z_loc", opening_z_loc_vars)  

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Vertical Splitter")
        self.obj_bp["IS_VERTICAL_SPLITTER_BP"] = True

        common_prompts.add_cabinet_prompts(self)
        common_prompts.add_splitter_prompts(self)

        calc_distance_obj = self.add_empty('Calc Distance Obj')
        calc_distance_obj.empty_display_size = .001

        opening_height_calculator = self.obj_prompts.pyclone.add_calculator("Opening Height Calculator",calc_distance_obj)

        thickness = self.get_prompt('Thickness').get_var("thickness")
        height = self.obj_z.pyclone.get_var('location.z','height')

        opening_height_calculator.set_total_distance("height-thickness*(" + str(self.vertical_openings) +"-1)",[thickness,height])

        for i in range(1,self.vertical_openings+1):
            size = eval("self.opening_" + str(i) + "_height")
            prompt = opening_height_calculator.add_calculator_prompt('Opening ' + str(i) + ' Height')
            if size == 0:
                prompt.equal = True
            else:
                prompt.distance_value = size

        self.add_splitters()