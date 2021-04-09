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
preview_collections["molding_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["molding_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["entry_door_panel_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["entry_door_panel_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["entry_door_frame_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["entry_door_frame_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["entry_door_handle_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["entry_door_handle_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["window_insert_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["window_insert_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["window_frame_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["window_frame_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["dishwasher_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["dishwasher_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["refrigerator_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["refrigerator_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["cooktop_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["cooktop_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["active_asset_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["active_asset_items"] = pc_pointer_utils.create_image_preview_collection()

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

#MOLDING
def enum_molding_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_molding_path()
    pcoll = preview_collections["molding_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_molding_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_molding_path(),self.molding_category)
    pcoll = preview_collections["molding_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_molding_category(self,context):
    if preview_collections["molding_items"]:
        bpy.utils.previews.remove(preview_collections["molding_items"])
        preview_collections["molding_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_molding_names(self,context)

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
def enum_entry_door_panel_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_entry_door_panel_path()
    pcoll = preview_collections["entry_door_panel_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_entry_door_panels_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_entry_door_panel_path(),self.entry_door_panel_category)
    pcoll = preview_collections["entry_door_panel_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_entry_door_panel_category(self,context):
    if preview_collections["entry_door_panel_items"]:
        bpy.utils.previews.remove(preview_collections["entry_door_panel_items"])
        preview_collections["entry_door_panel_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_entry_door_panels_names(self,context)           

#ENTRY DOOR FRAMES     
def enum_entry_door_frame_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_entry_door_frame_path()
    pcoll = preview_collections["entry_door_frame_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_entry_door_frame_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_entry_door_frame_path(),self.entry_door_frame_category)
    pcoll = preview_collections["entry_door_frame_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_entry_door_frame_category(self,context):
    if preview_collections["entry_door_frame_items"]:
        bpy.utils.previews.remove(preview_collections["entry_door_frame_items"])
        preview_collections["entry_door_frame_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_entry_door_frame_names(self,context)

#ENTRY DOOR HANDLES     
def enum_entry_door_handle_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_entry_door_handle_path()
    pcoll = preview_collections["entry_door_handle_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_entry_door_handle_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_entry_door_handle_path(),self.entry_door_handle_category)
    pcoll = preview_collections["entry_door_handle_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_entry_door_handle_category(self,context):
    if preview_collections["entry_door_handle_items"]:
        bpy.utils.previews.remove(preview_collections["entry_door_handle_items"])
        preview_collections["entry_door_handle_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_entry_door_handle_names(self,context)

#WINDOW INSERTS     
def enum_window_insert_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_window_insert_path()
    pcoll = preview_collections["window_insert_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_window_insert_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_window_insert_path(),self.window_insert_category)
    pcoll = preview_collections["window_insert_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_window_insert_category(self,context):
    if preview_collections["window_insert_items"]:
        bpy.utils.previews.remove(preview_collections["window_insert_items"])
        preview_collections["window_insert_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_window_insert_names(self,context)

#WINDOW FRAMES     
def enum_window_frame_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_window_frame_path()
    pcoll = preview_collections["window_frame_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_window_frame_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_window_frame_path(),self.window_frame_category)
    pcoll = preview_collections["window_frame_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_window_frame_category(self,context):
    if preview_collections["window_frame_items"]:
        bpy.utils.previews.remove(preview_collections["window_frame_items"])
        preview_collections["window_frame_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_window_frame_names(self,context)

#DISHWASHERS
def enum_dishwasher_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_dishwasher_path()
    pcoll = preview_collections["dishwasher_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_dishwasher_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_dishwasher_path(),self.dishwasher_category)
    pcoll = preview_collections["dishwasher_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_dishwasher_category(self,context):
    if preview_collections["dishwasher_items"]:
        bpy.utils.previews.remove(preview_collections["dishwasher_items"])
        preview_collections["dishwasher_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_dishwasher_names(self,context)           

#REFRIGERATORS
def enum_refrigerator_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_refrigerator_path()
    pcoll = preview_collections["refrigerator_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_refrigerator_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_refrigerator_path(),self.refrigerator_category)
    pcoll = preview_collections["refrigerator_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_refrigerator_category(self,context):
    if preview_collections["refrigerator_items"]:
        bpy.utils.previews.remove(preview_collections["refrigerator_items"])
        preview_collections["refrigerator_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_refrigerator_names(self,context)

#COOKTOPS
def enum_cooktop_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_paths.get_cooktop_path()
    pcoll = preview_collections["cooktop_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_cooktop_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_paths.get_cooktop_path(),self.cooktop_category)
    pcoll = preview_collections["cooktop_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_cooktop_category(self,context):
    if preview_collections["cooktop_items"]:
        bpy.utils.previews.remove(preview_collections["cooktop_items"])
        preview_collections["cooktop_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_cooktop_names(self,context)   

#ACTIVE CATEGORY
def enum_active_asset_categories(self,context):
    if context is None:
        return []
    path = self.get_active_category_path()
    icon_dir = path

    pcoll = preview_collections["active_asset_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_active_asset_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(self.get_active_category_path(),self.active_asset_category)
    pcoll = preview_collections["active_asset_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_active_asset_tab(self,context):
    bpy.utils.previews.remove(preview_collections["active_asset_categories"])
    preview_collections["active_asset_categories"] = pc_pointer_utils.create_image_preview_collection()     

    enum_active_asset_categories(self,context)   
    update_active_asset_category(self,context)  

    self.active_asset_index = 0

def update_active_asset_category(self,context):
    if preview_collections["active_asset_categories"]:
        bpy.utils.previews.remove(preview_collections["active_asset_items"])
        preview_collections["active_asset_items"] = pc_pointer_utils.create_image_preview_collection()     

        for i in self.active_asset_collection:
            self.active_asset_collection.remove(0)

        path = os.path.join(self.get_active_category_path(),self.active_asset_category)

        if os.path.exists(path):
            image_paths = []
            for fn in os.listdir(path):
                if fn.lower().endswith(".blend"):
                    image_paths.append(fn)

            for i, name in enumerate(image_paths):
                filepath = os.path.join(path, name)
                name, ext = os.path.splitext(name)        
                item = self.active_asset_collection.add()
                item.name = name
                item.asset_path = filepath

    enum_active_asset_names(self,context)         