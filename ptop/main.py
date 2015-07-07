import threading, logging
import argparse
from ptop import __version__, _log_file
from ptop.statistics import Statistics
from ptop.interfaces import PtopGUI
from ptop.plugins import SENSORS_LIST

logger = logging.getLogger('ptop.main')

def main():
    try:
        # command line argument parsing
        parser = argparse.ArgumentParser(description='ptop argument parser')
        parser.add_argument('-t',
                            dest='theme',
                            action='store',
                            type=str,
                            required=False,
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
            theme = 'dark'
        # app wide global stop flag
        global_stop_event = threading.Event()

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
        with open(_log_file,'w'):
            pass
        raise SystemExit



if __name__ == '__main__':
    main()