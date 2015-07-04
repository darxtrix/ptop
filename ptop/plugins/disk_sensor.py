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
        # there can be many text (key,value) pairs to display corresponding to each key
        self.currentValue['text'] = {'/' : []}
        # no graph part will be there
        disk_usage = psutil.disk_usage('/')
        self.currentValue['text']['/'].append(('Total',float(disk_usage.total)/(1024*1024)))
        self.currentValue['text']['/'].append(('Used',float(disk_usage.used)/(1024*1024)))
        self.currentValue['text']['/'].append(('Percent',int(disk_usage.percent)))


disk_sensor = DiskSensor(name='Disk',sensorType='text',interval=1)
