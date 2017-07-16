'''
    Graphical User Interface for ptop
'''

import npyscreen, math
import psutil, logging
from drawille import Canvas
from ptop.utils import ThreadJob

# global flags defining actions, would like them to be object vars
TIME_SORT = False
MEMORY_SORT = False

class CustomMultiLineAction(npyscreen.MultiLineAction):
    '''
        Making custom MultiLineAction by adding the handlers
    '''
    def __init__(self,*args,**kwargs):
        super(CustomMultiLineAction,self).__init__(*args,**kwargs)
        self.add_handlers({
            "^N": self.sort_by_memory,
            "^H": self.sort_by_time,
            "^K": self.kill_process,
            "q" : self.quit
        })

        self._logger = logging.getLogger(__name__)

    def sort_by_time(self,*args,**kwargs):
        # fuck .. that's why NPSManaged was required, i.e you can access the app instance within widgets
        global TIME_SORT,MEMORY_SORT
        MEMORY_SORT = False
        TIME_SORT = True

    def sort_by_memory(self,*args,**kwargs):
        global TIME_SORT,MEMORY_SORT
        TIME_SORT = False
        MEMORY_SORT = True

    def kill_process(self,*args,**kwargs):
        pid = self.values[self.cursor_line].split()[1]
        self._logger.info("Terminating process with pid {0}".format(pid))
        target = psutil.Process(int(pid))
        try:
            target.terminate()
            self._logger.info("Terminated process with pid {0}".format(pid))
        except:
            self._logger.info("Not able to terminate process with pid: {0}".format(pid),
                              exc_info=True)


    def quit(self,*args,**kwargs):
        raise KeyboardInterrupt


class MultiLineWidget(npyscreen.BoxTitle):
    '''
        A framed widget containing multiline text
    '''
    _contained_widget = npyscreen.MultiLineEdit


class MultiLineActionWidget(npyscreen.BoxTitle):
    '''
        A framed widget containing multiline text
    '''
    _contained_widget = CustomMultiLineAction


class WindowForm(npyscreen.FormBaseNew):
    '''
        Frameless Form
    '''
    def create(self, *args, **kwargs):
        super(WindowForm, self).create(*args, **kwargs)
    
    def while_waiting(self):
        pass


class PtopGUI(npyscreen.NPSApp):
    '''
        GUI class for ptop
    '''
    def __init__(self,statistics,stop_event,arg):
        self.statistics = statistics
        self.arg = arg
        # Global stop event
        self.stop_event = stop_event
        # thread for updating
        self.update_thread = None
        # Flag to check if user is interacting
        self.is_user_interacting = False

        # main form
        self.window = None 

        # widgets
        self.basic_stats = None
        self.memory_chart = None
        self.cpu_chart = None
        self.processes_table = None
        self.actions = None

        # internal data structures
        # c.set(89,31) -- here the corner point will be set
        # the upper bounds are the excluded points
        self.CHART_HEIGHT = 32
        self.CHART_WIDTH = 90
        self.cpu_array = None
        self.memory_array = None

        # logger
        self._logger = logging.getLogger(__name__)

    def get_theme(self):
        '''
            choose a theme from a given values of themes
            :param arg: Theme to be selected corresponding to the arg
        '''
        self.themes = {
            'elegant'      : npyscreen.Themes.ElegantTheme,
            'colorful'     : npyscreen.Themes.ColorfulTheme,
            'simple'       : npyscreen.Themes.DefaultTheme,
            'dark'         : npyscreen.Themes.TransparentThemeDarkText,
            'light'        : npyscreen.Themes.TransparentThemeLightText,
            'blackonwhite' : npyscreen.Themes.BlackOnWhiteTheme
        }
        return self.themes[self.arg]

    def draw_chart(self,canvas,y,chart_type):
        '''
            :param y: The next height to draw
            :param canvas: The canvas on which to draw
            :param chart_type: cpu/memory
        '''
        if chart_type == 'cpu':
            chart_array = self.cpu_array
        else:
            chart_array = self.memory_array
        
        for i in range(self.CHART_WIDTH):
            if i >= 2:
                chart_array[i-2] = chart_array[i]
        # width of each peak is 2 units
        chart_array[self.CHART_WIDTH-1] = y
        chart_array[self.CHART_WIDTH-2] = y

        for x in xrange(0,self.CHART_WIDTH):
            for y in xrange(self.CHART_HEIGHT,self.CHART_HEIGHT-chart_array[x],-1):
                canvas.set(x,y)

        return canvas.frame(0,0,self.CHART_WIDTH,self.CHART_HEIGHT)

    def while_waiting(self):
        '''
            called periodically when user is not pressing any key
        '''
        if not self.update_thread:
            t = ThreadJob(self.update,self.stop_event,1)
            self.update_thread = t
            self.update_thread.start()
            self._logger.info('Started GUI update thread')

    def update(self):
        '''
            Update the form in background, this is called inside the ThreadJob 
            and will continue getting called once started
        '''
                # get the information
        try:
            disk_info = self.statistics['Disk']['text']['/']
            swap_info = self.statistics['Memory']['text']['swap_memory']
            memory_info = self.statistics['Memory']['text']['memory']
            self._logger.info(memory_info)
            processes_info = self.statistics['Process']['text']
            system_info = self.statistics['System']['text']
            cpu_info = self.statistics['CPU']['graph']

            # overview 
            row1 = "Disk Usage (/) {4}{0: <6}/{1: >6} MB{4}{2: >2} %{5}Processes{4}{3: <8}".format(disk_info["used"],
                                                                                                   disk_info["total"],
                                                                                                   disk_info["percentage"],
                                                                                                   processes_info["running_processes"],
                                                                                                   " "*int(4*self.X_SCALING_FACTOR),
                                                                                                   " "*int(9*self.X_SCALING_FACTOR))

            row2 = "Swap Memory    {4}{0: <6}/{1: >6} MB{4}{2: >2} %{5}Threads  {4}{3: <8}".format(swap_info["active"],
                                                                                                   swap_info["total"],
                                                                                                   swap_info["percentage"],
                                                                                                   processes_info["running_threads"],
                                                                                                   " "*int(4*self.X_SCALING_FACTOR),
                                                                                                   " "*int(9*self.X_SCALING_FACTOR))

            row3 = "Main Memory    {4}{0: <6}/{1: >6} MB{4}{2: >2} %{5}Boot Time{4}{3: <8}".format(memory_info["active"],
                                                                                                   memory_info["total"],
                                                                                                   memory_info["percentage"],
                                                                                                   system_info['running_time'],
                                                                                                   " "*int(4*self.X_SCALING_FACTOR),
                                                                                                   " "*int(9*self.X_SCALING_FACTOR))

            self.basic_stats.value = row1 + '\n' + row2 + '\n' + row3
            self.basic_stats.display()

            ### cpu_usage chart
            cpu_canvas = Canvas()
            next_peak_height = int(math.ceil((float(cpu_info['percentage'])/100)*self.CHART_HEIGHT))
            self.cpu_chart.value = (self.draw_chart(cpu_canvas,next_peak_height,'cpu'))
            self.cpu_chart.display()

            ### memory_usage chart
            memory_canvas = Canvas()
            next_peak_height = int(math.ceil((float(memory_info['percentage'])/100)*self.CHART_HEIGHT))
            self.memory_chart.value = self.draw_chart(memory_canvas,next_peak_height,'memory')
            self.memory_chart.display()

            ### processes_table
            processes_table = self.statistics['Process']['table']

            # check sorting flags
            if MEMORY_SORT:
                sorted_table = sorted(processes_table,key=lambda k:k['memory'],reverse=True)
            elif TIME_SORT:
                sorted_table = sorted(processes_table,key=lambda k:k['rawtime'],reverse=True)
            else:
                sorted_table = processes_table

            # to keep things pre computed
            temp_list = []
            for proc in sorted_table:
                if proc['user'] == system_info['user']:
                    temp_list.append("{0: <30} {1: >5}{5}{2: <10}{5}{3}{5}{4: >6.2f} % \
                    ".format( (proc['name'][:25] + '...') if len(proc['name']) > 25 else proc['name'],
                               proc['id'],
                               proc['user'],
                               proc['time'],
                               proc['memory'],
                               " "*int(5*self.X_SCALING_FACTOR))
                    )
            self.processes_table.entry_widget.values = temp_list
            self.processes_table.display()

        # catch the fucking KeyError caused to c
        # cumbersome point of reading the stats data structures
        except KeyError:
            self._logger.info("Not able to read the stats",exc_info=True)

    def main(self):
        npyscreen.setTheme(self.get_theme())

        # time(ms) to wait for user interactions
        self.keypress_timeout_default = 10

        # setting the main window form
        self.window = WindowForm(parentApp=self,
                                 name="ptop[http://darxtrix.in/ptop]")

        self._logger.info("Detected terminal size to be {0}".format(self.window.curses_pad.getmaxyx()))

        max_y,max_x = self.window.curses_pad.getmaxyx()

        # Minimum terminal size should be used for scaling
        # $ tput cols & $ tput lines
        self.Y_SCALING_FACTOR = float(max_y)/27
        self.X_SCALING_FACTOR = float(max_x)/104

        #####      Overview widget     #######

        OVERVIEW_WIDGET_REL_X = 1
        OVERVIEW_WIDGET_REL_Y = 1
        OVERVIEW_WIDGET_HEIGHT = int(math.ceil(5*self.Y_SCALING_FACTOR))
        OVERVIEW_WIDGET_WIDTH = int(100*self.X_SCALING_FACTOR)
        self.basic_stats = self.window.add(MultiLineWidget,
                                           name="Overview",
                                           relx=OVERVIEW_WIDGET_REL_X,
                                           rely=OVERVIEW_WIDGET_REL_Y,
                                           max_height=OVERVIEW_WIDGET_HEIGHT,
                                           max_width=OVERVIEW_WIDGET_WIDTH
                                           )
        self._logger.info("Overview information box drawn, x1 {0} x2 {1} y1 {2} y2 {3}".format(OVERVIEW_WIDGET_REL_X,
                                                                                               OVERVIEW_WIDGET_REL_X+OVERVIEW_WIDGET_WIDTH,
                                                                                               OVERVIEW_WIDGET_REL_Y,
                                                                                               OVERVIEW_WIDGET_REL_Y+OVERVIEW_WIDGET_HEIGHT)
                                                                                               )
        self.basic_stats.value = ""
        self.basic_stats.entry_widget.editable = False


        ######    Memory Usage widget  #########

        MEMORY_USAGE_WIDGET_REL_X = 1
        MEMORY_USAGE_WIDGET_REL_Y = int(math.ceil(5*self.Y_SCALING_FACTOR)+1)
        MEMORY_USAGE_WIDGET_HEIGHT = int(10*self.Y_SCALING_FACTOR)
        MEMORY_USAGE_WIDGET_WIDTH = int(50*self.X_SCALING_FACTOR)
        self.memory_chart = self.window.add(MultiLineWidget,
                                            name="Memory Usage",
                                            relx=MEMORY_USAGE_WIDGET_REL_X,
                                            rely=MEMORY_USAGE_WIDGET_REL_Y,
                                            max_height=MEMORY_USAGE_WIDGET_HEIGHT,
                                            max_width=MEMORY_USAGE_WIDGET_WIDTH
                                            )
        self._logger.info("Memory Usage information box drawn, x1 {0} x2 {1} y1 {2} y2 {3}".format(MEMORY_USAGE_WIDGET_REL_X,
                                                                                                   MEMORY_USAGE_WIDGET_REL_X+MEMORY_USAGE_WIDGET_WIDTH,
                                                                                                   MEMORY_USAGE_WIDGET_REL_Y,
                                                                                                   MEMORY_USAGE_WIDGET_REL_Y+MEMORY_USAGE_WIDGET_HEIGHT)
                                                                                                   )
        self.memory_chart.value = ""
        self.memory_chart.entry_widget.editable = False


        ######    CPU Usage widget  #########

        CPU_USAGE_WIDGET_REL_X = int(52*self.X_SCALING_FACTOR)
        CPU_USAGE_WIDGET_REL_Y = int(math.ceil(5*self.Y_SCALING_FACTOR)+1)
        CPU_USAGE_WIDGET_HEIGHT = int(10*self.Y_SCALING_FACTOR)
        CPU_USAGE_WIDGET_WIDTH = int(49*self.X_SCALING_FACTOR)
        self.cpu_chart = self.window.add(MultiLineWidget,
                                         name="CPU Usage",
                                         relx=CPU_USAGE_WIDGET_REL_X,
                                         rely=CPU_USAGE_WIDGET_REL_Y,
                                         max_height=CPU_USAGE_WIDGET_HEIGHT,
                                         max_width=CPU_USAGE_WIDGET_WIDTH
                                         )
        self._logger.info("CPU Usage information box drawn, x1 {0} x2 {1} y1 {2} y2 {3}".format(CPU_USAGE_WIDGET_REL_X,
                                                                                                CPU_USAGE_WIDGET_REL_X+CPU_USAGE_WIDGET_WIDTH,
                                                                                                CPU_USAGE_WIDGET_REL_Y,
                                                                                                CPU_USAGE_WIDGET_REL_Y+CPU_USAGE_WIDGET_HEIGHT)
                                                                                                )
        self.cpu_chart.value = "" 
        self.cpu_chart.entry_widget.editable = False


        ######    Processes Info widget  #########

        PROCESSES_INFO_WIDGET_REL_X = 1
        PROCESSES_INFO_WIDGET_REL_Y = int(16*self.Y_SCALING_FACTOR)
        PROCESSES_INFO_WIDGET_HEIGHT = int(8*self.Y_SCALING_FACTOR)
        PROCESSES_INFO_WIDGET_WIDTH = int(100*self.X_SCALING_FACTOR)
        self.processes_table = self.window.add(MultiLineActionWidget,
                                               name="Processes",
                                               relx=PROCESSES_INFO_WIDGET_REL_X,
                                               rely=PROCESSES_INFO_WIDGET_REL_Y,
                                               max_height=PROCESSES_INFO_WIDGET_HEIGHT,
                                               max_width=PROCESSES_INFO_WIDGET_WIDTH
                                               )
        self._logger.info("Processes information box drawn, x1 {0} x2 {1} y1 {2} y2 {3}".format(PROCESSES_INFO_WIDGET_REL_X,
                                                                                                PROCESSES_INFO_WIDGET_REL_X+PROCESSES_INFO_WIDGET_WIDTH,
                                                                                                PROCESSES_INFO_WIDGET_REL_Y,
                                                                                                PROCESSES_INFO_WIDGET_REL_Y+PROCESSES_INFO_WIDGET_HEIGHT)
                                                                                                )
        self.processes_table.entry_widget.values = []
        self.processes_table.entry_widget.scroll_exit = False
        self.cpu_chart.entry_widget.editable = False


        ######   Actions widget  #########

        ACTIONS_WIDGET_REL_X = 1
        ACTIONS_WIDGET_REL_Y = int(24*self.Y_SCALING_FACTOR)
        self.actions = self.window.add(npyscreen.FixedText,
                                       relx=ACTIONS_WIDGET_REL_X,
                                       rely=ACTIONS_WIDGET_REL_Y
                                       )
        self._logger.info("Actions box drawn, x1 {0} y1 {1}".format(ACTIONS_WIDGET_REL_X,  
                                                                    ACTIONS_WIDGET_REL_Y)
                                                                    )
        self.actions.value = "^K : Kill     ^N : Sort by Memory     ^H : Sort by Time      g : top    q : quit "
        self.actions.display()
        self.actions.editable = False

        ######   CPU/Memory charts  #########

        # self.CHART_WIDTH = int(self.CHART_WIDTH*self.X_SCALING_FACTOR)
        # self.CHART_HEIGHT = int(self.CHART_HEIGHT*self.Y_SCALING_FACTOR)
        self.CHART_HEIGHT = int(math.floor((CPU_USAGE_WIDGET_HEIGHT-2)*4))
        self.CHART_WIDTH = int(math.floor((CPU_USAGE_WIDGET_WIDTH-2)*2))
        # self.CHART_HEIGHT = max_y
        # self.CHART_WIDTH = max_x
        self._logger.info("Memory and CPU charts dimension, width {0} height {1}".format(self.CHART_WIDTH,
                                                                                         self.CHART_HEIGHT)
                                                                                         )

        # fix for index error
        self.cpu_array = [0]*self.CHART_WIDTH
        self.memory_array = [0]*self.CHART_WIDTH

        # add subwidgets to the parent widget
        self.window.edit()


