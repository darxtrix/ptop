'''
    Graphical User Interface for ptop
'''

import npyscreen, math, drawille
import psutil, logging, weakref
from ptop.utils import ThreadJob
from ptop.constants import SYSTEM_USERS, SUPPORTED_THEMES


# global flags defining actions, would like them to be object vars
TIME_SORT = False
MEMORY_SORT = False
PROCESS_RELEVANCE_SORT = True
PREVIOUS_TERMINAL_WIDTH = None
PREVIOUS_TERMINAL_HEIGHT = None

class ProcessDetailsInfoBox(npyscreen.Popup):
    def create(self,local_ports):
        super(ProcessDetailsInfoBox,self).create()
        self.details_box_heading = self.add(npyscreen.TitleText, name='Ports used by the process',)
        self.details_box = self.add(npyscreen.BufferPager)
        self.details_box.values.extend(local_ports)
        self.details_box.display()

    def adjust_widgets(self):
        pass


class ProcessFilterInputBox(npyscreen.Popup):
    '''
        Helper widget(input-box) that is used for filtering the processes list 
        on the basis of entered filtering string in the widget
    '''
    def create(self):
        super(ProcessFilterInputBox, self).create()
        self.filterbox = self.add(npyscreen.TitleText, name='Filter String:', )
        self.nextrely += 1
        self.statusline = self.add(npyscreen.Textfield, color = 'LABEL', editable = False)
    
    def updatestatusline(self):
        '''
            This updates the status line that displays how many processes in the 
            processes list are matching to the filtering string
        '''
        self.owner_widget._filter = self.filterbox.value
        total_matches = self.owner_widget.filter_processes()
        if self.filterbox.value == None or self.filterbox.value == '':
            self.statusline.value = ''
        elif total_matches == 0: 
            self.statusline.value = '(No Matches)'
        elif total_matches == 1:
            self.statusline.value = '(1 Match)'
        else:
            self.statusline.value = '(%s Matches)' % total_matches
    
    def adjust_widgets(self):
        '''
            This method is called on any text change in filter box.
        '''
        self.updatestatusline()
        self.statusline.display()


class CustomMultiLineAction(npyscreen.MultiLineAction):
    '''
        Making custom MultiLineAction by adding the handlers
    '''
    def __init__(self,*args,**kwargs):
        super(CustomMultiLineAction,self).__init__(*args,**kwargs)
        self.add_handlers({
            "^N" : self.sort_by_memory,
            "^T" : self.sort_by_time,
            "^K" : self.kill_process,
            "^Q" : self.quit,
            "^R" : self.reset,
            "^H" : self.do_process_filtering_work,
            "^F" : self.show_detailed_process_info
        })
        self._filtering_flag = False
        self._logger = logging.getLogger(__name__)
        self._unfiltered_values = None

    def is_filtering_on(self):
        return self._filtering_flag

    def set_unfiltered_values(self, processes_info):
        self._unfiltered_values = processes_info

    def sort_by_time(self,*args,**kwargs):
        # fuck .. that's why NPSManaged was required, i.e you can access the app instance within widgets
        self._logger.info("Sorting the process table by time")
        global TIME_SORT,MEMORY_SORT
        MEMORY_SORT = False
        TIME_SORT = True
        PROCESS_RELEVANCE_SORT = False

    def sort_by_memory(self,*args,**kwargs):
        self._logger.info("Sorting the process table by memory")
        global TIME_SORT,MEMORY_SORT
        TIME_SORT = False
        MEMORY_SORT = True
        PROCESS_RELEVANCE_SORT = False

    def reset(self,*args,**kwargs):
        self._logger.info("Resetting the process table")
        global TIME_SORT, MEMORY_SORT
        TIME_SORT = False
        MEMORY_SORT = False
        PROCESS_RELEVANCE_SORT = True
        self._filtering_flag = False

    def do_process_filtering_work(self,*args,**kwargs):
        '''
            Dynamically instantiate a process filtering box used
            to offload the process filtering work
        '''
        self.process_filtering_helper = ProcessFilterInputBox()
        self.process_filtering_helper.owner_widget = weakref.proxy(self)
        self.process_filtering_helper.display()
        self.process_filtering_helper.edit()

    def show_detailed_process_info(self,*args,**kwargs):
        """
            Display the extra process information. Extra information includes
            open ports and the opened files list
        """
        self._logger.info("Showing process details for the selected process")
        self.process_details_view_helper = ProcessDetailsInfoBox()
        self.process_details_view_helper.owner_widget = weakref.proxy(self)
        self.process_details_view_helper.display()
        self.process_details_view_helper.edit()

    def filter_processes(self):
        '''
            This method is used to filter the processes in the processes table on the 
            basis of the filtering string entered in the filter box
            When the user presses OK in the input box widget the value of the processes 
            table is set to **filtered** processes 
            It returns the count of the processes matched to the filtering string
        '''
        self._logger.info("Filtering processes on the basis of filter : {0}".format(self._filter))
        match_count = 0
        filtered_processes = []
        self._filtering_flag = True
        for val in self._unfiltered_values:
            if self._filter in str.lower(val):
                match_count += 1
                filtered_processes.append(val)
        self.values = filtered_processes
        return match_count


    def kill_process(self,*args,**kwargs):
        # Get the PID of the selected process
        previous_parsed_text = ""
        pid_to_kill = None
        for _ in self.values[self.cursor_line].split():
            if _ in SYSTEM_USERS:
                pid_to_kill = int(previous_parsed_text)
                break
            else:
                previous_parsed_text = _
        self._logger.info("Terminating process with pid {0}".format(pid_to_kill))
        target = psutil.Process(int(pid_to_kill))
        try:
            target.terminate()
            self._logger.info("Terminated process with pid {0}".format(pid_to_kill))
        except:
            self._logger.info("Not able to terminate process with pid: {0}".format(pid_to_kill),
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
        GUI class for ptop. 
        This controls the rendering of the main window and acts as the registering point
        for all other widgets
    '''
    def __init__(self,statistics,stop_event,arg):
        self.statistics = statistics
        # Command line arguments passed, currently used for selecting themes
        self.arg = arg
        # Global stop event
        self.stop_event = stop_event
        # thread for updating
        self.update_thread = None
        # Flag to check if user is interacting (not used)
        self.is_user_interacting = False

        # Main form
        self.window = None 

        # Widgets
        self.basic_stats = None
        self.memory_chart = None
        self.cpu_chart = None
        self.processes_table = None

        # Actions bar
        self.actions = None

        '''
            Refer the other comment in .draw() function, this is legacy behavior
            # internal data structures
            # c.set(89,31) -- here the corner point will be set
            # the upper bounds are the excluded points
            self.CHART_HEIGHT = 32
            self.CHART_WIDTH = 90
        '''
        self.CHART_HEIGHT = None
        self.CHART_WIDTH = None
        self.cpu_array = None
        self.memory_array = None

        # logger
        self._logger = logging.getLogger(__name__)

    def _get_theme(self):
        '''
            choose a theme from a given values of themes
            :param arg: Theme to be selected corresponding to the arg
        '''
        self.themes = SUPPORTED_THEMES
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
        # if not self.update_thread:
        #     t = ThreadJob(self.update,self.stop_event,1)
        #     self.update_thread = t
        #     self.update_thread.start()
        self._logger.info('Updating GUI due to no keyboard interrupt')
        '''
            Earlier a thread job was being used to update the GUI
            in background but while_waiting is getting called after 10ms
            (keypress_timeout_default) so no more thread job is required
            Only issue is that when user is interacting constantly the GUI
            won't update
        '''
        terminal_width,terminal_height = drawille.getTerminalSize()
        self._logger.info("Equating terminal sizes, old {0}*{1} vs {2}*{3}".format(PREVIOUS_TERMINAL_WIDTH,
                                                                                   PREVIOUS_TERMINAL_HEIGHT,
                                                                                   terminal_width,
                                                                                   terminal_height
                                                                                   ))

        # In case the terminal size is changed, try resizing the terminal and redrawing ptop
        if terminal_width != PREVIOUS_TERMINAL_WIDTH or terminal_height != PREVIOUS_TERMINAL_HEIGHT:
            self._logger.info("Terminal Size changed, updating the GUI")
            self.window.erase()
            self.draw()
            self.update()
        # In case the terminal size is not changed, don't redraw the GUI, just update the contents
        else:
            self.update()

    def update(self):
        '''
            Update the form in background, this used to be called inside the ThreadJob 
            and but now is getting called automatically in while_waiting
        '''
        try:
            disk_info = self.statistics['Disk']['text']['/']
            swap_info = self.statistics['Memory']['text']['swap_memory']
            memory_info = self.statistics['Memory']['text']['memory']
            processes_info = self.statistics['Process']['text']
            system_info = self.statistics['System']['text']
            cpu_info = self.statistics['CPU']['graph']

            #### Overview information ####

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
            # Lazy update to GUI
            self.basic_stats.update(clear=True)


            ####  CPU Usage information ####

            cpu_canvas = drawille.Canvas()
            next_peak_height = int(math.ceil((float(cpu_info['percentage'])/100)*self.CHART_HEIGHT))
            self.cpu_chart.value = (self.draw_chart(cpu_canvas,next_peak_height,'cpu'))
            self.cpu_chart.update(clear=True)

            #### Memory Usage information ####

            memory_canvas = drawille.Canvas()
            next_peak_height = int(math.ceil((float(memory_info['percentage'])/100)*self.CHART_HEIGHT))
            self.memory_chart.value = self.draw_chart(memory_canvas,next_peak_height,'memory')
            self.memory_chart.update(clear=True)

            #### Processes table ####

            self._processes_data = self.statistics['Process']['table']

            # check sorting flags
            if MEMORY_SORT:
                sorted_processes_data = sorted(self._processes_data,key=lambda k:k['memory'],reverse=True)
                self._logger.info("Memory sorting done for process table")
            elif TIME_SORT:
                sorted_processes_data = sorted(self._processes_data,key=lambda k:k['rawtime'],reverse=True)
                self._logger.info("Time sorting done for process table")
            elif PROCESS_RELEVANCE_SORT:
                sorted_processes_data = sorted(self._processes_data,key=lambda k:k['rawtime'])
                self._logger.info("Sorting on the basis of relevance")
            else:
                sorted_processes_data = self._processes_data
                self._logger.info("Resetting the sorting behavior")

            # to keep things pre computed
            curtailed_processes_data = []
            for proc in sorted_processes_data:
                curtailed_processes_data.append("{0: <30} {1: >5}{6}{2: <10}{6}{3}{6}{4: >6.2f} % {6}{5}\
                ".format( (proc['name'][:25] + '...') if len(proc['name']) > 25 else proc['name'],
                           proc['id'],
                           proc['user'],
                           proc['time'],
                           proc['memory'],
                           proc['local_ports'],
                           " "*int(5*self.X_SCALING_FACTOR))
                )
            if not self.processes_table.entry_widget.is_filtering_on():
                self.processes_table.entry_widget.values =  curtailed_processes_data
            self.processes_table.entry_widget.set_unfiltered_values(curtailed_processes_data)
            self.processes_table.entry_widget.update(clear=True)

            ''' This will update all the lazy updates at once, instead of .display() [fast]
                .DISPLAY()[slow] is used to avoid glitches or gibberish text on the terminal
            '''
            self.window.DISPLAY()

        # catch the fucking KeyError caused to c
        # cumbersome point of reading the stats data structures
        except KeyError:
            self._logger.info("Some of the stats reading failed",exc_info=True)

    def draw(self):
        # setting the main window form
        self.window = WindowForm(parentApp=self,
                                 name="ptop[http://darxtrix.in/ptop]"
                                 )

        self._logger.info("Detected terminal size to be {0}".format(self.window.curses_pad.getmaxyx()))

        max_y,max_x = self.window.curses_pad.getmaxyx()
        global PREVIOUS_TERMINAL_HEIGHT, PREVIOUS_TERMINAL_WIDTH
        PREVIOUS_TERMINAL_HEIGHT = max_y
        PREVIOUS_TERMINAL_WIDTH = max_x

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

        ACTIONS_WIDGET_REL_X = 2
        ACTIONS_WIDGET_REL_Y = int(24*self.Y_SCALING_FACTOR)
        self.actions = self.window.add(npyscreen.FixedText,
                                       relx=ACTIONS_WIDGET_REL_X,
                                       rely=ACTIONS_WIDGET_REL_Y
                                       )
        self._logger.info("Actions box drawn, x1 {0} y1 {1}".format(ACTIONS_WIDGET_REL_X,  
                                                                    ACTIONS_WIDGET_REL_Y)
                                                                    )
        self.actions.value = "^K:Kill\t\t^N:Memory Sort\t\t^T:Time Sort\t\t^R:Reset\t\tg:Top\t\t^Q:Quit\t\t^F:Filter"
        self.actions.display()
        self.actions.editable = False

        ######   CPU/Memory charts  #########

        '''
            Earlier static dimensions (32*90) were used after multiplication with the corresponding
            scaling factors now the dimensions of the CPU_WIDGETS/MEMORY _WIDGETS are used for calculation
            of the dimensions of the charts. There is padding of width 1 between the boundaries of the widgets 
            and the charts

            # self.CHART_WIDTH = int(self.CHART_WIDTH*self.X_SCALING_FACTOR)
            # self.CHART_HEIGHT = int(self.CHART_HEIGHT*self.Y_SCALING_FACTOR)
        '''
        self.CHART_HEIGHT = int(math.floor((CPU_USAGE_WIDGET_HEIGHT-2)*4))
        self.CHART_WIDTH = int(math.floor((CPU_USAGE_WIDGET_WIDTH-2)*2))
        self._logger.info("Memory and CPU charts dimension, width {0} height {1}".format(self.CHART_WIDTH,
                                                                                         self.CHART_HEIGHT)
                                                                                         )

        # fix for index error
        self.cpu_array = [0]*self.CHART_WIDTH
        self.memory_array = [0]*self.CHART_WIDTH

        # add subwidgets to the parent widget
        self.window.edit()

    def main(self):
        npyscreen.setTheme(self._get_theme())

        # time(ms) to wait for user interactions
        self.keypress_timeout_default = 10
        self.draw()