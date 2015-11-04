'''Some gromacs utilities'''
from chemlab.io import datafile
import os
import shutil

import subprocess
from chemlab.md.simulation import to_mdp
from chemlab.md.potential import to_top
import logging
import fcntl
import time

kernel = get_ipython().kernel

def _set_process_async(process):
    """Make the process read/write methods unblocking"""
    for fd in [process.stderr.fileno(), process.stdout.fileno()]:
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

class AsyncCalculation(object):
    
    def __init__(self, process, simulation, directory, output_function):
        self.process = process
        _set_process_async(process)
        self.directory = directory
        self.simulation = simulation
        self.output_function = output_function
        from tornado.ioloop import PeriodicCallback
        self._timer = PeriodicCallback(self._produce_output, 100)
        self._timer.start()

    def wait(self, poll=0.1):
        kernel = get_ipython().kernel
        while self.process.poll() is None:
            kernel.do_one_iteration()
        
    def _produce_output(self):
        # kernel = get_ipython().kernel
        try:
            line = self.process.stderr.read(512)
            self.output_function(line)
        except IOError:
            pass
        try:
            line = self.process.stdout.read(512)
            self.output_function(line)
        except IOError:
            pass
        
        if self.process.poll() is not None:
            self._timer.stop()
            self.output_function("\n### Process terminated {} ###".format(self.process.returncode))
            # kernel.do_one_iteration()
        
    def get_system(self):
        out = datafile(os.path.join(self.directory, 'confout.gro')).read('system')
        ret = self.simulation.system.copy()
        ret.r_array = out.r_array
        return ret
    
    def cancel(self):
        self.process.kill()
    
    def __del__(self):
        if self.process.poll() is None:
            self.cancel()

from ipywidgets.widgets import Textarea
from IPython.display import display  

def run_gromacs(simulation, directory, clean=False):
    if clean is False and os.path.exists(directory):
        raise ValueError('Cannot override {}, use option clean=True'.format(directory))
    else:
        shutil.rmtree(directory, ignore_errors=True)
        os.mkdir(directory)
    
    # Parameter file
    mdpfile = to_mdp(simulation)
    with open(os.path.join(directory, 'grompp.mdp'), 'w') as fd:
        fd.write(mdpfile)
    
    # Topology file
    topfile = to_top(simulation.system, simulation.potential)
    with open(os.path.join(directory, 'topol.top'), 'w') as fd:
        fd.write(topfile)
    
    # Simulation file
    datafile(os.path.join(directory, 'conf.gro'), 'w').write('system', simulation.system)
    
    
    process = subprocess.Popen('cd {} && grompp_d && exec mdrun_d -v'.format(directory), 
                               shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)

    output_box = Textarea()
    output_box.height = '200px'
    output_box.font_family = 'monospace'
    output_box.color = '#AAAAAA'
    output_box.background_color = 'black'
    output_box.width = '800px'
    display(output_box)
    def output_function(text, output_box=output_box):
        output_box.value += text.decode('utf8')
        output_box.scroll_to_bottom()
    
    return AsyncCalculation(process, simulation, directory, output_function)
    
    
