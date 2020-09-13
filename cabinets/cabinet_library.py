from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinets
from . import data_cabinet_doors
from . import data_cabinet_interiors
from . import data_cabinet_carcass
from . import data_appliances
from . import data_cabinet_splitter

class Base_Door_Cabinet(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.carcass = data_cabinet_carcass.Base_Advanced()
        self.interior = data_cabinet_interiors.Shelves()
        self.exterior = data_cabinet_doors.Door()
        self.exterior.cabinet_type = 'Base'
        self.splitter = None
        

class Base_2_Door_Cabinet(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.width = pc_unit.inch(36)
        self.carcass = data_cabinet_carcass.Base_Advanced()
        self.interior = None
        self.exterior = data_cabinet_doors.Door()
        self.exterior.door_swing = 2
        self.exterior.cabinet_type = 'Base'
        self.splitter = None


class Tall_Door_Cabinet(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.carcass = data_cabinet_carcass.Tall_Advanced()
        self.interior = None
        self.exterior = data_cabinet_doors.Door()
        self.exterior.cabinet_type = 'Tall'
        self.splitter = None


class Tall_2_Door_Cabinet(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.width = pc_unit.inch(36)
        self.carcass = data_cabinet_carcass.Tall_Advanced()
        self.interior = None
        self.exterior = data_cabinet_doors.Door()
        self.exterior.door_swing = 2
        self.exterior.cabinet_type = 'Tall'
        self.splitter = None


class Upper_Door_Cabinet(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.carcass = data_cabinet_carcass.Upper_Advanced()
        self.interior = None
        self.exterior = data_cabinet_doors.Door()
        self.exterior.cabinet_type = 'Upper'
        self.splitter = None


class Upper_2_Door_Cabinet(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.width = pc_unit.inch(36)
        self.carcass = data_cabinet_carcass.Upper_Advanced()
        self.interior = None
        self.exterior = data_cabinet_doors.Door()
        self.exterior.door_swing = 2
        self.exterior.cabinet_type = 'Upper'
        self.splitter = None


class Drawer_Cabinet(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.carcass = data_cabinet_carcass.Base_Advanced()
        self.interior = None
        self.exterior = data_cabinet_doors.Drawers()
        self.exterior.drawer_qty = 3
        self.splitter = None


class Open_Cabinet(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.carcass = data_cabinet_carcass.Base_Advanced()
        self.interior = None
        self.exterior = None
        self.splitter = None        


class Splitter_Cabinet(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.carcass = data_cabinet_carcass.Tall_Advanced()
        self.interior = None
        self.exterior = None
        self.splitter = data_cabinet_splitter.Vertical_Splitter()
        self.splitter.vertical_openings = 2
        self.splitter.exterior_1 = data_cabinet_doors.Door()
        self.splitter.exterior_1.door_swing = 2
        self.splitter.exterior_1.cabinet_type = 'Upper'
        self.splitter.exterior_1.prompts = {"Half Overlay Bottom":True}
        self.splitter.exterior_2 = data_cabinet_doors.Door()
        self.splitter.exterior_2.door_swing = 2
        self.splitter.exterior_2.cabinet_type = 'Base'    
        self.splitter.exterior_2.prompts = {"Half Overlay Top":True}    
