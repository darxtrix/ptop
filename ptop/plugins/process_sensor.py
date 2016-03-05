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
        # there will be two parts of the returned value, one will be text and other graph
        # there can be many text (key,value) pairs to display corresponding to each key
        self.currentValue['text'] = { 'running_processes' : 0,'running_threads' : 0}
        # nested structure is used for keeping the info of processes
        self.currentValue['table'] = []

    def format_time(self, d):
        ret = '{0} day{1} '.format(d.days, ' s'[d.days > 1]) if d.days else ''
        h = d.seconds // 3600
        s = d.seconds - 3600 * h
        m = s // 60
        s -= m * 60
        return ret + '{0:2d}:{1:02d}:{2:02d}'.format(h, m, s)

    # overriding the upate method
    def update(self):
        # flood the data
        thread_count = 0 #keep track number of threads
        proc_count = 0 #keep track of number of processes
        proc_info_list = []
        for proc in psutil.process_iter():
            # info of a single process
            proc_info = {}
            proc_info['id'] = proc.pid
            proc_info['name'] = proc.name()
            # getting more info about the process
            p = psutil.Process(proc.pid)
            proc_info['user'] = p.username()
            delta = datetime.timedelta(seconds=(time.time() - p.create_time()))
            proc_info['rawtime'] = delta
            proc_info['time'] =  self.format_time(delta)
            proc_info['cpu'] = p.cpu_percent()
            proc_info['memory'] = round(p.memory_percent(),2)
            proc_info['command'] = ' '.join(p.cmdline())
            # increamenting the thread_count and proc_count
            thread_count += p.num_threads()
            proc_count += 1
            # recording the info
            proc_info_list.append(proc_info)

        # padding time
        time_len = max((len(proc['time']) for proc in proc_info_list))
        for proc in proc_info_list:
            proc['time'] = '{0: >{1}}'.format(proc['time'], time_len)

        self.currentValue['table'] = []
        self.currentValue['table'].extend(proc_info_list)
        self.currentValue['text']['running_processes'] = str(proc_count)
        self.currentValue['text']['running_threads'] = str(thread_count)

# make the process sensor less frequent as it takes more time to fetch info
process_sensor = ProcessSensor(name='Process',sensorType='table',interval=1)



