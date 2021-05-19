import bpy
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_closets, data_closet_inserts

class Closet_Starter(data_closets.Closet_Starter):

    def __init__(self):
        pass

class Shelves(data_closet_inserts.Shelves):

    def __init__(self):
        pass    

class Hanging_Rod(data_closet_inserts.Hanging_Rod):

    def __init__(self):
        pass        

class Double_Hang(data_closet_inserts.Hanging_Rod):

    def __init__(self):
        self.is_double = True        

class Base_Doors(data_closet_inserts.Base_Doors):

    def __init__(self):
        pass          

class Tall_Doors(data_closet_inserts.Tall_Doors):

    def __init__(self):
        pass             

class Upper_Doors(data_closet_inserts.Upper_Doors):

    def __init__(self):
        pass             

class Drawers(data_closet_inserts.Drawers):

    def __init__(self):
        pass             

class Single_Shelf(data_closet_inserts.Single_Shelf):

    def __init__(self):
        pass          

class Cubbies(data_closet_inserts.Cubbies):

    def __init__(self):
        pass        