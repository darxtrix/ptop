#-*- coding: utf-8 -*-
'''
    Temperature sensor plugin

    Generates the Temperature usage stats
'''
from ptop.core import Plugin
import psutil

class TemperatureSensor(Plugin):
    def __init__(self,**kwargs):
        super(TemperatureSensor,self).__init__(**kwargs)
        self.currentValue['text'] = {}

    # overriding the update method
    def update(self):
        # temperature usage
        temperature = psutil.sensors_temperatures(fahrenheit=False)
        cpu_temp = temperature["coretemp"][0].current
        # update the temperature
        self.currentValue['text']['temp'] = str(cpu_temp)+'°C'


temperature_sensor = TemperatureSensor(name='Temperature',sensorType='text',interval=0.5)