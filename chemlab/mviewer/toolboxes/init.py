__builtins__['viewer'] = viewer

from core import *
from select_ import * # Shadow the global select
from display import *
from orderpar import *
from art import *

#background_color('white')
add_post_processing(SSAOEffect, kernel_size=128)
#add_post_processing(FXAAEffect)
#add_post_processing(GammaCorrectionEffect)

#load_system('/home/gabriele/projects/NaCl/dissolution/nacl-sink-500/start.gro')
#load_trajectory('/home/gabriele/projects/NaCl/dissolution/nacl-sink-500/traj.xtc')
#select_molecules('H2O')
#delete()
