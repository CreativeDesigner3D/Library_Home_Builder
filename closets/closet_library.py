import bpy
from ..pc_lib import pc_types, pc_unit, pc_utils
from . import data_closets, data_closet_inserts

class Tall_Starter(data_closets.Closet_Starter):

    def __init__(self):
        self.is_hanging = False

class Hanging_Starter(data_closets.Closet_Starter):

    def __init__(self):
        self.is_hanging = True

class Base_Starter(data_closets.Closet_Starter):

    def __init__(self):
        self.is_hanging = False
        self.is_base = True

class Tall_L_Shelves(data_closets.Closet_Inside_Corner):

    def __init__(self):
        pass

class Hanging_L_Shelves(data_closets.Closet_Inside_Corner):

    def __init__(self):
        self.is_hanging = True

class Corner_Filler(data_closets.Closet_Inside_Corner_Filler):

    def __init__(self):
        pass

class Adj_Shelves(data_closet_inserts.Shelves):

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

class Single_Drawer(data_closet_inserts.Single_Drawer):

    def __init__(self):
        pass             

class Single_Shelf(data_closet_inserts.Single_Shelf):

    def __init__(self):
        pass          

class Slanted_Shoe_Shelf(data_closet_inserts.Slanted_Shoe_Shelf):

    def __init__(self):
        pass        

class Cubbies(data_closet_inserts.Cubbies):

    def __init__(self):
        pass        

class Wire_Baskets(data_closet_inserts.Wire_Baskets):

    def __init__(self):
        pass            

class Fixed_Shelf_1(data_closet_inserts.Vertical_Splitter):

    def __init__(self):
        self.splitter_qty = 1          

class Fixed_Shelf_2(data_closet_inserts.Vertical_Splitter):

    def __init__(self):
        self.splitter_qty = 2    

class Fixed_Shelf_3(data_closet_inserts.Vertical_Splitter):

    def __init__(self):
        self.splitter_qty = 3    

class Fixed_Shelf_4(data_closet_inserts.Vertical_Splitter):

    def __init__(self):
        self.splitter_qty = 4              

class Horizontal_Splitter_1(data_closet_inserts.Horizontal_Splitter):

    def __init__(self):
        self.splitter_qty = 1          

class Horizontal_Splitter_2(data_closet_inserts.Horizontal_Splitter):

    def __init__(self):
        self.splitter_qty = 2    

class Horizontal_Splitter_3(data_closet_inserts.Horizontal_Splitter):

    def __init__(self):
        self.splitter_qty = 3    

class Horizontal_Splitter_4(data_closet_inserts.Horizontal_Splitter):

    def __init__(self):
        self.splitter_qty = 4                          