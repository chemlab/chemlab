light_grey =      [200,200,200,255]
red      =        [240,0,0,255]    
white     =       [255,255,255,255]
black   =         [0, 0, 0, 255]
                              
light_blue  =     [143,143,255,255]
sulphur_yellow =  [255,200,50,255] 
green   =         [0,255,0,255]    
                              
orange   =        [255,165,0,255]  
blue      =       [0,0,255,255]    
forest_green =    [34,139,34,255]  
brown   =         [165,42,42,255]  
                              
dark_grey  =      [128,128,144,255]
goldenrod  =      [218,165,32,255] 
purple      =     [160,32.240,255] 
                              
firebrick    =    [178,34,34,255]  
pink          =   [255,192,203,255]
deep_pink      =  [255,20,147,255] 



# Default color
default = deep_pink

map = {
"C": light_grey,
"O": red,
"H": white,

"N": light_blue,
"S": sulphur_yellow,
"Cl": green,
"B": green,
    
"Ph": orange,
"Fe": orange,
"Ba": orange,

"Na": blue,
"Mg": forest_green,
    
"Zn": brown,
"Cu": brown,
"Ni":brown,
"Br":brown,

"Ca":dark_grey,
"Mn":dark_grey,
"Al":dark_grey,
"Ti":dark_grey,
"Cr":dark_grey,
"Ag":dark_grey,

"F": goldenrod,    
"Si": goldenrod,
"Au": goldenrod,
    
"I": purple,
    
"Li":firebrick,
"He":pink,
}
# Making the guy case_insensitive
for k,v in map.items():
    map[k.lower()] = v
    map[k.upper()] = v