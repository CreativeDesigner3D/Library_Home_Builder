import bpy
import os
from .pc_lib import pc_types, pc_unit, pc_utils, pc_pointer_utils
from . import home_builder_paths

preview_collections = {}
preview_collections["material_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["material_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["pull_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["pull_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["sink_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["sink_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["faucet_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["faucet_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["range_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["range_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["range_hood_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["range_hood_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["cabinet_door_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["cabinet_door_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["entry_door_panel_items"] = pc_pointer_utils.create_image_preview_collection()

#MATERIALS
def enum_material_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_material_path()
    pcoll = preview_collections["material_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_material_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_material_path(),self.material_category)
    pcoll = preview_collections["material_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_material_category(self,context):
    if preview_collections["material_items"]:
        bpy.utils.previews.remove(preview_collections["material_items"])
        preview_collections["material_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_material_names(self,context)

#PULLS
def enum_pull_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_pull_path()
    pcoll = preview_collections["pull_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_pull_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_pull_path(),self.pull_category)
    pcoll = preview_collections["pull_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_pull_category(self,context):
    if preview_collections["pull_items"]:
        bpy.utils.previews.remove(preview_collections["pull_items"])
        preview_collections["pull_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_pull_names(self,context)

#SINKS
def enum_sink_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_sink_path()
    pcoll = preview_collections["sink_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_sink_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_sink_path(),self.sink_category)
    pcoll = preview_collections["sink_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_sink_category(self,context):
    if preview_collections["sink_items"]:
        bpy.utils.previews.remove(preview_collections["sink_items"])
        preview_collections["sink_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_sink_names(self,context)    


#FAUCETS
def enum_faucet_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_faucet_path()
    pcoll = preview_collections["faucet_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_faucet_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_faucet_path(),self.faucet_category)
    pcoll = preview_collections["faucet_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_faucet_category(self,context):
    if preview_collections["faucet_items"]:
        bpy.utils.previews.remove(preview_collections["faucet_items"])
        preview_collections["faucet_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_faucet_names(self,context)        

#RANGES   
def enum_range_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_range_path()
    pcoll = preview_collections["range_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_range_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_range_path(),self.range_category)
    pcoll = preview_collections["range_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_range_category(self,context):
    if preview_collections["range_items"]:
        bpy.utils.previews.remove(preview_collections["range_items"])
        preview_collections["range_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_range_names(self,context)      

#RANGE HOODS  
def enum_range_hood_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_range_hood_path()
    pcoll = preview_collections["range_hood_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_range_hood_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_range_hood_path(),self.range_hood_category)
    pcoll = preview_collections["range_hood_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_range_hood_category(self,context):
    if preview_collections["range_hood_items"]:
        bpy.utils.previews.remove(preview_collections["range_hood_items"])
        preview_collections["range_hood_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_range_hood_names(self,context)          

#CABINET DOORS  
def enum_cabinet_door_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_cabinet_door_path()
    pcoll = preview_collections["cabinet_door_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_cabinet_door_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_cabinet_door_path(),self.cabinet_door_category)
    pcoll = preview_collections["cabinet_door_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_cabinet_door_category(self,context):
    if preview_collections["cabinet_door_items"]:
        bpy.utils.previews.remove(preview_collections["cabinet_door_items"])
        preview_collections["cabinet_door_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_cabinet_door_names(self,context)              

#ENTRY DOOR PANELS     
def enum_entry_door_panels_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_entry_door_panel_path())
    pcoll = preview_collections["entry_door_panel_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)