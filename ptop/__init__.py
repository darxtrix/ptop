# -*- coding: utf-8 -*-
'''
    ptop(http://github.com/black-perl)

    Author : Ankush Sharma (http://black-perl.me)
    Licence : MIT © 2015
'''
import sys,os
import logging

__version__ = '0.0.2'

# setting the config
logging.basicConfig(filename='./logs/ptop.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

logger = logging.getLogger('ptop_logger')

sys.path.append( os.path.join(
    (os.path.dirname(__file__)),
    'ptop'
))