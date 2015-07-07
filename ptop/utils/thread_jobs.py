'''
    Classes to provide the functionality of updating the stats off the main thread,
    run things as a thread job
'''

import threading

class ThreadJob(threading.Thread):
    def __init__(self,callback,event,interval):
        '''runs the callback function after interval seconds

        :param callback:  callback function to invoke
        :param event: external event for controlling the update operation
        :param interval: time in seconds after which are required to fire the callback
        :type callback: function
        :type interval: int
        '''
        self.callback = callback
        self.event = event
        self.interval = interval
        super(ThreadJob,self).__init__()

    def run(self):
        while not self.event.wait(self.interval):
            self.callback()