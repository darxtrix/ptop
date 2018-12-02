# -*- coding: utf-8 -*-
'''
    Graphical User Interface for ptop
'''
from collections import OrderedDict
import json
import inspect
import npyscreen, math, drawille
import psutil, logging, weakref, sys
from ptop.utils import ThreadJob
from ptop.constants import SYSTEM_USERS, SUPPORTED_THEMES


# global flags defining actions, would like them to be object vars
TIME_SORT = False
MEMORY_SORT = False
PROCESS_RELEVANCE_SORT = True
PREVIOUS_TERMINAL_WIDTH = None
PREVIOUS_TERMINAL_HEIGHT = None

KEYBINDINGS_FILE = 'keybindings.json'
shortcut_keys = OrderedDict()


class ProcessDetailsInfoBox(npyscreen.PopupWide):
    '''
    This widget is used to who the detailed information about the selected process
    in the processes table. Curretly only the port information is shown for a selected
    process.
`   '''
    #Set them to fix the position
    SHOW_ATX  = 0
    SHOW_ATY  = 0
    DEFAULT_COLUMNS = PREVIOUS_TERMINAL_WIDTH

    def __init__(self,local_ports,process_pid,open_files):
        self._local_ports = local_ports
        self._process_pid = process_pid
        self._open_files = open_files
        super(ProcessDetailsInfoBox,self).__init__()

    def create(self,**kwargs):
        '''
            Sub widgets [details_box_heading,details_box] are only shown in GUI if
            they are created in the create() method
        '''
        super(ProcessDetailsInfoBox,self).create()

        self._logger = logging.getLogger(__name__)
        self._logger.info("Showing the local ports {0} and files opened and are being used by the process with pid {1}".format(self._local_ports,
                                                                                         str(self._process_pid)))
        #logger.info("Showing the local ports {0} and files opened and are being used by the process with pid {1}".format(self._local_ports,str(self._process_pid)))
                        #             self.details_box_heading = self.add(npyscreen.TitleText, name='No ports used by the process {0}'.format(str(self._process_pid)),)
        self.details_box_heading = self.add(npyscreen.TitleText, name='Showing info for process with PID {0}'.format(str(self._process_pid)))
        self.details_box = self.add(npyscreen.BufferPager)
        if len(self._local_ports) != 0 and len(self._open_files)!= 0:
            self.details_box.values.extend(['System ports used by the process are:\n'])
            self.details_box.values.extend(self._local_ports)
            self.details_box.values.extend('\n')
            self.details_box.values.extend(['Files opened by this process are:\n'])
            self.details_box.values.extend('\n')
            self.details_box.values.extend(self._open_files)
        elif len(self._open_files) != 0:
            self.details_box.values.extend(['Files opened by this process are:\n'])
            self.details_box.values.extend(self._open_files)
            self.details_box.values.extend('\n')
            self.details_box.values.extend(['The process is not using any System ports.\n'])
        elif len(self._local_ports) != 0:
            self.details_box.values.extend(['System ports used by the process are:\n'])
            self.details_box.values.extend(self._local_ports)
            self.details_box.values.extend('\n')
            self.details_box.values.extend(['No files are opened by this process.\n'])
        else:
            self.details_box.values.extend(['No system ports are used and no files are opened by this process.\n'])
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
        self._filtering_flag = False
        self._logger = logging.getLogger(__name__)
        handlers = self._read_keybindings()
        self.add_handlers(handlers)
        '''
            Non-sorted processes table entries, practically this will never be 
            None beacuse the user will ask for a certain process info only 
            after chossing one from the processes table
        '''
        self._uncurtailed_process_data = None

    def _read_keybindings(self):
        global shortcut_keys
        keybindings = {}

        with open(KEYBINDINGS_FILE) as f:
            bindings = json.load(f)

        methods = self._get_class_methods()

        # we extract the methods by name and assign them to the key
        for binding in bindings:
            if binding[1]:
                keybindings[binding[0]] = methods["_" + binding[1]]
            shortcut_keys[binding[0]] = binding[2]

        return keybindings

    def _get_class_methods(self):
        methods = {}
        for method in inspect.getmembers(self, inspect.ismethod):
            methods[method[0]] = method[1]
        return methods

    def _get_selected_process_pid(self):
        '''
            Parses the process pid from the selected line in the process
            table
        '''
        previous_parsed_text = ""
        for _ in self.values[self.cursor_line].split():
            if _ in SYSTEM_USERS:
                selected_process_pid = int(previous_parsed_text)
                break
            else:
                previous_parsed_text = _
        return selected_process_pid

    def _get_local_ports_used_by_a_process(self,process_pid):
        """
            Given the process_id returns the list of local ports used by
            the process
        """
        for proc in self._uncurtailed_process_data:
            if proc['id'] == process_pid:
                return proc['local_ports']

    def _get_list_of_open_files(self,process_pid):
        """
            Given the Process ID, return the list of all the open files
        """
        opened_files_by_proces = []
        p = psutil.Process(process_pid)
        for i in p.open_files():
            opened_files_by_proces.append(i[0])
        return opened_files_by_proces

    def _sort_by_time(self,*args,**kwargs):
        # fuck .. that's why NPSManaged was required, i.e you can access the app instance within widgets
        self._logger.info("Sorting the process table by time")
        global TIME_SORT,MEMORY_SORT
        MEMORY_SORT = False
        TIME_SORT = True
        PROCESS_RELEVANCE_SORT = False

    def _sort_by_memory(self,*args,**kwargs):
        self._logger.info("Sorting the process table by memory")
        global TIME_SORT,MEMORY_SORT
        TIME_SORT = False
        MEMORY_SORT = True
        PROCESS_RELEVANCE_SORT = False

    def _reset(self,*args,**kwargs):
        self._logger.info("Resetting the process table")
        global TIME_SORT, MEMORY_SORT
        TIME_SORT = False
        MEMORY_SORT = False
        PROCESS_RELEVANCE_SORT = True
        self._filtering_flag = False

    def _do_process_filtering_work(self,*args,**kwargs):
        '''
            Dynamically instantiate a process filtering box used
            to offload the process filtering work
        '''
        self.process_filtering_helper = ProcessFilterInputBox()
        self.process_filtering_helper.owner_widget = weakref.proxy(self)
        self.process_filtering_helper.display()
        self.process_filtering_helper.edit()

    def _show_detailed_process_info(self,*args,**kwargs):
        """
            Display the extra process information. Extra information includes
            open ports and the opened files list
        """
        self._logger.info("Showing process details for the selected process")
        # This is not working, local_ports information is not getting passed in the
        # create method of self._logger = logging.getLogger(__name__)
        # self.process_details_view_helper = ProcessDetailsInfoBox(local_ports=['1','2','3'])
        process_pid = self._get_selected_process_pid()
        local_ports = self._get_local_ports_used_by_a_process(process_pid)
        open_files = self._get_list_of_open_files(process_pid)
        self.process_details_view_helper = ProcessDetailsInfoBox(local_ports,process_pid,open_files)
        self.process_details_view_helper.owner_widget = weakref.proxy(self)
        self.process_details_view_helper.display()
        self.process_details_view_helper.edit()

    #_kill_process takes *args, **kwargs
    def _kill_process(self,*args,**kwargs):
        # Get the PID of the selected process
        pid_to_kill = self._get_selected_process_pid()
        self._logger.info("Terminating process with pid {0}".format(pid_to_kill))
        try:
            target = psutil.Process(int(pid_to_kill)) # Handle NoSuchProcessError
            target.terminate()
            self._logger.info("Terminated process with pid {0}".format(pid_to_kill))
        except:
            self._logger.info("Not able to terminate process with pid: {0}".format(pid_to_kill),
                              exc_info=True)

    def _quit(self,*args,**kwargs):
        raise KeyboardInterrupt

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
        for val in self.values:
            if self._filter in str.lower(val):
                match_count += 1
                filtered_processes.append(val)
        self.values = filtered_processes
        return match_count

    def is_filtering_on(self):
        return self._filtering_flag

    def set_uncurtailed_process_data(self, processes_info):
        self._uncurtailed_process_data = processes_info


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
    def __init__(self,statistics,stop_event,arg,sensor_refresh_rates):
        self.statistics = statistics
        # Command line arguments passed, currently used for selecting themes
        self.arg = arg
        # Global stop event
        self.stop_event = stop_event
        # thread for updating
        self.update_thread = None
        # Flag to check if user is interacting (not used)
        self.is_user_interacting = False
        # GUI refresh rate should be minimum of all sensor refresh rates
        self.refresh_rate = min(sensor_refresh_rates.values())

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

        for x in range(0,self.CHART_WIDTH):
            for y in range(self.CHART_HEIGHT,self.CHART_HEIGHT-chart_array[x],-1):
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
            network_info = self.statistics['Network']['text']

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

            row3 = "Main Memory    {4}{0: <6}/{1: >6} MB{4}{2: >2} %{5}Boot Time{4}{3: <8} hours".format(memory_info["active"],
                                                                                                   memory_info["total"],
                                                                                                   memory_info["percentage"],
                                                                                                   str(system_info["running_time"]),
                                                                                                   " "*int(4*self.X_SCALING_FACTOR),
                                                                                                   " "*int(9*self.X_SCALING_FACTOR))
            row4 = "Network Speed  {2}{0: <3}↓ {1: <3}↑ MB/s".format(network_info["download_speed_in_mb"],
                                                                     network_info["upload_speed_in_mb"],
                                                                     " "*int(4*self.X_SCALING_FACTOR),
                                                                     " "*int(9*self.X_SCALING_FACTOR))

            self.basic_stats.value = row1 + '\n' + row2 + '\n' + row3 + '\n' + row4
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
            # Set the processes data dictionary to uncurtailed processes data
            self.processes_table.entry_widget.set_uncurtailed_process_data(self._processes_data)
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
        # Setting the main window form
        self.window = WindowForm(parentApp=self,
                                 name="ptop [http://darxtrix.in/ptop]"
                                 )
        MIN_ALLOWED_TERMINAL_WIDTH = 104
        MIN_ALLOWED_TERMINAL_HEIGHT = 28

        # Setting the terminal dimensions by querying the underlying curses library
        self._logger.info("Detected terminal size to be {0}".format(self.window.curses_pad.getmaxyx()))
        global PREVIOUS_TERMINAL_HEIGHT, PREVIOUS_TERMINAL_WIDTH
        max_y,max_x = self.window.curses_pad.getmaxyx()
        PREVIOUS_TERMINAL_HEIGHT = max_y
        PREVIOUS_TERMINAL_WIDTH = max_x

        # Also make ptop exists cleanly if screen is drawn beyond the lower limit
        if max_x < MIN_ALLOWED_TERMINAL_WIDTH or \
            max_y < MIN_ALLOWED_TERMINAL_HEIGHT:
            self._logger.info("Terminal sizes than width = 104 and height = 28, exiting")
            sys.stdout.write("Ptop does not support terminals with resolution smaller than 104*28. Please resize your terminal and try again.")
            raise KeyboardInterrupt

        # Minimum terminal size should be used for scaling
        # $ tput cols & $ tput lines can be used for getting the terminal dimensions
        # ptop won't be reponsive beyond (cols=104, lines=27)
        self.Y_SCALING_FACTOR = float(max_y)/28
        self.X_SCALING_FACTOR = float(max_x)/104

        #####      Defaults            #######
        LEFT_OFFSET = 1
        TOP_OFFSET = 1

        #####      Overview widget     #######
        OVERVIEW_WIDGET_REL_X = LEFT_OFFSET
        OVERVIEW_WIDGET_REL_Y = TOP_OFFSET
        # equivalent to math.ceil =>  [ int(109.89) = 109 ]
        OVERVIEW_WIDGET_HEIGHT = int(6*self.Y_SCALING_FACTOR)
        OVERVIEW_WIDGET_WIDTH = int(100*self.X_SCALING_FACTOR)
        self._logger.info("Trying to draw Overview information box, x1 {0} x2 {1} y1 {2} y2 {3}".format(OVERVIEW_WIDGET_REL_X,
                                                                                               OVERVIEW_WIDGET_REL_X+OVERVIEW_WIDGET_WIDTH,
                                                                                               OVERVIEW_WIDGET_REL_Y,
                                                                                               OVERVIEW_WIDGET_REL_Y+OVERVIEW_WIDGET_HEIGHT)
                                                                                               )
        self.basic_stats = self.window.add(MultiLineWidget,
                                           name="Overview",
                                           relx=OVERVIEW_WIDGET_REL_X,
                                           rely=OVERVIEW_WIDGET_REL_Y,
                                           max_height=OVERVIEW_WIDGET_HEIGHT,
                                           max_width=OVERVIEW_WIDGET_WIDTH
                                           )
        self.basic_stats.value = ""
        self.basic_stats.entry_widget.editable = False


        ######    Memory Usage widget  #########
        MEMORY_USAGE_WIDGET_REL_X = LEFT_OFFSET
        MEMORY_USAGE_WIDGET_REL_Y = OVERVIEW_WIDGET_REL_Y + OVERVIEW_WIDGET_HEIGHT
        MEMORY_USAGE_WIDGET_HEIGHT = int(10*self.Y_SCALING_FACTOR)
        MEMORY_USAGE_WIDGET_WIDTH = int(50*self.X_SCALING_FACTOR)
        self._logger.info("Trying to draw Memory Usage information box, x1 {0} x2 {1} y1 {2} y2 {3}".format(MEMORY_USAGE_WIDGET_REL_X,
                                                                                                   MEMORY_USAGE_WIDGET_REL_X+MEMORY_USAGE_WIDGET_WIDTH,
                                                                                                   MEMORY_USAGE_WIDGET_REL_Y,
                                                                                                   MEMORY_USAGE_WIDGET_REL_Y+MEMORY_USAGE_WIDGET_HEIGHT)
                                                                                                   )
        self.memory_chart = self.window.add(MultiLineWidget,
                                            name="Memory Usage",
                                            relx=MEMORY_USAGE_WIDGET_REL_X,
                                            rely=MEMORY_USAGE_WIDGET_REL_Y,
                                            max_height=MEMORY_USAGE_WIDGET_HEIGHT,
                                            max_width=MEMORY_USAGE_WIDGET_WIDTH
                                            )
        self.memory_chart.value = ""
        self.memory_chart.entry_widget.editable = False


        ######    CPU Usage widget  #########
        CPU_USAGE_WIDGET_REL_X = MEMORY_USAGE_WIDGET_REL_X + MEMORY_USAGE_WIDGET_WIDTH
        CPU_USAGE_WIDGET_REL_Y = MEMORY_USAGE_WIDGET_REL_Y
        CPU_USAGE_WIDGET_HEIGHT = MEMORY_USAGE_WIDGET_HEIGHT
        CPU_USAGE_WIDGET_WIDTH = MEMORY_USAGE_WIDGET_WIDTH
        self._logger.info("Trying to draw CPU Usage information box, x1 {0} x2 {1} y1 {2} y2 {3}".format(CPU_USAGE_WIDGET_REL_X,
                                                                                                CPU_USAGE_WIDGET_REL_X+CPU_USAGE_WIDGET_WIDTH,
                                                                                                CPU_USAGE_WIDGET_REL_Y,
                                                                                                CPU_USAGE_WIDGET_REL_Y+CPU_USAGE_WIDGET_HEIGHT)
                                                                                                )
        self.cpu_chart = self.window.add(MultiLineWidget,
                                         name="CPU Usage",
                                         relx=CPU_USAGE_WIDGET_REL_X,
                                         rely=CPU_USAGE_WIDGET_REL_Y,
                                         max_height=CPU_USAGE_WIDGET_HEIGHT,
                                         max_width=CPU_USAGE_WIDGET_WIDTH
                                         )
        self.cpu_chart.value = ""
        self.cpu_chart.entry_widget.editable = False


        ######    Processes Info widget  #########
        PROCESSES_INFO_WIDGET_REL_X = LEFT_OFFSET
        PROCESSES_INFO_WIDGET_REL_Y = CPU_USAGE_WIDGET_REL_Y + CPU_USAGE_WIDGET_HEIGHT
        PROCESSES_INFO_WIDGET_HEIGHT = int(8*self.Y_SCALING_FACTOR)
        PROCESSES_INFO_WIDGET_WIDTH = OVERVIEW_WIDGET_WIDTH
        self._logger.info("Trying to draw Processes information box, x1 {0} x2 {1} y1 {2} y2 {3}".format(PROCESSES_INFO_WIDGET_REL_X,
                                                                                                PROCESSES_INFO_WIDGET_REL_X+PROCESSES_INFO_WIDGET_WIDTH,
                                                                                                PROCESSES_INFO_WIDGET_REL_Y,
                                                                                                PROCESSES_INFO_WIDGET_REL_Y+PROCESSES_INFO_WIDGET_HEIGHT)
                                                                                                )
        self.processes_table = self.window.add(MultiLineActionWidget,
                                               name="Processes ( name - PID - user - age - memory - system_ports )",
                                               relx=PROCESSES_INFO_WIDGET_REL_X,
                                               rely=PROCESSES_INFO_WIDGET_REL_Y,
                                               max_height=PROCESSES_INFO_WIDGET_HEIGHT,
                                               max_width=PROCESSES_INFO_WIDGET_WIDTH-1
                                               )
        self.processes_table.entry_widget.values = []
        self.processes_table.entry_widget.scroll_exit = False
        self.cpu_chart.entry_widget.editable = False


        ######   Actions widget  #########
        # By default this widget takes 3 lines and 1 line for text and 2 for the invisible boundary lines
        # So (tput lines - rely) should be at least 3
        ACTIONS_WIDGET_REL_X = LEFT_OFFSET
        ACTIONS_WIDGET_REL_Y = PROCESSES_INFO_WIDGET_REL_Y + PROCESSES_INFO_WIDGET_HEIGHT
        self._logger.info("Trying to draw the actions box, x1 {0} y1 {1}".format(ACTIONS_WIDGET_REL_X,
                                                                    ACTIONS_WIDGET_REL_Y)
                                                                    )
        self.actions = self.window.add(npyscreen.FixedText,
                                       relx=ACTIONS_WIDGET_REL_X,
                                       rely=ACTIONS_WIDGET_REL_Y
                                       )
        global shortcut_keys
        for k, v in shortcut_keys.items():
            self.actions.value += k + ":" + v + "\t\t"

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

        if self.refresh_rate < 1000:
            self.keypress_timeout_default = int(self.refresh_rate/100)

        self.draw()
