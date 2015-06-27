'''
    CPU sensor plugin

    Generates the CPU usage stats
'''
from ptop.core import Plugin
import psutil

class CPUSensor(Plugin):
    def __init__(self,**kwargs):
        super(CPUSensor,self).__init__(**kwargs)

    # overriding the update method
    def update(self):
        cpu_info = {}
        # there will be two parts of the returned value, one will be text and other graph
        # there can be many text (key,value) pairs to display corresponding to each key
        cpu_info['text'] = {}
        # there will be one averaged value
        cpu_info['graph'] = {'percentage' : ''}
        # cpu usage
        cpu_usage = psutil.cpu_percent(percpu=True)
        num_cores = len(cpu_usage)
        cpu_info['text']['number_of_cores'] = str(num_cores)
        for ctr in range(num_cores):
            cpu_info['text']['core{0}'.format(ctr+1)] = cpu_usage[ctr]
        # average cpu usage
        cpu_info['graph']['percentage'] = sum(cpu_usage)/num_cores
        # finally set the updated value to currentValue
        self.currentValue = cpu_info


