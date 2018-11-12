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

        parser.add_argument('-cpu',
                            dest='cpu',
                            action='store',
                            type=float,
                            required=False,
                            help=
                            '''
                                Input sensor
        						update interval in
        						milli seconds less than 1000.
        						For example 500
                            ''')

        parser.add_argument('-disk',
                            dest='disk',
                            action='store',
                            type=float,
                            required=False,
                            help=
                            '''
                                Input sensor
        						update interval in
        						milli seconds less than 1000.
        						For example 500
                            ''')

        parser.add_argument('-mem',
                            dest='mem',
                            action='store',
                            type=float,
                            required=False,
                            help=
                            '''
                                Input sensor
        						update interval in
        						milli seconds less than 1000.
        						For example 500
                            ''')

        parser.add_argument('-proc',
                            dest='proc',
                            action='store',
                            type=float,
                            required=False,
                            help=
                            '''
                                Input sensor
        						update interval in
        						milli seconds less than 1000.
        						For example 500
                            ''')

        parser.add_argument('-sys',
                            dest='sys',
                            action='store',
                            type=float,
                            required=False,
                            help=
                            '''
                                Input sensor
        						update interval in
        						milli seconds less than 1000.
        						For example 500
                            ''')
        
        parser.add_argument('-v',
                            action='version',
                            version='ptop {}'.format(__version__))

        results = parser.parse_args()

        if results.theme:
            theme = results.theme
        else:
            theme = 'elegant'

        if results.cpu:
            cput = float(results.cpu)
            if cput>1000:
            	cput = 1000
        else:
            cput = 500

        if results.disk:
            diskt = float(results.disk)
            if diskt>1000:
            	diskt = 1000
        else:
            diskt = 500

        if results.mem:
            memt = float(results.mem)
            if memt>1000:
            	memt = 1000
        else:
            memt = 500

        if results.proc:
            proct = float(results.proc)
            if proct>1000:
            	proct = 1000
        else:
            proct = 500

        if results.sys:
            syst = float(results.sys)
            if syst>1000:
            	syst = 1000
        else:
            syst = 500

        sensor_rate = [cput, diskt, memt, proct, syst]
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