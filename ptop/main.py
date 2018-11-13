import threading, logging
import argparse
from ptop import __version__, _log_file
from ptop.statistics import Statistics
from ptop.interfaces import PtopGUI
from ptop.plugins import SENSORS_LIST
from ptop.constants import SUPPORTED_THEMES

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

        parser.add_argument('-csrt',
                            dest='csrt',
                            action='store',
                            type=float,
                            required=False,
                            help=
                            '''
                                CPU sensor response time;
        						update interval in
        						milli seconds less than 1000.
        						For example 500
                            ''')

        parser.add_argument('-dsrt',
                            dest='dsrt',
                            action='store',
                            type=float,
                            required=False,
                            help=
                            '''
                                Disk sensor response time;
                                Input sensor
        						update interval in
        						milli seconds less than 1000.
        						For example 500
                            ''')

        parser.add_argument('-msrt',
                            dest='msrt',
                            action='store',
                            type=float,
                            required=False,
                            help=
                            '''
                                Memory sensor response time;
                                Input sensor
        						update interval in
        						milli seconds less than 1000.
        						For example 500
                            ''')

        parser.add_argument('-psrt',
                            dest='psrt',
                            action='store',
                            type=float,
                            required=False,
                            help=
                            '''
                                Process sensor response time;
                                Input sensor
        						update interval in
        						milli seconds less than 1000.
        						For example 500
                            ''')

        parser.add_argument('-ssrt',
                            dest='ssrt',
                            action='store',
                            type=float,
                            required=False,
                            help=
                            '''
                                System sensor response time;
                                Input sensor
        						update interval in
        						milli seconds less than 1000.
        						For example 500
                            ''')
        
        parser.add_argument('-v',
                            action='version',
                            version='ptop {}'.format(__version__))

        results = parser.parse_args()

        theme = (results.theme if results.theme else 'elegant')
        csrt = (results.csrt if results.csrt else 1000)
        csrt = (1000 if csrt>1000 else csrt)
        dsrt = (results.dsrt if results.dsrt else 1000)
        dsrt = (1000 if dsrt>1000 else dsrt)
        msrt = (results.msrt if results.msrt else 1000)
        msrt = (1000 if msrt>1000 else msrt)
        psrt = (results.psrt if results.psrt else 1000)
        psrt = (1000 if psrt>1000 else psrt)
        ssrt = (results.ssrt if results.ssrt else 1000)
        ssrt = (1000 if ssrt>1000 else ssrt)
    
        srt = [csrt, dsrt, msrt, psrt, ssrt]
        sensor_rate = {SENSORS_LIST[i]: srt[i] for i in range(len(SENSORS_LIST))}
        
        # app wide global stop flag
        global_stop_event = threading.Event()

        s = Statistics(SENSORS_LIST,global_stop_event,sensor_rate)
        # internally uses a thread Job 
        s.generate()
        logger.info('Statistics generating started')
        app = PtopGUI(s.statistics,global_stop_event,theme,sensor_rate)
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



if __name__ == '__main__':
    main()
