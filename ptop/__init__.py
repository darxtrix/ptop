# -*- coding: utf-8 -*-
'''
    ptop(http://github.com/black-perl)

    Author : Ankush Sharma (http://black-perl.me)
    Licence : MIT © 2015
'''
import sys,os
import logging

__version__ = '0.0.6'

__dir__ = os.path.dirname(__file__)

# setting the config
_log_file = os.path.join(os.path.expanduser('~'),'.ptop.log')
 # create file if not exists
if not os.path.exists(_log_file):
    open(_log_file,'w').close()

logging.basicConfig(filename=_log_file,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

logger = logging.getLogger('ptop_logger')

sys.path.append( os.path.join(
    (os.path.dirname(__file__)),
    'ptop'
))