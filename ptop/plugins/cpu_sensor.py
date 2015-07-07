'''
    CPU sensor plugin

    Generates the CPU usage stats
'''
from ptop.core import Plugin
import psutil

class CPUSensor(Plugin):
    def __init__(self,**kwargs):
        super(CPUSensor,self).__init__(**kwargs)
        # there will be two parts of the returned value, one will be text and other graph
        # there can be many text (key,value) pairs to display corresponding to each key
        self.currentValue['text'] = {}
        # there will be one averaged value
        self.currentValue['graph'] = {'percentage' : ''}

    # overriding the update method
    def update(self):
        # cpu usage
        cpu_usage = psutil.cpu_percent(percpu=True)
        num_cores = len(cpu_usage)
        self.currentValue['text']['number_of_cores'] = str(num_cores)
        for ctr in range(num_cores):
            self.currentValue['text']['core{0}'.format(ctr+1)] = cpu_usage[ctr]
        # average cpu usage
        self.currentValue['graph']['percentage'] = sum(cpu_usage)/num_cores


cpu_sensor = CPUSensor(name='CPU',sensorType='chart',interval=0.5)


