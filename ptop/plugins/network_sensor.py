'''
    Network sensor plugin

    Generates the Network usage stats
'''
from ptop.core import Plugin
import psutil

class NetworkSensor(Plugin):
    def __init__(self,**kwargs):
        super(NetworkSensor,self).__init__(**kwargs)
        # there will be two parts of the returned value, one will be text and other graph
        # there can be many text (key,value) pairs to display corresponding to each key
        self.currentValue['text'] = {}

    # overriding the update method
    def update(self):
        # network usage
        network_usage = psutil.net_io_counters()
        num_cores = len(network_usage)
        self.currentValue['text']['sent'] = str(round(network_usage[0]*0.000001,2))
        self.currentValue['text']['received'] = str(round(network_usage[1]*0.000001,2))

network_sensor = NetworkSensor(name='Network',sensorType='chart',interval=0.5)