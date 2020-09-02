import bpy
import os
from bpy.types import (
        Operator,
        Panel,
        PropertyGroup,
        UIList,
        AddonPreferences,
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
import inspect
from .pc_lib import pc_types, pc_unit, pc_utils, pc_pointer_utils
from . import home_builder_utils
from . import home_builder_enums
from . import home_builder_paths
from .walls import data_walls
from .doors import door_library
from .cabinets import cabinet_library
from .cabinets import data_appliances
from .windows import window_library

library_modules = [cabinet_library,
                   data_walls,
                   door_library,
                   window_library,
                   data_appliances]

class Pointer(PropertyGroup):
    category: bpy.props.StringProperty(name="Category")
    item_name: bpy.props.StringProperty(name="Item Name")

class Asset(PropertyGroup):
    is_selected: BoolProperty(name="Is Selected",default=False)
    preview_found: BoolProperty(name="Preivew Found",default=False)
    library_path: StringProperty(name="Library Path")
    package_name: StringProperty(name="Package Name")
    module_name: StringProperty(name="Module Name")
    category_name: StringProperty(name="Category Name")
    class_name: StringProperty(name="Class Name")

class Home_Builder_AddonPreferences(AddonPreferences):
    bl_idname = __package__

    assets_filepath: StringProperty(
        name="Assets Filepath",
        subtype='FILE_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "assets_filepath")

class Home_Builder_Window_Manager_Props(PropertyGroup):
    assets: CollectionProperty(name='Assets',type=Asset)

    def get_assets(self):
        for asset in self.assets:
            self.assets.remove(0)

        library_path = home_builder_paths.get_library_path()
        for module in library_modules:
            for name, obj in inspect.getmembers(module):
                if hasattr(obj,'show_in_library') and name != 'ops' and obj.show_in_library:
                    asset = self.assets.add()
                    asset.name = name.replace("_"," ")
                    asset.category_name = obj.category_name
                    asset.library_path = os.path.join(library_path,asset.category_name)
                    asset.package_name = module.__name__.split(".")[-2]
                    asset.module_name = module.__name__.split(".")[-1]
                    asset.class_name = name

    def get_asset(self,filepath):
        directory, file = os.path.split(filepath)
        filename, ext = os.path.splitext(file)   
                
        #TODO:GET RIGHT CLASS
        for asset in self.assets:
            if asset.library_path in filepath and filename == asset.name:
                obj = eval(asset.module_name + "." + asset.class_name + "()")
                # obj.set_name(asset.name)
                return obj

    @classmethod
    def register(cls):
        bpy.types.WindowManager.home_builder = PointerProperty(
            name="Home Builder Props",
            description="Home Builder Props",
            type=cls,
        )
        
    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.home_builder

class Home_Builder_Scene_Props(PropertyGroup):
    ui_tabs: EnumProperty(name="UI Tabs",
                          items=[('DEFAULTS',"Defaults","Default Library Settings"),
                                 ('CONSTRUCTION',"Construction","Show the Cabinet Construction Options"),
                                 ('MATERIALS',"Materials","Show the Material Options"),
                                 ('MOLDINGS',"Moldings","Show the Molding Options"),
                                 ('FRONTS',"Fronts","Show the Door and Drawer Front Options"),
                                 ('HARDWARE',"Hardware","Show the Hardware Options"),
                                 ('LIBRARY',"Library","Show the Library Options")],
                          default='DEFAULTS')

    size_tabs: EnumProperty(name="Size Tabs",
                          items=[('CABINETS',"Cabinets","Show the Cabinet Size Options"),
                                 ('DOORS',"Doors","Show the Door Options"),
                                 ('WINDOWS',"Windows","Show the Window Options"),
                                 ('WALLS',"Walls","Show the Wall Options")],
                          default='CABINETS')

    active_category: StringProperty(name="Active Category")

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

    window_height_from_floor: bpy.props.FloatProperty(name="Window Height from Floor",
                                                      description="This is location windows are placed from the floor.",
                                                      default=pc_unit.inch(40.0),
                                                      unit='LENGTH')

    material_pointers: bpy.props.CollectionProperty(name="Material Pointers",type=Pointer)
    pull_pointers: bpy.props.CollectionProperty(name="Pull Pointers",type=Pointer)

    material_category: bpy.props.EnumProperty(name="Material Category",
        items=home_builder_enums.enum_material_categories,
        update=home_builder_enums.update_material_category)
    material_name: bpy.props.EnumProperty(name="Material Name",
        items=home_builder_enums.enum_material_names)

    pull_category: bpy.props.EnumProperty(name="Pull Category",
        items=home_builder_enums.enum_pull_categories,
        update=home_builder_enums.update_pull_category)
    pull_name: bpy.props.EnumProperty(name="Pull Name",
        items=home_builder_enums.enum_pull_names)

    def draw_sizes(self,layout):
        box = layout.box()

        split = box.split(factor=.25)
        tab_col = split.column()
        tab_col.prop(self,'size_tabs',expand=True)

        prop_col = split.column()
        if self.size_tabs == 'CABINETS':
            col = layout.column(align=True)
            split = col.split(factor=.7,align=True)

            box = prop_col.box()
            box.label(text="Standard Cabinet Sizes:")
            
            row = box.row(align=True)
            row.label(text="Base:")
            row.prop(self,"base_cabinet_height",text="Height")
            row.prop(self,"base_cabinet_depth",text="Depth")
            
            row = box.row(align=True)
            row.label(text="Tall:")
            row.prop(self,"tall_cabinet_height",text="Height")
            row.prop(self,"tall_cabinet_depth",text="Depth")
            
            row = box.row(align=True)
            row.label(text="Upper:")
            row.prop(self,"upper_cabinet_height",text="Height")
            row.prop(self,"upper_cabinet_depth",text="Depth")

            row = box.row(align=True)
            row.label(text="Sink:")
            row.prop(self,"sink_cabinet_height",text="Height")
            row.prop(self,"sink_cabinet_depth",text="Depth")
            
            row = box.row(align=True)
            row.label(text="Suspended:")
            row.prop(self,"suspended_cabinet_height",text="Height")
            row.prop(self,"suspended_cabinet_depth",text="Depth")
            
            row = box.row(align=True)
            row.label(text="1 Door Wide:")
            row.prop(self,"width_1_door",text="Width")
            
            row = box.row(align=True)
            row.label(text="2 Door Wide:")
            row.prop(self,"width_2_door",text="Width")
            
            row = box.row(align=True)
            row.label(text="Drawer Stack Width:")
            row.prop(self,"width_drawer",text="Width")
            
            box = box.box()
            box.label(text="Blind Cabinet Widths:")
            
            row = box.row(align=True)
            row.label(text='Base:')
            row.prop(self,"base_width_blind",text="Width")
            
            row = box.row(align=True)
            row.label(text='Tall:')
            row.prop(self,"tall_width_blind",text="Width")
            
            row = box.row(align=True)
            row.label(text='Upper:')
            row.prop(self,"upper_width_blind",text="Width")
            
            box = col.box()
            box.label(text="Inside Corner Cabinet Sizes:")
            row = box.row(align=True)
            row.label(text="Base:")
            row.prop(self,"base_inside_corner_size",text="")
            
            row = box.row(align=True)
            row.label(text="Upper:")
            row.prop(self,"upper_inside_corner_size",text="")
            
            box = col.box()
            box.label(text="Placement:")
            row = box.row(align=True)
            row.label(text="Height Above Floor:")
            row.prop(self,"height_above_floor",text="")
            
            box = col.box()
            box.label(text="Drawer Heights:")
            row = box.row(align=True)
            row.prop(self,"equal_drawer_stack_heights")
            if not self.equal_drawer_stack_heights:
                row.prop(self,"top_drawer_front_height")

        if self.size_tabs == 'DOORS':
            pass
        if self.size_tabs == 'WINDOWS':
            pass
        if self.size_tabs == 'WALLS':
            box = prop_col.box()
            box.label(text="Default Wall Size",icon='MOD_BUILD')

            # box = prop_col.box()                      
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
        right_row.operator('home_builder.update_scene_materials',text="Update Materials",icon='FILE_REFRESH')

        box = right_col.box()
        col = box.column(align=True)
        for mat in self.material_pointers:
            row = col.row()
            row.operator('home_builder.update_material_pointer',text=mat.name,icon='FORWARD').pointer_name = mat.name
            row.label(text=mat.category + " - " + mat.item_name,icon='MATERIAL')

    def draw_tools(self,layout):
        box = layout.box()
        box.label(text="General Room Tools",icon='MOD_BUILD')   
        box.operator('home_builder.auto_add_molding',text="Auto Add Base Molding")
        box.operator('home_builder.auto_add_molding',text="Auto Add Crown Molding")              
        box.operator('home_builder.draw_floor_plane',text="Add Floor")

        box = layout.box()
        box.label(text="Room Lighting Tools",icon='MOD_BUILD')  
        box.operator('home_builder.add_room_light',text="Add Room Light")

        box = layout.box()
        box.label(text="2D Drawing Tools",icon='MOD_BUILD')  
        box.operator('home_builder.generate_2d_views',text="Generate 2D View Scenes")      
        box.operator('home_builder.toggle_dimensions',text="Show Dimensions")

        box = layout.box()
        box.label(text="Thumbnail Tools",icon='MOD_BUILD')  
        box.operator('home_builder.render_asset_thumbnails',text="Generate Library Thumbnails") 

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

        right_row = right_col.row()
        right_row.scale_y = 1.3
        right_row.operator('home_builder.update_scene_pulls',text="Update Pulls",icon='FILE_REFRESH')

        box = right_col.box()
        col = box.column(align=True)
        for pull in self.pull_pointers:
            row = col.row()
            row.operator('home_builder.update_pull_pointer',text=pull.name,icon='FORWARD').pointer_name = pull.name
            row.label(text=pull.category + " - " + pull.item_name,icon='MODIFIER_ON')

    def draw_library(self,layout):
        layout = layout

        layout.operator('home_builder.render_asset_thumbnails')
        split = layout.split()

        left_col = split.column()
        right_col = split.column()

        cabinet_box = left_col.box()
        cabinet_box.label(text="Cabinets")
        cabinet_col = cabinet_box.column(align=True)

        wall_box = left_col.box()
        wall_box.label(text="Walls")
        wall_col = wall_box.column(align=True)

        appliance_box = right_col.box()
        appliance_box.label(text="Appliances")
        appliance_col = appliance_box.column(align=True)
        wm_props = home_builder_utils.get_wm_props(bpy.context.window_manager)

        door_window_box = right_col.box()
        door_window_box.label(text="Doors and Windows")
        door_window_col = door_window_box.column(align=True)

        for asset in wm_props.assets:
            text = asset.name
            if asset.category_name == 'Appliances':
                appliance_col.prop(asset,'is_selected',text=text)            
            if asset.category_name == 'Cabinets':
                cabinet_col.prop(asset,'is_selected',text=text)
            if asset.category_name == 'Walls': 
                wall_col.prop(asset,'is_selected',text=text)
            if asset.category_name == 'Doors and Windows':
                door_window_col.prop(asset,'is_selected',text=text)                

    def draw(self,layout):
        col = layout.column(align=True)

        row = col.row(align=True)
        row.scale_y = 1.3
        row.prop_enum(self, "ui_tabs", 'DEFAULTS', icon='CON_SAMEVOL', text="Defaults") 
        row.prop_enum(self, "ui_tabs", 'CONSTRUCTION', icon='MOD_BUILD', text="Construction") 
        row.prop_enum(self, "ui_tabs", 'MATERIALS', icon='COLOR', text="Materials") 
        row.prop_enum(self, "ui_tabs", 'MOLDINGS', icon='MOD_SMOOTH', text="Moldings") 
        row.prop_enum(self, "ui_tabs", 'FRONTS', icon='FACESEL', text="Fronts") 
        row.prop_enum(self, "ui_tabs", 'HARDWARE', icon='MODIFIER_ON', text="Hardware") 
        row.prop_enum(self, "ui_tabs", 'LIBRARY', icon='TOOL_SETTINGS', text="Library") 

        box = col.box()

        if self.ui_tabs == 'DEFAULTS':
            self.draw_sizes(box)

        if self.ui_tabs == 'CONSTRUCTION':
            pass

        if self.ui_tabs == 'MATERIALS':
            self.draw_materials(box)

        if self.ui_tabs == 'MOLDINGS':
            pass          

        if self.ui_tabs == 'FRONTS':
            pass

        if self.ui_tabs == 'HARDWARE':
            self.draw_hardware(box)            

        if self.ui_tabs == 'LIBRARY':
            self.draw_library(box)

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

    pointer_name: bpy.props.StringProperty(name="Pointer Name")

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
    Asset,
    Home_Builder_AddonPreferences,
    Home_Builder_Window_Manager_Props,
    Home_Builder_Object_Props,
    Home_Builder_Scene_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)        