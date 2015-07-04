'''
    Process sensor plugin

    Generates the running processes information
'''
from ptop.core import Plugin
import psutil
import datetime, time

class ProcessSensor(Plugin):
    def __init__(self,**kwargs):
        super(ProcessSensor,self).__init__(**kwargs)

    # overriding the upate method
    def update(self):
        # there will be two parts of the returned value, one will be text and other graph
        # there can be many text (key,value) pairs to display corresponding to each key
        self.currentValue['text'] = { 'running_processes' : '','running_threads' : 0}
        # nested structure is used for keeping the info of processes
        self.currentValue['table'] = []
        # flood the data
        thread_count = 0 #keep track number of threads
        proc_count = 0 #keep track of number of processes
        for proc in psutil.process_iter():
            # info of a single process
            proc_info = {}
            proc_info['id'] = proc.pid
            proc_info['name'] = proc.name
            # getting more info about the process
            p = psutil.Process(proc.pid)
            proc_info['user'] = p.username()
            proc_info['time'] = datetime.timedelta(seconds=(time.time() - p.create_time()))
            proc_info['cpu'] = p.cpu_percent()
            proc_info['memory'] = p.memory_percent()
            proc_info['command'] = ' '.join(p.cmdline())
            # increamenting the thread_count and proc_count
            thread_count += p.num_threads()
            proc_count += 1
            # recording the info
            self.currentValue['table'].append(proc_info)

        self.currentValue['text']['running_processes'] = str(proc_count)
        self.currentValue['text']['running_threads'] = str(thread_count)


process_sensor = ProcessSensor(name='Process',sensorType='table',interval=0.5)



