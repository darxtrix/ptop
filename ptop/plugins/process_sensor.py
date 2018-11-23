'''
    Process sensor plugin

    Generates the running processes information
'''
import psutil, getpass
import datetime, time, logging
from ptop.core import Plugin
from ptop.constants import (PRIVELAGED_USERS, 
                            INVALID_PROCESSES,
                            SYSTEM_USERS
                            )


class ProcessSensor(Plugin):
    def __init__(self,**kwargs):
        super(ProcessSensor,self).__init__(**kwargs)
        # there will be two parts of the returned value, one will be text and other graph
        # there can be many text (key,value) pairs to display corresponding to each key
        self.currentValue['text'] = { 'running_processes' : 0,'running_threads' : 0}
        # nested structure is used for keeping the info of processes
        self.currentValue['table'] = []
        self._currentSystemUser = getpass.getuser()
        self._logger = logging.getLogger(__name__)

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
            '''
             Getting more info about the processes
             In case of MacOSx all of the processes that are returned by psutil.process_iter()
             for all the users(root, adminstrator, normal user)
             There should be a check for the current user is root or not 
             because getting further process info for root processes as a normal 
             user will give Permission Denied #10
            '''
            p = psutil.Process(proc.pid)
            proc_info['user'] = p.username()
            try:
                if ((proc_info['user'] == self._currentSystemUser) or (self._currentSystemUser in PRIVELAGED_USERS)) \
                        and p.status() not in INVALID_PROCESSES:
                    delta = datetime.timedelta(seconds=(time.time() - p.create_time()))
                    proc_info['rawtime'] = time.time() - p.create_time()
                    proc_info['time'] =  self.format_time(delta)
                    proc_info['command'] = ' '.join(p.cmdline())
                    # incrementing the thread_count and proc_count
                    thread_count += p.num_threads()
                    proc_info['cpu'] = p.cpu_percent()
                    proc_info['memory'] = round(p.memory_percent(),2)
                    # Add information of the local ports used by the process
                    proc_info['local_ports'] = [x.laddr[1] for x in p.connections()]
                    # Add information of the open files by the process
                    proc_info['open_files'] = p.open_files()
                    proc_count += 1
                    # recording the info
                    proc_info_list.append(proc_info)
                    # Aggregate all the system users
                    if proc_info['user'] not in SYSTEM_USERS:
                        SYSTEM_USERS.append(proc_info['user'])
            except:
                '''
                    In case ptop does not have privelages to access info for some of the processes
                    just log them and don't show them in the processes table
                '''
                self._logger.info('''Not able to get info for process {0} with status {1} invoked by user {2}, ptop
                                   is invoked by the user {3}'''.format(str(p.pid),
                                                                        p.status(),
                                                                        p.username(),
                                                                        self._currentSystemUser
                                                                        ),
                                                                        exc_info=True)

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