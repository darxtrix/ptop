import threading, logging
from ptop.statistics import Statistics
from interfaces import PtopGUI
from plugins import SENSORS_LIST

logger = logging.getLogger('ptop.main')

def main():
    try:
        # app wide global stop flag
        global_stop_event = threading.Event()

        s = Statistics(SENSORS_LIST,global_stop_event)
        # internally uses a thread Job 
        s.generate()
        logger.info('Statistics generating started')

        app = PtopGUI(s.statistics,global_stop_event)
        # blocking call
        logger.info('Starting the GUI application')
        app.run()


    # catch the kill signals here and perform the clean up
    except KeyboardInterrupt:
        global_stop_event.set()
        # clear log file
        with open('./logs/ptop.log', 'w'):
            pass
        raise SystemExit



if __name__ == '__main__':
    main()