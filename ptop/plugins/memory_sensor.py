'''
    Memory sensor plugin

    Generates the memory usage information of the system
'''
from ptop.core import Plugin
import psutil

class MemorySensor(Plugin):
    def __init__(self,**kwargs):
        super(MemorySensor,self).__init__(**kwargs)
        # there will be two parts of the returned value, one will be text and other graph
        # there can be many text (key,value) pairs to display corresponding to each key
        self.currentValue['text'] = { 'memory' : {},'swap_memory' : {}}
        # there will be only one graph info
        self.currentValue['graph'] = {'percentage' : ''}

    # overriding the update method
    def update(self):
        # virtual memory
        vmem = psutil.virtual_memory()
        self.currentValue['text']['memory']['total'] = int(float(vmem.total)/(1024*1024))
        self.currentValue['text']['memory']['active'] = int(float(vmem.active)/(1024*1024))
        self.currentValue['text']['memory']['percentage'] = int(vmem.percent)
        self.currentValue['graph']['percentage'] = int(vmem.percent)
        # swap memory
        smem = psutil.swap_memory()
        self.currentValue['text']['swap_memory']['total'] = int(float(smem.total)/(1024*1024))
        self.currentValue['text']['swap_memory']['active'] = int(float(smem.used)/(1024*1024))
        
        if smem.total:
            self.currentValue['text']['swap_memory']['percentage'] = int(float(smem.used)/smem.total)*100
        else:
            self.currentValue['text']['swap_memory']['percentage'] = 0


memory_sensor = MemorySensor(name='Memory',sensorType='chart',interval=0.5)





