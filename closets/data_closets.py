import bpy
import time
import math
from os import path
from ..pc_lib import pc_types, pc_unit, pc_utils

from . import common_prompts
from . import data_closet_parts
from .. import home_builder_utils
from .. import home_builder_pointers

class Closet_Starter(pc_types.Assembly):
    show_in_library = True
    category_name = "CLOSETS"
    subcategory_name = "FLOOR_PANELS"

    opening_qty = 4
    panels = []

    def add_opening_prompts(self):
        width = self.obj_x.pyclone.get_var('location.x','width')
        p_thickness = self.get_prompt("Panel Thickness").get_var("p_thickness")

        calc_distance_obj = self.add_empty('Calc Distance Obj')
        calc_distance_obj.empty_display_size = .001
        opening_calculator = self.obj_prompts.pyclone.add_calculator("Opening Calculator",calc_distance_obj)

        for i in range(1,self.opening_qty+1):
            opening_calculator.add_calculator_prompt('Opening ' + str(i) + ' Width')
            self.add_prompt("Opening " + str(i) + " Height",'DISTANCE',self.obj_z.location.z)
            self.add_prompt("Opening " + str(i) + " Depth",'DISTANCE',math.fabs(self.obj_y.location.y))
            self.add_prompt("Opening " + str(i) + " Floor Mounted",'CHECKBOX',True)

        opening_calculator.set_total_distance('width-p_thickness*' + str(self.opening_qty+1),[width,p_thickness])

    def add_panel(self,index,previous_panel):
        previous_panel_x = previous_panel.obj_bp.pyclone.get_var('location.x',"previous_panel_x")

        height = self.obj_z.pyclone.get_var('location.z','height')
        opening_width_prompt = self.get_prompt("Opening " + str(index) + " Width")
        opening_width = opening_width_prompt.get_var("Opening Calculator","opening_width")
        opening_depth = self.get_prompt("Opening " + str(index) + " Depth").get_var('opening_depth')
        opening_height = self.get_prompt("Opening " + str(index) + " Height").get_var('opening_height')
        floor = self.get_prompt("Opening " + str(index) + " Floor Mounted").get_var('floor')
        next_floor = self.get_prompt("Opening " + str(index+1) + " Floor Mounted").get_var('next_floor')
        next_depth = self.get_prompt("Opening " + str(index+1) + " Depth").get_var('next_depth')
        next_height = self.get_prompt("Opening " + str(index+1) + " Height").get_var('next_height')
        left_filler = self.get_prompt("Left Side Wall Filler").get_var("left_filler")

        depth = self.obj_y.pyclone.get_var('location.y','depth')
        p_thickness = self.get_prompt("Panel Thickness").get_var("p_thickness")

        panel = data_closet_parts.add_closet_part(self)
        panel.obj_bp["IS_PANEL_BP"] = True
        panel.set_name('Panel ' + str(index))
        panel.loc_x('previous_panel_x+opening_width+p_thickness',[previous_panel_x,opening_width,p_thickness])
        panel.loc_y(value = 0)
        panel.loc_z('min(IF(floor,0,IF(next_floor,0,height-opening_height)),IF(next_floor,0,IF(floor,0,height-next_height)))',
                    [floor,next_floor,height,opening_height,next_height])
        panel.rot_y(value=math.radians(-90))
        panel.rot_z(value=0)
        panel.dim_x('max(IF(floor,opening_height,IF(next_floor,height,opening_height)),IF(next_floor,next_height,IF(floor,height,next_height)))',
                    [floor,height,next_floor,opening_height,next_height])
        panel.dim_y('-max(opening_depth,next_depth)',[opening_depth,next_depth])
        panel.dim_z('-p_thickness',[p_thickness])
        return panel

    def add_shelf(self,index,left_panel,right_panel):
        left_panel_x = left_panel.obj_bp.pyclone.get_var('location.x','left_panel_x')
        right_panel_x = right_panel.obj_bp.pyclone.get_var('location.x','right_panel_x')

        opening_depth = self.get_prompt("Opening " + str(index) + " Depth").get_var('opening_depth')
        p_thickness = self.get_prompt("Panel Thickness").get_var("p_thickness")
        s_thickness = self.get_prompt("Shelf Thickness").get_var("s_thickness")

        shelf = data_closet_parts.add_closet_part(self)
        shelf.obj_bp["IS_SHELF_BP"] = True
        shelf.set_name('Shelf ' + str(index))
        shelf.loc_x('left_panel_x+p_thickness',[left_panel_x,p_thickness])
        shelf.loc_y(value = 0)
        shelf.loc_z(value = 0)
        shelf.rot_y(value = 0)
        shelf.rot_z(value = 0)
        if right_panel.obj_z.location.z > 0:
            shelf.dim_x('right_panel_x-left_panel_x-(p_thickness*2)',[left_panel_x,right_panel_x,p_thickness])
        else:
            shelf.dim_x('right_panel_x-left_panel_x-p_thickness',[left_panel_x,right_panel_x,p_thickness])
        shelf.dim_y('-opening_depth',[opening_depth])
        shelf.dim_z('s_thickness',[s_thickness])
        home_builder_utils.flip_normals(shelf)
        return shelf

    def add_toe_kick(self,index,left_panel,right_panel):
        left_panel_x = left_panel.obj_bp.pyclone.get_var('location.x','left_panel_x')
        right_panel_x = right_panel.obj_bp.pyclone.get_var('location.x','right_panel_x')

        opening_depth = self.get_prompt("Opening " + str(index) + " Depth").get_var('opening_depth')
        p_thickness = self.get_prompt("Panel Thickness").get_var("p_thickness")
        s_thickness = self.get_prompt("Shelf Thickness").get_var("s_thickness")
        kick_height = self.get_prompt("Closet Kick Height").get_var("kick_height")
        kick_setback = self.get_prompt("Closet Kick Setback").get_var("kick_setback")

        kick = data_closet_parts.add_closet_part(self)
        kick.obj_bp["IS_SHELF_BP"] = True
        kick.set_name('Kick ' + str(index))
        kick.loc_x('left_panel_x+p_thickness',[left_panel_x,p_thickness])
        kick.loc_y('-opening_depth+kick_setback',[opening_depth,kick_setback])
        kick.loc_z(value = 0)
        kick.rot_x(value = math.radians(-90))
        kick.rot_y(value = 0)
        kick.rot_z(value = 0)
        if right_panel.obj_z.location.z > 0:
            kick.dim_x('right_panel_x-left_panel_x-(p_thickness*2)',[left_panel_x,right_panel_x,p_thickness])
        else:
            kick.dim_x('right_panel_x-left_panel_x-p_thickness',[left_panel_x,right_panel_x,p_thickness])
        kick.dim_y('-kick_height',[kick_height])
        kick.dim_z('s_thickness',[s_thickness])
        home_builder_utils.flip_normals(kick)
        return kick

    def add_opening(self,index,left_panel,right_panel):
        left_panel_x = left_panel.obj_bp.pyclone.get_var('location.x','left_panel_x')
        right_panel_x = right_panel.obj_bp.pyclone.get_var('location.x','right_panel_x')

        opening_depth = self.get_prompt("Opening " + str(index) + " Depth").get_var('opening_depth')
        opening_height = self.get_prompt("Opening " + str(index) + " Height").get_var('opening_height')
        p_thickness = self.get_prompt("Panel Thickness").get_var("p_thickness")
        s_thickness = self.get_prompt("Shelf Thickness").get_var("s_thickness")
        kick_height = self.get_prompt("Closet Kick Height").get_var("kick_height")

        opening = data_closet_parts.add_closet_opening(self)
        opening.set_name('Opening ' + str(index))
        opening.loc_x('left_panel_x+p_thickness',[left_panel_x,p_thickness])
        opening.loc_y('-opening_depth',[opening_depth])
        opening.loc_z('kick_height+s_thickness',[kick_height,s_thickness])
        opening.rot_x(value = 0)
        opening.rot_y(value = 0)
        opening.rot_z(value = 0)
        if right_panel.obj_z.location.z > 0:
            opening.dim_x('right_panel_x-left_panel_x-(p_thickness*2)',[left_panel_x,right_panel_x,p_thickness])
        else:
            opening.dim_x('right_panel_x-left_panel_x-p_thickness',[left_panel_x,right_panel_x,p_thickness])
        opening.dim_y('opening_depth',[opening_depth])
        opening.dim_z('opening_height-kick_height-(s_thickness*2)',[opening_height,kick_height,s_thickness])
        return opening

    def pre_draw(self):
        self.create_assembly()

        self.obj_x.location.x = pc_unit.inch(96)
        self.obj_y.location.y = -pc_unit.inch(12)
        self.obj_z.location.z = pc_unit.millimeter(2131)

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        reference = data_closet_parts.add_closet_part(self)
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
        self.panels = []
        start_time = time.time()

        self.obj_bp["IS_CLOSET_BP"] = True
        self.obj_bp["PROMPT_ID"] = "home_builder.closet_prompts" 
        self.obj_bp["MENU_ID"] = "HOMEBUILDER_MT_cabinet_menu"
        self.obj_y['IS_MIRROR'] = True

        width = self.obj_x.pyclone.get_var('location.x','width')
        height = self.obj_z.pyclone.get_var('location.z','height')
        depth = self.obj_y.pyclone.get_var('location.y','depth')

        common_prompts.add_closet_thickness_prompts(self)
        panel_thickness_var = self.get_prompt("Panel Thickness").get_var("panel_thickness_var")
        shelf_thickness_var = self.get_prompt("Shelf Thickness").get_var("shelf_thickness_var")        
        closet_kick_height = self.add_prompt("Closet Kick Height",'DISTANCE',pc_unit.inch(2.5)) 

        closet_kick_height_var = closet_kick_height.get_var("closet_kick_height_var")
        closet_kick_setback = self.add_prompt("Closet Kick Setback",'DISTANCE',pc_unit.inch(1.125)) 
        left_end_condition = self.add_prompt("Left End Condition",'COMBOBOX',0,["EP","WP","CP","OFF"]) 
        lec = left_end_condition.get_var("lec")
        right_end_condition = self.add_prompt("Right End Condition",'COMBOBOX',0,["EP","WP","CP","OFF"]) 
        rec = right_end_condition.get_var("rec")
        left_side_wall_filler = self.add_prompt("Left Side Wall Filler",'DISTANCE',0) 
        left_filler = left_side_wall_filler.get_var("left_filler")
        right_side_wall_filler = self.add_prompt("Right Side Wall Filler",'DISTANCE',0) 
        right_filler = right_side_wall_filler.get_var("right_filler")
        bridge_left = self.add_prompt("Bridge Left",'CHECKBOX',False) 
        bridge_right = self.add_prompt("Bridge Right",'CHECKBOX',False) 
        left_bridge_shelf_width = self.add_prompt("Left Bridge Shelf Width",'DISTANCE',pc_unit.inch(12)) 
        right_bridge_shelf_width = self.add_prompt("Right Bridge Shelf Width",'DISTANCE',pc_unit.inch(12)) 
        b_left = bridge_left.get_var("b_left")
        b_right = bridge_right.get_var("b_right")
        b_left_width = left_bridge_shelf_width.get_var("b_left_width")
        b_right_width = right_bridge_shelf_width.get_var("b_right_width")

        self.add_opening_prompts()

        depth_1 = self.get_prompt("Opening 1 Depth").get_var("depth_1")
        height_1 = self.get_prompt("Opening 1 Height").get_var("height_1")
        floor_1 = self.get_prompt("Opening 1 Floor Mounted").get_var("floor_1")
        depth_last = self.get_prompt("Opening " + str(self.opening_qty) + " Depth").get_var("depth_last")
        height_last = self.get_prompt("Opening " + str(self.opening_qty) + " Height").get_var("height_last")
        floor_last = self.get_prompt("Opening " + str(self.opening_qty) + " Floor Mounted").get_var("floor_last")
        s_thickness = self.get_prompt("Shelf Thickness").get_var("s_thickness")

        left_side = data_closet_parts.add_closet_part(self)
        left_side.obj_bp["IS_PANEL_BP"] = True
        left_side.set_name('Left Panel')
        left_side.loc_x('left_filler',[left_filler])
        left_side.loc_y(value = 0)
        left_side.loc_z('IF(floor_1,0,height-height_1)',[floor_1,height,height_1])
        left_side.rot_y(value=math.radians(-90))
        left_side.rot_z(value=0)
        left_side.dim_x('height_1',[height_1])
        left_side.dim_y('-depth_1',[depth_1])
        left_side.dim_z('-panel_thickness_var',[panel_thickness_var])
        self.panels.append(left_side)
        bpy.context.view_layer.update()

        left_bridge = data_closet_parts.add_closet_part(self)
        left_bridge.obj_bp["IS_BRIDGE_BP"] = True
        left_bridge.set_name('Left Bridge Bottom')
        left_bridge.loc_x('-b_left_width',[b_left_width])
        left_bridge.loc_y(value = 0)
        left_bridge.loc_z('closet_kick_height_var',[closet_kick_height_var])
        left_bridge.rot_y(value = 0)
        left_bridge.rot_z(value = 0)
        left_bridge.dim_x('b_left_width',[b_left_width])
        left_bridge.dim_y('-depth_1',[depth_1])
        left_bridge.dim_z('s_thickness',[s_thickness])
        hide = left_bridge.get_prompt("Hide")
        hide.set_formula('IF(b_left,False,True)',[b_left])
        home_builder_utils.flip_normals(left_bridge)

        right_bridge = data_closet_parts.add_closet_part(self)
        right_bridge.obj_bp["IS_BRIDGE_BP"] = True
        right_bridge.set_name('Right Bridge Bottom')
        right_bridge.loc_x('width',[width])
        right_bridge.loc_y(value = 0)
        right_bridge.loc_z('closet_kick_height_var',[closet_kick_height_var])
        right_bridge.rot_y(value = 0)
        right_bridge.rot_z(value = 0)
        right_bridge.dim_x('b_right_width',[b_right_width])
        right_bridge.dim_y('-depth_last',[depth_last])
        right_bridge.dim_z('s_thickness',[s_thickness])
        hide = right_bridge.get_prompt("Hide")
        hide.set_formula('IF(b_right,False,True)',[b_right])        
        home_builder_utils.flip_normals(right_bridge)

        previous_panel = None
        for i in range(1,self.opening_qty):
            if previous_panel == None:
                previous_panel = self.add_panel(i,left_side)
                self.panels.append(previous_panel)
            else:
                previous_panel = self.add_panel(i,previous_panel)
                self.panels.append(previous_panel)

        right_side = data_closet_parts.add_closet_part(self)
        right_side.obj_bp["IS_PANEL_BP"] = True
        right_side.set_name('Right Panel')
        right_side.loc_x('width-right_filler',[width,right_filler])
        right_side.loc_y(value = 0)
        right_side.loc_z('IF(floor_last,0,height-height_last)',[floor_last,height,height_last])
        right_side.rot_y(value=math.radians(-90))
        right_side.rot_z(value=0)
        right_side.dim_x('height_last',[height_last])
        right_side.dim_y('-depth_last',[depth_last])
        right_side.dim_z('panel_thickness_var',[panel_thickness_var])
        home_builder_utils.flip_normals(right_side)
        self.panels.append(right_side)

        bpy.context.view_layer.update()

        for index, panel in enumerate(self.panels):
            if index + 1 < len(self.panels):
                opening_height = self.get_prompt("Opening " + str(index+1) + " Height").get_var('opening_height')
                floor = self.get_prompt("Opening " + str(index+1) + " Floor Mounted").get_var('floor')

                bottom = self.add_shelf(index + 1,panel,self.panels[index+1])
                bottom.loc_z('closet_kick_height_var',[closet_kick_height_var])

                top = self.add_shelf(index + 1,panel,self.panels[index+1])
                top.loc_z('IF(floor,opening_height,height)-shelf_thickness_var',[floor,opening_height,height,shelf_thickness_var])

                kick = self.add_toe_kick(index + 1,panel,self.panels[index+1])

                opening = self.add_opening(index + 1,panel,self.panels[index+1])

        calculator = self.get_calculator('Opening Calculator')
        bpy.context.view_layer.update()
        calculator.calculate()
        print("Closet: Draw Time --- %s seconds ---" % (time.time() - start_time))