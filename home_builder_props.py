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
from .pc_lib import pc_types, pc_unit, pc_utils
from . import home_builder_utils
from . import home_builder_enums
from . import home_builder_paths
from . import home_builder_pointers
from .walls import data_walls
from .doors_windows import door_window_library
from .cabinets import cabinet_library
from .cabinets import data_appliances
from .closets import closet_library

library_modules = [cabinet_library,
                   closet_library,
                   data_walls,
                   door_window_library,
                   data_appliances]

class Pointer(PropertyGroup):
    category: bpy.props.StringProperty(name="Category")
    item_name: bpy.props.StringProperty(name="Item Name")


class PointerGroup(PropertyGroup):
    pointers: bpy.props.CollectionProperty(name="Pointers",type=Pointer)


class Asset(PropertyGroup):
    is_selected: BoolProperty(name="Is Selected",default=False)
    preview_found: BoolProperty(name="Preivew Found",default=False)
    asset_path: StringProperty(name="Asset Path")
    library_path: StringProperty(name="Library Path")
    package_name: StringProperty(name="Package Name")
    module_name: StringProperty(name="Module Name")
    category_name: StringProperty(name="Category Name")
    subcategory_name: StringProperty(name="Subcategory Name")
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

        library_path = home_builder_paths.get_asset_folder_path()
        for module in library_modules:
            for name, obj in inspect.getmembers(module):
                if hasattr(obj,'show_in_library') and name != 'ops' and obj.show_in_library:
                    asset = self.assets.add()
                    asset.name = name.replace("_"," ")
                    asset.category_name = obj.category_name
                    asset.subcategory_name = obj.subcategory_name
                    asset.library_path = os.path.join(library_path,asset.category_name,asset.subcategory_name)
                    # if asset.category_name == 'Closets':
                    #     asset.subcategory_name = obj.subcategory_name
                    #     asset.library_path = os.path.join(library_path,asset.category_name,asset.subcategory_name)
                    # else:
                    #     asset.library_path = os.path.join(library_path,asset.category_name)
                    asset.package_name = module.__name__.split(".")[-2]
                    asset.module_name = module.__name__.split(".")[-1]
                    asset.class_name = name

    def get_asset(self,filepath):
        import importlib.util
        directory, file = os.path.split(filepath)
        filename, ext = os.path.splitext(file)   
        spec = importlib.util.spec_from_file_location("module.name",os.path.join(directory,filename+".py"))
        foo = importlib.util.module_from_spec(spec)
        # print('MY VAR',foo.my_var)
        # print('FOO',foo)
        spec.loader.exec_module(foo)
        c = foo.Item()
        c.name()
        # print('MY VAR',foo.my_var)
        # print('SCRIPT',script)
        # print("SCRIPT_PATH",os.path.join(directory,filename+".py"))
        # print('GET ASSET',filepath)
        #TODO:GET RIGHT CLASS
        for asset in self.assets:
            if asset.library_path in filepath and filename == asset.name:
                obj = eval(asset.module_name + "." + asset.class_name + "()")
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

def update_active_asset_index(self,context):
    active_asset = self.active_asset_collection[self.active_asset_index]
    self.active_assets = active_asset.name

def update_library_path(self,context):
    root_path = os.path.join(home_builder_paths.get_asset_folder_path(),self.library_tabs)
    if self.library_tabs == 'ROOMS':
        final_path = os.path.join(root_path,self.room_tabs)
    if self.library_tabs == 'KITCHENS':
        final_path = os.path.join(root_path,self.kitchen_tabs)
    if self.library_tabs == 'BATHS':
        final_path = os.path.join(root_path,self.bath_tabs)       
    if self.library_tabs == 'CLOSETS':
        final_path = os.path.join(root_path,self.closet_tabs)     
    if os.path.exists(final_path):
        pc_utils.update_file_browser_path(context,final_path)       

class Home_Builder_Scene_Props(PropertyGroup):    
    ui_tabs: EnumProperty(name="UI Tabs",
                          items=[('DEFAULTS',"Library","Default Library Settings"),
                                 ('MATERIALS',"Materials","Show the Material Options"),
                                 ('MOLDINGS',"Moldings","Show the Molding Options"),
                                 ('FRONTS',"Fronts","Show the Door and Drawer Front Options"),
                                 ('HARDWARE',"Hardware","Show the Hardware Options"),
                                 ('LIBRARY',"Assets","Show the Available Asset Options")],
                          default='DEFAULTS')

    default_tabs: EnumProperty(name="Default Tabs",
                          items=[('CABINETS_SIZES',"Cabinet Sizes","Show the Cabinet Size Options"),
                                 ('CABINET_CONSTRUCTION',"Cabinet Construction","Show the Cabinet Construction Options"),
                                 ('CLOSET_CONSTRUCTION',"Closet Construction","Show the Closet Construction Options"),
                                 ('DOOR_SIZES',"Entry Door Sizes","Show the Door Options"),
                                 ('WINDOW_SIZES',"Window Sizes","Show the Window Options"),
                                 ('WALLS',"Walls","Show the Wall Options")],
                          default='CABINETS_SIZES')

    asset_tabs: EnumProperty(name="Default Tabs",
                             items=[('PYTHON',"Python Classes","Show the Assets Defined in Python"),
                                    ('BUILT_IN_APPLIANCES',"Built in Appliances","Show the Built in Appliances"),
                                    ('CABINET_DOORS',"Cabinet Doors","Show the Cabinet Doors"),
                                    ('CABINET_PARTS',"Cabinet Parts","Show the Cabinet Parts"),
                                    ('CABINET_PULLS',"Cabinet Pulls","Show the Cabinet Pulls"),
                                    ('COOKTOPS',"Cooktops","Show the Cooktops"),
                                    ('DISHWASHERS',"Dishwashers","Show the Dishwashers"),
                                    ('ENTRY_DOOR_FRAMES',"Entry Door Frames","Show the Entry Door Frames"),
                                    ('ENTRY_DOOR_HANDLES',"Entry Door Handles","Show the Entry Door Handles"),
                                    ('ENTRY_DOOR_PANELS',"Entry Door Panels","Show the Entry Door Panels"),
                                    ('FAUCETS',"Faucets","Show the Faucets"),
                                    ('MATERIALS',"Materials","Show the Materials"),
                                    ('MOLDINGS',"Moldings","Show the Moldings"),
                                    ('RANGE_HOODS',"Range Hoods","Show the Range Hoods"),
                                    ('RANGES',"Ranges","Show the Ranges"),
                                    ('REFRIGERATORS',"Refrigerators","Show the Refrigerators"),
                                    ('SINKS',"Sinks","Show the Sinks"),
                                    ('WINDOW_FRAMES',"Window Frames","Show the Window Frames"),
                                    ('WINDOW_INSERTS',"Window Inserts","Show the Window Inserts")],
                             default='PYTHON',
                             update=home_builder_enums.update_active_asset_tab)

    selected_part: EnumProperty(name="Part",
                                items=[('APPLIED_PANEL',"Applied Panel","Add Applied Panel"),
                                       ('COUNTERTOP',"Countertop","Add Countertop"),
                                       ('MOLDING_BASE',"Molding Base","Molding Base"),
                                       ('MOLDING_CROWN',"Molding Crown","Molding Crown"),
                                       ('MOLDING_LIGHT',"Molding Light Rail","Molding Light Rail")],
                                default='APPLIED_PANEL')   

    library_tabs: EnumProperty(name="Library Tabs",
                          items=[('ROOMS',"Rooms","Show the Room Library"),
                                 ('KITCHENS',"Kitchens","Show the Kitchen Library"),
                                 ('BATHS',"Baths","Show the Bathroom Library"),
                                 ('CLOSETS',"Closets","Show the Closet Library")],
                          default='ROOMS',
                          update=update_library_path)

    room_tabs: EnumProperty(name="Room Tabs",
                          items=[('WALLS',"Walls","Show the Walls"),
                                 ('DOORS',"Doors","Show the Doors"),
                                 ('WINDOWS',"Windows","Show the Windows"),
                                 ('OBSTACLES',"Obstacles","Show the Obstacles")],
                          default='WALLS',
                          update=update_library_path)

    kitchen_tabs: EnumProperty(name="Kitchen Tabs",
                          items=[('APPLIANCES',"Appliances","Show the Appliances"),
                                 ('CABINETS',"Cabinets","Show the Cabinets"),
                                 ('PARTS',"Parts","Show the Parts"),
                                 ('CUSTOM_CABINETS',"Custom Cabinets","Show the Custom Cabinets"),
                                 ('DECORATIONS',"Decorations","Show the Kitchen Decorations")],
                          default='APPLIANCES',
                          update=update_library_path)

    bath_tabs: EnumProperty(name="Bath Tabs",
                          items=[('FIXTURES',"Fixtures","Show the Bathroom Fixtures"),
                                 ('VANITIES',"Vanities","Show the Bathroom Vanities"),
                                 ('MIRRORS',"Mirrors","Show the Bathroom Mirrors"),
                                 ('DECORATIONS',"Decorations","Show the Bathroom Decorations")],
                          default='FIXTURES',
                          update=update_library_path)

    closet_tabs: EnumProperty(name="Closet Tabs",
                          items=[('STARTERS',"Starters","Show the Closet Starters"),
                                 ('HANGING_PANELS',"Hanging Panels","Show the Hanging Closet Panels"),
                                 ('INSERTS',"Inserts","Show the Closet Inserts"),
                                 ('SPLITTERS',"Splitters","Show the Closet Splitters"),
                                 ('CLOSET_ACCESSORIES',"Accessories","Show the Closet Accessories"),
                                 ('CLOSET_PARTS',"Parts","Show the Closet Parts"),
                                 ('DECORATIONS',"Decorations","Show the Closet Decorations")],
                          default='STARTERS',
                          update=update_library_path)

    sidebar_tabs: EnumProperty(name="Sidebar Tabs",
                          items=[('PROPERTIES',"Properties","Properties"),
                                 ('TOOLS',"Tools","Tools")],
                          default='PROPERTIES')
    show_wall_options: bpy.props.BoolProperty(name="Show Wall Options",
                                           description="Show Wall Options",
                                           default=False)
    show_cabinet_tools: bpy.props.BoolProperty(name="Show Cabinet Tools",
                                           description="Show Cabinet Tools",
                                           default=False)                                                
    show_cabinet_front_tools: bpy.props.BoolProperty(name="Show Cabinet Front Tools",
                                           description="Show Cabinet Front Tools",
                                           default=False)                                           
    show_hardware_tools: bpy.props.BoolProperty(name="Show Hardware Tools",
                                           description="Show Hardware Tools",
                                           default=False)
    show_2d_view_options: bpy.props.BoolProperty(name="Show 2D View Options",
                                           description="Show 2D View Options",
                                           default=False)
    show_cabinet_placement_options: bpy.props.BoolProperty(name="Show Cabinet Placement Options",
                                           description="Show Cabinet Placement Options",
                                           default=False)
    show_material_options: bpy.props.BoolProperty(name="Show Material Options",
                                           description="Show Material Options",
                                           default=False)     
    show_material_pointer_options: bpy.props.BoolProperty(name="Show Material Pointer Options",
                                           description="Show Material Pointer Options",
                                           default=False)    
    show_report_options: bpy.props.BoolProperty(name="Show Report Options",
                                           description="Show Report Options",
                                           default=False)                    
    show_add_part_options: bpy.props.BoolProperty(name="Show Add Part Options",
                                           description="Show Add Part Options",
                                           default=False)     
    show_closet_options: bpy.props.BoolProperty(name="Show Closet Options",
                                           description="Show Closet Options",
                                           default=False)           

    active_category: StringProperty(name="Active Category")
    active_subcategory: StringProperty(name="Active Subcategory")

    wall_height: FloatProperty(name="Wall Height",default=pc_unit.inch(96),subtype='DISTANCE')
    wall_thickness: FloatProperty(name="Wall Thickness",default=pc_unit.inch(6),subtype='DISTANCE')

    default_closet_depth: bpy.props.FloatProperty(name="Default Closet Depth",
                                                 description="Default depth for closets",
                                                 default=pc_unit.inch(14.0),
                                                 unit='LENGTH')

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

    upper_stacked_cabinet_height: bpy.props.FloatProperty(name="Upper Stacked Cabinet Height",
                                                description="Default Height for Stacked Upper Cabinet Height",
                                                default=pc_unit.inch(46.0),
                                                unit='LENGTH')

    stacked_top_cabinet_height: bpy.props.FloatProperty(name="Stacked Top Cabinet Height",
                                                description="Default Height for the Top Cabinet on Stacked Cabinets",
                                                default=pc_unit.inch(12.0),
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

    use_design_carcass: bpy.props.BoolProperty(name="Use Design Carcass",
                                               description="Turn this on to speed up drawing time by using a simple carcass assembly.",
                                               default=True)

    #CABINET TOE KICK
    base_assembly_type: EnumProperty(name="Base Assembly Type",
                          items=[('NOTCH_SIDES',"Notch Sides","Notch the sides of the cabinet"),
                                 ('SIDES_TO_FLOOR',"Sides to Floor","Run the side of the cabinet to the floor without notch"),
                                 ('LEG_LEVELERS',"Leg Levelers","Use Leg Levelers"),
                                 ('SEPARATE_BOX',"Separate Box","Use separate box"),
                                 ('NO_ASSEMBLY',"No Assembly","Do not include a base assembly")],
                          default='NOTCH_SIDES')

    toe_kick_height: bpy.props.FloatProperty(name="Toe Kick Height",
                                             description="This is the default height of the toe kick.",
                                             default=pc_unit.inch(4.0),
                                             unit='LENGTH')

    toe_kick_setback: bpy.props.FloatProperty(name="Toe Kick Setback",
                                             description="This is the default setback of the toe kick.",
                                             default=pc_unit.inch(4.0),
                                             unit='LENGTH')

    #CABINET COUNTERTOPS
    add_backsplash: bpy.props.BoolProperty(name="Add Backsplash",
                                           description="Check this to include a countertop backsplash",
                                           default=True)

    countertop_backsplash_height: bpy.props.FloatProperty(name="Coutnertop Backsplash Height",
                                                          description="Enter the Height for the Countertop Backsplash",
                                                          default=pc_unit.inch(4.0))

    countertop_front_overhang: bpy.props.FloatProperty(name="Countertop Front Overhang",
                                                       description="This front overhang of the countertop.",
                                                       default=pc_unit.inch(1.0),
                                                       unit='LENGTH')

    countertop_side_overhang: bpy.props.FloatProperty(name="Countertop Side Overhang",
                                                       description="This is the side overhang of countertops with Finished Ends",
                                                       default=pc_unit.inch(1.0),
                                                       unit='LENGTH')

    countertop_rear_overhang: bpy.props.FloatProperty(name="Countertop Rear Overhang",
                                                       description="This is the rear overhang of countertops.",
                                                       default=pc_unit.inch(1.0),
                                                       unit='LENGTH')     

    #CABINET LIGHTING
    add_toe_kick_lighting: bpy.props.BoolProperty(name="Add Toe Kick Lighting",
                                                   description="This will add toe kick lighting to cabinets",
                                                   default=False)

    add_under_cabinet_lighting: bpy.props.BoolProperty(name="Add Under Cabinet Lighting",
                                                        description="This will add lighting under upper cabinets",
                                                        default=False)

    add_top_inside_lighting: bpy.props.BoolProperty(name="Add Top Inside Lighting",
                                                    description="This will add lighting to the top interior of cabinets",
                                                    default=False)                                                   

    add_side_inside_lighting: bpy.props.BoolProperty(name="Add Side Inside Lighting",
                                                      description="This will add lighting to the side interior of cabinets",
                                                      default=False)     

    lighting_dim_from_front: bpy.props.FloatProperty(name="Lighting Dim From Front",
                                                       description="This is the dim from the front of the cabinet to the light.",
                                                       default=pc_unit.inch(1.5),
                                                       unit='LENGTH')     

    lighting_dim_from_sides: bpy.props.FloatProperty(name="Lighting Dim From Sides",
                                                       description="This is the inset amount for lights from the side of the cabinet",
                                                       default=pc_unit.inch(.75),
                                                       unit='LENGTH')   

    cabinet_lighting_width: bpy.props.FloatProperty(name="Cabinet Lighting Width",
                                                       description="This is the width of the cabinet lighting strip",
                                                       default=pc_unit.inch(.75),
                                                       unit='LENGTH')   

    closet_corner_spacing: bpy.props.FloatProperty(name="Closet Corner Spacing",
                                                 description="Offset for closets when meeting in corner",
                                                 default=pc_unit.inch(12.0),
                                                 unit='LENGTH')

    #ENTRY DOORS
    single_door_width: bpy.props.FloatProperty(name="Single Door Width",
                                               description="Is the width of single entry doors",
                                               default=pc_unit.inch(36),
                                               unit='LENGTH')

    double_door_width: bpy.props.FloatProperty(name="Double Door Width",
                                               description="Is the width of double entry doors",
                                               default=pc_unit.inch(72),
                                               unit='LENGTH')

    door_height: bpy.props.FloatProperty(name="Double Door Width",
                                         description="Is the width of double entry doors",
                                         default=pc_unit.inch(70),
                                         unit='LENGTH')     

    #WINDOWS
    window_height_from_floor: bpy.props.FloatProperty(name="Window Height from Floor",
                                                      description="This is the height off the window from the floor",
                                                      default=pc_unit.inch(40),
                                                      unit='LENGTH')

    window_height: bpy.props.FloatProperty(name="Window Height",
                                           description="This is the height of windows",
                                           default=pc_unit.inch(40),
                                           unit='LENGTH')

    #POINTERS                                   
    material_group_index: bpy.props.IntProperty(name="Material Group Index")                
    material_pointer_groups: bpy.props.CollectionProperty(name="Material Pointer Groups",type=PointerGroup)

    pull_pointers: bpy.props.CollectionProperty(name="Pull Pointers",type=Pointer)
    cabinet_door_pointers: bpy.props.CollectionProperty(name="Cabinet Door Pointers",type=Pointer)
    molding_pointers: bpy.props.CollectionProperty(name="Molding Pointers",type=Pointer)

    active_asset_category: bpy.props.EnumProperty(name="Active Asset Category",
        items=home_builder_enums.enum_active_asset_categories,
        update=home_builder_enums.update_active_asset_category)
    active_assets: bpy.props.EnumProperty(name="Active Assets",
        items=home_builder_enums.enum_active_asset_names)
    active_asset_collection: bpy.props.CollectionProperty(name="Active Asset Collection",type=Asset)
    active_asset_index: bpy.props.IntProperty(name="Active Asset Index",update=update_active_asset_index)

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

    cabinet_door_category: bpy.props.EnumProperty(name="Cabinet Door Category",
        items=home_builder_enums.enum_cabinet_door_categories,
        update=home_builder_enums.update_cabinet_door_category)
    cabinet_door_name: bpy.props.EnumProperty(name="Cabinet Door Name",
        items=home_builder_enums.enum_cabinet_door_names)

    molding_category: bpy.props.EnumProperty(name="Molding Category",
        items=home_builder_enums.enum_molding_categories,
        update=home_builder_enums.update_molding_category)
    molding_name: bpy.props.EnumProperty(name="Molding Name",
        items=home_builder_enums.enum_molding_names)

    def draw_sizes(self,layout):
        # box = layout.box()

        split = layout.split(factor=.25)
        tab_col = split.column()
        tab_col.prop(self,'default_tabs',expand=True)

        prop_col = split.column()
        if self.default_tabs == 'CABINETS_SIZES':
            # col = layout.column(align=True)
            # split = col.split(factor=.7,align=True)

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
            
            box = prop_col.box()
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
            
            box = prop_col.box()
            box.label(text="Inside Corner Cabinet Sizes:")
            row = box.row(align=True)
            row.label(text="Base:")
            row.prop(self,"base_inside_corner_size",text="")
            
            row = box.row(align=True)
            row.label(text="Upper:")
            row.prop(self,"upper_inside_corner_size",text="")

            box = prop_col.box()
            box.label(text="Stacked Cabinet Sizes:")
            
            row = box.row(align=True)
            row.label(text="Upper Total Height:")
            row.prop(self,"upper_stacked_cabinet_height",text="")
            row = box.row(align=True)
            row.label(text="Top Cabinet Height:")
            row.prop(self,"stacked_top_cabinet_height",text="")

            box = prop_col.box()
            box.label(text="Upper Placement:")
            row = box.row(align=True)
            row.label(text="Height Above Floor:")
            row.prop(self,"height_above_floor",text="")
            
            box = prop_col.box()
            box.label(text="Drawer Heights:")
            row = box.row(align=True)
            row.prop(self,"equal_drawer_stack_heights")
            if not self.equal_drawer_stack_heights:
                row.prop(self,"top_drawer_front_height")

        if self.default_tabs == 'CABINET_CONSTRUCTION':
            box = prop_col.box()
            row = box.row(align=True)
            row.label(text="General Construction Options:")
            row = box.row(align=True)
            row.prop(self,"use_design_carcass",text="Use Design Carcass")
            
            box = prop_col.box()
            box.label(text="Cabinet Base Assembly:")
            
            # row = box.row(align=True)
            # row.label(text="Base Assembly Type")
            # row.prop(self,"base_assembly_type",text="")

            row = box.row(align=True)
            row.label(text="Base Assembly Size")
            row.prop(self,"toe_kick_height",text="Height")
            row.prop(self,"toe_kick_height",text="Setback")

            box = prop_col.box()
            box.label(text="Cabinet Countertop:")
            
            # row = box.row(align=True)
            # row.label(text="Backsplash")
            # row.prop(self,"add_backsplash",text="")
            # row.prop(self,"countertop_backsplash_height",text="Height")

            row = box.row(align=True)
            row.label(text="Overhang")
            row.prop(self,"countertop_front_overhang",text="Front")
            row.prop(self,"countertop_rear_overhang",text="Rear")
            row.prop(self,"countertop_side_overhang",text="Side")

            # box = prop_col.box()
            # row = box.row(align=True)
            # row.label(text="Cabinet Lighting:")
            # row.operator('home_builder.update_cabinet_lighting',text="",icon='FILE_REFRESH',emboss=False)
            # row = box.row(align=True)
            # row.prop(self,"add_toe_kick_lighting",text="Toe Kick")
            # row.prop(self,"add_under_cabinet_lighting",text="Under Cabinet")
            # row.prop(self,"add_top_inside_lighting",text="Inside Top")
            # row.prop(self,"add_side_inside_lighting",text="Inside Sides")
            # row = box.row(align=True)
            # row.label(text="Cabinet Lighting Location:")            
            # row.prop(self,"lighting_dim_from_front",text="Dim From Front")
            # row.prop(self,"lighting_dim_from_sides",text="Dim From Sides")
            # row = box.row(align=True)
            # row.label(text="Cabinet Lighting Size:")              
            # row.prop(self,"cabinet_lighting_width",text="Width")

        if self.default_tabs == 'CLOSET_CONSTRUCTION':
            box = prop_col.box()
            row = box.row(align=True)
            row.label(text="General Construction Options:")
            row = box.row(align=True)
            row.label(text="Closet Corner Spacing")
            row.prop(self,"closet_corner_spacing",text="")    
            row = box.row(align=True)
            row.label(text="Default Closet Depth")
            row.prop(self,"default_closet_depth",text="")    
    
        if self.default_tabs == 'DOOR_SIZES':
            box = prop_col.box()
            row = box.row(align=True)
            row.label(text="Door Width:")
            row.prop(self,"single_door_width",text="Single")
            row.prop(self,"single_door_width",text="Double")
            row = box.row(align=True)
            row.label(text="Door Height:")
            row.prop(self,"door_height",text="Height")            

        if self.default_tabs == 'WINDOW_SIZES':
            box = prop_col.box()
            row = box.row(align=True)
            row.label(text="Window Height:")
            row.prop(self,"window_height",text="Height")

            row = box.row(align=True)
            row.label(text="Window Placement:")
            row.prop(self,"window_height_from_floor",text="Height From Floor")   

        if self.default_tabs == 'WALLS':
            box = prop_col.box()
            box.label(text="Default Wall Size",icon='MOD_BUILD')

            row = box.row()
            row.label(text="Default Wall Height")
            row.prop(self,'wall_height',text="")

            row = box.row()
            row.label(text="Default Wall Thickness")
            row.prop(self,'wall_thickness',text="")

    def draw_moldings(self,layout):
        split = layout.split(factor=.25)
        left_col = split.column()
        right_col = split.column()

        molding_box = left_col.box()
        row = molding_box.row()
        row.label(text="Molding Selections:")

        molding_box.prop(self,'molding_category',text="",icon='FILE_FOLDER')  
        molding_box.template_icon_view(self,"molding_name",show_labels=True)  

        right_row = right_col.row()
        right_row.scale_y = 1.3
        right_row.operator('home_builder.auto_add_molding',text="Add Molding to Room",icon='FILE_REFRESH')
        right_row.menu('HOME_BUILDER_MT_pointer_menu',text="",icon='TRIA_DOWN')

        box = right_col.box()
        col = box.column(align=True)
        for molding in self.molding_pointers:
            row = col.row()
            row.operator('home_builder.update_molding_pointer',text=molding.name,icon='FORWARD').pointer_name = molding.name
            row.label(text=molding.category + " - " + molding.item_name,icon='MODIFIER_ON')

    def draw_materials(self,layout):
        split = layout.split(factor=.25)
        left_col = split.column()
        right_col = split.column()

        material_box = left_col.box()
        row = material_box.row()
        row.label(text="Material Selections:")
        material_box.prop(self,'material_category',text="",icon='FILE_FOLDER')  
        material_box.template_icon_view(self,"material_name",show_labels=True)  

        material_group = self.material_pointer_groups[self.material_group_index]

        right_row = right_col.row()
        right_row.scale_y = 1.3
        right_row.menu('HOME_BUILDER_MT_change_global_material_group',text=material_group.name,icon='COLOR')
        right_row.operator('home_builder.update_scene_materials',text="Update Materials",icon='FILE_REFRESH')    

        box = right_col.box()
        box.operator('home_builder.add_material_pointer',text="Add Pointer")
        col = box.column(align=True)
        for mat in material_group.pointers:
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
        hardware_box.template_icon_view(self,"pull_name",show_labels=True)  

        right_row = right_col.row()
        right_row.scale_y = 1.3
        right_row.operator('home_builder.update_scene_pulls',text="Update Pulls",icon='FILE_REFRESH')
        right_row.menu('HOME_BUILDER_MT_pointer_menu',text="",icon='TRIA_DOWN')

        box = right_col.box()
        col = box.column(align=True)
        for pull in self.pull_pointers:
            row = col.row()
            row.operator('home_builder.update_pull_pointer',text=pull.name,icon='FORWARD').pointer_name = pull.name
            row.label(text=pull.category + " - " + pull.item_name,icon='MODIFIER_ON')

    def draw_fronts(self,layout):
        split = layout.split(factor=.25)
        left_col = split.column()
        right_col = split.column()

        cabinet_door_box = left_col.box()
        row = cabinet_door_box.row()
        row.label(text="Door Selections:")

        cabinet_door_box.prop(self,'cabinet_door_category',text="",icon='FILE_FOLDER')  
        cabinet_door_box.template_icon_view(self,"cabinet_door_name",show_labels=True)  

        right_row = right_col.row(align=True)
        right_row.scale_y = 1.3
        right_row.operator('home_builder.update_all_cabinet_doors',text="Update All Cabinet Fronts",icon='FILE_REFRESH')
        right_row.operator('home_builder.update_selected_cabinet_doors',text="Update Selected Cabinet Fronts",icon='RESTRICT_SELECT_OFF')
        right_row.separator()
        right_row.menu('HOME_BUILDER_MT_pointer_menu',text="",icon='TRIA_DOWN')

        box = right_col.box()
        col = box.column(align=True)
        for cabinet_door in self.cabinet_door_pointers:
            row = col.row()
            row.operator('home_builder.update_cabinet_door_pointer',text=cabinet_door.name,icon='FORWARD').pointer_name = cabinet_door.name
            row.label(text=cabinet_door.category + " - " + cabinet_door.item_name,icon='MODIFIER_ON')

    def draw_library(self,layout):
        split = layout.split(factor=.25)
        left_col = split.column()
        right_col = split.column()

        left_col.prop(self,'asset_tabs',expand=True)

        if self.asset_tabs == 'PYTHON':
            row = right_col.row()
            row.scale_y = 1.3
            row.operator('home_builder.render_asset_thumbnails')

            split = right_col.split()

            asset_left_col = split.column()
            asset_right_col = split.column()

            cabinet_box = asset_left_col.box()
            cabinet_box.label(text="Cabinets")
            cabinet_col = cabinet_box.column(align=True)

            closet_box = asset_left_col.box()
            closet_box.label(text="Closets")
            closet_col = closet_box.column(align=True)

            wall_box = asset_left_col.box()
            wall_box.label(text="Walls")
            wall_col = wall_box.column(align=True)

            appliance_box = asset_right_col.box()
            appliance_box.label(text="Appliances")
            appliance_col = appliance_box.column(align=True)

            door_box = asset_right_col.box()
            door_box.label(text="Doors")
            door_col = door_box.column(align=True)

            window_box = asset_right_col.box()
            window_box.label(text="Windows")
            window_col = window_box.column(align=True)

            wm_props = home_builder_utils.get_wm_props(bpy.context.window_manager)
            for asset in wm_props.assets:
                text = asset.name
                if asset.category_name == 'KITCHENS' and asset.subcategory_name == 'APPLIANCES':
                    appliance_col.prop(asset,'is_selected',text=text)            
                if asset.category_name == 'KITCHENS' and asset.subcategory_name == 'CABINETS':
                    cabinet_col.prop(asset,'is_selected',text=text)
                if asset.category_name == 'CLOSETS':
                    closet_col.prop(asset,'is_selected',text=text)                    
                if asset.category_name == 'ROOMS' and asset.subcategory_name == 'WALLS': 
                    wall_col.prop(asset,'is_selected',text=text)
                if asset.category_name == 'ROOMS'and asset.subcategory_name == 'DOORS':
                    door_col.prop(asset,'is_selected',text=text)     
                if asset.category_name == 'ROOMS'and asset.subcategory_name == 'WINDOWS':
                    window_col.prop(asset,'is_selected',text=text)                      
        else:
            row = right_col.row()
            row.scale_y = 1.3
            split = row.split(factor=.70)
            list_col = split.column()
            image_col = split.column()            
            
            list_col.prop(self,'active_asset_category',text="")
            image_col.menu('HOME_BUILDER_MT_asset_commands_menu',text="Commands")

            split = right_col.split(factor=.70)
            list_col = split.column()
            image_col = split.column()

            list_col.template_list("HOME_BUILDER_UL_assets"," ", self, "active_asset_collection", self, "active_asset_index",rows=16,type='DEFAULT')
            image_col.template_icon_view(self,"active_assets",show_labels=True)  

    def get_active_category_path(self):
        if self.asset_tabs == 'BUILT_IN_APPLIANCES':
            return home_builder_paths.get_built_in_appliances_path()
        if self.asset_tabs == 'CABINET_DOORS':
            return home_builder_paths.get_cabinet_door_path()
        if self.asset_tabs == 'CABINET_PARTS':
            return home_builder_paths.get_cabinet_parts_path()
        if self.asset_tabs == 'CABINET_PULLS':
            return home_builder_paths.get_pull_path()
        if self.asset_tabs == 'COOKTOPS':
            return home_builder_paths.get_cooktop_path()
        if self.asset_tabs == 'DISHWASHERS':
            return home_builder_paths.get_dishwasher_path()
        if self.asset_tabs == 'ENTRY_DOOR_FRAMES':
            return home_builder_paths.get_entry_door_frame_path()
        if self.asset_tabs == 'ENTRY_DOOR_HANDLES':
            return home_builder_paths.get_entry_door_handle_path()
        if self.asset_tabs == 'ENTRY_DOOR_PANELS':
            return home_builder_paths.get_entry_door_panel_path()
        if self.asset_tabs == 'FAUCETS':
            return home_builder_paths.get_faucet_path()
        if self.asset_tabs == 'MATERIALS':
            return home_builder_paths.get_material_path()
        if self.asset_tabs == 'MOLDINGS':
            return home_builder_paths.get_molding_path()
        if self.asset_tabs == 'RANGE_HOODS':
            return home_builder_paths.get_range_hood_path()
        if self.asset_tabs == 'RANGES':
            return home_builder_paths.get_range_path()             
        if self.asset_tabs == 'REFRIGERATORS':
            return home_builder_paths.get_refrigerator_path()     
        if self.asset_tabs == 'SINKS':
            return home_builder_paths.get_sink_path()     
        if self.asset_tabs == 'WINDOW_FRAMES':
            return home_builder_paths.get_window_frame_path()     
        if self.asset_tabs == 'WINDOW_INSERTS':
            return home_builder_paths.get_window_insert_path()                                                                                                                                                                            
        
    def draw(self,layout):
        col = layout.column(align=True)

        row = col.row(align=True)
        row.scale_y = 1.3
        row.prop_enum(self, "ui_tabs", 'DEFAULTS', icon='HOME', text="Library") 
        row.prop_enum(self, "ui_tabs", 'MATERIALS', icon='COLOR', text="Materials") 
        row.prop_enum(self, "ui_tabs", 'MOLDINGS', icon='MOD_SMOOTH', text="Moldings") 
        row.prop_enum(self, "ui_tabs", 'FRONTS', icon='FACESEL', text="Fronts") 
        row.prop_enum(self, "ui_tabs", 'HARDWARE', icon='MODIFIER_ON', text="Hardware") 
        row.prop_enum(self, "ui_tabs", 'LIBRARY', icon='FILE_IMAGE', text="Assets") 

        box = col.box()

        if self.ui_tabs == 'DEFAULTS':
            self.draw_sizes(box)

        if self.ui_tabs == 'MATERIALS':
            self.draw_materials(box)

        if self.ui_tabs == 'MOLDINGS':
            self.draw_moldings(box)

        if self.ui_tabs == 'FRONTS':
            self.draw_fronts(box)

        if self.ui_tabs == 'HARDWARE':
            self.draw_hardware(box)            

        if self.ui_tabs == 'LIBRARY':
            self.draw_library(box)

    def library_path_not_correct(self,context):
        current_path = context.space_data.params.directory.decode('utf-8')
        if not os.path.exists(current_path):
            return True
        if self.library_tabs not in current_path:
            return True
        if self.library_tabs == 'ROOMS':
            if self.room_tabs not in current_path:
                return True
        if self.library_tabs == 'KITCHENS':
            if self.kitchen_tabs not in current_path:
                return True
        if self.library_tabs == 'BATHS':
            if self.bath_tabs not in current_path:
                return True
        if self.library_tabs == 'CLOSETS':
            if self.closet_tabs not in current_path:
                return True                    
        return False

    def draw_filebrowser_header(self,layout,context):
        main_box = layout.box()
        col = main_box.column()

        row = col.row()
        row.scale_y = 1.3       
        row.label(text="Home Builder v0.1",icon='HOME') 
        row.separator()
        row.popover(panel="HOME_BUILDER_PT_library_settings",text="Settings",icon='SETTINGS')

        if self.library_path_not_correct(context):
            main_box.operator('home_builder.reload_library')
        else:
            box = main_box.box()
            box.label(text="Library")
            lib_col = box.column(align=True)
            row = lib_col.row(align=True)
            row.scale_y = 1.3
            row.prop_enum(self, "library_tabs", 'ROOMS') 
            row.prop_enum(self, "library_tabs", 'KITCHENS') 
            row.prop_enum(self, "library_tabs", 'BATHS')  
            row.prop_enum(self, "library_tabs", 'CLOSETS') 

            if self.library_tabs == 'ROOMS':
                box = main_box.box()
                box.label(text="Rooms")
                col = box.column(align=True)
                row = col.row(align=True)
                row.scale_y = 1.3
                row.prop_enum(self, "room_tabs", 'WALLS') 
                row.prop_enum(self, "room_tabs", 'DOORS') 
                row.prop_enum(self, "room_tabs", 'WINDOWS')  
                row.prop_enum(self, "room_tabs", 'OBSTACLES')  

            if self.library_tabs == 'KITCHENS':
                box = main_box.box()
                box.label(text="Kitchens")
                col = box.column(align=True)
                row = col.row(align=True)
                row.scale_y = 1.3
                row.prop_enum(self, "kitchen_tabs", 'APPLIANCES') 
                row.prop_enum(self, "kitchen_tabs", 'CABINETS') 
                row.prop_enum(self, "kitchen_tabs", 'PARTS')  
                row = col.row(align=True)
                row.scale_y = 1.3                
                row.prop_enum(self, "kitchen_tabs", 'CUSTOM_CABINETS')  
                row.prop_enum(self, "kitchen_tabs", 'DECORATIONS')  

            if self.library_tabs == 'BATHS':
                box = main_box.box()
                box.label(text="Bathroom")
                col = box.column(align=True)
                row = col.row(align=True)
                row.scale_y = 1.3
                row.prop_enum(self, "bath_tabs", 'FIXTURES') 
                row.prop_enum(self, "bath_tabs", 'VANITIES') 
                row.prop_enum(self, "bath_tabs", 'MIRRORS')  
                row.prop_enum(self, "bath_tabs", 'DECORATIONS')  

            if self.library_tabs == 'CLOSETS':
                box = main_box.box()
                box.label(text="Closets")
                col = box.column(align=True)
                row = col.row(align=True)
                row.scale_y = 1.3
                row.prop_enum(self, "closet_tabs", 'STARTERS') 
                row.prop_enum(self, "closet_tabs", 'INSERTS')  
                row.prop_enum(self, "closet_tabs", 'CLOSET_PARTS') 
                row = col.row(align=True)
                row.scale_y = 1.3     
                row.prop_enum(self, "closet_tabs", 'SPLITTERS')     
                row.prop_enum(self, "closet_tabs", 'CLOSET_ACCESSORIES')     
                row.prop_enum(self, "closet_tabs", 'DECORATIONS') 

            if (self.library_tabs == 'KITCHENS' and self.kitchen_tabs == 'CUSTOM_CABINETS') or \
               (self.library_tabs == 'BATHS' and self.bath_tabs == 'VANITIES'):
                if context.object:
                    obj_bp = pc_utils.get_assembly_bp(context.object)

                    if obj_bp:
                        row = main_box.row()
                        row.label(text='Selected Assembly: ' + obj_bp.name)
                        row.operator('pc_assembly.select_parent',text="",icon='SORT_DESC')
                        row = main_box.row()
                        row.operator('home_builder.save_custom_cabinet',text="Save Custom Cabinet",icon='SCREEN_BACK')    
                    else:
                        row = main_box.row()
                        row.label(text='Select Assembly to Save')   
                else:
                    row = main_box.row()
                    row.label(text='No Object Selected')                       


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

def update_material_group_index(self,context):
    if self.id_data.type != 'EMPTY':
        home_builder_pointers.assign_materials_to_object(self.id_data)
    
class Home_Builder_Object_Props(PropertyGroup):

    connected_object: bpy.props.PointerProperty(name="Connected Object",
                                                type=bpy.types.Object,
                                                description="This is the used to store objects that are connected together.")

    insert_opening: bpy.props.PointerProperty(name="Insert Opening",
                                                type=bpy.types.Object,
                                                description="This is the opening the insert is assigned to.")

    pointer_name: bpy.props.StringProperty(name="Pointer Name")

    material_group_index: bpy.props.IntProperty(name="Material Group Index",update=update_material_group_index)                
    pull_group_index: bpy.props.IntProperty(name="Pull Group Index")
    cabinet_door_group_index: bpy.props.IntProperty(name="Cabinet Door Group Index")

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
    PointerGroup,
    Asset,
    Home_Builder_AddonPreferences,
    Home_Builder_Window_Manager_Props,
    Home_Builder_Object_Props,
    Home_Builder_Scene_Props,
)

register, unregister = bpy.utils.register_classes_factory(classes)        