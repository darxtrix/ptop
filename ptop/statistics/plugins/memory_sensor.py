'''
    Memory sensor plugin

    Generates the memory usage information of the system
'''
from ptop.core import Plugin
import psutil

class MemorySensor(Plugin):
    def __init__(self,**kwargs):
        super(MemorySensor,self).__init__(**kwargs)

    # overriding the update method
    def update(self):
        memory_info = {}
        # there will be two parts of the returned value, one will be text and other graph
        # there can be many text (key,value) pairs to display corresponding to each key
        memory_info['text'] = { 'memory' : [],'swap_memory' : []}
        # there will be only one graph info
        memory_info['graph'] = {'percentage' : ''}
        # virtual memory
        vmem = psutil.virtual_memory()
        memory_info['text']['memory'].append(('Total',float(vmem.total)/(1024*1024)))
        memory_info['text']['memory'].append(('Active',float(vmem.active)/(1024*1024)))
        memory_info['graph']['percentage'] = int(vmem.percent)
        # swap memory
        smem = psutil.swap_memory()
        memory_info['text']['swap_memory'].append(('Total',float(smem.total)/(1024*1024)))
        memory_info['text']['swap_memory'].append(('Active',float(smem.used)/(1024*1024)))
        # finally setting the updated value to current value
        self.currentValue = memory_info





