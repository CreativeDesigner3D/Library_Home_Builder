from .pc_lib import pc_types, pc_unit, pc_utils

class Hole(pc_types.Assembly):

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
        self.create_assembly("Hole")

        self.obj_x.location.x = pc_unit.inch(120) #Length
        self.obj_y.location.y = pc_unit.inch(4)   #Depth
        self.obj_z.location.z = pc_unit.inch(2)   #Thickness

        #When assigning vertices to a hook the transformation is made so the size must be 0
        # size = (self.obj_x.location.x,self.obj_y.location.y,self.obj_z.location.z)
        size = (0,0,0)
        self.obj_mesh = pc_utils.create_cube_mesh("Hole",size)
        self.obj_mesh.hide_render = True
        self.add_object(self.obj_mesh)
        self.obj_mesh['IS_BOOLEAN'] = True

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