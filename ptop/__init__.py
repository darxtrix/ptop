import sys,os
import logging

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