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
        self._sent_bytes_in_mb = 0
        self._received_bytes_in_mb = 0

    # overriding the update method
    def update(self):
        # network usage
        network_usage = psutil.net_io_counters()
        current_sent_bytes_in_mb = round(network_usage[0]*0.000001,4)
        current_received_bytes_in_mb = round(network_usage[1]*0.000001,4)
        # update the network speeds
        self.currentValue['text']['upload_speed_in_mb'] = str(round(current_sent_bytes_in_mb-self._sent_bytes_in_mb,2))
        self.currentValue['text']['download_speed_in_mb'] = str(round(current_received_bytes_in_mb-self._received_bytes_in_mb,2))
        self._sent_bytes_in_mb = current_sent_bytes_in_mb
        self._received_bytes_in_mb = current_received_bytes_in_mb


network_sensor = NetworkSensor(name='Network',sensorType='chart',interval=1)