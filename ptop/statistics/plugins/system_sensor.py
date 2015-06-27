'''
    System sensor plugin

    Generates the basic system info
'''
from ptop.core import Plugin
import psutil, socket, getpass
import datetime

class SystemSensor(Plugin):
    def __init__(self,**kwargs):
        super(SystemSensor,self).__init__(**kwargs)

    # overriding the update method
    def update(self):
        system_info = {}
        # only text part for the system info
        system_info['text'] = {}
        # updating values
        system_info['text']['user'] = getpass.get_user()
        system_info['text']['host_name'] = socket.gethostname()
        system_info['text']['running_time'] = datetime.timedelta(seconds=psutil.boot_time())
        # setting the value
        self.currentValue = system_info['text']

        
        


