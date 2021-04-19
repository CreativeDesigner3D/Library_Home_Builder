print("HELLO FROM DISHWASER LIBRARY ITEM")
from .... import pc_lib

class Item(pc_lib.pc_types.Assembly):

    def name(self):
        print("MY NAME")

my_var = 1
