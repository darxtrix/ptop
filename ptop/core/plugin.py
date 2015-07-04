'''
    ptop.core.plugin
    
    This module define the BaseClass for plugin. It defines the basic rules that are to be followed by a new plugin.
'''

class Plugin(object):
    ''' 
        Base Plugin class
    '''
    def __init__(self,name,sensorType,interval):
        '''creates an instance of the class

        Initialize the instance of a Plugin class.

        :param name: Name of the plugin
        :param sensorType: How to render the plugin on the screen
        :param interval: The interval after which to update the stats
        :type sensorType: Chart or Table
        :rtype: Instance of Plugin class
        '''
        self.name = name
        self.type = sensorType
        self.interval = interval
        self.currentValue = {}

    def update(self):
        '''updates the plugin currentValue

        :rtype: dict 
        '''
        # to be overrided by the child class

    @property
    def text_info(self):
        '''return the text part of the currentValue

        :rtype: dict
        '''
        return self.currentValue['text']

    @property
    def graph_info(self):
        '''return the graph part of the currentValue

        :rtype: dict
        '''
        try:
            return self.currentValue['graph']
        except KeyError:
            raise Exception('The plugin does not have any graphical information')

    @property
    def table_info(self):
        '''return the table part of the currentValue

        :rtype: list
        '''
        try:
            return self.currentValue['table']
        except KeyError:
            raise Exception('The plugin does not have any tabular information')

