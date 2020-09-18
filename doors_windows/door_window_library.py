from . import data_doors_windows

class Window(data_doors_windows.Standard_Window):
    show_in_library = True
    category_name = "Doors and Windows"
    
    def __init__(self):
        pass

class Door(data_doors_windows.Standard_Door):
    show_in_library = True
    category_name = "Doors and Windows"
    
    def __init__(self):
        pass    