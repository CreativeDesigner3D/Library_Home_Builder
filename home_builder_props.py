import bpy
import os
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        )
from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        CollectionProperty,
        EnumProperty,
        )
from .pc_lib import pc_types, pc_unit, pc_utils, pc_pointer_utils
from . import home_builder_utils

preview_collections = {}
preview_collections["material_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["material_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["pull_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["pull_items"] = pc_pointer_utils.create_image_preview_collection()

def enum_material_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_utils.get_material_path()
    pcoll = preview_collections["material_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_material_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_utils.get_material_path(),self.material_category)
    pcoll = preview_collections["material_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_material_category(self,context):
    if preview_collections["material_items"]:
        bpy.utils.previews.remove(preview_collections["material_items"])
        preview_collections["material_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_material_names(self,context)

def enum_pull_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_utils.get_pull_path()
    pcoll = preview_collections["pull_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_pull_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_utils.get_pull_path(),self.pull_category)
    pcoll = preview_collections["pull_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_pull_category(self,context):
    if preview_collections["pull_items"]:
        bpy.utils.previews.remove(preview_collections["pull_items"])
        preview_collections["pull_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_pull_names(self,context)


class Pointer(PropertyGroup):
    category: bpy.props.StringProperty(name="Category")
    item_name: bpy.props.StringProperty(name="Item Name")


class Home_Builder_Scene_Props(PropertyGroup):
    room_tabs: EnumProperty(name="Room Tabs",
                            items=[('ROOM_SIZES',"Room Sizes","Show the Room Sizes"),
                                   ('MATERIALS',"Room Materials","Show the Room Materials"),
                                   ('ROOM_TOOLS',"Room Tools","Show the Room Tools")],
                            default='ROOM_SIZES')

    active_category: StringProperty(name="Active Category",default="")

    wall_height: FloatProperty(name="Wall Height",default=pc_unit.inch(96),subtype='DISTANCE')
    wall_thickness: FloatProperty(name="Wall Thickness",default=pc_unit.inch(6),subtype='DISTANCE')

    base_cabinet_depth: bpy.props.FloatProperty(name="Base Cabinet Depth",
                                                 description="Default depth for base cabinets",
                                                 default=pc_unit.inch(23.0),
                                                 unit='LENGTH')
    
    base_cabinet_height: bpy.props.FloatProperty(name="Base Cabinet Height",
                                                  description="Default height for base cabinets",
                                                  default=pc_unit.inch(34.0),
                                                  unit='LENGTH')
    
    base_inside_corner_size: bpy.props.FloatProperty(name="Base Inside Corner Size",
                                                     description="Default width and depth for the inside base corner cabinets",
                                                     default=pc_unit.inch(36.0),
                                                     unit='LENGTH')
    
    tall_cabinet_depth: bpy.props.FloatProperty(name="Tall Cabinet Depth",
                                                 description="Default depth for tall cabinets",
                                                 default=pc_unit.inch(25.0),
                                                 unit='LENGTH')
    
    tall_cabinet_height: bpy.props.FloatProperty(name="Tall Cabinet Height",
                                                  description="Default height for tall cabinets",
                                                  default=pc_unit.inch(84.0),
                                                  unit='LENGTH')
    
    upper_cabinet_depth: bpy.props.FloatProperty(name="Upper Cabinet Depth",
                                                  description="Default depth for upper cabinets",
                                                  default=pc_unit.inch(12.0),
                                                  unit='LENGTH')
    
    upper_cabinet_height: bpy.props.FloatProperty(name="Upper Cabinet Height",
                                                   description="Default height for upper cabinets",
                                                   default=pc_unit.inch(34.0),
                                                   unit='LENGTH')
    
    upper_inside_corner_size: bpy.props.FloatProperty(name="Upper Inside Corner Size",
                                                      description="Default width and depth for the inside upper corner cabinets",
                                                      default=pc_unit.inch(24.0),
                                                      unit='LENGTH')
    
    sink_cabinet_depth: bpy.props.FloatProperty(name="Upper Cabinet Depth",
                                                 description="Default depth for sink cabinets",
                                                 default=pc_unit.inch(23.0),
                                                 unit='LENGTH')
    
    sink_cabinet_height: bpy.props.FloatProperty(name="Upper Cabinet Height",
                                                  description="Default height for sink cabinets",
                                                  default=pc_unit.inch(34.0),
                                                  unit='LENGTH')

    suspended_cabinet_depth: bpy.props.FloatProperty(name="Upper Cabinet Depth",
                                                      description="Default depth for suspended cabinets",
                                                      default=pc_unit.inch(23.0),
                                                      unit='LENGTH')
    
    suspended_cabinet_height: bpy.props.FloatProperty(name="Upper Cabinet Height",
                                                       description="Default height for suspended cabinets",
                                                       default=pc_unit.inch(6.0),
                                                       unit='LENGTH')

    column_width: bpy.props.FloatProperty(name="Column Width",
                                           description="Default width for cabinet columns",
                                           default=pc_unit.inch(2),
                                           unit='LENGTH')

    width_1_door: bpy.props.FloatProperty(name="Width 1 Door",
                                           description="Default width for one door wide cabinets",
                                           default=pc_unit.inch(18.0),
                                           unit='LENGTH')
    
    width_2_door: bpy.props.FloatProperty(name="Width 2 Door",
                                           description="Default width for two door wide and open cabinets",
                                           default=pc_unit.inch(36.0),
                                           unit='LENGTH')
    
    width_drawer: bpy.props.FloatProperty(name="Width Drawer",
                                           description="Default width for drawer cabinets",
                                           default=pc_unit.inch(18.0),
                                           unit='LENGTH')
    
    base_width_blind: bpy.props.FloatProperty(name="Base Width Blind",
                                               description="Default width for base blind corner cabinets",
                                               default=pc_unit.inch(48.0),
                                               unit='LENGTH')
    
    tall_width_blind: bpy.props.FloatProperty(name="Tall Width Blind",
                                               description="Default width for tall blind corner cabinets",
                                               default=pc_unit.inch(48.0),
                                               unit='LENGTH')
    
    blind_panel_reveal: bpy.props.FloatProperty(name="Blind Panel Reveal",
                                                 description="Default reveal for blind panels",
                                                 default=pc_unit.inch(3.0),
                                                 unit='LENGTH')
    
    inset_blind_panel: bpy.props.BoolProperty(name="Inset Blind Panel",
                                               description="Check this to inset the blind panel into the cabinet carcass",
                                               default=True)
    
    upper_width_blind: bpy.props.FloatProperty(name="Upper Width Blind",
                                                description="Default width for upper blind corner cabinets",
                                                default=pc_unit.inch(36.0),
                                                unit='LENGTH')

    height_above_floor: bpy.props.FloatProperty(name="Height Above Floor",
                                                 description="Default height above floor for upper cabinets",
                                                 default=pc_unit.inch(84.0),
                                                 unit='LENGTH')
    
    equal_drawer_stack_heights: bpy.props.BoolProperty(name="Equal Drawer Stack Heights", 
                                                        description="Check this make all drawer stack heights equal. Otherwise the Top Drawer Height will be set.", 
                                                        default=True)
    
    top_drawer_front_height: bpy.props.FloatProperty(name="Top Drawer Front Height",
                                                      description="Default top drawer front height.",
                                                      default=pc_unit.inch(6.0),
                                                      unit='LENGTH')

    material_pointers: bpy.props.CollectionProperty(name="Material Pointers",type=Pointer)
    pull_pointers: bpy.props.CollectionProperty(name="Pull Pointers",type=Pointer)

    material_category: bpy.props.EnumProperty(name="Material Category",items=enum_material_categories,update=update_material_category)
    material_name: bpy.props.EnumProperty(name="Material Name",items=enum_material_names)

    pull_category: bpy.props.EnumProperty(name="Pull Category",items=enum_pull_categories,update=update_pull_category)
    pull_name: bpy.props.EnumProperty(name="Pull Name",items=enum_pull_names)

    def draw_room_sizes(self,layout):
        box = layout.box()
        box.label(text="Default Wall Size",icon='MOD_BUILD')

        row = box.row()
        row.label(text="Default Wall Height")
        row.prop(self,'wall_height',text="")

        row = box.row()
        row.label(text="Default Wall Thickness")
        row.prop(self,'wall_thickness',text="")

    def draw_materials(self,layout):
        split = layout.split(factor=.25)
        left_col = split.column()
        right_col = split.column()

        material_box = left_col.box()
        row = material_box.row()
        row.label(text="Material Selections:")

        material_box.prop(self,'material_category',text="",icon='FILE_FOLDER')  
        if len(self.material_name) > 0:
            material_box.template_icon_view(self,"material_name",show_labels=True)  

        right_row = right_col.row()
        right_row.scale_y = 1.3
        right_row.operator('room.update_scene_materials',text="Update Materials",icon='FILE_REFRESH')

        box = right_col.box()
        col = box.column(align=True)
        for mat in self.material_pointers:
            row = col.row()
            row.operator('room.update_material_pointer',text=mat.name,icon='FORWARD').pointer_name = mat.name
            row.label(text=mat.category + " - " + mat.item_name,icon='MATERIAL')

    def draw_room_tools(self,layout):
        box = layout.box()
        box.label(text="General Room Tools",icon='MOD_BUILD')   
        box.operator('room.draw_molding',text="Auto Add Base Molding")
        box.operator('room.draw_molding',text="Auto Add Crown Molding")              
        box.operator('room.draw_floor_plane',text="Add Floor")

        box = layout.box()
        box.label(text="Room Lighting Tools",icon='MOD_BUILD')  
        box.operator('room.add_room_light',text="Add Room Light")

        box = layout.box()
        box.label(text="2D Drawing Tools",icon='MOD_BUILD')  
        box.operator('room.draw_molding',text="Generate 2D View Scenes")      
        box.operator('room.draw_molding',text="Show Dimensions")

    def draw_hardware(self,layout):
        split = layout.split(factor=.25)
        left_col = split.column()
        right_col = split.column()

        hardware_box = left_col.box()
        row = hardware_box.row()
        row.label(text="Pull Selections:")

        hardware_box.prop(self,'pull_category',text="",icon='FILE_FOLDER')  
        if len(self.pull_name) > 0:
            hardware_box.template_icon_view(self,"pull_name",show_labels=True)  

        # right_row = right_col.row()
        # right_row.scale_y = 1.3
        # right_row.operator('kitchen.update_scene_pulls',text="Update Pulls",icon='FILE_REFRESH')

        box = right_col.box()
        col = box.column(align=True)
        for pull in self.pull_pointers:
            row = col.row()
            # row.operator('kitchen.update_pull_pointer',text=pull.name,icon='FORWARD').pointer_name = pull.name
            row.label(text=pull.category + " - " + pull.item_name,icon='MODIFIER_ON')

    def draw(self,layout):
        col = layout.column(align=True)

        row = col.row(align=True)
        row.scale_y = 1.3        
        row.prop_enum(self, "room_tabs", 'ROOM_SIZES', icon='PROPERTIES', text="Settings") 
        row.prop_enum(self, "room_tabs", 'MATERIALS', icon='COLOR', text="Materials") 
        row.prop_enum(self, "room_tabs", 'ROOM_TOOLS', icon='MODIFIER_ON', text="Tools") 

        box = col.box()

        if self.room_tabs == 'ROOM_SIZES':
            self.draw_room_sizes(box)

        if self.room_tabs == 'MATERIALS':
            self.draw_materials(box)

        if self.room_tabs == 'ROOM_TOOLS':
            self.draw_room_tools(box)
            self.draw_hardware(box)

    @classmethod
    def register(cls):
        bpy.types.Scene.home_builder = PointerProperty(
            name="Home Builder Props",
            description="Home Builder Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.home_builder

class Home_Builder_Object_Props(PropertyGroup):

    connected_object: bpy.props.PointerProperty(name="Connected Object",
                                                type=bpy.types.Object,
                                                description="This is the used to store objects that are connected together.")

    @classmethod
    def register(cls):
        bpy.types.Object.home_builder = PointerProperty(
            name="Home Builder Props",
            description="Home Builder Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Object.home_builder

classes = (
    Pointer,
    Home_Builder_Object_Props,
    Home_Builder_Scene_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)        