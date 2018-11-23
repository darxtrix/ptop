'''
    Classes to provide the functionality of updating the stats off the main thread,
    run things as a thread job
'''

import threading,logging

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
        self.logger = logging.getLogger(__name__)
        super(ThreadJob,self).__init__()

    def run(self):
        self.logger.info('Started thread job for the sensor {0}'.format(self.callback))
        while not self.event.wait(self.interval):
            self.callback()
        self.logger.info("Finished thread job {0}".format(self.callback))
