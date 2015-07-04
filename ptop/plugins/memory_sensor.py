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
        # there will be two parts of the returned value, one will be text and other graph
        # there can be many text (key,value) pairs to display corresponding to each key
        self.currentValue['text'] = { 'memory' : [],'swap_memory' : []}
        # there will be only one graph info
        self.currentValue['graph'] = {'percentage' : ''}
        # virtual memory
        vmem = psutil.virtual_memory()
        self.currentValue['text']['memory'].append(('Total',float(vmem.total)/(1024*1024)))
        self.currentValue['text']['memory'].append(('Active',float(vmem.active)/(1024*1024)))
        self.currentValue['graph']['percentage'] = int(vmem.percent)
        # swap memory
        smem = psutil.swap_memory()
        self.currentValue['text']['swap_memory'].append(('Total',float(smem.total)/(1024*1024)))
        self.currentValue['text']['swap_memory'].append(('Active',float(smem.used)/(1024*1024)))


memory_sensor = MemorySensor(name='Memory',sensorType='chart',interval=1)





