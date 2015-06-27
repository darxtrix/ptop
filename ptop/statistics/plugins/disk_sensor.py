'''
    Disk Sensor Plugin
'''
from ptop.core import Plugin
import psutil

class DiskSensor(Plugin):
    def __init__(self,**kwargs):
        super(DiskSensor,self).__init__(**kwargs)

    # overriding the update method
    def update(self):
        disk_info = {}
        # there can be many text (key,value) pairs to display corresponding to each key
        disk_info['text'] = {'/' : []}
        # no graph part will be there
        disk_usage = psutil.disk_usage('/')
        disk_info['text']['/'].append(('Total',float(disk_usage.total)/1024*1024))
        disk_info['text']['/'].append(('Used',float(disk_usage.used)/1024*1024))
        disk_info['text']['/'].append(('Percent',int(disk_usage.percent)))
        # update the curentValue
        self.currentValue = disk_info
