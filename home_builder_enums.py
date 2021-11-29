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

#CLOSETS
PANEL_HEIGHTS=[('83','3 5/6"','3 5/6"'),
               ('115','4 9/16"','4 9/16"'),
               ('147','5 13/16"','5 13/16"'),
               ('179','7 1/16"','7 1/16"'),
               ('211','8 5/16"','8 5/16"'),
               ('243','9 5/8"','9 5/8"'),
               ('275','10 7/8"','10 7/8"'),
               ('307','12 1/8"','12 1/8"'),
               ('339','13 3/8"','13 3/8"'),
               ('371','14 5/8"','14 5/8"'),
               ('403','15 7/8"','15 7/8"'),
               ('435','17 1/8"','17 1/8"'),
               ('467','18 3/8"','18 3/8"'),
               ('499','19 11/16"','19 11/16"'),
               ('531','20 15/16"','20 15/16"'),
               ('563','22 3/16"','22 3/16"'),
               ('595','23 7/16"','23 7/16"'),
               ('627','24 3/4"','24 3/4"'),
               ('659','26"','26"'),
               ('691','27 1/4"','27 1/4"'),
               ('723','28 1/2"','28 1/2"'),
               ('755','29 3/4"','29 3/4"'),
               ('787','31"','31"'),
               ('819','32 1/4"','32 1/4"'),
               ('851','33 9/16"','33 9/16"'),
               ('883','34 3/4"','34 3/4"'),
               ('915','36 1/16"','36 1/16"'),
               ('947','37 5/16"','37 5/16"'),
               ('979','38 9/16"','38 9/16"'),
               ('1011','39 13/16"','39 13/16"'),
               ('1043','41 1/16"','41 1/16"'),
               ('1075','42 3/8"','42 3/8"'),
               ('1107','43 9/16"','43 9/16"'),
               ('1139','44 7/8"','44 7/8"'),
               ('1171','46 1/8"','46 1/8"'),
               ('1203','47 3/8"','47 3/8"'),
               ('1235','48 5/8"','48 5/8"'),
               ('1267','49 7/8"','49 7/8"'),
               ('1299','51 3/16"','51 3/16"'),
               ('1331','52 7/16"','52 7/16"'),
               ('1363','53 11/16"','53 11/16"'),
               ('1395','54 15/16"','54 15/16"'),
               ('1427','56 1/4"','56 1/4"'),
               ('1459','57 1/2"','57 1/2"'),
               ('1491','58 11/16"','58 11/16"'),
               ('1523','60"','60"'),
               ('1555','61 1/4"','61 1/4"'),
               ('1587','62 1/2"','62 1/2"'),
               ('1619','63 3/4"','63 3/4"'),
               ('1651','65"','65"'),
               ('1683','66 1/4"','66 1/4"'),
               ('1715','67 1/2"','67 1/2"'),
               ('1748','68 13/16"','68 13/16"'),
               ('1779','70 1/16"','70 1/16"'),
               ('1811','71 5/16"','71 5/16"'),
               ('1843','72 5/8"','72 5/8"'),
               ('1875','73 13/16"','73 13/16"'),
               ('1907','75 1/8"','75 1/8"'),
               ('1939','76 3/8"','76 3/8"'),
               ('1971','77 5/8"','77 5/8"'),
               ('2003','78 15/16"','78 15/16"'),
               ('2035','80 3/16"','80 3/16"'),
               ('2067','81 7/16"','81 7/16"'),
               ('2099','82 11/16"','82 11/16"'),
               ('2131','83 15/16"','83 15/16"'),
               ('2163','85 1/4"','85 1/4"'),
               ('2195','86 1/2"','86 1/2"'),
               ('2227','87 3/4"','87 3/4"'),
               ('2259','89"','89"'),
               ('2291','90 1/4"','90 1/4"'),
               ('2323','91 1/2"','91 1/2"'),
               ('2355','92 3/4"','92 3/4"'),
               ('2387','94"','94"'),
               ('2419','95 5/16"','95 5/16"'),
               ('2451','96 1/2"','96 1/2"'),
               ('2483','97 13/16"','97 13/16"'),
               ('2515','99 1/16"','99 1/16"'),
               ('2547','100 5/16"','100 5/16"'),
               ('2579','101 5/8"','101 5/8"'),
               ('2611','102 7/8"','102 7/8"'),
               ('2643','104 1/8"','104 1/8"'),
               ('2675','105 3/8"','106 5/8"'),
               ('2707','106 5/8"','106 5/8"'),
               ('2739','107 15/16"','107 15/16"'),
               ('2771','109 1/8"','109 1/8"'),
               ('2807','110 7/8"','110 7/8"'),
               ('2835','111 11/16"','111 11/16"'),
               ('2867','112 15/16"','112 15/16"'),
               ('2899','114 3/16"','114 3/16"'),
               ('2931','115 1/2"','115 1/2"'),
               ('2963','116 3/4"','116 3/4"'),
               ('2995','118"','118"'),
               ('3027','119 1/4"','119 1/4"'),
               ('3059','120 1/2"','120 1/2"')]

OPENING_HEIGHTS=[('12.95','1/2"','1/2"'),
                 ('44.95','1 3/4"','1 3/4"'),
                 ('76.95','3"','3"'),
                 ('108.95','4 1/4"','4 1/4"'),
                 ('140.95','5 1/2"','5 1/2"'),
                 ('172.95','6 1/2"','6 1/2"'),
                 ('204.95','8"','8"'),
                 ('236.95','9 1/3"','9 1/3"'),
                 ('268.95','10 1/2"','10 1/2"'),
                 ('300.95','11 3/4"','11 3/4"'),
                 ('332.95','13 1/8"','13 1/8"'),
                 ('364.95','14 3/8"','14 3/8"'),
                 ('396.95','15 5/8"','15 5/8"'),
                 ('428.95','16 3/4"','16 3/4"'),
                 ('460.95','18 1/8"','18 1/8"'),
                 ('492.95','19 1/2"','19 1/2"'),
                 ('524.95','20 1/2"','20 1/2"'),
                 ('556.95','22"','22"'),
                 ('588.95','23 1/8"','23 1/8"'),
                 ('620.95','24 1/2"','24 1/2"'),
                 ('652.95','25 3/4"','25 3/4"'),
                 ('684.95','27"','27"'),
                 ('716.95','28 1/4"','28 1/4"'),
                 ('748.95','29 1/2"','29 1/2"'),
                 ('780.95','30 3/4"','30 3/4"'),
                 ('812.95','32"','32"'),
                 ('844.95','33 1/4"','33 1/4"'),
                 ('876.95','34 1/2"','34 1/2"'),
                 ('908.95','35 3/4"','35 3/4"'),
                 ('940.95','37"','37"'),
                 ('972.95','38 1/4"','38 1/4"'),
                 ('1004.95','39 1/2"','39 1/2"'),
                 ('1036.95','40 3/4"','40 3/4"'),
                 ('1068.95','42"','42"'),
                 ('1100.95','43 1/4"','43 1/4"'),
                 ('1132.95','44 1/2"','44 1/2"'),
                 ('1164.95','45 3/4"','45 3/4"'),
                 ('1196.95','47"','47"'),
                 ('1228.95','48 1/2"','48 1/2"'),
                 ('1260.95','49 3/4"','49 3/4"'),
                 ('1292.95','51"','51"'),
                 ('1324.95','52 1/4"','52 1/4"'),
                 ('1356.95','53 1/2"','53 1/2"'),
                 ('1388.95','54 3/4"','54 3/4"'),
                 ('1420.95','56"','56"'),
                 ('1452.95','57 1/4"','57 1/4"'),
                 ('1484.95','58 1/2"','58 1/2"'),
                 ('1516.95','59 3/4"','59 3/4"'),
                 ('1548.95','61"','61"'),
                 ('1580.95','62 1/4"','62 1/4"'),
                 ('1612.95','63 1/2"','63 1/2"'),
                 ('1644.95','64 3/4"','64 3/4"'),
                 ('1676.95','66"','66"'),
                 ('1740.95','67 1/4"','67 1/4"'),
                 ('1772.95','68 1/2"','68 1/2"'),
                 ('1804.95','69 3/4"','69 3/4"'),
                 ('1836.95','71"','71"'),
                 ('1868.95','72 1/4"','72 1/4"'),
                 ('1900.95','73 1/2"','73 1/2"'),
                 ('1932.95','74 3/4"','74 3/4"')]

# FRONT_HEIGHTS=[('93.15','3 3/4"','3 3/4"'),
#                ('125.15','5"','5"'),
#                ('157.15','6 1/4"','6 1/4"'),
#                ('189.15','7 1/2"','7 1/2"'),
#                ('221.15','8 3/4"','8 3/4"'),
#                ('253.15','10"','10"'),
#                ('285.15','11 1/4"','11 1/4"'),
#                ('317.15','12 1/2"','12 1/2"'),
#                ('349.15', '13 3/4"', '13 3/4"'),
#                ('381.15', '15"', '15"')]

FRONT_HEIGHTS=[('76.95','3 3/4"','3"'),
               ('108.95','5"','4 1/4"'),
               ('140.95','6 1/4"','5 1/2"'),
               ('172.95','7 1/2"','6 1/2"'),
               ('204.95','8 3/4"','8"'),
               ('236.95','10"','9 1/3"'),
               ('268.95','11 1/4"','10 1/2"'),
               ('300.95','12 1/2"','11 3/4"'),
               ('332.95','13 3/4"','13 1/8"'),
               ('364.95','15"','14 3/8"')]

KICK_HEIGHTS=[('64','2 1/2"','2 1/2"'),
              ('96','3 3/4"','2 1/2"'),
              ('128','5"','2 1/2"'),
              ('160','6 1/4"','2 1/2"'),
              ('192','7 1/2"','2 1/2"'),
              ('224','8 3/4"','2 1/2"'),
              ('256','10"','2 1/2"'),
              ('288','11 1/4"','2 1/2"'),
              ('320','12 1/2"','2 1/2"')]
