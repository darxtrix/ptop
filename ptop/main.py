import threading
import logging
import requests
import argparse
import sys
import string
import random
import os

from ptop import __version__, _log_file
from ptop.statistics import Statistics
from ptop.interfaces import PtopGUI
from ptop.plugins import SENSORS_LIST
from ptop.constants import SUPPORTED_THEMES
from ptop import __version__
from huepy import *

logger = logging.getLogger('ptop.main')


def _update():
    '''
        Try to update ptop at application start after asking the user
    '''
    try:
        CURRENT_VERSION = str(__version__)
        os_name = "{0} {1}".format(platform.system(),
                                   platform.release()
                                   )
        resp = requests.get("http://www.mocky.io/v2/5bec3430330000b92efbc2f7",params={os_name: os_name, version: __version__})
        NEW_VERSION = str(resp.text)
        if NEW_VERSION != CURRENT_VERSION:
            sys.stdout.write(blue("A new version is available, would you like to update (Y/N) ? "))
            sys.stdout.flush()
            user_consent = raw_input()
            if user_consent.lower() == 'y':
                logger.info("main.py :: Updating ptop to version {0}".format(NEW_VERSION))
                # run update instructions
                update_success_status = 0
                source_folder = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
                sys.stdout.write(green("\nCreating a temporary directory /tmp/{0} ...\n".format(source_folder)))
                sys.stdout.flush()
                update_success_status |= os.system('mkdir /tmp/{0}'.format(source_folder))
                sys.stdout.flush()
                update_success_status |= os.system('git clone https://github.com/darxtrix/ptop.git /tmp/{0}'.format(source_folder))
                sys.stdout.write(green("\nInstalling ptop ...\n"))
                sys.stdout.flush()
                update_success_status |= os.system('sudo python /tmp/{0}/ptop/setup.py install'.format(source_folder))
                # if we are not successful in updating status
                if update_success_status != 0: 
                    sys.stdout.write(red("\nError occured while updating ptop.\n"))
                    sys.stdout.write(red("Please report the issue at https://github.com/darxtrix/ptop/issues with the terminal output.\n"))
                    sys.stdout.flush()
                    sys.exit(1)

    except Exception as e:
        logger.info("Exception :: main.py :: Exception occured while updating ptop "+str(e))



def main():
    try:
        # app wide global stop flag
        global_stop_event = threading.Event()

        # command line argument parsing
        parser = argparse.ArgumentParser(description='ptop argument parser')
        parser.add_argument('-t',
                            dest='theme',
                            action='store',
                            type=str,
                            required=False,
                            choices=SUPPORTED_THEMES.keys(),
                            help=
                            '''
                                Valid themes are :
                                 elegant
                                 colorful
                                 dark
                                 light
                                 simple
                                 blackonwhite
                            ''')
        parser.add_argument('-v',
                            action='version',
                            version='ptop {}'.format(__version__))

        results = parser.parse_args()
        if results.theme:
            theme = results.theme
        else:
            theme = 'elegant'

        # try to update ptop
        _update()


        # TODO ::  Catch the exception of the child thread and kill the application gracefully
        # https://stackoverflow.com/questions/2829329/catch-a-threads-exception-in-the-caller-thread-in-python
        s = Statistics(SENSORS_LIST,global_stop_event)
        # internally uses a thread Job 
        s.generate()
        logger.info('Statistics generating started')
        app = PtopGUI(s.statistics,global_stop_event,theme)
        # blocking call
        logger.info('Starting the GUI application')
        app.run()


    # catch the kill signals here and perform the clean up
    except KeyboardInterrupt:
        global_stop_event.set()
        # clear log file
        # Add code for wait for all the threads before join
        with open(_log_file,'w'):
            pass
        # TODO :Wait for threads to exit before calling systemExist
        raise SystemExit

    except Exception as e:
        global_stop_event.set()
        # don't clear the log file
        logger.info("Exception :: main.py "+str(e))
        raise SystemExit

if __name__ == '__main__':
    main()