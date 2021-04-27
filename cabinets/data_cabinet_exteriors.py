import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinet_parts
from .. import home_builder_utils
from .. import home_builder_pointers
from .. import home_builder_paths
from . import common_prompts
from os import path

exterior_selection = [('SELECT_EXTERIOR',"Select Exterior","Select Exterior"),
                      ('OPEN',"Open","Open"),
                      ('LEFT_SWING_DOOR',"Left Swing Doors","Left Swing Doors"),
                      ('RIGHT_SWING_DOOR',"Right Swing Doors","Right Swing Doors"),
                      ('DOUBLE_DOORS',"Double Doors","Double Doors"),
                      ('2_DOOR_2_DRAWER',"2 Door 2 Drawer","2 Door 2 Drawer"),
                      ('1_DOOR_1_DRAWER',"1 Door 1 Drawer","1 Door 1 Drawer"),
                      ('2_DOOR_1_DRAWER',"2 Door 1 Drawer","2 Door 1 Drawer"),
                    #   ('SLIDING_DOORS',"Sliding Doors","Sliding Doors"),
                      ('1_DRAWERS',"1 Drawer","1 Drawer"),
                      ('2_DRAWERS',"2 Drawers","2 Drawers"),
                      ('3_DRAWERS',"3 Drawers","3 Drawers"),
                      ('4_DRAWERS',"4 Drawers","4 Drawers"),
                      ('5_DRAWERS',"5 Drawers","5 Drawers"),
                      ('6_DRAWERS',"6 Drawers","6 Drawers")]

def get_class_from_name(name):
    exterior = None
    if name == 'LEFT_SWING_DOOR':
        exterior = Doors()
        exterior.door_swing = 0
    elif name == 'RIGHT_SWING_DOOR':
        exterior = Doors()       
        exterior.door_swing = 1      
    elif name == 'DOUBLE_DOORS':
        exterior = Doors()          
        exterior.door_swing = 2 
    elif name == '2_DOOR_2_DRAWER':
        exterior = Door_Drawer()
        exterior.two_drawers = True
        exterior.door_swing = 2
    elif name == '1_DOOR_1_DRAWER':
        exterior = Door_Drawer()
        exterior.door_swing = 0
    elif name == '2_DOOR_1_DRAWER':
        exterior = Door_Drawer()
        exterior.door_swing = 2
    elif name == 'SLIDING_DOORS':
        exterior = Doors()#TODO
    elif name == '1_DRAWERS':
        exterior = Drawers()
        exterior.drawer_qty = 1
    elif name == '2_DRAWERS':
        exterior = Drawers()      
        exterior.drawer_qty = 2    
    elif name == '3_DRAWERS':
        exterior = Drawers()       
        exterior.drawer_qty = 3   
    elif name == '4_DRAWERS':
        exterior = Drawers()          
        exterior.drawer_qty = 4
    elif name == '5_DRAWERS':
        exterior = Drawers()      
        exterior.drawer_qty = 5                                                                                                  
    elif name == '6_DRAWERS':
        exterior = Drawers()
        exterior.drawer_qty = 6
    return exterior


class Cabinet_Exterior(pc_types.Assembly):
    carcass_type = '' #Base, Tall, Upper

    def add_overlay_prompts(self):
        hot = self.get_prompt("Half Overlay Top").get_var('hot')
        hob = self.get_prompt("Half Overlay Bottom").get_var('hob')
        hol = self.get_prompt("Half Overlay Left").get_var('hol')
        hor = self.get_prompt("Half Overlay Right").get_var('hor')
        material_thickness = self.get_prompt("Material Thickness").get_var('material_thickness')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        tr = self.get_prompt("Top Reveal").get_var('tr')
        br = self.get_prompt("Bottom Reveal").get_var('br')
        lr = self.get_prompt("Left Reveal").get_var('lr')
        rr = self.get_prompt("Right Reveal").get_var('rr')

        overlay_prompt_obj = self.add_empty('Overlay Prompt Obj')
        overlay_prompt_obj.empty_display_size = .01

        to = overlay_prompt_obj.pyclone.add_prompt('DISTANCE',"Top Overlay")
        bo = overlay_prompt_obj.pyclone.add_prompt('DISTANCE',"Bottom Overlay")
        lo = overlay_prompt_obj.pyclone.add_prompt('DISTANCE',"Left Overlay")
        ro = overlay_prompt_obj.pyclone.add_prompt('DISTANCE',"Right Overlay")

        to.set_formula('IF(hot,(material_thickness-vertical_gap)/2,material_thickness-tr)',[hot,material_thickness,vertical_gap,tr])
        bo.set_formula('IF(hob,(material_thickness-vertical_gap)/2,material_thickness-br)',[hob,material_thickness,vertical_gap,br])
        lo.set_formula('IF(hol,(material_thickness-vertical_gap)/2,material_thickness-lr)',[hol,material_thickness,vertical_gap,lr])
        ro.set_formula('IF(hor,(material_thickness-vertical_gap)/2,material_thickness-rr)',[hor,material_thickness,vertical_gap,rr])

        return to, bo, lo, ro

    def replace_front(self,old_front,pointer):
        new_front = data_cabinet_parts.add_door_part(self,pointer)
        scene_props = home_builder_utils.get_scene_props(bpy.context.scene)
        pull_pointer = None

        if pointer.name == 'Base Cabinet Doors':
            pull_pointer = scene_props.pull_pointers["Base Cabinet Pulls"]
        if pointer.name == 'Tall Cabinet Doors':
            pull_pointer = scene_props.pull_pointers["Tall Cabinet Pulls"]
        if pointer.name == 'Upper Cabinet Doors':
            pull_pointer = scene_props.pull_pointers["Upper Cabinet Pulls"]          
        if pointer.name == 'Drawer Fronts':
            pull_pointer = scene_props.pull_pointers["Drawer Pulls"]       

        if "Drawer" in pointer.name:
            self.add_drawer_pull(new_front,pull_pointer)
        else:
            self.add_door_pull(new_front,pull_pointer)

        home_builder_utils.update_assembly_id_props(new_front,self)
        home_builder_utils.replace_assembly(old_front,new_front)
        home_builder_utils.hide_empties(new_front.obj_bp)

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

        pull_path = path.join(home_builder_paths.get_pull_path(),pointer.category,pointer.item_name + ".blend")
        pull_obj = home_builder_utils.get_object(pull_path)
        pull_obj['IS_CABINET_PULL'] = True
        home_builder_utils.get_object_props(pull_obj).pointer_name = "Drawer Pulls"
        front.add_object(pull_obj)
        pull_obj.parent = front.obj_bp
        pull_obj.pyclone.loc_x('(drawer_front_height/2)',[drawer_front_height])
        pull_obj.pyclone.loc_y('(fabs(drawer_front_width)/2)*-1',[drawer_front_width])
        pull_obj.pyclone.loc_z('front_thickness',[front_thickness])
        pull_obj.rotation_euler.x = math.radians(-90)
        pull_obj.rotation_euler.y = math.radians(0)
        pull_obj.rotation_euler.z = math.radians(90)
        pull_obj.pyclone.hide('IF(turn_off_pulls,True,hide_drawer_front)',[turn_off_pulls,hide_drawer_front])

        home_builder_pointers.assign_pointer_to_object(pull_obj,"Cabinet Pull Finish")

    def draw_prompts(self,layout,context):
        open_door = self.get_prompt("Open Door")
        front_height_calculator = self.get_calculator("Front Height Calculator")
        door_swing = self.get_prompt("Door Swing")
        turn_off_pulls = self.get_prompt("Turn Off Pulls")
        top_drawer_front_height = self.get_prompt("Top Drawer Front Height")
        carcass_type = self.get_prompt("Carcass Type")
        add_two_drawer_fronts = self.get_prompt("Add Two Drawer Fronts")

        if open_door:
            open_door.draw(layout,allow_edit=False)

        if door_swing:
            door_swing.draw(layout,allow_edit=False)    

        if turn_off_pulls:
            row = layout.row()
            row.label(text="Pulls:")
            row.prop(turn_off_pulls,'checkbox_value',text="Off")

            pull_horizontal_location = self.get_prompt("Pull Horizontal Location")

            if carcass_type.get_value() == 'Base':
                base_pull_location = self.get_prompt("Base Pull Vertical Location")
                row.prop(pull_horizontal_location,'distance_value',text="X")
                row.prop(base_pull_location,'distance_value',text="Z")
            if carcass_type.get_value() == 'Tall':
                tall_pull_location = self.get_prompt("Tall Pull Vertical Location")
                row.prop(pull_horizontal_location,'distance_value',text="X")
                row.prop(tall_pull_location,'distance_value',text="Z")                
            if carcass_type.get_value() == 'Upper':
                upper_pull_location = self.get_prompt("Upper Pull Vertical Location")     
                row.prop(pull_horizontal_location,'distance_value',text="X")
                row.prop(upper_pull_location,'distance_value',text="Z")                       
            if carcass_type.get_value() == 'Drawer':
                pass            
        
        if add_two_drawer_fronts:
            row = layout.row()
            row.label(text="Add Two Drawer Fronts")
            row.prop(add_two_drawer_fronts,'checkbox_value',text="")

        if top_drawer_front_height:
            row = layout.row()
            row.label(text="Top Drawer Front Height")
            row.prop(top_drawer_front_height,'distance_value',text="")

        if front_height_calculator:
            for prompt in front_height_calculator.prompts:
                prompt.draw(layout)      
            row = layout.row()   
            row.scale_y = 1.3
            props = row.operator('pc_prompts.run_calculator',text="Calculate Drawer Front Heights")
            props.calculator_name = front_height_calculator.name
            props.obj_name = self.obj_prompts.name

class Doors(Cabinet_Exterior):

    door_swing = 0 # Left = 0, Right = 1, Double = 2
    
    def set_pull_props(self,obj):
        obj['IS_CABINET_PULL'] = True
        home_builder_pointers.assign_pointer_to_object(obj,"Cabinet Pull Finish")  
        if self.carcass_type == 'Base':
            home_builder_utils.get_object_props(obj).pointer_name = "Base Cabinet Pulls"
        if self.carcass_type == 'Tall':
            home_builder_utils.get_object_props(obj).pointer_name = "Tall Cabinet Pulls"
        if self.carcass_type == 'Upper':
            home_builder_utils.get_object_props(obj).pointer_name = "Upper Cabinet Pulls"

    def draw(self):
        self.create_assembly("Doors")
        self.obj_bp["IS_DOORS_BP"] = True
        self.obj_bp["IS_EXTERIOR_BP"] = True
        # self.obj_bp["EXTERIOR_NAME"] = "DOORS"
        
        common_prompts.add_carcass_prompts(self)
        common_prompts.add_cabinet_prompts(self)
        common_prompts.add_door_prompts(self)
        common_prompts.add_front_prompts(self)
        common_prompts.add_front_overlay_prompts(self)
        common_prompts.add_pull_prompts(self)
        common_prompts.add_thickness_prompts(self)

        carcass_type = self.get_prompt("Carcass Type")
        carcass_type.set_value(self.carcass_type)

        door_swing_prompt = self.get_prompt("Door Swing")
        door_swing_prompt.set_value(self.door_swing)

        #VARS
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

        props = home_builder_utils.get_scene_props(bpy.context.scene)

        front_pointer = None
        pull_pointer = None
        if self.carcass_type == 'Base':
            front_pointer = props.cabinet_door_pointers["Base Cabinet Doors"]
            pull_pointer = props.pull_pointers["Base Cabinet Pulls"]
        if self.carcass_type == 'Tall':
            front_pointer = props.cabinet_door_pointers["Tall Cabinet Doors"]
            pull_pointer = props.pull_pointers["Tall Cabinet Pulls"]
        if self.carcass_type == 'Upper':
            front_pointer = props.cabinet_door_pointers["Upper Cabinet Doors"]
            pull_pointer = props.pull_pointers["Upper Cabinet Pulls"]

        #LEFT DOOR
        l_door = data_cabinet_parts.add_door_part(self,front_pointer)
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
        r_door = data_cabinet_parts.add_door_part(self,front_pointer)
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

        self.set_prompts()


class Drawers(Cabinet_Exterior):
    category_name = "Cabinet Exteriors"
    carcass_type = '' #Base, Tall, Upper

    drawer_qty = 3

    def add_drawer_front(self,index,prev_drawer_empty,calculator,to,lo,ro):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        drawer_front_height = self.get_prompt("Drawer Front " + str(index) + " Height").get_var(calculator.name,'drawer_front_height')
        x = self.obj_x.pyclone.get_var('location.x','x')
        y = self.obj_y.pyclone.get_var('location.y','y')
        z = self.obj_z.pyclone.get_var('location.z','z')
        top_overlay = to.get_var('top_overlay')
        left_overlay = lo.get_var('left_overlay')
        right_overlay = ro.get_var('right_overlay')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')

        front_empty = self.add_empty('Front Z Location ' + str(index))
        front_empty.empty_display_size = .001

        if prev_drawer_empty:
            prev_drawer_z_loc = prev_drawer_empty.pyclone.get_var('location.z','prev_drawer_z_loc')
            front_empty.pyclone.loc_z('prev_drawer_z_loc-drawer_front_height-vertical_gap',[prev_drawer_z_loc,drawer_front_height,vertical_gap])
        else:
            front_empty.pyclone.loc_z('z-drawer_front_height+top_overlay',[z,drawer_front_height,top_overlay])        
        
        drawer_z_loc = front_empty.pyclone.get_var('location.z',"drawer_z_loc")

        front_pointer = props.cabinet_door_pointers["Drawer Fronts"]
        pull_pointer = props.pull_pointers["Drawer Pulls"]

        drawer_front = data_cabinet_parts.add_door_part(self,front_pointer)
        drawer_front.set_name('Drawer Front')
        drawer_front.loc_x('-left_overlay',[left_overlay])
        drawer_front.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        drawer_front.loc_z('drawer_z_loc',[drawer_z_loc])
        drawer_front.rot_x(value = math.radians(90))
        drawer_front.rot_y(value = math.radians(-90))
        drawer_front.dim_x('drawer_front_height',[drawer_front_height])
        drawer_front.dim_y('(x+left_overlay+right_overlay)*-1',[x,left_overlay,right_overlay])
        drawer_front.dim_z('front_thickness',[front_thickness])

        self.add_drawer_pull(drawer_front,pull_pointer)

        return front_empty

    def draw(self):
        self.create_assembly("Drawers")
        self.obj_bp["IS_DRAWERS_BP"] = True
        self.obj_bp["IS_EXTERIOR_BP"] = True
        self.obj_bp["EXTERIOR_NAME"] = "DRAWERS"

        common_prompts.add_carcass_prompts(self)
        common_prompts.add_drawer_prompts(self)
        common_prompts.add_thickness_prompts(self)
        common_prompts.add_front_prompts(self)
        common_prompts.add_front_overlay_prompts(self)
        common_prompts.add_drawer_pull_prompts(self)

        carcass_type = self.get_prompt("Carcass Type")
        carcass_type.set_value("Drawer")

        to, bo, lo, ro = self.add_overlay_prompts()

        calc_distance_obj = self.add_empty('Calc Distance Obj')
        calc_distance_obj.empty_display_size = .001
        front_height_calculator = self.obj_prompts.pyclone.add_calculator("Front Height Calculator",calc_distance_obj)

        drawer = None
        for i in range(self.drawer_qty):
            front_height_calculator.add_calculator_prompt('Drawer Front ' + str(i + 1) + ' Height')
            drawer = self.add_drawer_front(i + 1,drawer,front_height_calculator,to,lo,ro)

        z = self.obj_z.pyclone.get_var('location.z','z')
        top_overlay = to.get_var('top_overlay')
        bottom_overlay = bo.get_var('bottom_overlay')
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        
        front_height_calculator.set_total_distance('z+top_overlay+bottom_overlay-vertical_gap*' + str(self.drawer_qty-1),[z,top_overlay,bottom_overlay,vertical_gap])

        self.set_prompts()


class Door_Drawer(Cabinet_Exterior):

    door_swing = 0 # Left = 0, Right = 1, Double = 2
    two_drawers = False

    def set_pull_props(self,obj):
        obj['IS_CABINET_PULL'] = True
        home_builder_pointers.assign_pointer_to_object(obj,"Cabinet Pull Finish")  
        if self.carcass_type == 'Base':
            home_builder_utils.get_object_props(obj).pointer_name = "Base Cabinet Pulls"
        if self.carcass_type == 'Tall':
            home_builder_utils.get_object_props(obj).pointer_name = "Tall Cabinet Pulls"
        if self.carcass_type == 'Upper':
            home_builder_utils.get_object_props(obj).pointer_name = "Upper Cabinet Pulls"

    def draw(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        self.create_assembly("Door Drawer")
        self.obj_bp["IS_DOORS_BP"] = True
        self.obj_bp["IS_EXTERIOR_BP"] = True
        # self.obj_bp["EXTERIOR_NAME"] = "DOORS"
        
        common_prompts.add_carcass_prompts(self)
        common_prompts.add_cabinet_prompts(self)
        common_prompts.add_door_prompts(self)
        common_prompts.add_front_prompts(self)
        common_prompts.add_front_overlay_prompts(self)
        common_prompts.add_pull_prompts(self)
        common_prompts.add_thickness_prompts(self)

        door_swing_prompt = self.get_prompt("Door Swing")
        door_swing_prompt.set_value(self.door_swing)

        add_two_drawer_fronts = self.add_prompt("Add Two Drawer Fronts",'CHECKBOX',self.two_drawers)
        add_two_drawer_fronts_var = add_two_drawer_fronts.get_var('add_two_drawer_fronts_var')

        top_df_height = self.add_prompt("Top Drawer Front Height",'DISTANCE',pc_unit.inch(6))
        top_df_height_var = top_df_height.get_var('top_df_height_var')

        carcass_type = self.get_prompt("Carcass Type")
        carcass_type.set_value(self.carcass_type)

        door_swing_prompt = self.get_prompt("Door Swing")
        door_swing_prompt.set_value(self.door_swing)

        #VARS
        x = self.obj_x.pyclone.get_var('location.x','x')
        z = self.obj_z.pyclone.get_var('location.z','z')        
        vertical_gap = self.get_prompt("Vertical Gap").get_var('vertical_gap')
        h_gap = self.get_prompt("Horizontal Gap").get_var('h_gap')
        door_swing = door_swing_prompt.get_var('door_swing')
        door_to_cabinet_gap = self.get_prompt("Door to Cabinet Gap").get_var('door_to_cabinet_gap')
        front_thickness = self.get_prompt("Front Thickness").get_var('front_thickness')
        door_rotation = self.get_prompt("Door Rotation").get_var('door_rotation')
        open_door = self.get_prompt("Open Door").get_var('open_door')

        to, bo, lo, ro = self.add_overlay_prompts()

        to_var = to.get_var("to_var")
        bo_var = bo.get_var("bo_var")
        lo_var = lo.get_var("lo_var")
        ro_var = ro.get_var("ro_var")

        front_pointer = None
        pull_pointer = None
        if self.carcass_type == 'Base':
            front_pointer = props.cabinet_door_pointers["Base Cabinet Doors"]
            pull_pointer = props.pull_pointers["Base Cabinet Pulls"]
        if self.carcass_type == 'Tall':
            front_pointer = props.cabinet_door_pointers["Tall Cabinet Doors"]
            pull_pointer = props.pull_pointers["Tall Cabinet Pulls"]
        if self.carcass_type == 'Upper':
            front_pointer = props.cabinet_door_pointers["Upper Cabinet Doors"]
            pull_pointer = props.pull_pointers["Upper Cabinet Pulls"]
        drawer_front_pointer = props.cabinet_door_pointers["Drawer Fronts"]
        drawer_pull_pointer = props.pull_pointers["Drawer Pulls"]

        #LEFT DOOR
        l_door = data_cabinet_parts.add_door_part(self,front_pointer)
        l_door.loc_x('-lo_var',[lo_var])
        l_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        l_door.loc_z('-bo_var',[bo_var])
        l_door.rot_x(value = math.radians(90))
        l_door.rot_y(value = math.radians(-90))
        l_door.rot_z('-door_rotation*open_door',[door_rotation,open_door])
        l_door.dim_x('z+to_var+bo_var-top_df_height_var-h_gap',[z,to_var,bo_var,top_df_height_var,h_gap])
        l_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)*-1',[door_swing,x,lo_var,ro_var,vertical_gap])            
        l_door.dim_z('front_thickness',[front_thickness])
        hide = l_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==1,True,False)',[door_swing])
        self.add_door_pull(l_door,pull_pointer)

        #RIGHT DOOR
        r_door = data_cabinet_parts.add_door_part(self,front_pointer)
        r_door.loc_x('x+ro_var',[x,ro_var])
        r_door.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        r_door.loc_z('-bo_var',[bo_var])
        r_door.rot_x(value = math.radians(90))
        r_door.rot_y(value = math.radians(-90))
        r_door.rot_z('door_rotation*open_door',[door_rotation,open_door])   
        r_door.dim_x('z+to_var+bo_var-top_df_height_var-h_gap',[z,to_var,bo_var,top_df_height_var,h_gap])
        r_door.dim_y('IF(door_swing==2,((x+lo_var+ro_var)-vertical_gap)/2,x+lo_var+ro_var)',[door_swing,x,lo_var,ro_var,vertical_gap])     
        r_door.dim_z('front_thickness',[front_thickness])
        hide = r_door.get_prompt("Hide") 
        hide.set_formula('IF(door_swing==0,True,False)',[door_swing])
        self.add_door_pull(r_door,pull_pointer)

        drawer_front = data_cabinet_parts.add_door_part(self,drawer_front_pointer)
        drawer_front.set_name('Drawer Front')
        drawer_front.loc_x('-lo_var',[lo_var])
        drawer_front.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        drawer_front.loc_z('z+to_var-top_df_height_var',[z,to_var,top_df_height_var])
        drawer_front.rot_x(value = math.radians(90))
        drawer_front.rot_y(value = math.radians(-90))
        drawer_front.dim_x('top_df_height_var',[top_df_height_var])
        drawer_front.dim_y('IF(add_two_drawer_fronts_var,(((x+lo_var+ro_var)-vertical_gap)/2)*-1,(x+lo_var+ro_var)*-1)',[add_two_drawer_fronts_var,x,lo_var,ro_var,vertical_gap])
        drawer_front.dim_z('front_thickness',[front_thickness])
        self.add_drawer_pull(drawer_front,drawer_pull_pointer)

        drawer_front = data_cabinet_parts.add_door_part(self,drawer_front_pointer)
        drawer_front.set_name('Drawer Front')
        drawer_front.loc_x('(x/2)+(vertical_gap/2)',[x,vertical_gap])
        drawer_front.loc_y('-door_to_cabinet_gap',[door_to_cabinet_gap])
        drawer_front.loc_z('z+to_var-top_df_height_var',[z,to_var,top_df_height_var])
        drawer_front.rot_x(value = math.radians(90))
        drawer_front.rot_y(value = math.radians(-90))
        drawer_front.dim_x('top_df_height_var',[top_df_height_var])
        drawer_front.dim_y('(((x+lo_var+ro_var)-vertical_gap)/2)*-1',[x,lo_var,ro_var,vertical_gap])
        drawer_front.dim_z('front_thickness',[front_thickness])
        hide = drawer_front.get_prompt('Hide')
        hide.set_formula('IF(add_two_drawer_fronts_var,False,True)',[add_two_drawer_fronts_var])
        self.add_drawer_pull(drawer_front,drawer_pull_pointer)

        self.set_prompts()