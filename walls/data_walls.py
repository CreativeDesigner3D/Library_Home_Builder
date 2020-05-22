import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
import time
from .. import home_builder_utils
from . import data_parts

class Wall(pc_types.Assembly):
    show_in_library = True
    
    def render(self):
        self.draw_wall()

    def draw_wall(self):
        self.create_assembly("Wall Mesh")
        props = home_builder_utils.get_scene_props(bpy.context.scene)

        #ASSIGN PROPERTY
        self.obj_bp["IS_WALL_BP"] = True

        #Set Default Dimensions
        self.obj_x.location.x = pc_unit.inch(120) #Length
        self.obj_y.location.y = props.wall_thickness
        self.obj_z.location.z = props.wall_height

        #Add Objects
        left_angle_empty = self.add_empty("Left Angle")
        right_angle_empty = self.add_empty("Right Angle")

        size = (0,0,0)
        obj_mesh = pc_utils.create_cube_mesh("Wall Mesh",size)
        self.add_object(obj_mesh)

        #Assign Mesh Hooks
        vgroup = obj_mesh.vertex_groups[left_angle_empty.name]
        vgroup.add([1,5],1,'ADD')  

        vgroup = obj_mesh.vertex_groups[right_angle_empty.name]
        vgroup.add([2,6],1,'ADD')

        vgroup = obj_mesh.vertex_groups[self.obj_x.name]
        vgroup.add([3,7],1,'ADD')        

        vgroup = obj_mesh.vertex_groups[self.obj_z.name]
        vgroup.add([4,5,6,7],1,'ADD')        

        hook = obj_mesh.modifiers.new('XHOOK','HOOK')
        hook.object = self.obj_x
        hook.vertex_indices_set([3,7])

        hook = obj_mesh.modifiers.new('LEFTANGLE','HOOK')
        hook.object = left_angle_empty
        hook.vertex_indices_set([1,5])

        hook = obj_mesh.modifiers.new('RIGHTANGLE','HOOK')
        hook.object = right_angle_empty
        hook.vertex_indices_set([2,6])        

        hook = obj_mesh.modifiers.new('ZHOOK','HOOK')
        hook.object = self.obj_z
        hook.vertex_indices_set([4,5,6,7])

        #Assign Drivers
        length = self.obj_x.pyclone.get_var('location.x','length')
        wall_thickness = self.obj_y.pyclone.get_var('location.y','wall_thickness')

        left_angle = self.obj_prompts.pyclone.add_prompt('ANGLE',"Left Angle")
        right_angle = self.obj_prompts.pyclone.add_prompt('ANGLE',"Right Angle")

        left_angle_var = left_angle.get_var('left_angle_var')
        right_angle_var = right_angle.get_var('right_angle_var')

        left_angle_empty.pyclone.loc_x('tan(left_angle_var)*wall_thickness',[left_angle_var,wall_thickness])
        left_angle_empty.pyclone.loc_y('wall_thickness',[wall_thickness])

        right_angle_empty.pyclone.loc_x('length+tan(right_angle_var)*wall_thickness',[length,right_angle_var,wall_thickness])
        right_angle_empty.pyclone.loc_y('wall_thickness',[wall_thickness])


class Wall_with_Studs(pc_types.Assembly):
    show_in_library = True

    def render(self):
        self.draw_wall()

    def draw_wall(self):
        start_time = time.time()
        #Create Assembly
        props = home_builder_utils.get_scene_props(bpy.context.scene)
        self.create_assembly("Wall")

        #ASSIGN PROPERTY
        self.obj_bp["IS_WALL_BP"] = True

        #Set Default Dimensions
        self.obj_x.location.x = pc_unit.inch(120) #Length
        self.obj_y.location.y = props.wall_thickness
        self.obj_z.location.z = props.wall_height

        #Figure out how to run operators from draw function
        # bpy.ops.mesh.primitive_circle_add()
        # bpy.context.view_layer.objects.active.parent = self.obj_bp
        
        #Get Product Variables
        length = self.obj_x.pyclone.get_var('location.x','length')
        wall_thickness = self.obj_y.pyclone.get_var('location.y','wall_thickness')
        height = self.obj_z.pyclone.get_var('location.z','height')

        #Add Prompts
        left_angle = self.obj_prompts.pyclone.add_prompt('ANGLE',"Left Angle")
        right_angle = self.obj_prompts.pyclone.add_prompt('ANGLE',"Right Angle")

        stud_spacing_distance = self.obj_prompts.pyclone.add_prompt('DISTANCE',"Stud Spacing Distance")
        stud_spacing_distance.set_value(pc_unit.inch(16))

        material_thickness = self.obj_prompts.pyclone.add_prompt('DISTANCE',"Material Thickness")
        material_thickness.set_value(pc_unit.inch(2))

        #Get Prompt Variables
        material_thickness = material_thickness.get_var("material_thickness")
        stud_spacing_distance = stud_spacing_distance.get_var("stud_spacing_distance")

        #Add Parts
        bottom_plate = self.add_assembly(data_parts.Stud())
        bottom_plate.set_name('Bottom Plate')
        bottom_plate.loc_x(value=0)
        bottom_plate.loc_y(value=0)
        bottom_plate.loc_z(value=0)
        bottom_plate.dim_x('length',[length])
        bottom_plate.dim_y('wall_thickness',[wall_thickness])
        bottom_plate.dim_z('material_thickness',[material_thickness])

        top_plate = self.add_assembly(data_parts.Stud())
        top_plate.set_name('Top Plate')
        top_plate.loc_x(value=0)
        top_plate.loc_y(value=0)
        top_plate.loc_z('height',[height])
        top_plate.dim_x('length',[length])
        top_plate.dim_y('wall_thickness',[wall_thickness])
        top_plate.dim_z('-material_thickness',[material_thickness])

        first_stud = self.add_assembly(data_parts.Stud())
        first_stud.set_name('First Stud')
        first_stud.loc_x(value=0)
        first_stud.loc_y(value=0)
        first_stud.loc_z('material_thickness',[material_thickness])
        first_stud.rot_y(value=math.radians(-90))
        first_stud.dim_x('height-(material_thickness*2)',[height,material_thickness])
        first_stud.dim_y('wall_thickness',[wall_thickness])
        first_stud.dim_z('-material_thickness',[material_thickness])

        last_stud = self.add_assembly(data_parts.Stud())
        last_stud.set_name('Last Stud')
        last_stud.loc_x('length',[length])
        last_stud.loc_y(value=0)
        last_stud.loc_z('material_thickness',[material_thickness])
        last_stud.rot_y(value=math.radians(-90))
        last_stud.dim_x('height-(material_thickness*2)',[height,material_thickness])
        last_stud.dim_y('wall_thickness',[wall_thickness])
        last_stud.dim_z('material_thickness',[material_thickness])

        center_stud = self.add_assembly(data_parts.Stud())
        center_stud.set_name('Center Stud')
        center_stud.loc_x('stud_spacing_distance',[stud_spacing_distance])
        center_stud.loc_y(value=0)
        center_stud.loc_z('material_thickness',[material_thickness])
        center_stud.rot_y(value=math.radians(-90))
        center_stud.dim_x('height-(material_thickness*2)',[height,material_thickness])
        center_stud.dim_y('wall_thickness',[wall_thickness])
        center_stud.dim_z('material_thickness',[material_thickness])

        qty = center_stud.get_prompt('Quantity')
        offset = center_stud.get_prompt('Array Offset')

        qty.set_formula('(length-material_thickness)/stud_spacing_distance',[length,material_thickness,stud_spacing_distance])
        offset.set_formula('-stud_spacing_distance',[stud_spacing_distance])  
             
        print("WALL: Draw Time --- %s seconds ---" % (time.time() - start_time))


class Room(pc_types.Assembly):
    show_in_library = True

    def draw(self):
        start_time = time.time()
        
        #Create Assembly
        props = home_builder_utils.get_scene_props(bpy.context.scene)
        self.create_assembly("Room")

        #ASSIGN PROPERTY
        self.obj_bp["IS_ROOM_BP"] = True

        #Set Default Dimensions
        self.obj_x.location.x = pc_unit.inch(120) #Length
        self.obj_y.location.y = pc_unit.inch(120) #Depth
        self.obj_z.location.z = props.wall_height

        #Get Product Variables
        length = self.obj_x.pyclone.get_var('location.x','length')
        depth = self.obj_y.pyclone.get_var('location.y','depth')
        height = self.obj_z.pyclone.get_var('location.z','height')

        #Add Prompts
        wall_thickness = self.obj_prompts.pyclone.add_prompt('DISTANCE',"Wall Thickness")

        #Set Prompt Formulas or default values
        wall_thickness.set_value(props.wall_thickness)

        #Get Prompt Variables
        wall_thickness = wall_thickness.get_var("wall_thickness")

        front_wall = self.add_assembly(Wall())
        front_wall.draw_wall()
        front_wall.obj_bp.location = (0,0,0)
        front_wall.obj_bp.parent = self.obj_bp        
        front_wall.set_name("Front Wall")
        front_wall.loc_x(value=0)
        front_wall.loc_y(value=0)
        front_wall.loc_z(value=0)
        front_wall.rot_z(value=math.radians(0))
        front_wall.dim_x('length',[length])
        front_wall.dim_y('wall_thickness',[wall_thickness])
        front_wall.dim_z('height',[height])

        back_wall = self.add_assembly(Wall())
        back_wall.draw_wall()
        back_wall.obj_bp.location = (0,0,0)
        back_wall.obj_bp.parent = self.obj_bp            
        back_wall.set_name("Back Wall")
        back_wall.loc_x(value=0)
        back_wall.loc_y('depth-wall_thickness',[depth,wall_thickness])
        back_wall.loc_z(value=0)
        back_wall.rot_z(value=math.radians(0))
        back_wall.dim_x('length',[length])
        back_wall.dim_y('wall_thickness',[wall_thickness])
        back_wall.dim_z('height',[height])

        left_wall = self.add_assembly(Wall())
        left_wall.draw_wall()
        left_wall.obj_bp.location = (0,0,0)
        left_wall.obj_bp.parent = self.obj_bp            
        left_wall.set_name("Left Wall")
        left_wall.loc_x('length',[length])
        left_wall.loc_y('wall_thickness',[wall_thickness])
        left_wall.loc_z(value=0)
        left_wall.rot_z(value=math.radians(90))
        left_wall.dim_x('depth-(wall_thickness*2)',[depth,wall_thickness])
        left_wall.dim_y('wall_thickness',[wall_thickness])
        left_wall.dim_z('height',[height])      

        right_wall = self.add_assembly(Wall())
        right_wall.draw_wall()
        right_wall.obj_bp.location = (0,0,0)
        right_wall.obj_bp.parent = self.obj_bp            
        right_wall.set_name("Right Wall")
        right_wall.loc_x(value=0)
        right_wall.loc_y('wall_thickness',[wall_thickness])
        right_wall.loc_z(value=0)
        right_wall.rot_z(value=math.radians(90))
        right_wall.dim_x('depth-(wall_thickness*2)',[depth,wall_thickness])
        right_wall.dim_y('-wall_thickness',[wall_thickness])
        right_wall.dim_z('height',[height])            

        print("ROOM: Draw Time --- %s seconds ---" % (time.time() - start_time))