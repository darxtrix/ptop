from ptop.statistics import Statistics
from interfaces import PtopGUI
from plugins import SENSORS_LIST

def main():
    s = Statistics(SENSORS_LIST)
    # internally uses a thread Job 
    s.generate()
    app = PtopGUI(s.statistics)
    app.run()


if __name__ == '__main__':
    main()