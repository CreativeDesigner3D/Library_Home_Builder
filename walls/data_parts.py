import bpy
import math
from ..pc_lib import pc_types, pc_unit, pc_utils
import time

class Cube(pc_types.Assembly):

    def draw(self):
        start_time = time.time()
        self.create_assembly("Cube")

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
        obj_mesh = pc_utils.create_cube_mesh("Cube",size)
        self.add_object(obj_mesh)

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

        #THIS OPERATION TAKES THE LONGEST
        # obj_mesh.bp_props.hook_vertex_group_to_object(self.obj_x.name,self.obj_x)
        # obj_mesh.bp_props.hook_vertex_group_to_object(self.obj_y.name,self.obj_y)
        # obj_mesh.bp_props.hook_vertex_group_to_object(self.obj_z.name,self.obj_z)
        print("STUD: Draw Time --- %s seconds ---" % (time.time() - start_time))

class Stud(pc_types.Assembly):
    show_in_library = True

    def draw(self):
        start_time = time.time()
        self.create_assembly("Stud")

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
        obj_mesh = pc_utils.create_cube_mesh("Bottom Plate",size)
        self.add_object(obj_mesh)

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

        #THIS OPERATION TAKES THE LONGEST
        # obj_mesh.bp_props.hook_vertex_group_to_object(self.obj_x.name,self.obj_x)
        # obj_mesh.bp_props.hook_vertex_group_to_object(self.obj_y.name,self.obj_y)
        # obj_mesh.bp_props.hook_vertex_group_to_object(self.obj_z.name,self.obj_z)
        print("STUD: Draw Time --- %s seconds ---" % (time.time() - start_time))