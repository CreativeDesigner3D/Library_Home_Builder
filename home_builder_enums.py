import bpy
import os
from .pc_lib import pc_types, pc_unit, pc_utils, pc_pointer_utils
from . import home_builder_utils

preview_collections = {}
preview_collections["material_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["material_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["pull_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["pull_items"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["sink_categories"] = pc_pointer_utils.create_image_preview_collection()
preview_collections["sink_items"] = pc_pointer_utils.create_image_preview_collection()

#MATERIALS
def enum_material_categories(self,context):
    if context is None:
        return []
    
    icon_dir = home_builder_utils.get_material_path()
    pcoll = preview_collections["material_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_material_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_utils.get_material_path(),self.material_category)
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
    
    icon_dir = home_builder_utils.get_pull_path()
    pcoll = preview_collections["pull_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_pull_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_utils.get_pull_path(),self.pull_category)
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
    
    icon_dir = home_builder_utils.get_sink_path()
    pcoll = preview_collections["sink_categories"]
    return pc_pointer_utils.get_folder_enum_previews(icon_dir,pcoll)

def enum_sink_names(self,context):
    if context is None:
        return []
    
    icon_dir = os.path.join(home_builder_utils.get_sink_path(),self.sink_category)
    pcoll = preview_collections["sink_items"]
    return pc_pointer_utils.get_image_enum_previews(icon_dir,pcoll)

def update_sink_category(self,context):
    if preview_collections["sink_items"]:
        bpy.utils.previews.remove(preview_collections["sink_items"])
        preview_collections["sink_items"] = pc_pointer_utils.create_image_preview_collection()     
        
    enum_sink_names(self,context)    