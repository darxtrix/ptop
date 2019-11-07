#-*- coding: utf-8 -*-
'''
    GPU sensor plugin

    Generates the GPU usage stats
'''
from ptop.core import Plugin
import GPUtil,subprocess

class GPUSensor(Plugin):
    def __init__(self,**kwargs):
        super(GPUSensor,self).__init__(**kwargs)
        # there will be two parts of the returned value, one will be text and other graph
        # there can be many text (key,value) pairs to display corresponding to each key
        self.currentValue['text'] = {'number_of_gpus' : len(GPUtil.getGPUs()), 'temperature' : ''}
        # there will be one averaged value
        self.currentValue['graph'] = {'percentage' : 0}

    # overriding the update method
    def update(self):
        # gpu usage
        gpus = GPUtil.getGPUs()
        num_gpus = len(gpus)
        gpu_usage = [x.load for x in gpus]
        self.currentValue['text']['number_of_gpus'] = num_gpus
        for ctr in range(num_gpus):
            self.currentValue['text']['gpu{0}'.format(ctr+1)] = gpu_usage[ctr]
        #average gpu usage
        if(num_gpus!=0):
            self.currentValue['graph']['percentage'] = (sum(gpu_usage)*100)/num_gpus
            proc = subprocess.Popen('nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader',
                                    stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)
            output,error = proc.communicate()
            temp = output.split()[0]
            self.currentValue['text']['temperature']=temp+'°C'
        else:
            self.currentValue['graph']['percentage'] = 0
        
gpu_sensor = GPUSensor(name='GPU',sensorType='chart',interval=0.5)