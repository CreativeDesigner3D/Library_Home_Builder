import os

def get_library_path():
    return os.path.join(os.path.dirname(__file__),'library')   
    
def get_asset_folder_path():
    return os.path.join(os.path.dirname(__file__),'assets')

def get_material_path():
    return os.path.join(get_asset_folder_path(),'Materials') 

def get_pull_path():
    return os.path.join(get_asset_folder_path(),'Cabinet Pulls') 

def get_sink_path():
    return os.path.join(get_asset_folder_path(),'Sinks') 

def get_faucet_path():
    return os.path.join(get_asset_folder_path(),'Faucets') 

def get_range_path():
    return os.path.join(get_asset_folder_path(),'Ranges')     

def get_range_hood_path():
    return os.path.join(get_asset_folder_path(),'Range Hoods')         