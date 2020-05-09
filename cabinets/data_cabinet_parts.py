from ..pc_lib import pc_types, pc_unit, pc_utils
from .. import home_builder_utils
from os import path

ASSET_DIR = home_builder_utils.get_asset_folder_path()
PART = path.join(ASSET_DIR,"Cutparts","Part.blend")

class Cutpart(pc_types.Assembly):
    category_name = "Parts"

    def draw(self):
        self.create_assembly("Part")

        self.obj_x.location.x = pc_unit.inch(120) #Length
        self.obj_y.location.y = pc_unit.inch(4)   #Depth
        self.obj_z.location.z = pc_unit.inch(2)   #Thickness

        quantity = self.obj_prompts.pyclone.add_prompt('QUANTITY',"Quantity")
        array_offset = self.obj_prompts.pyclone.add_prompt('DISTANCE',"Array Offset")
        quantity.set_value(1)
        array_offset.set_value(pc_unit.inch(16))

        qty = quantity.get_var("qty")
        array_offset = array_offset.get_var("array_offset")

        #When assigning vertices to a hook the transformation is made so the size must be 0
        # size = (self.obj_x.location.x,self.obj_y.location.y,self.obj_z.location.z)
        size = (0,0,0)
        obj_mesh = pc_utils.create_cube_mesh("Part",size)
        self.add_object(obj_mesh)

        uv_layer = obj_mesh.data.uv_layers.new()

        vgroup = obj_mesh.vertex_groups[self.obj_x.name]
        vgroup.add([2,3,6,7],1,'ADD')        

        vgroup = obj_mesh.vertex_groups[self.obj_y.name]
        vgroup.add([1,2,5,6],1,'ADD')

        vgroup = obj_mesh.vertex_groups[self.obj_z.name]
        vgroup.add([4,5,6,7],1,'ADD')        

        hook = obj_mesh.modifiers.new('XHOOK','HOOK')
        hook.object = self.obj_x
        hook.vertex_indices_set([2,3,6,7])

        hook = obj_mesh.modifiers.new('YHOOK','HOOK')
        hook.object = self.obj_y
        hook.vertex_indices_set([1,2,5,6])

        hook = obj_mesh.modifiers.new('ZHOOK','HOOK')
        hook.object = self.obj_z
        hook.vertex_indices_set([4,5,6,7])

        array = obj_mesh.modifiers.new('Quantity','ARRAY')
        array.use_constant_offset = True
        array.use_relative_offset = False
        obj_mesh.pyclone.modifier(array,'count',-1,'qty',[qty])
        obj_mesh.pyclone.modifier(array,'constant_offset_displace',2,'array_offset',[array_offset])    

        bevel = obj_mesh.modifiers.new('Bevel','BEVEL')    
        bevel.width = .001


class Square_Cutout(pc_types.Assembly):
    category_name = "Machining"

    obj_mesh = None

    def assign_boolean(self,assembly):
        for child in assembly.obj_bp.children:
            if child.type == 'MESH':       
                mod = child.modifiers.new(self.obj_mesh.name,'BOOLEAN')
                mod.object = self.obj_mesh
                mod.operation = 'DIFFERENCE'    
        self.obj_mesh.hide_viewport = True
        self.obj_mesh.display_type = 'WIRE'             

    def draw(self):
        self.create_assembly("Square Cutout")

        self.obj_x.location.x = pc_unit.inch(120) #Length
        self.obj_y.location.y = pc_unit.inch(4)   #Depth
        self.obj_z.location.z = pc_unit.inch(2)   #Thickness

        #When assigning vertices to a hook the transformation is made so the size must be 0
        # size = (self.obj_x.location.x,self.obj_y.location.y,self.obj_z.location.z)
        size = (0,0,0)
        self.obj_mesh = pc_utils.create_cube_mesh("Part",size)
        self.add_object(self.obj_mesh)

        uv_layer = self.obj_mesh.data.uv_layers.new()

        vgroup = self.obj_mesh.vertex_groups[self.obj_x.name]
        vgroup.add([2,3,6,7],1,'ADD')

        vgroup = self.obj_mesh.vertex_groups[self.obj_y.name]
        vgroup.add([1,2,5,6],1,'ADD')

        vgroup = self.obj_mesh.vertex_groups[self.obj_z.name]
        vgroup.add([4,5,6,7],1,'ADD')

        hook = self.obj_mesh.modifiers.new('XHOOK','HOOK')
        hook.object = self.obj_x
        hook.vertex_indices_set([2,3,6,7])

        hook = self.obj_mesh.modifiers.new('YHOOK','HOOK')
        hook.object = self.obj_y
        hook.vertex_indices_set([1,2,5,6])

        hook = self.obj_mesh.modifiers.new('ZHOOK','HOOK')
        hook.object = self.obj_z
        hook.vertex_indices_set([4,5,6,7])


class Hardware_Part(pc_types.Assembly):
    category_name = "Parts"
    prompt_id = "room.part_prompts"
    placement_id = "room.draw_multiple_walls"    

class Buyout_Part(pc_types.Assembly):
    category_name = "Parts"
    prompt_id = "room.part_prompts"
    placement_id = "room.draw_multiple_walls"        

class Extruded_Part(pc_types.Assembly):
    category_name = "Parts"
    prompt_id = "room.part_prompts"
    placement_id = "room.draw_multiple_walls"            

def add_countertop_part(assembly):
    part = pc_types.Assembly(assembly.add_assembly_from_file(PART))
    assembly.add_assembly(part)
    home_builder_utils.add_bevel(part)
    home_builder_utils.assign_countertop_pointers(part)
    home_builder_utils.assign_materials_to_assembly(part)
    return part

def add_door_part(assembly):
    part = pc_types.Assembly(assembly.add_assembly_from_file(PART))
    assembly.add_assembly(part)
    home_builder_utils.add_bevel(part)
    home_builder_utils.assign_door_pointers(part)
    home_builder_utils.assign_materials_to_assembly(part)
    return part

def add_carcass_part(assembly):
    part = pc_types.Assembly(assembly.add_assembly_from_file(PART))
    assembly.add_assembly(part)
    home_builder_utils.add_bevel(part)
    home_builder_utils.assign_material_pointers(part)
    home_builder_utils.assign_materials_to_assembly(part)
    return part

def add_rectangular_part(assembly):
    part = pc_types.Assembly(assembly.add_assembly_from_file(PART))
    assembly.add_assembly(part)
    home_builder_utils.add_bevel(part)
    home_builder_utils.assign_material_pointers(part)
    home_builder_utils.assign_materials_to_assembly(part)
    return part

def add_square_cutout(assembly):
    part = pc_types.Assembly(assembly.add_assembly_from_file(PART))
    assembly.add_assembly(part)
    return part    