from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_cabinets
from . import data_cabinet_doors
from . import data_cabinet_carcass

class Base_Cabinet(data_cabinets.Standard_Cabinet):

    def __init__(self):
        self.carcass = data_cabinet_carcass.Base_Advanced()
        self.interior = None
        self.exterior = data_cabinet_doors.Door()
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