import bpy
from .cabinets import cabinet_library
from . import home_builder_utils
from .pc_lib import pc_utils

class home_builder_OT_draw_cabinet_sample(bpy.types.Operator):
    bl_idname = "home_builder.draw_cabinet_sample"
    bl_label = "Draw Cabinet Sample"
    bl_description = "This is a sample operator to draw cabinets"
    bl_options = {'UNDO'}
    
    def set_mute_drivers_property(self,obj,mute):
        drivers = pc_utils.get_drivers(obj)
        for driver in drivers:
            driver.mute = mute

    def link_obj_and_children_to_collection(self,collection,obj):
        collection.objects.link(obj)
        for child in obj.children:
            self.link_obj_and_children_to_collection(collection,child)

    def select_object_and_children(self,obj):
        #You must mute drivers so hidden objects can be selected
        self.set_mute_drivers_property(obj,True)
        obj.hide_select = False
        obj.hide_viewport = False
        obj.select_set(True)
        for child in obj.children:
            self.select_object_and_children(child)

    def unmute_drivers_for_obj_and_children_and_hide_empties(self,obj):
        self.set_mute_drivers_property(obj,False)
        if obj.type == 'EMPTY':
            obj.hide_viewport = True
        for child in obj.children:
            self.unmute_drivers_for_obj_and_children_and_hide_empties(child)

    def execute(self, context):
        #---MINIMUM CODE TO DRAW A CABINET
        #Create instance of Base 2 Door Cabinet
        base_cabinet = cabinet_library.Base_2_Door()
        #Call pre_draw() this is used when placing cabinet with modal function
        base_cabinet.pre_draw()
        #Call draw() this adds all of the parts to the cabinet
        base_cabinet.draw()
        #This hides empties. This is not nessasry but showing all empties makes the scene look busy
        home_builder_utils.hide_empties(base_cabinet.obj_bp)

        #---DRAW ANOTHER CABINET
        base_1_door_cabinet = cabinet_library.Base_1_Door()
        base_1_door_cabinet.pre_draw()
        base_1_door_cabinet.draw()
        #---TURN ON SINK
        add_sink = base_1_door_cabinet.get_prompt("Add Sink")
        add_sink.set_value(True)
        base_1_door_cabinet.add_sink("_Sample","Generic Large Sink")
        home_builder_utils.hide_empties(base_1_door_cabinet.obj_bp)

        #---MOVE CABINET AFTER PLACING
        base_1_door_cabinet.obj_bp.location.x = 2
        base_1_door_cabinet.obj_bp.location.y = .1
        base_1_door_cabinet.obj_bp.location.z = .01

        #---ROTATE CABINET AFTER PLACING
        base_1_door_cabinet.obj_bp.rotation_euler.z = .25

        #---CHANGE SIZE OF CABINET
        base_1_door_cabinet.obj_x.location.x = .5
        base_1_door_cabinet.obj_y.location.y = -.4 #base point is back left of cabinet, so y dim is negative
        base_1_door_cabinet.obj_z.location.z = 1

        #---MODIFY PROMPT OF CABINET
        ctop_back_overhang = base_1_door_cabinet.get_prompt("Countertop Overhang Back")
        ctop_back_overhang.set_value(.25)

        #---MODIFY PROMPT OF CARCASS
        toe_kick_height = base_1_door_cabinet.carcasses[0].get_prompt("Toe Kick Height")
        toe_kick_height.set_value(.25)        

        #---REMOVE CABINETS FROM ALL COLLECTIONS
        bpy.ops.object.select_all(action='DESELECT')
        self.select_object_and_children(base_1_door_cabinet.obj_bp)
        self.select_object_and_children(base_cabinet.obj_bp)
        bpy.ops.collection.objects_remove_all()

        #---ADD CABINETS TO NEW COLLECTIONS
        bpy.ops.object.select_all(action='DESELECT')     
        bpy.ops.collection.create(name="CABINET COLLECTION")
        collection = bpy.data.collections["CABINET COLLECTION"]
        bpy.context.scene.collection.children.link(collection)
        self.link_obj_and_children_to_collection(collection,base_1_door_cabinet.obj_bp)
        self.link_obj_and_children_to_collection(collection,base_cabinet.obj_bp)
        self.unmute_drivers_for_obj_and_children_and_hide_empties(base_1_door_cabinet.obj_bp)
        self.unmute_drivers_for_obj_and_children_and_hide_empties(base_cabinet.obj_bp)
        return {'FINISHED'}


class HOME_BUILDER_MT_sample_menu(bpy.types.Menu):
    bl_label = "Home Builder Sample Operators"

    def draw(self, _context):
        layout = self.layout
        layout.operator('home_builder.draw_cabinet_sample')


def draw_view3d_menu(self,context):
    layout = self.layout
    layout.menu('HOME_BUILDER_MT_sample_menu')


def register():
    bpy.utils.register_class(home_builder_OT_draw_cabinet_sample)
    bpy.utils.register_class(HOME_BUILDER_MT_sample_menu)
    bpy.types.VIEW3D_MT_editor_menus.append(draw_view3d_menu)
    
def unregister():
    bpy.utils.register_class(home_builder_OT_draw_cabinet_sample)
    bpy.utils.unregister_class(HOME_BUILDER_MT_sample_menu)