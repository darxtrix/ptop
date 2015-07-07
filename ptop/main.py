import threading
from ptop.statistics import Statistics
from interfaces import PtopGUI
from plugins import SENSORS_LIST

def main():
    try:
        # app wide global stop flag
        global_stop_event = threading.Event()

        s = Statistics(SENSORS_LIST,global_stop_event)
        # internally uses a thread Job 
        s.generate()

        app = PtopGUI(s.statistics,global_stop_event)
        # blocking call
        app.run()

    # catch the kill signals here and perform the clean up
    except KeyboardInterrupt:
        global_stop_event.set()
        raise SystemExit



if __name__ == '__main__':
    main()