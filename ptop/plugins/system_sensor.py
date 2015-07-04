'''
    System sensor plugin

    Generates the basic system info
'''
from ptop.core import Plugin
import psutil, socket, getpass
import datetime, time

class SystemSensor(Plugin):
    def __init__(self,**kwargs):
        super(SystemSensor,self).__init__(**kwargs)

    # overriding the update method
    def update(self):
        # only text part for the system info
        self.currentValue['text'] = {}
        # updating values
        self.currentValue['text']['user'] = getpass.getuser()
        self.currentValue['text']['host_name'] = socket.gethostname()
        self.currentValue['text']['running_time'] = datetime.timedelta(seconds=int(time.time() - psutil.boot_time()))

        
system_sensor = SystemSensor(name='System',sensorType='text',interval=1)
        


