import bpy
import os

def get_addon_preferences():
    preferences = bpy.context.preferences
    return preferences.addons[__package__].preferences

def get_library_path():
    return os.path.join(os.path.dirname(__file__),'library')   
    
def get_asset_folder_path():
    prefs = get_addon_preferences()

    if not prefs:
        return os.path.join(os.path.dirname(__file__),'assets')
    
    if os.path.exists(prefs.assets_filepath):
        return prefs.assets_filepath
    else:
        return os.path.join(os.path.dirname(__file__),'assets')

def get_assembly_path():
    return os.path.join(get_asset_folder_path(),'ASSEMBLIES') 

def get_material_path():
    return os.path.join(get_asset_folder_path(),'Materials') 

def get_custom_cabinet_library_path():
    return os.path.join(get_asset_folder_path(),"KITCHENS","CUSTOM_CABINETS")   

def get_vanity_library_path():
    return os.path.join(get_asset_folder_path(),"BATHS","VANITIES")  

def get_pull_path():
    return os.path.join(get_asset_folder_path(),'Cabinet Pulls') 

def get_sink_path():
    return os.path.join(get_asset_folder_path(),'Sinks') 

def get_faucet_path():
    return os.path.join(get_asset_folder_path(),'Faucets') 

def get_range_path():
    return os.path.join(get_asset_folder_path(),'KITCHENS','RANGES')     

def get_built_in_appliances_path():
    return os.path.join(get_asset_folder_path(),'Built in Appliances') 

def get_range_hood_path():
    return os.path.join(get_asset_folder_path(),'Range Hoods')         

def get_dishwasher_path():
    return os.path.join(get_asset_folder_path(),'KITCHENS','DISHWASHERS')     

def get_refrigerator_path():
    return os.path.join(get_asset_folder_path(),'KITCHENS','REFRIGERATORS')     

def get_cooktop_path():
    return os.path.join(get_asset_folder_path(),'Cooktops')    

def get_cabinet_door_path():
    return os.path.join(get_asset_folder_path(),'Cabinet Doors')        

def get_cabinet_door_panel_path(pointer):
    return os.path.join(get_cabinet_door_path(),pointer.category,pointer.item_name + ".blend")

def get_entry_door_frame_path():
    return os.path.join(get_asset_folder_path(),'Entry Door Frames')  

def get_entry_door_jamb_path():
    return os.path.join(get_asset_folder_path(),'Entry Door Jambs')

def get_entry_door_handle_path():
    return os.path.join(get_asset_folder_path(),'Entry Door Handles')       

def get_entry_door_panel_path():
    return os.path.join(get_asset_folder_path(),'Entry Door Panels')      

def get_window_frame_path():
    return os.path.join(get_asset_folder_path(),'Window Frames')   

def get_window_insert_path():
    return os.path.join(get_asset_folder_path(),'Window Inserts')     

def get_molding_path():
    return os.path.join(get_asset_folder_path(),'Moldings')             