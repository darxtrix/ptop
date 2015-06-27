'''
    Module ptop.statistics

    Generate stats by using the plugins in the ../plugins directory and gather the common info in one section so as 
    to render the info in the GUI
'''

import socket, getpass, os

class Statistics:
    def __init__(self):
        '''
            Record keeping for primitive system parameters
        '''
        self.plugin_dir = os.path.join(os.path.dirname(__file__),'plugins') #plugins directory
        self.plugins = [ a.split('.py')[0] for a in next(os.walk(self.plugin_dir))[2] ] #plugins list

    def generate(self):
        '''
            Generate the stats using the plugins list periodically
        '''
        

