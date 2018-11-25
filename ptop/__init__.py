# -*- coding: utf-8 -*-
'''
    ptop(http://github.com/darxtrix)

    Author : Ankush Sharma (http://darxtrix.in)
    Licence : MIT © 2015
'''
import sys,os
import logging

__dir__ = os.path.dirname(os.path.abspath(__file__))

__version__ = '1.1'

# setting the config
_log_file = os.path.join(os.path.expanduser('~'),'.ptop.log')
 # create file if not exists
if not os.path.exists(_log_file):
    open(_log_file,'w').close()

logging.basicConfig(filename=_log_file,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger('ptop_logger')

sys.path.append( os.path.join(
    (os.path.dirname(__file__)),
    'ptop'
))