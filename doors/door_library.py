from . import data_doors

class Door(data_doors.Standard_Door):
    show_in_library = True
    category_name = "Doors and Windows"
    
    def __init__(self):
        pass