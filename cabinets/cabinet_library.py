import bpy
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinets
from . import data_cabinet_exteriors
from . import data_cabinet_interiors
from . import data_cabinet_carcass
from . import data_appliances
from . import data_cabinet_splitter
from .. import home_builder_utils

class Base_1_Door(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.carcass = data_cabinet_carcass.Base_Advanced()
        self.carcass.interior = data_cabinet_interiors.Shelves()
        self.carcass.exterior = data_cabinet_exteriors.Doors()
        self.splitter = None
        self.cabinet_type = "Base"
        

class Base_2_Door(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.width = pc_unit.inch(36)
        self.carcass = data_cabinet_carcass.Base_Advanced()
        self.carcass.interior = None
        self.carcass.exterior = data_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 2
        self.cabinet_type = "Base"


class Base_2_Door_2_Drawer(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.width = pc_unit.inch(36)
        self.carcass = data_cabinet_carcass.Base_Advanced()
        self.carcass.interior = None
        self.carcass.exterior = data_cabinet_exteriors.Door_Drawer()
        self.carcass.exterior.door_swing = 2
        self.carcass.exterior.two_drawers = True
        self.cabinet_type = "Base"


class Base_2_Door_1_Drawer(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.width = pc_unit.inch(36)
        self.carcass = data_cabinet_carcass.Base_Advanced()
        self.carcass.interior = None
        self.carcass.exterior = data_cabinet_exteriors.Door_Drawer()
        self.carcass.exterior.door_swing = 2
        self.carcass.exterior.two_drawers = False
        self.cabinet_type = "Base"


class Base_1_Door_1_Drawer(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.width = pc_unit.inch(18)
        self.carcass = data_cabinet_carcass.Base_Advanced()
        self.carcass.interior = None
        self.carcass.exterior = data_cabinet_exteriors.Door_Drawer()
        self.carcass.exterior.door_swing = 0
        self.carcass.exterior.two_drawers = False
        self.cabinet_type = "Base"


class Base_Blind_1_Door(data_cabinets.Blind_Corner_Cabinet):

    def __init__(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)
        self.width = props.base_width_blind
        self.carcass = data_cabinet_carcass.Base_Advanced()
        self.carcass.interior = data_cabinet_interiors.Shelves()
        self.carcass.exterior = data_cabinet_exteriors.Doors()
        self.cabinet_type = "Base"


class Tall_1_Door(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.carcass = data_cabinet_carcass.Tall_Advanced()
        self.carcass.interior = None
        self.carcass.exterior = data_cabinet_exteriors.Doors()
        self.cabinet_type = "Tall"


class Tall_2_Door(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.width = pc_unit.inch(36)
        self.carcass = data_cabinet_carcass.Tall_Advanced()
        self.carcass.interior = None
        self.carcass.exterior = data_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 2
        self.cabinet_type = "Tall"


class Upper_1_Door(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.carcass = data_cabinet_carcass.Upper_Advanced()
        self.carcass.interior = None
        self.carcass.exterior = data_cabinet_exteriors.Doors()
        self.cabinet_type = "Upper"


class Upper_2_Door(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.width = pc_unit.inch(36)
        self.carcass = data_cabinet_carcass.Upper_Advanced()
        self.carcass.interior = None
        self.carcass.exterior = data_cabinet_exteriors.Doors()
        self.carcass.exterior.door_swing = 2
        self.cabinet_type = "Upper"


class Upper_Blind_1_Door(data_cabinets.Blind_Corner_Cabinet):

    def __init__(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)
        self.width = props.upper_width_blind
        self.carcass = data_cabinet_carcass.Upper_Advanced()
        self.carcass.interior = data_cabinet_interiors.Shelves()
        self.carcass.exterior = data_cabinet_exteriors.Doors()
        self.cabinet_type = "Upper"


class Base_Drawer(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.carcass = data_cabinet_carcass.Base_Advanced()
        self.carcass.interior = None
        self.carcass.exterior = data_cabinet_exteriors.Drawers()
        self.carcass.exterior.drawer_qty = 3
        self.cabinet_type = "Base"


class Base_Open(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.carcass = data_cabinet_carcass.Base_Advanced()
        self.carcass.interior = data_cabinet_interiors.Shelves()
        self.carcass.exterior = None
        self.cabinet_type = "Base"     


class Tall_Open(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.carcass = data_cabinet_carcass.Tall_Advanced()
        self.carcass.interior = data_cabinet_interiors.Shelves()
        self.carcass.interior.shelf_qty = 3
        self.carcass.exterior = None
        self.cabinet_type = "Tall"


class Tall_Blind_1_Door(data_cabinets.Blind_Corner_Cabinet):

    def __init__(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)
        self.width = props.tall_width_blind
        self.carcass = data_cabinet_carcass.Tall_Advanced()
        self.carcass.interior = data_cabinet_interiors.Shelves()
        self.carcass.exterior = data_cabinet_exteriors.Doors()
        self.cabinet_type = "Tall"

# class Tall_Split(data_cabinets.Standard_Cabinet):

#     def __init__(self):
#         self.carcass = data_cabinet_carcass.Tall_Advanced()
#         self.carcass.interior = None
#         self.carcass.exterior = None
#         self.carcass.splitter = data_cabinet_splitter.Vertical_Splitter()
#         self.carcass.splitter.vertical_openings = 2
#         self.carcass.splitter.exterior_1 = data_cabinet_exteriors.Doors()
#         self.carcass.splitter.exterior_1.door_swing = 2
#         self.carcass.splitter.exterior_1.cabinet_type = 'Upper'
#         self.carcass.splitter.exterior_1.prompts = {"Half Overlay Bottom":True}
#         self.carcass.splitter.exterior_2 = data_cabinet_exteriors.Doors()
#         self.carcass.splitter.exterior_2.door_swing = 2
#         self.carcass.splitter.exterior_2.cabinet_type = 'Base'    
#         self.carcass.splitter.exterior_2.prompts = {"Half Overlay Top":True}    

class Tall_Stacked(data_cabinets.Stacked_Cabinet):

    def __init__(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)
        self.height = props.tall_cabinet_height
        self.depth = props.tall_cabinet_depth
        self.bottom_cabinet_height = props.tall_cabinet_height - props.stacked_top_cabinet_height
        self.top_carcass = data_cabinet_carcass.Upper_Advanced()
        self.top_carcass.interior = data_cabinet_interiors.Shelves()
        self.top_carcass.exterior = data_cabinet_exteriors.Doors()
        self.bottom_carcass = data_cabinet_carcass.Base_Advanced()
        self.bottom_carcass.interior = data_cabinet_interiors.Shelves()
        self.bottom_carcass.exterior = data_cabinet_exteriors.Doors()      
        self.bottom_carcass.exterior.carcass_type = "Tall"  
        self.cabinet_type = "Tall"

class Upper_Stacked(data_cabinets.Stacked_Cabinet):

    def __init__(self):
        props = home_builder_utils.get_scene_props(bpy.context.scene)
        self.width = pc_unit.inch(36)
        self.height = props.upper_stacked_cabinet_height
        self.depth = props.upper_cabinet_depth
        self.bottom_cabinet_height = props.upper_stacked_cabinet_height - props.stacked_top_cabinet_height
        self.z_loc = props.height_above_floor - props.upper_stacked_cabinet_height
        self.top_carcass = data_cabinet_carcass.Upper_Advanced()
        self.top_carcass.interior = data_cabinet_interiors.Shelves()
        self.top_carcass.exterior = data_cabinet_exteriors.Doors()
        self.top_carcass.exterior.door_swing = 2
        self.bottom_carcass = data_cabinet_carcass.Upper_Advanced()
        self.bottom_carcass.interior = data_cabinet_interiors.Shelves()
        self.bottom_carcass.exterior = data_cabinet_exteriors.Doors()    
        self.bottom_carcass.exterior.door_swing = 2
        self.cabinet_type = "Upper"


class Upper_Open(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.width = pc_unit.inch(36)
        self.carcass = data_cabinet_carcass.Upper_Advanced()
        self.carcass.interior = data_cabinet_interiors.Shelves()
        self.carcass.interior.shelf_qty = 2
        self.carcass.exterior = None
        self.cabinet_type = "Upper"