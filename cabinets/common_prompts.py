from ..pc_lib import pc_types, pc_unit, pc_utils

def add_cabinet_prompts(assembly):
    assembly.add_prompt("Cabinet Type",'COMBOBOX',0,["Base","Tall","Upper","Suspended"])

def add_filler_prompts(assembly):
    assembly.add_prompt("Left Adjustment Width",'DISTANCE',pc_unit.inch(0))
    assembly.add_prompt("Right Adjustment Width",'DISTANCE',pc_unit.inch(0))

def add_front_prompts(assembly):
    assembly.add_prompt("Inset Front",'CHECKBOX',False)
    assembly.add_prompt("Door to Cabinet Gap",'DISTANCE',pc_unit.inch(.125))
    assembly.add_prompt("Front Thickness",'DISTANCE',pc_unit.inch(.75))

def add_sink_prompts(assembly):
    assembly.add_prompt("Add Sink",'CHECKBOX',False)
    assembly.add_prompt("Add Faucet",'CHECKBOX',False)

def add_door_prompts(assembly):
    door_swing = assembly.add_prompt("Door Swing",'COMBOBOX',0,["Left","Right"])
    door_swing.combobox_columns = 2
    assembly.add_prompt("Door Rotation",'ANGLE',120)
    assembly.add_prompt("Open Door",'PERCENTAGE',0)

def add_front_overlay_prompts(assembly):
    assembly.add_prompt("Half Overlay Top",'CHECKBOX',False)
    assembly.add_prompt("Half Overlay Bottom",'CHECKBOX',False)
    assembly.add_prompt("Half Overlay Left",'CHECKBOX',False)
    assembly.add_prompt("Half Overlay Right",'CHECKBOX',False)
    assembly.add_prompt("Inset Reveal",'DISTANCE',pc_unit.inch(.125))
    # assembly.add_prompt("Top Overlay",'DISTANCE',pc_unit.inch(.6875))
    # assembly.add_prompt("Bottom Overlay",'DISTANCE',pc_unit.inch(.6875))
    # assembly.add_prompt("Left Overlay",'DISTANCE',pc_unit.inch(.6875))
    # assembly.add_prompt("Right Overlay",'DISTANCE',pc_unit.inch(.6875))
    assembly.add_prompt("Vertical Gap",'DISTANCE',pc_unit.inch(.125))

def add_pull_prompts(assembly):
    assembly.add_prompt("Base Pull Vertical Location",'DISTANCE',pc_unit.inch(1.5))
    assembly.add_prompt("Tall Pull Vertical Location",'DISTANCE',pc_unit.inch(45))
    assembly.add_prompt("Upper Pull Vertical Location",'DISTANCE',pc_unit.inch(1.5))
    assembly.add_prompt("Pull Horizontal Location",'DISTANCE',pc_unit.inch(2))
    assembly.add_prompt("Pull Length",'DISTANCE',pc_unit.inch(0))

def add_drawer_pull_prompts(assembly):
    assembly.add_prompt("Center Pull On Front",'CHECKBOX',False)
    assembly.add_prompt("Drawer Pull Vertical Location",'DISTANCE',pc_unit.inch(2))

def add_countertop_prompts(assembly):
    assembly.add_prompt("Add Backsplash",'CHECKBOX',True)
    assembly.add_prompt("Add Left Backsplash",'CHECKBOX',False)
    assembly.add_prompt("Add Right Backsplash",'CHECKBOX',False)
    assembly.add_prompt("Side Splash Setback",'DISTANCE',pc_unit.inch(2.75))
    assembly.add_prompt("Deck Thickness",'DISTANCE',pc_unit.inch(1.5))
    assembly.add_prompt("Splash Thickness",'DISTANCE',pc_unit.inch(.75))    

def add_countertop_overhang_prompts(assembly):
    pass

def add_base_assembly_prompts(assembly):
    assembly.add_prompt("Toe Kick Height",'DISTANCE',pc_unit.inch(4))
    assembly.add_prompt("Toe Kick Setback",'DISTANCE',pc_unit.inch(3.25))
    assembly.add_prompt("Boolean Overhang",'DISTANCE',pc_unit.inch(1))  

def add_carcass_prompts(assembly):
    assembly.add_prompt("Left Finished End",'CHECKBOX',True)
    assembly.add_prompt("Right Finished End",'CHECKBOX',True)
    assembly.add_prompt("Finished Back",'CHECKBOX',True)
    assembly.add_prompt("Run Sides to Floor",'CHECKBOX',True)
    # assembly.add_prompt("Material Thickness",'DISTANCE',pc_unit.inch(.75))    
    
def add_cabinet_lighting_prompts(assembly):
    assembly.add_prompt("Add Top Light",'CHECKBOX',False)    
    assembly.add_prompt("Add Side Light",'CHECKBOX',False)  
    assembly.add_prompt("Add Bottom Light",'CHECKBOX',False)  
    assembly.add_prompt("Lighting Width",'DISTANCE',pc_unit.inch(.75)) 
    assembly.add_prompt("Lighting Dim From Front",'DISTANCE',pc_unit.inch(1.5)) 
    assembly.add_prompt("Lighting Inset From Sides",'DISTANCE',pc_unit.inch(.75)) 

def add_splitter_prompts(assembly):
    assembly.add_prompt("Thickness",'DISTANCE',pc_unit.inch(.75))
    assembly.add_prompt("Left Thickness",'DISTANCE',pc_unit.inch(.75))
    assembly.add_prompt("Right Thickness",'DISTANCE',pc_unit.inch(.75))
    assembly.add_prompt("Top Thickness",'DISTANCE',pc_unit.inch(.75))
    assembly.add_prompt("Bottom Thickness",'DISTANCE',pc_unit.inch(.75))
    assembly.add_prompt("Extend Top Amount",'DISTANCE',pc_unit.inch(0))
    assembly.add_prompt("Extend Bottom Amount",'DISTANCE',pc_unit.inch(0))

def add_interior_shelf_prompts(assembly):
    assembly.add_prompt("Shelf Quantity",'QUANTITY',1) 
    assembly.add_prompt("Shelf Setback",'DISTANCE',pc_unit.inch(.25))  
    assembly.add_prompt("Shelf Clip Gap",'DISTANCE',pc_unit.inch(.125))  
    # assembly.add_prompt("Material Thickness",'DISTANCE',pc_unit.inch(.75)) 

def add_thickness_prompts(assembly):
    assembly.add_prompt("Material Thickness",'DISTANCE',pc_unit.inch(.75)) 
