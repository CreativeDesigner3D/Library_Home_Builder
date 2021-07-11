from ..pc_lib import pc_unit
from . import data_doors_windows

class Window_Small(data_doors_windows.Standard_Window):
    show_in_library = True
    category_name = "ROOMS"
    subcategory_name = "WINDOWS"
    catalog_name = "_Sample"

    def __init__(self):
        self.width = pc_unit.inch(36)
        self.height = pc_unit.inch(40)
        self.depth = pc_unit.inch(6)

class Window_Large(data_doors_windows.Standard_Window):
    show_in_library = True
    category_name = "ROOMS"
    subcategory_name = "WINDOWS"
    catalog_name = "_Sample"
    
    def __init__(self):
        self.width = pc_unit.inch(70)
        self.height = pc_unit.inch(55)
        self.depth = pc_unit.inch(6)

class Door_Single(data_doors_windows.Standard_Door):
    show_in_library = True
    category_name = "ROOMS"
    subcategory_name = "DOORS"
    catalog_name = "_Sample"
    
    def __init__(self):
        self.width = pc_unit.inch(36)
        self.prompts = {"Entry Door Swing":0}    

class Door_Double(data_doors_windows.Standard_Door):
    show_in_library = True
    category_name = "ROOMS"
    subcategory_name = "DOORS"
    catalog_name = "_Sample"
    
    def __init__(self):
        self.width = pc_unit.inch(72)
        self.prompts = {"Entry Door Swing":2}   