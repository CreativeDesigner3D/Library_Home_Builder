from ..pc_lib import pc_utils, pc_unit, pc_types

class Wall(pc_types.Assembly):
    show_in_library = True
    category_name = "Walls"

    def draw(self):
        print('HELLOW')

class Framing_Wall(pc_types.Assembly):
    show_in_library = True
    category_name = "Walls"

class Die_Wall(pc_types.Assembly):
    show_in_library = True
    category_name = "Walls"

class Brick_Wall(pc_types.Assembly):
    show_in_library = True
    category_name = "Walls"

class Stone_Wall(pc_types.Assembly):
    show_in_library = True
    category_name = "Walls"

class Wood_Fence(pc_types.Assembly):
    show_in_library = True
    category_name = "Fence"