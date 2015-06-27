'''
    ptop.core.plugin
    
    This module define the BaseClass for plugin. It defines the basic rules that are to be followed by a new plugin.
'''

class Plugin:
    ''' 
        Base Plugin class
    '''
    def __init__(self,name,sensorType,interval,initialValue):
        '''creates an instance of the class

        Initialize the instance of a Plugin class.

        :param name: Name of the plugin
        :param sensorType: How to render the plugin on the screen
        :param interval: The interval after which to update the stats
        :param initialValue: The initial value to be set for the plugin
        :type sensorType: Chart or Table
        :rtype: Instance of Plugin class
        '''
        self.name = name
        self.type = sensorType
        self.interval = interval
        self.currentValue = initialValue

    def update(self):
        '''updates the plugin value

        :rtype: dict 
        '''
        # to be overrided by child class
