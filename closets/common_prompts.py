import bpy
from ..pc_lib import pc_types, pc_unit, pc_utils
from .. import home_builder_utils

def add_front_prompts(assembly):
    assembly.add_prompt("Front Thickness",'DISTANCE',pc_unit.inch(.75))
    assembly.add_prompt("Turn Off Pulls",'CHECKBOX',False)

def add_door_prompts(assembly):
    door_swing = assembly.add_prompt("Door Swing",'COMBOBOX',0,["Left","Right","Double"])
    door_swing.combobox_columns = 3
    assembly.add_prompt("Door Rotation",'ANGLE',120)
    assembly.add_prompt("Open Door",'PERCENTAGE',0)
    assembly.add_prompt("Door Type",'TEXT',"")

def add_drawer_prompts(assembly):
    assembly.add_prompt("Open Drawer",'PERCENTAGE',0)
    assembly.add_prompt("Drawer Box Gap",'DISTANCE',pc_unit.inch(.25))

def add_drawer_pull_prompts(assembly):
    props = home_builder_utils.get_scene_props(bpy.context.scene)
    assembly.add_prompt("Center Pull On Front",'CHECKBOX',props.center_pulls_on_drawer_front)
    assembly.add_prompt("Drawer Pull Vertical Location",'DISTANCE',props.pull_vertical_location_drawers)
    
def add_pull_prompts(assembly):
    props = home_builder_utils.get_scene_props(bpy.context.scene)
    assembly.add_prompt("Base Pull Vertical Location",'DISTANCE',props.pull_vertical_location_base)
    assembly.add_prompt("Tall Pull Vertical Location",'DISTANCE',props.pull_vertical_location_tall)
    assembly.add_prompt("Upper Pull Vertical Location",'DISTANCE',props.pull_vertical_location_upper)
    assembly.add_prompt("Pull Horizontal Location",'DISTANCE',props.pull_dim_from_edge)    
    assembly.add_prompt("Pull Length",'DISTANCE',pc_unit.inch(0))
    
def add_front_overlay_prompts(assembly):
    assembly.add_prompt("Inset Front",'CHECKBOX',False)
    assembly.add_prompt("Door to Cabinet Gap",'DISTANCE',pc_unit.inch(.125))    
    assembly.add_prompt("Half Overlay Top",'CHECKBOX',True)
    assembly.add_prompt("Half Overlay Bottom",'CHECKBOX',True)
    assembly.add_prompt("Half Overlay Left",'CHECKBOX',True)
    assembly.add_prompt("Half Overlay Right",'CHECKBOX',True)
    assembly.add_prompt("Inset Reveal",'DISTANCE',pc_unit.inch(.125))
    assembly.add_prompt("Top Reveal",'DISTANCE',pc_unit.inch(.0625))
    assembly.add_prompt("Bottom Reveal",'DISTANCE',pc_unit.inch(0))
    assembly.add_prompt("Left Reveal",'DISTANCE',pc_unit.inch(.0625))
    assembly.add_prompt("Right Reveal",'DISTANCE',pc_unit.inch(.0625))
    assembly.add_prompt("Vertical Gap",'DISTANCE',pc_unit.inch(.125))
    assembly.add_prompt("Horizontal Gap",'DISTANCE',pc_unit.inch(.125))

def add_closet_toe_kick_prompts(assembly):
    assembly.add_prompt("Closet Kick Height",'DISTANCE',pc_unit.millimeter(96)) 
    assembly.add_prompt("Closet Kick Setback",'DISTANCE',pc_unit.inch(1.625)) 

def add_closet_thickness_prompts(assembly):
    assembly.add_prompt("Shelf Thickness",'DISTANCE',pc_unit.inch(.75))
    assembly.add_prompt("Panel Thickness",'DISTANCE',pc_unit.inch(.75))