import bpy
import time
import math
from os import path
from ..pc_lib import pc_types, pc_unit, pc_utils

from . import common_prompts
from . import data_cabinet_parts
from .. import home_builder_utils
from .. import home_builder_pointers
from .. import home_builder_paths

class Wood_Drawer_Box(pc_types.Assembly):

    def draw(self):
        self.create_assembly()
        self.obj_bp["IS_DRAWER_BOX_BP"] = True
        self.set_name("Wood Drawer Box")

        self.add_prompt("Hide",'CHECKBOX',False)
        self.add_prompt("Drawer Side Thickness",'DISTANCE',pc_unit.inch(.75))
        self.add_prompt("Front Back Thickness",'DISTANCE',pc_unit.inch(.75))
        self.add_prompt("Drawer Bottom Thickness",'DISTANCE',pc_unit.inch(.25))
        self.add_prompt("Drawer Box Bottom Dado Depth",'DISTANCE',pc_unit.inch(.25))
        self.add_prompt("Drawer Bottom Z Location",'DISTANCE',pc_unit.inch(.5))
        self.add_prompt("Drawer Slide Gap",'DISTANCE',pc_unit.inch(.25))
        self.add_prompt("Drawer Top Gap",'DISTANCE',pc_unit.inch(1))
        self.add_prompt("Drawer Bottom Gap",'DISTANCE',pc_unit.inch(1))
        self.add_prompt("Left Overlay",'DISTANCE',0)
        self.add_prompt("Right Overlay",'DISTANCE',0)
        self.add_prompt("Top Overlay",'DISTANCE',0)
        self.add_prompt("Bottom Overlay",'DISTANCE',0)

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        h = self.get_prompt("Hide").get_var('h')
        dt = self.get_prompt("Drawer Side Thickness").get_var('dt')
        fbt = self.get_prompt("Front Back Thickness").get_var('fbt')
        bt = self.get_prompt("Drawer Bottom Thickness").get_var('bt')
        dado_depth = self.get_prompt("Drawer Box Bottom Dado Depth").get_var('dado_depth')
        b_z_loc = self.get_prompt("Drawer Bottom Z Location").get_var('b_z_loc')
        slide_gap = self.get_prompt("Drawer Slide Gap").get_var('slide_gap')
        lo = self.get_prompt("Left Overlay").get_var('lo')
        ro = self.get_prompt("Right Overlay").get_var('ro')
        to = self.get_prompt("Top Overlay").get_var('to')
        bo = self.get_prompt("Bottom Overlay").get_var('bo')
        t_gap = self.get_prompt("Drawer Top Gap").get_var('t_gap')
        b_gap = self.get_prompt("Drawer Bottom Gap").get_var('b_gap')

        left_side = data_cabinet_parts.add_cabinet_shelf(self)
        left_side.obj_bp['IS_CUTPART_BP'] = True
        left_side.obj_bp['IS_LEFT_DRAWER_SIDE_BP'] = True
        left_side.set_name("Left Drawer Side")
        left_side.loc_x('lo+slide_gap',[lo,slide_gap])
        left_side.loc_y(value = 0)
        left_side.loc_z('bo+b_gap',[bo,b_gap])
        left_side.rot_x(value = math.radians(90))
        left_side.rot_y(value = 0)
        left_side.rot_z(value = math.radians(90))
        left_side.dim_x('depth',[depth])
        left_side.dim_y('height-to-bo-t_gap-b_gap',[height,to,bo,t_gap,b_gap])
        left_side.dim_z('dt',[dt])

        right_side = data_cabinet_parts.add_cabinet_shelf(self)
        right_side.obj_bp['IS_CUTPART_BP'] = True
        right_side.set_name("Right Drawer Side")
        right_side.obj_bp['IS_RIGHT_DRAWER_SIDE_BP'] = True
        right_side.loc_x('width-ro-slide_gap',[width,ro,slide_gap])
        right_side.loc_y(value = 0)
        right_side.loc_z('bo+b_gap',[bo,b_gap])
        right_side.rot_x(value = math.radians(90))
        right_side.rot_y(value = 0)
        right_side.rot_z(value = math.radians(90))
        right_side.dim_x('depth',[depth])
        right_side.dim_y('height-to-bo-t_gap-b_gap',[height,to,bo,t_gap,b_gap])
        right_side.dim_z('-dt',[dt])          

        front = data_cabinet_parts.add_cabinet_shelf(self)
        front.obj_bp['IS_CUTPART_BP'] = True
        front.obj_bp['IS_DRAWER_SUB_FRONT_BP'] = True
        front.set_name("Drawer Front")
        front.loc_x('dt+lo+slide_gap',[dt,lo,slide_gap])
        front.loc_y(value = 0)
        front.loc_z('bo+b_gap',[bo,b_gap])
        front.rot_x(value = math.radians(90))
        front.rot_y(value = 0)
        front.rot_z(value = 0)
        front.dim_x('width-(dt*2)-lo-ro-(slide_gap*2)',[width,dt,lo,ro,slide_gap])
        front.dim_y('height-to-bo-t_gap-b_gap',[height,to,bo,t_gap,b_gap])
        front.dim_z('-fbt',[fbt])              

        back = data_cabinet_parts.add_cabinet_shelf(self)
        back.obj_bp['IS_CUTPART_BP'] = True
        back.obj_bp['IS_DRAWER_BACK_BP'] = True
        back.set_name("Drawer Back")
        back.loc_x('dt+lo+slide_gap',[dt,lo,slide_gap])
        back.loc_y('depth',[depth])
        back.loc_z('bo+b_gap',[bo,b_gap])
        back.rot_x(value = math.radians(90))
        back.rot_y(value = 0)
        back.rot_z(value = 0)
        back.dim_x('width-(dt*2)-lo-ro-(slide_gap*2)',[width,dt,lo,ro,slide_gap])
        back.dim_y('height-to-bo-t_gap-b_gap',[height,to,bo,t_gap,b_gap])
        back.dim_z('fbt',[fbt])            

        bottom = data_cabinet_parts.add_cabinet_shelf(self)
        bottom.obj_bp['IS_CUTPART_BP'] = True
        bottom.obj_bp['IS_DRAWER_BOTTOM_BP'] = True
        bottom.set_name("Drawer Bottom")
        bottom.loc_x('width-dt+dado_depth-slide_gap-ro',[width,dt,dado_depth,slide_gap,ro])
        bottom.loc_y('fbt-dado_depth',[fbt,dado_depth])
        bottom.loc_z('b_z_loc+bo+b_gap',[b_z_loc,bo,b_gap])
        bottom.rot_x(value = 0)
        bottom.rot_y(value = 0)
        bottom.rot_z(value = math.radians(90))
        bottom.dim_x('depth-(fbt*2)+(dado_depth*2)',[depth,fbt,dado_depth])
        bottom.dim_y('width-(dt*2)+(dado_depth*2)-lo-ro-(slide_gap*2)',[width,dt,dado_depth,lo,ro,slide_gap])
        bottom.dim_z('-bt',[bt])            


class BLUM_Metabox_Static(pc_types.Assembly):

    opening_height = 0
    opening_depth = 0

    N_HEIGHT = pc_unit.inch(2.125)
    M_HEIGHT = pc_unit.inch(3.375)
    K_HEIGHT = pc_unit.inch(4.625)
    H_HEIGHT = pc_unit.inch(5.875)

    LENGTH_270 = pc_unit.millimeter(270)
    LENGTH_350 = pc_unit.millimeter(350)
    LENGTH_400 = pc_unit.millimeter(400)
    LENGTH_450 = pc_unit.millimeter(450)
    LENGTH_500 = pc_unit.millimeter(500)
    LENGTH_550 = pc_unit.millimeter(550)

    def get_side_size(self,opening_height,opening_depth):
        height_name = self.get_prompt("Height Name")
        length_name = self.get_prompt("Length Name")

        if opening_height >= pc_unit.inch(6.81):
            
            if opening_depth >= pc_unit.inch(21.77855):
                height_name.set_value("H")
                length_name.set_value("550")
                return self.H_HEIGHT, self.LENGTH_550
            if opening_depth >= pc_unit.inch(19.81005):
                height_name.set_value("H")
                length_name.set_value("500")
                return self.H_HEIGHT, self.LENGTH_500
            if opening_depth >= pc_unit.inch(17.84154):
                height_name.set_value("H")
                length_name.set_value("450")
                return self.H_HEIGHT, self.LENGTH_450
            if opening_depth >= pc_unit.inch(15.87304):
                height_name.set_value("H")
                length_name.set_value("400")
                return self.H_HEIGHT, self.LENGTH_400
            if opening_depth >= pc_unit.inch(13.90453937):
                height_name.set_value("H")
                length_name.set_value("350")
                return self.H_HEIGHT, self.LENGTH_350
            if opening_depth >= pc_unit.inch(10.75493):
                height_name.set_value("M")
                length_name.set_value("270")
                return self.M_HEIGHT, self.LENGTH_270              
        if opening_height >= pc_unit.inch(5.55):
            if opening_depth >= pc_unit.inch(21.77855):
                height_name.set_value("K")
                length_name.set_value("550")
                return self.K_HEIGHT, self.LENGTH_550
            if opening_depth >= pc_unit.inch(19.81005):
                height_name.set_value("K")
                length_name.set_value("500")
                return self.K_HEIGHT, self.LENGTH_500
            if opening_depth >= pc_unit.inch(17.84154):
                height_name.set_value("K")
                length_name.set_value("450")
                return self.K_HEIGHT, self.LENGTH_450
            if opening_depth >= pc_unit.inch(15.87304):
                height_name.set_value("K")
                length_name.set_value("400")
                return self.K_HEIGHT, self.LENGTH_400
            if opening_depth >= pc_unit.inch(13.90453937):
                height_name.set_value("K")
                length_name.set_value("350")
                return self.K_HEIGHT, self.LENGTH_350
            if opening_depth >= pc_unit.inch(10.75493):
                height_name.set_value("M")
                length_name.set_value("270")
                return self.M_HEIGHT, self.LENGTH_270    
        if opening_height >= pc_unit.inch(4.28):
            if opening_depth >= pc_unit.inch(21.77855):
                height_name.set_value("N")
                length_name.set_value("550")
                return self.N_HEIGHT, self.LENGTH_550
            if opening_depth >= pc_unit.inch(19.81005):
                height_name.set_value("N")
                length_name.set_value("500")
                return self.N_HEIGHT, self.LENGTH_500
            if opening_depth >= pc_unit.inch(17.84154):
                height_name.set_value("N")
                length_name.set_value("450")
                return self.N_HEIGHT, self.LENGTH_450
            if opening_depth >= pc_unit.inch(15.87304):
                height_name.set_value("N")
                length_name.set_value("400")
                return self.N_HEIGHT, self.LENGTH_400
            if opening_depth >= pc_unit.inch(13.90453937):
                height_name.set_value("N")
                length_name.set_value("350")
                return self.N_HEIGHT, self.LENGTH_350
            if opening_depth >= pc_unit.inch(10.75493):
                return 0, 0 
        if opening_height >= pc_unit.inch(3.03):
            return 0, 0
        return 0, 0

    def set_size(self,opening_height,opening_depth):
        self.opening_height = opening_height
        self.opening_depth = opening_depth

    def draw(self):
        self.create_assembly()
        self.obj_bp["IS_DRAWER_BOX_BP"] = True
        self.obj_bp["IS_METABOX_BP"] = True
        self.set_name("BLUM Metabox")

        self.add_prompt("Hide",'CHECKBOX',False)
        self.add_prompt("Drawer Side Thickness",'DISTANCE',pc_unit.inch(.1181))
        self.add_prompt("Front Back Thickness",'DISTANCE',pc_unit.inch(.75))
        self.add_prompt("Drawer Bottom Thickness",'DISTANCE',pc_unit.inch(.75))
        self.add_prompt("Drawer Slide Gap",'DISTANCE',pc_unit.millimeter(31))
        self.add_prompt("Drawer Top Gap",'DISTANCE',pc_unit.inch(1))
        self.add_prompt("Drawer Bottom Gap",'DISTANCE',pc_unit.millimeter(5))
        self.add_prompt("Height Name",'TEXT',"")
        self.add_prompt("Length Name",'TEXT',"")
        self.add_prompt("Left Overlay",'DISTANCE',0).get_var('lo')
        self.add_prompt("Right Overlay",'DISTANCE',0).get_var('ro')
        self.add_prompt("Top Overlay",'DISTANCE',0).get_var('to')
        self.add_prompt("Bottom Overlay",'DISTANCE',0).get_var('bo')

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        lo = self.get_prompt("Left Overlay").get_var("lo")
        ro = self.get_prompt("Right Overlay").get_var("ro")
        to = self.get_prompt("Top Overlay").get_var("to")
        bo = self.get_prompt("Bottom Overlay").get_var("bo")
        dt = self.get_prompt("Drawer Side Thickness").get_var('dt')
        fbt = self.get_prompt("Front Back Thickness").get_var('fbt')
        bt = self.get_prompt("Drawer Bottom Thickness").get_var('bt')
        slide_gap = self.get_prompt("Drawer Slide Gap").get_var('slide_gap')
        height_name = self.get_prompt("Height Name")
        length_name = self.get_prompt("Length Name")
        b_thickness = self.get_prompt("Drawer Bottom Thickness").get_value()
        b_gap = self.get_prompt("Drawer Bottom Gap").get_var('b_gap')
        t_gap = self.get_prompt("Drawer Top Gap").get_var('t_gap')
        
        height, depth = self.get_side_size(self.opening_height,self.opening_depth)

        side_name = "Blum Metabox Side " + height_name.get_value() + " " + length_name.get_value() + "mm Left.blend"
        left_side = data_cabinet_parts.add_empty_assembly(self)
        left_side.obj_bp['IS_CUTPART_BP'] = True
        left_side.obj_bp['IS_DUMMY_PART'] = True
        left_side.obj_bp['IS_LEFT_DRAWER_SIDE_BP'] = True
        left_side.obj_bp['IS_METABOX_PART'] = True
        left_side.set_name("Left Drawer Side")
        # left_side.loc_x('lo+slide_gap',[lo,slide_gap])
        left_side.loc_x('lo+.0254',[lo])
        left_side.loc_y(value = 0)
        left_side.loc_z('bo+b_gap',[bo,b_gap])
        left_side.rot_x(value = math.radians(90))
        left_side.rot_y(value = 0)
        left_side.rot_z(value = math.radians(90))
        left_side.dim_x(value = depth)
        left_side.dim_y(value = height)
        left_side.dim_z('dt',[dt])
        if path.exists(path.join(home_builder_paths.get_metabox_hardware_path(),side_name)):
            obj = left_side.add_object_from_file(path.join(home_builder_paths.get_metabox_hardware_path(),side_name))
            obj.location = (0.000927,-0.002275,-0.025467)
            obj.rotation_euler.x = math.radians(-90)
            obj.rotation_euler.y = math.radians(-90)
        if path.exists(path.join(home_builder_paths.get_metabox_hardware_path(),"Fixing Bracket Blum Metabox Expando Dowel Left.blend")):
            obj = left_side.add_object_from_file(path.join(home_builder_paths.get_metabox_hardware_path(),"Fixing Bracket Blum Metabox Expando Dowel Left.blend"))
            obj.location = (-0.010486,0.028922,-0.023583)
            obj.rotation_euler.x = math.radians(-90)
            obj.rotation_euler.y = math.radians(-90)

        right_side = data_cabinet_parts.add_empty_assembly(self)
        right_side.obj_bp['IS_CUTPART_BP'] = True
        right_side.obj_bp['IS_DUMMY_PART'] = True
        right_side.obj_bp['IS_RIGHT_DRAWER_SIDE_BP'] = True
        right_side.obj_bp['IS_METABOX_PART'] = True
        right_side.set_name("Right Drawer Side")
        # right_side.loc_x('width-ro-slide_gap',[width,ro,slide_gap])
        right_side.loc_x('width-ro-.0254',[width,ro])
        right_side.loc_y(value = 0)
        right_side.loc_z('bo+b_gap',[bo,b_gap])
        right_side.rot_x(value = math.radians(90))
        right_side.rot_y(value = 0)
        right_side.rot_z(value = math.radians(90))
        right_side.dim_x(value = depth)
        right_side.dim_y(value = height)
        right_side.dim_z('-dt',[dt])
        if path.exists(path.join(home_builder_paths.get_metabox_hardware_path(),side_name)):
            obj = right_side.add_object_from_file(path.join(home_builder_paths.get_metabox_hardware_path(),side_name))
            obj.location = (0.000927,-0.002275,0.025467)
            obj.scale.x = -1
            obj.rotation_euler.x = math.radians(-90)
            obj.rotation_euler.y = math.radians(-90)
        if path.exists(path.join(home_builder_paths.get_metabox_hardware_path(),"Fixing Bracket Blum Metabox Expando Dowel Left.blend")):
            obj = right_side.add_object_from_file(path.join(home_builder_paths.get_metabox_hardware_path(),"Fixing Bracket Blum Metabox Expando Dowel Left.blend"))
            obj.scale.x = -1
            obj.location = (-0.010486,0.028922,0.023583)
            obj.rotation_euler.x = math.radians(-90)
            obj.rotation_euler.y = math.radians(-90)

        back = data_cabinet_parts.add_cabinet_shelf(self)
        props = home_builder_utils.get_object_props(back.obj_bp)
        props.ebl1 = True        
        back.obj_bp['IS_CUTPART_BP'] = True
        back.obj_bp['IS_DRAWER_BACK_BP'] = True
        back.obj_bp['IS_METABOX_PART'] = True
        back.set_name("Metabox Drawer Back " + height_name.get_value())
        back.loc_x('lo+(slide_gap/2)',[lo,slide_gap])
        back.loc_y(value=depth)
        back.loc_z('bo+b_gap+bt',[bo,b_gap,bt])
        back.rot_x(value = math.radians(90))
        back.rot_y(value = 0)
        back.rot_z(value = 0)
        back.dim_x('width-lo-ro-slide_gap',[width,lo,ro,slide_gap])
        back.dim_y(value=height-b_thickness)
        back.dim_z('fbt',[fbt])            

        bottom = data_cabinet_parts.add_cabinet_shelf(self)
        bottom.obj_bp['IS_CUTPART_BP'] = True
        bottom.obj_bp['IS_DRAWER_BOTTOM_BP'] = True
        bottom.obj_bp['IS_METABOX_PART'] = True
        bottom.set_name("Drawer Bottom")
        bottom.loc_x('width-(slide_gap/2)-ro',[width,slide_gap,ro])
        bottom.loc_y(value = 0)
        bottom.loc_z('bo+b_gap',[bo,b_gap])
        bottom.rot_x(value = 0)
        bottom.rot_y(value = 0)
        bottom.rot_z(value = math.radians(90))
        bottom.dim_x(value = depth - pc_unit.millimeter(2))
        bottom.dim_y('width-lo-ro-slide_gap',[width,lo,ro,slide_gap])
        bottom.dim_z('bt',[bt])


class BLUM_Tandembox_Static(pc_types.Assembly):

    opening_height = 0
    opening_depth = 0

    N_HEIGHT = pc_unit.millimeter(69)
    M_HEIGHT = pc_unit.millimeter(84)
    B_HEIGHT = pc_unit.millimeter(146)
    D_HEIGHT = pc_unit.millimeter(207)

    LENGTH_270 = pc_unit.millimeter(270)
    LENGTH_350 = pc_unit.millimeter(350)
    LENGTH_400 = pc_unit.millimeter(400)
    LENGTH_450 = pc_unit.millimeter(450)
    LENGTH_500 = pc_unit.millimeter(500)
    LENGTH_550 = pc_unit.millimeter(550)

    def get_side_size(self,opening_height,opening_depth):
        height_name = self.get_prompt("Height Name")
        length_name = self.get_prompt("Length Name")

        if opening_height >= pc_unit.inch(9.33):
            
            if opening_depth >= pc_unit.inch(21.77855):
                height_name.set_value("D")
                length_name.set_value("550")
                return self.D_HEIGHT, self.LENGTH_550
            if opening_depth >= pc_unit.inch(19.81005):
                height_name.set_value("D")
                length_name.set_value("500")
                return self.D_HEIGHT, self.LENGTH_500
            if opening_depth >= pc_unit.inch(17.84154):
                height_name.set_value("D")
                length_name.set_value("450")
                return self.D_HEIGHT, self.LENGTH_450
            if opening_depth >= pc_unit.inch(15.87304):
                height_name.set_value("D")
                length_name.set_value("400")
                return self.D_HEIGHT, self.LENGTH_400
            if opening_depth >= pc_unit.inch(13.90453937):
                height_name.set_value("D")
                length_name.set_value("350")
                return self.D_HEIGHT, self.LENGTH_350
            if opening_depth >= pc_unit.inch(10.75493):
                height_name.set_value("M")
                length_name.set_value("270")
                return self.M_HEIGHT, self.LENGTH_270              
        if opening_height >= pc_unit.inch(6.81):
            if opening_depth >= pc_unit.inch(21.77855):
                height_name.set_value("B")
                length_name.set_value("550")
                return self.B_HEIGHT, self.LENGTH_550
            if opening_depth >= pc_unit.inch(19.81005):
                height_name.set_value("B")
                length_name.set_value("500")
                return self.B_HEIGHT, self.LENGTH_500
            if opening_depth >= pc_unit.inch(17.84154):
                height_name.set_value("B")
                length_name.set_value("450")
                return self.B_HEIGHT, self.LENGTH_450
            if opening_depth >= pc_unit.inch(15.87304):
                height_name.set_value("B")
                length_name.set_value("400")
                return self.B_HEIGHT, self.LENGTH_400
            if opening_depth >= pc_unit.inch(13.90453937):
                height_name.set_value("B")
                length_name.set_value("350")
                return self.B_HEIGHT, self.LENGTH_350
            if opening_depth >= pc_unit.inch(10.75493):
                height_name.set_value("M")
                length_name.set_value("270")
                return self.M_HEIGHT, self.LENGTH_270    
        if opening_height >= pc_unit.inch(4.28):
            if opening_depth >= pc_unit.inch(21.77855):
                height_name.set_value("M")
                length_name.set_value("550")
                return self.N_HEIGHT, self.LENGTH_550
            if opening_depth >= pc_unit.inch(19.81005):
                height_name.set_value("M")
                length_name.set_value("500")
                return self.N_HEIGHT, self.LENGTH_500
            if opening_depth >= pc_unit.inch(17.84154):
                height_name.set_value("M")
                length_name.set_value("450")
                return self.N_HEIGHT, self.LENGTH_450
            if opening_depth >= pc_unit.inch(15.87304):
                height_name.set_value("M")
                length_name.set_value("400")
                return self.N_HEIGHT, self.LENGTH_400
            if opening_depth >= pc_unit.inch(13.90453937):
                height_name.set_value("M")
                length_name.set_value("350")
                return self.N_HEIGHT, self.LENGTH_350
            if opening_depth >= pc_unit.inch(10.75493):
                return 0, 0 
        if opening_height >= pc_unit.inch(3.03):
            return 0, 0
        return 0, 0

    def set_size(self,opening_height,opening_depth):
        self.opening_height = opening_height
        self.opening_depth = opening_depth

    def draw(self):
        self.create_assembly()
        self.obj_bp["IS_DRAWER_BOX_BP"] = True
        self.obj_bp["IS_TANDEMBOX_BP"] = True
        self.set_name("BLUM Tandembox")

        self.add_prompt("Hide",'CHECKBOX',False)
        self.add_prompt("Drawer Side Thickness",'DISTANCE',pc_unit.inch(.1181))
        self.add_prompt("Front Back Thickness",'DISTANCE',pc_unit.inch(.625))
        self.add_prompt("Drawer Bottom Thickness",'DISTANCE',pc_unit.inch(.625))
        self.add_prompt("Drawer Slide Gap",'DISTANCE',pc_unit.millimeter(31))
        self.add_prompt("Drawer Top Gap",'DISTANCE',pc_unit.inch(1))
        self.add_prompt("Drawer Bottom Gap",'DISTANCE',pc_unit.millimeter(9))
        self.add_prompt("Drawer Back Width Deduction",'DISTANCE',pc_unit.millimeter(87))
        self.add_prompt("Drawer Bottom Width Deduction",'DISTANCE',pc_unit.millimeter(75))
        self.add_prompt("Height Name",'TEXT',"")
        self.add_prompt("Length Name",'TEXT',"")
        self.add_prompt("Left Overlay",'DISTANCE',0).get_var('lo')
        self.add_prompt("Right Overlay",'DISTANCE',0).get_var('ro')
        self.add_prompt("Top Overlay",'DISTANCE',0).get_var('to')
        self.add_prompt("Bottom Overlay",'DISTANCE',0).get_var('bo')

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        lo = self.get_prompt("Left Overlay").get_var("lo")
        ro = self.get_prompt("Right Overlay").get_var("ro")
        to = self.get_prompt("Top Overlay").get_var("to")
        bo = self.get_prompt("Bottom Overlay").get_var("bo")
        dt = self.get_prompt("Drawer Side Thickness").get_var('dt')
        fbt = self.get_prompt("Front Back Thickness").get_var('fbt')
        bt = self.get_prompt("Drawer Bottom Thickness").get_var('bt')
        slide_gap = self.get_prompt("Drawer Slide Gap").get_var('slide_gap')
        height_name = self.get_prompt("Height Name")
        length_name = self.get_prompt("Length Name")
        b_thickness = self.get_prompt("Drawer Bottom Thickness").get_value()
        b_gap = self.get_prompt("Drawer Bottom Gap").get_var('b_gap')
        t_gap = self.get_prompt("Drawer Top Gap").get_var('t_gap')
        back_deduction = self.get_prompt("Drawer Back Width Deduction").get_var('back_deduction')
        bottom_deduction = self.get_prompt("Drawer Bottom Width Deduction").get_var('bottom_deduction')
        
        height, depth = self.get_side_size(self.opening_height,self.opening_depth)

        back_height = 0
        if height_name.get_value() == 'N':
            back_height = pc_unit.millimeter(69)
        if height_name.get_value() == 'M':
            back_height = pc_unit.millimeter(84)
        if height_name.get_value() == 'B':
            back_height = pc_unit.millimeter(135)
        if height_name.get_value() == 'D':
            back_height = pc_unit.millimeter(199)

        left_side = data_cabinet_parts.add_cabinet_shelf(self)
        left_side.obj_bp['IS_CUTPART_BP'] = True
        left_side.obj_bp['IS_DUMMY_PART'] = True
        left_side.obj_bp['IS_LEFT_DRAWER_SIDE_BP'] = True
        left_side.obj_bp['IS_TANDEMBOX_PART'] = True
        left_side.set_name("Left Drawer Side")
        # left_side.loc_x('lo+slide_gap',[lo,slide_gap])
        left_side.loc_x('lo+.0254',[lo])
        left_side.loc_y(value = 0)
        left_side.loc_z('bo+b_gap',[bo,b_gap])
        left_side.rot_x(value = math.radians(90))
        left_side.rot_y(value = 0)
        left_side.rot_z(value = math.radians(90))
        left_side.dim_x(value = depth)
        left_side.dim_y(value = height)
        left_side.dim_z('dt',[dt])

        right_side = data_cabinet_parts.add_cabinet_shelf(self)
        right_side.obj_bp['IS_CUTPART_BP'] = True
        right_side.obj_bp['IS_DUMMY_PART'] = True
        right_side.obj_bp['IS_RIGHT_DRAWER_SIDE_BP'] = True
        right_side.obj_bp['IS_TANDEMBOX_PART'] = True
        right_side.set_name("Right Drawer Side")
        # right_side.loc_x('width-ro-slide_gap',[width,ro,slide_gap])
        right_side.loc_x('width-ro-.0254',[width,ro])
        right_side.loc_y(value = 0)
        right_side.loc_z('bo+b_gap',[bo,b_gap])
        right_side.rot_x(value = math.radians(90))
        right_side.rot_y(value = 0)
        right_side.rot_z(value = math.radians(90))
        right_side.dim_x(value = depth)
        right_side.dim_y(value = height)
        right_side.dim_z('-dt',[dt])

        back = data_cabinet_parts.add_cabinet_shelf(self)
        props = home_builder_utils.get_object_props(back.obj_bp)
        props.ebl1 = True        
        back.obj_bp['IS_CUTPART_BP'] = True
        back.obj_bp['IS_DRAWER_BACK_BP'] = True
        back.obj_bp['IS_TANDEMBOX_PART'] = True
        back.set_name("Tandembox Drawer Back " + height_name.get_value())
        back.loc_x('lo+(back_deduction/2)',[lo,back_deduction])
        back.loc_y(value=depth)
        back.loc_z('bo+b_gap',[bo,b_gap])
        back.rot_x(value = math.radians(90))
        back.rot_y(value = 0)
        back.rot_z(value = 0)
        back.dim_x('width-lo-ro-back_deduction',[width,lo,ro,back_deduction])
        back.dim_y(value=back_height)
        back.dim_z('fbt',[fbt])            

        bottom = data_cabinet_parts.add_cabinet_shelf(self)
        bottom.obj_bp['IS_CUTPART_BP'] = True
        bottom.obj_bp['IS_DRAWER_BOTTOM_BP'] = True
        bottom.obj_bp['IS_TANDEMBOX_PART'] = True
        bottom.set_name("Tandem Drawer Bottom")
        bottom.loc_x('width-(bottom_deduction/2)-ro',[width,bottom_deduction,ro])
        bottom.loc_y(value = 0)
        bottom.loc_z('bo+b_gap',[bo,b_gap])
        bottom.rot_x(value = 0)
        bottom.rot_y(value = 0)
        bottom.rot_z(value = math.radians(90))
        bottom.dim_x(value = depth - pc_unit.millimeter(24))
        bottom.dim_y('width-lo-ro-bottom_deduction',[width,lo,ro,bottom_deduction])
        bottom.dim_z('bt',[bt])


class HETTICH_AvanTech_You(pc_types.Assembly):

    opening_height = 0
    opening_depth = 0

    HEIGHT_77 = pc_unit.millimeter(77)
    HEIGHT_101 = pc_unit.millimeter(101)
    HEIGHT_139 = pc_unit.millimeter(139)
    HEIGHT_187 = pc_unit.millimeter(187)
    HEIGHT_251 = pc_unit.millimeter(251)

    LENGTH_270 = pc_unit.millimeter(270)
    LENGTH_300 = pc_unit.millimeter(300)
    LENGTH_350 = pc_unit.millimeter(350)
    LENGTH_400 = pc_unit.millimeter(400)
    LENGTH_450 = pc_unit.millimeter(450)
    LENGTH_500 = pc_unit.millimeter(500)
    LENGTH_550 = pc_unit.millimeter(550)
    LENGTH_600 = pc_unit.millimeter(600)

    def get_side_size(self,opening_height,opening_depth):
        height_name = self.get_prompt("Height Name")
        length_name = self.get_prompt("Length Name")            
        if opening_height >= pc_unit.inch(10.59):
            if opening_depth >= pc_unit.inch(23.80954724):
                height_name.set_value("139")
                length_name.set_value("600")
                return self.HEIGHT_139, self.LENGTH_600
            if opening_depth >= pc_unit.inch(21.84104331):
                height_name.set_value("139")
                length_name.set_value("550")
                return self.HEIGHT_139, self.LENGTH_550
            if opening_depth >= pc_unit.inch(19.87253937):
                height_name.set_value("251")
                length_name.set_value("500")
                return self.HEIGHT_251, self.LENGTH_500
            if opening_depth >= pc_unit.inch(17.90403543):
                height_name.set_value("251")
                length_name.set_value("450")
                return self.HEIGHT_251, self.LENGTH_450
            if opening_depth >= pc_unit.inch(15.9355315):
                height_name.set_value("251")
                length_name.set_value("400")
                return self.HEIGHT_251, self.LENGTH_400
            if opening_depth >= pc_unit.inch(13.96702756):
                height_name.set_value("251")
                length_name.set_value("350")
                return self.HEIGHT_251, self.LENGTH_350         
            if opening_depth >= pc_unit.inch(11.99852362):
                height_name.set_value("139")
                length_name.set_value("300")
                return self.HEIGHT_139, self.LENGTH_300     
        if opening_height >= pc_unit.inch(8.06):
            if opening_depth >= pc_unit.inch(23.80954724):
                height_name.set_value("139")
                length_name.set_value("600")
                return self.HEIGHT_139, self.LENGTH_600
            if opening_depth >= pc_unit.inch(21.84104331):
                height_name.set_value("139")
                length_name.set_value("550")
                return self.HEIGHT_139, self.LENGTH_550
            if opening_depth >= pc_unit.inch(19.87253937):
                height_name.set_value("187")
                length_name.set_value("500")
                return self.HEIGHT_187, self.LENGTH_500
            if opening_depth >= pc_unit.inch(17.90403543):
                height_name.set_value("187")
                length_name.set_value("450")
                return self.HEIGHT_187, self.LENGTH_450
            if opening_depth >= pc_unit.inch(15.9355315):
                height_name.set_value("187")
                length_name.set_value("400")
                return self.HEIGHT_187, self.LENGTH_400
            if opening_depth >= pc_unit.inch(13.96702756):
                height_name.set_value("187")
                length_name.set_value("350")
                return self.HEIGHT_187, self.LENGTH_350         
            if opening_depth >= pc_unit.inch(11.99852362):
                height_name.set_value("139")
                length_name.set_value("300")
                return self.HEIGHT_139, self.LENGTH_300     
        if opening_height >= pc_unit.inch(5.55):
            if opening_depth >= pc_unit.inch(23.80954724):
                height_name.set_value("139")
                length_name.set_value("600")
                return self.HEIGHT_139, self.LENGTH_600
            if opening_depth >= pc_unit.inch(21.84104331):
                height_name.set_value("139")
                length_name.set_value("550")
                return self.HEIGHT_139, self.LENGTH_550
            if opening_depth >= pc_unit.inch(19.87253937):
                height_name.set_value("139")
                length_name.set_value("500")
                return self.HEIGHT_139, self.LENGTH_500
            if opening_depth >= pc_unit.inch(17.90403543):
                height_name.set_value("139")
                length_name.set_value("450")
                return self.HEIGHT_139, self.LENGTH_450
            if opening_depth >= pc_unit.inch(15.9355315):
                height_name.set_value("139")
                length_name.set_value("400")
                return self.HEIGHT_139, self.LENGTH_400
            if opening_depth >= pc_unit.inch(13.96702756):
                height_name.set_value("139")
                length_name.set_value("350")
                return self.HEIGHT_139, self.LENGTH_350         
            if opening_depth >= pc_unit.inch(11.99852362):
                height_name.set_value("139")
                length_name.set_value("300")
                return self.HEIGHT_139, self.LENGTH_300     
        if opening_height >= pc_unit.inch(3.25):
            if opening_depth >= pc_unit.inch(23.80954724):
                height_name.set_value("")
                length_name.set_value("")
                return 0, 0
            if opening_depth >= pc_unit.inch(21.84104331):
                height_name.set_value("")
                length_name.set_value("")
                return 0, 0
            if opening_depth >= pc_unit.inch(19.87253937):
                height_name.set_value("")
                length_name.set_value("")
                return 0, 0
            if opening_depth >= pc_unit.inch(17.90403543):
                height_name.set_value("101")
                length_name.set_value("450")
                return self.HEIGHT_101, self.LENGTH_450
            if opening_depth >= pc_unit.inch(15.9355315):
                height_name.set_value("101")
                length_name.set_value("400")
                return self.HEIGHT_101, self.LENGTH_400
            if opening_depth >= pc_unit.inch(13.96702756):
                height_name.set_value("101")
                length_name.set_value("350")
                return self.HEIGHT_101, self.LENGTH_350         
            if opening_depth >= pc_unit.inch(11.99852362):
                height_name.set_value("")
                length_name.set_value("")
                return 0, 0     
            if opening_depth >= pc_unit.inch(10.75493):
                return 0, 0 
        if opening_height >= pc_unit.inch(3.03):
            return 0, 0
        return 0, 0

    def set_size(self,opening_height,opening_depth):
        self.opening_height = opening_height
        self.opening_depth = opening_depth

    def draw(self):
        self.create_assembly()
        self.obj_bp["IS_DRAWER_BOX_BP"] = True
        self.obj_bp["IS_AVANTECH_BP"] = True
        self.set_name("HETTICH AvanTech You")

        self.add_prompt("Hide",'CHECKBOX',False)
        self.add_prompt("Drawer Side Thickness",'DISTANCE',pc_unit.inch(.1181))
        self.add_prompt("Front Back Thickness",'DISTANCE',pc_unit.inch(.625))
        self.add_prompt("Drawer Bottom Thickness",'DISTANCE',pc_unit.inch(.625))
        self.add_prompt("Drawer Slide Gap",'DISTANCE',pc_unit.millimeter(31))
        self.add_prompt("Drawer Top Gap",'DISTANCE',pc_unit.inch(.7087))
        self.add_prompt("Drawer Bottom Gap",'DISTANCE',pc_unit.inch(.1969))
        self.add_prompt("Bottom Z Location",'DISTANCE',pc_unit.inch(1.1319))
        self.add_prompt("Drawer Back Width Deduction",'DISTANCE',pc_unit.millimeter(24))
        self.add_prompt("Drawer Bottom Width Deduction",'DISTANCE',pc_unit.millimeter(24))
        self.add_prompt("Height Name",'TEXT',"")
        self.add_prompt("Length Name",'TEXT',"")
        self.add_prompt("Left Overlay",'DISTANCE',0).get_var('lo')
        self.add_prompt("Right Overlay",'DISTANCE',0).get_var('ro')
        self.add_prompt("Top Overlay",'DISTANCE',0).get_var('to')
        self.add_prompt("Bottom Overlay",'DISTANCE',0).get_var('bo')

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        lo = self.get_prompt("Left Overlay").get_var("lo")
        ro = self.get_prompt("Right Overlay").get_var("ro")
        to = self.get_prompt("Top Overlay").get_var("to")
        bo = self.get_prompt("Bottom Overlay").get_var("bo")
        dt = self.get_prompt("Drawer Side Thickness").get_var('dt')
        fbt = self.get_prompt("Front Back Thickness").get_var('fbt')
        bt = self.get_prompt("Drawer Bottom Thickness").get_var('bt')
        slide_gap = self.get_prompt("Drawer Slide Gap").get_var('slide_gap')
        height_name = self.get_prompt("Height Name")
        length_name = self.get_prompt("Length Name")
        b_thickness = self.get_prompt("Drawer Bottom Thickness").get_value()
        b_gap_prompt = self.get_prompt("Drawer Bottom Gap")
        b_gap = b_gap_prompt.get_var('b_gap')
        t_gap_prompt = self.get_prompt("Drawer Top Gap")
        t_gap = t_gap_prompt.get_var('b_gap')
        back_deduction = self.get_prompt("Drawer Back Width Deduction").get_var('back_deduction')
        bottom_deduction = self.get_prompt("Drawer Bottom Width Deduction").get_var('bottom_deduction')
        bot_z_loc_prompt = self.get_prompt("Bottom Z Location")
        bot_z_loc = bot_z_loc_prompt.get_var("bot_z_loc")

        opening_height = self.opening_height - b_gap_prompt.get_value() - t_gap_prompt.get_value()
        height, depth = self.get_side_size(opening_height,self.opening_depth)

        back_height = 0
        if height_name.get_value() == '77':
            back_height = pc_unit.millimeter(30)
        if height_name.get_value() == '101':
            back_height = pc_unit.millimeter(54)
        if height_name.get_value() == '139':
            back_height = pc_unit.millimeter(92)
        if height_name.get_value() == '187':
            back_height = pc_unit.millimeter(140.5)
        if height_name.get_value() == '251':
            back_height = pc_unit.millimeter(204.5)

        left_side = data_cabinet_parts.add_cabinet_shelf(self)
        left_side.obj_bp['IS_CUTPART_BP'] = True
        left_side.obj_bp['IS_DUMMY_PART'] = True
        left_side.obj_bp['IS_LEFT_DRAWER_SIDE_BP'] = True
        left_side.obj_bp['IS_AVANTECH_PART'] = True
        left_side.set_name("Left Drawer Side")
        # left_side.loc_x('lo+slide_gap',[lo,slide_gap])
        left_side.loc_x('lo+.0254',[lo])
        left_side.loc_y(value = 0)
        left_side.loc_z('bo+b_gap',[bo,b_gap])
        left_side.rot_x(value = math.radians(90))
        left_side.rot_y(value = 0)
        left_side.rot_z(value = math.radians(90))
        left_side.dim_x(value = depth)
        left_side.dim_y(value = height)
        left_side.dim_z('dt',[dt])

        right_side = data_cabinet_parts.add_cabinet_shelf(self)
        right_side.obj_bp['IS_CUTPART_BP'] = True
        right_side.obj_bp['IS_DUMMY_PART'] = True
        right_side.obj_bp['IS_RIGHT_DRAWER_SIDE_BP'] = True
        right_side.obj_bp['IS_AVANTECH_PART'] = True
        right_side.set_name("Right Drawer Side")
        # right_side.loc_x('width-ro-slide_gap',[width,ro,slide_gap])
        right_side.loc_x('width-ro-.0254',[width,ro])
        right_side.loc_y(value = 0)
        right_side.loc_z('bo+b_gap',[bo,b_gap])
        right_side.rot_x(value = math.radians(90))
        right_side.rot_y(value = 0)
        right_side.rot_z(value = math.radians(90))
        right_side.dim_x(value = depth)
        right_side.dim_y(value = height)
        right_side.dim_z('-dt',[dt])

        back = data_cabinet_parts.add_cabinet_shelf(self)
        props = home_builder_utils.get_object_props(back.obj_bp)
        props.ebl1 = True
        back.obj_bp['IS_CUTPART_BP'] = True
        back.obj_bp['IS_DRAWER_BACK_BP'] = True
        back.obj_bp['IS_AVANTECH_PART'] = True
        back.set_name("AvanTech Drawer Back " + height_name.get_value())
        back.loc_x('lo+(back_deduction/2)',[lo,back_deduction])
        back.loc_y(value=depth)
        back.loc_z('bo+b_gap+bt',[bo,b_gap,bt])
        back.rot_x(value = math.radians(90))
        back.rot_y(value = 0)
        back.rot_z(value = 0)
        back.dim_x('width-lo-ro-back_deduction',[width,lo,ro,back_deduction])
        back.dim_y(value=back_height)
        back.dim_z('fbt',[fbt])            

        bottom = data_cabinet_parts.add_cabinet_shelf(self)
        bottom.obj_bp['IS_CUTPART_BP'] = True
        bottom.obj_bp['IS_DRAWER_BOTTOM_BP'] = True
        bottom.obj_bp['IS_AVANTECH_PART'] = True
        bottom.set_name("AvanTech Drawer Bottom")
        bottom.loc_x('width-(bottom_deduction/2)-ro',[width,bottom_deduction,ro])
        bottom.loc_y(value = 0)
        bottom.loc_z('bo+b_gap',[bo,b_gap])
        bottom.rot_x(value = 0)
        bottom.rot_y(value = 0)
        bottom.rot_z(value = math.radians(90))
        bottom.dim_x(value = depth - pc_unit.millimeter(21))
        bottom.dim_y('width-lo-ro-bottom_deduction',[width,lo,ro,bottom_deduction])
        bottom.dim_z('bt',[bt])


class BLUM_Metabox(pc_types.Assembly):

    def add_empty_calc_objects(self):
        opening_height_obj = self.add_empty('Drawer Box Height')
        opening_height_obj.empty_display_size = .001
        box_height_obj = self.add_empty('Drawer Box Height')
        box_height_obj.empty_display_size = .001
        box_length_obj = self.add_empty('Drawer Box Length')
        box_length_obj.empty_display_size = .001        
        return opening_height_obj, box_height_obj, box_length_obj

    def draw(self):
        self.create_assembly()
        self.obj_bp["IS_DRAWER_BOX_BP"] = True
        self.set_name("BLUM Metabox")

        opening_height_obj, box_height_obj, box_length_obj = self.add_empty_calc_objects()

        hide = self.add_prompt("Hide",'CHECKBOX',False)
        drawer_side_thickness = self.add_prompt("Drawer Side Thickness",'DISTANCE',pc_unit.millimeter(3))
        front_back_thickness = self.add_prompt("Front Back Thickness",'DISTANCE',pc_unit.inch(.75))
        bottom_thickness = self.add_prompt("Drawer Bottom Thickness",'DISTANCE',pc_unit.inch(.75))
        drawer_box_bottom_dado_depth = self.add_prompt("Drawer Box Bottom Dado Depth",'DISTANCE',pc_unit.inch(0))
        drawer_box_z_loc = self.add_prompt("Drawer Bottom Z Location",'DISTANCE',pc_unit.inch(.5))
        drawer_slide_gap = self.add_prompt("Drawer Slide Gap",'DISTANCE',pc_unit.millimeter(28))
        drawer_top_gap = self.add_prompt("Drawer Top Gap",'DISTANCE',pc_unit.inch(1))
        drawer_bottom_gap = self.add_prompt("Drawer Bottom Gap",'DISTANCE',pc_unit.millimeter(5))
        b_gap = drawer_bottom_gap.get_var('b_gap')
        lo = self.add_prompt("Left Overlay",'DISTANCE',0).get_var('lo')
        ro = self.add_prompt("Right Overlay",'DISTANCE',0).get_var('ro')
        to = self.add_prompt("Top Overlay",'DISTANCE',0).get_var('to')
        bo = self.add_prompt("Bottom Overlay",'DISTANCE',0).get_var('bo')

        n_min_h = self.add_prompt("N Min Height",'DISTANCE',pc_unit.millimeter(78)).get_var('n_min_h')
        m_min_h = self.add_prompt("M Min Height",'DISTANCE',pc_unit.millimeter(110)).get_var('m_min_h')
        k_min_h = self.add_prompt("K Min Height",'DISTANCE',pc_unit.millimeter(142)).get_var('k_min_h')
        h_min_h = self.add_prompt("H Min Height",'DISTANCE',pc_unit.millimeter(174)).get_var('h_min_h') 

        nh = self.add_prompt("N Height",'DISTANCE',pc_unit.inch(2.125)).get_var('nh')
        mh = self.add_prompt("M Height",'DISTANCE',pc_unit.inch(3.375)).get_var('mh')
        kh = self.add_prompt("K Height",'DISTANCE',pc_unit.inch(4.625)).get_var('kh')
        hh = self.add_prompt("H Height",'DISTANCE',pc_unit.inch(5.875)).get_var('hh')

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        dt = drawer_side_thickness.get_var('dt')
        fbt = front_back_thickness.get_var('fbt')
        bt = bottom_thickness.get_var('bt')
        dado_depth = drawer_box_bottom_dado_depth.get_var('dado_depth')
        slide_gap = drawer_slide_gap.get_var('slide_gap')
        
        t_gap = drawer_top_gap.get_var('t_gap')
        
        opening_height_obj.pyclone.loc_z('height-to-bo-t_gap-b_gap',[height,to,bo,t_gap,b_gap])
        o_h = opening_height_obj.pyclone.get_var('location.z','o_h')

        box_height_obj.pyclone.loc_z('IF(o_h>=h_min_h,hh,IF(o_h>=k_min_h,kh,IF(o_h>=m_min_h,mh,IF(o_h>=n_min_h,nh,0))))',
                                     [o_h,h_min_h,hh,k_min_h,kh,m_min_h,mh,n_min_h,nh])
        b_height = box_height_obj.pyclone.get_var('location.z','b_height')

        #IF(AND(o_h>INCH(4.330711),o_h<INCH(5.5905542)),.270,0)
        box_length_obj.pyclone.loc_y('IF(depth>=.550,.550,IF(depth>=.500,.500,IF(depth>=.450,.450,IF(depth>=.400,.400,IF(depth>=.350,.350,IF(depth>=.270,IF(AND(o_h>INCH(4.330711),o_h<INCH(5.5905542)),.270,0),0))))))',
                                     [depth,o_h])
        b_length = box_length_obj.pyclone.get_var('location.y','b_length')

        left_side = data_cabinet_parts.add_cabinet_shelf(self)
        left_side.obj_bp['IS_CUTPART_BP'] = True
        left_side.obj_bp['IS_LEFT_DRAWER_SIDE_BP'] = True
        left_side.set_name("Left Drawer Side")
        left_side.loc_x('lo+slide_gap',[lo,slide_gap])
        left_side.loc_y(value = 0)
        left_side.loc_z('bo+b_gap',[bo,b_gap])
        left_side.rot_x(value = math.radians(90))
        left_side.rot_y(value = 0)
        left_side.rot_z(value = math.radians(90))
        left_side.dim_x('b_length',[b_length])
        left_side.dim_y('b_height',[b_height])
        left_side.dim_z('dt',[dt])

        right_side = data_cabinet_parts.add_cabinet_shelf(self)
        right_side.obj_bp['IS_CUTPART_BP'] = True
        right_side.set_name("Right Drawer Side")
        right_side.obj_bp['IS_RIGHT_DRAWER_SIDE_BP'] = True
        right_side.loc_x('width-ro-slide_gap',[width,ro,slide_gap])
        right_side.loc_y(value = 0)
        right_side.loc_z('bo+b_gap',[bo,b_gap])
        right_side.rot_x(value = math.radians(90))
        right_side.rot_y(value = 0)
        right_side.rot_z(value = math.radians(90))
        right_side.dim_x('b_length',[b_length])
        right_side.dim_y('b_height',[b_height])
        right_side.dim_z('-dt',[dt])                   

        back = data_cabinet_parts.add_cabinet_shelf(self)
        back.obj_bp['IS_CUTPART_BP'] = True
        back.obj_bp['IS_DRAWER_BACK_BP'] = True
        back.set_name("Drawer Back")
        back.loc_x('dt+lo+slide_gap',[dt,lo,slide_gap])
        back.loc_y('b_length',[b_length])
        back.loc_z('bo+b_gap+bt',[bo,b_gap,bt])
        back.rot_x(value = math.radians(90))
        back.rot_y(value = 0)
        back.rot_z(value = 0)
        back.dim_x('width-(dt*2)-lo-ro-(slide_gap*2)',[width,dt,lo,ro,slide_gap])
        back.dim_y('b_height-bt',[b_height,bt])
        back.dim_z('fbt',[fbt])            

        bottom = data_cabinet_parts.add_cabinet_shelf(self)
        bottom.obj_bp['IS_CUTPART_BP'] = True
        bottom.obj_bp['IS_DRAWER_BOTTOM_BP'] = True
        bottom.set_name("Drawer Bottom")
        bottom.loc_x('width-dt+dado_depth-slide_gap-ro',[width,dt,dado_depth,slide_gap,ro])
        bottom.loc_y(value = 0)
        bottom.loc_z('bo+b_gap',[bo,b_gap])
        bottom.rot_x(value = 0)
        bottom.rot_y(value = 0)
        bottom.rot_z(value = math.radians(90))
        bottom.dim_x('b_length',[b_length])
        bottom.dim_y('width-(dt*2)+(dado_depth*2)-lo-ro-(slide_gap*2)',[width,dt,dado_depth,lo,ro,slide_gap])
        bottom.dim_z('bt',[bt])


class Buyout_Drawer_Box(pc_types.Assembly):

    def draw(self):
        self.create_assembly()
        self.obj_bp["IS_DRAWER_BOX_BP"] = True
        self.set_name("Buyout Drawer Box")

        hide = self.add_prompt("Hide",'CHECKBOX',False)
        self.add_prompt("Drawer Side Thickness",'DISTANCE',pc_unit.inch(.75))
        self.add_prompt("Front Back Thickness",'DISTANCE',pc_unit.inch(.75))
        self.add_prompt("Drawer Bottom Thickness",'DISTANCE',pc_unit.inch(.25))
        self.add_prompt("Drawer Box Bottom Dado Depth",'DISTANCE',pc_unit.inch(.25))
        self.add_prompt("Drawer Bottom Z Location",'DISTANCE',pc_unit.inch(.5))
        self.add_prompt("Drawer Slide Gap",'DISTANCE',pc_unit.inch(.25))
        self.add_prompt("Drawer Top Gap",'DISTANCE',pc_unit.inch(1))
        self.add_prompt("Drawer Bottom Gap",'DISTANCE',pc_unit.inch(1))
        self.add_prompt("Left Overlay",'DISTANCE',0)
        self.add_prompt("Right Overlay",'DISTANCE',0)
        self.add_prompt("Top Overlay",'DISTANCE',0)
        self.add_prompt("Bottom Overlay",'DISTANCE',0)

        width = self.obj_x.pyclone.get_var('location.x','width')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')
        dt = self.get_prompt("Drawer Side Thickness").get_var('dt')
        slide_gap = self.get_prompt("Drawer Slide Gap").get_var('slide_gap')
        lo = self.get_prompt("Left Overlay").get_var('lo')
        ro = self.get_prompt("Right Overlay").get_var('ro')
        to = self.get_prompt("Top Overlay").get_var('to')
        bo = self.get_prompt("Bottom Overlay").get_var('bo')
        t_gap = self.get_prompt("Drawer Top Gap").get_var('t_gap')
        b_gap = self.get_prompt("Drawer Bottom Gap").get_var('b_gap')

        left_side = pc_types.Assembly()
        left_side.create_assembly()
        self.add_assembly(left_side)
        left_side.obj_bp['IS_CUTPART_BP'] = True
        left_side.obj_bp['IS_DUMMY_PART'] = True
        left_side.obj_bp['IS_LEFT_DRAWER_SIDE_BP'] = True
        left_side.set_name("Left Drawer Side")
        left_side.loc_x('lo+slide_gap',[lo,slide_gap])
        left_side.loc_y(value = 0)
        left_side.loc_z('bo+b_gap',[bo,b_gap])
        left_side.rot_x(value = math.radians(90))
        left_side.rot_y(value = 0)
        left_side.rot_z(value = math.radians(90))
        left_side.dim_x('depth',[depth])
        left_side.dim_y('height-to-bo-t_gap-b_gap',[height,to,bo,t_gap,b_gap])
        left_side.dim_z('dt',[dt])
        left_side.obj_bp.hide_viewport = True  
        left_side.obj_x.hide_viewport = True  
        left_side.obj_y.hide_viewport = True  
        left_side.obj_z.hide_viewport = True  

        right_side = pc_types.Assembly()
        right_side.create_assembly()
        self.add_assembly(right_side)
        right_side.obj_bp['IS_CUTPART_BP'] = True
        right_side.obj_bp['IS_DUMMY_PART'] = True
        right_side.obj_bp['IS_RIGHT_DRAWER_SIDE_BP'] = True
        right_side.set_name("Right Drawer Side")
        right_side.loc_x('width-ro-slide_gap',[width,ro,slide_gap])
        right_side.loc_y(value = 0)
        right_side.loc_z('bo+b_gap',[bo,b_gap])
        right_side.rot_x(value = math.radians(90))
        right_side.rot_y(value = 0)
        right_side.rot_z(value = math.radians(90))
        right_side.dim_x('depth',[depth])
        right_side.dim_y('height-to-bo-t_gap-b_gap',[height,to,bo,t_gap,b_gap])
        right_side.dim_z('-dt',[dt])        
        right_side.obj_bp.hide_viewport = True  
        right_side.obj_x.hide_viewport = True  
        right_side.obj_y.hide_viewport = True  
        right_side.obj_z.hide_viewport = True  

        drawer_box = data_cabinet_parts.add_buyout_drawer(self)
        # drawer_box.obj_bp['IS_CUTPART_BP'] = True
        drawer_box.obj_bp['IS_DRAWER_BUYOUT_BP'] = True
        drawer_box.set_name("Drawer Box")
        drawer_box.loc_x('lo+slide_gap',[lo,slide_gap])
        drawer_box.loc_y(value = 0)
        drawer_box.loc_z('bo+b_gap',[bo,b_gap])
        drawer_box.rot_x(value = 0)
        drawer_box.rot_y(value = 0)
        drawer_box.rot_z(value = 0)
        drawer_box.dim_x('width-lo-ro-(slide_gap*2)',[width,lo,ro,slide_gap])
        drawer_box.dim_y('depth',[depth])
        drawer_box.dim_z('height-to-bo-t_gap-b_gap',[height,to,bo,t_gap,b_gap])      
        drawer_box.obj_bp.hide_viewport = True  
        drawer_box.obj_x.hide_viewport = True  
        drawer_box.obj_y.hide_viewport = True  
        drawer_box.obj_z.hide_viewport = True