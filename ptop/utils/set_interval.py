'''
    Utility function setInterval for invoking a function again and again 
    after a particular interval of time
'''

import threading

def setInterval(func,time):
    '''calls the supplied function after the supplied time in seconds

    :param func: Function to invoke
    :param time: Time interval
    :type func: Function
    :type time: Integer
    '''
    e = threading.Event()
    while not e.wait(time):
        func()