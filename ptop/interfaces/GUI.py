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
        target = psutil.Process(int(pid))
        target.terminate()

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
        self.CHART_LENGTH = 90
        self.cpu_array = None
        self.memory_array = None

        # logger
        self.logger = logging.getLogger('ptop.GUI')

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
        
        for i in range(self.CHART_LENGTH):
            if i >= 2:
                chart_array[i-2] = chart_array[i]
        # width of each peak is 2 units
        chart_array[self.CHART_LENGTH-1] = y
        chart_array[self.CHART_LENGTH-2] = y

        # now draw on the canvas
        for ctr in xrange(self.CHART_LENGTH):
            end_point = self.CHART_HEIGHT-chart_array[ctr]
            # end_point will be excluded
            for i in xrange(self.CHART_HEIGHT,end_point,-1):
                canvas.set(ctr,i)

        return canvas.frame(0,0,self.CHART_LENGTH,self.CHART_HEIGHT)

    def while_waiting(self):
        '''
            called periodically when user is not pressing any key
        '''
        if not self.update_thread:
            t = ThreadJob(self.update,self.stop_event,1)
            self.update_thread = t
            self.update_thread.start()
            self.logger.info('Started GUI update thread')

    def update(self):
        '''
            Update the form in background
        '''
                # get the information
        try:
            disk_info = self.statistics['Disk']['text']['/']
            swap_info = self.statistics['Memory']['text']['swap_memory']
            memory_info = self.statistics['Memory']['text']['memory']
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
                sorted_table = sorted(processes_table,key=lambda k:k['time'],reverse=True)
            else:
                sorted_table = processes_table

            # to keep things pre computed
            temp_list = []
            for proc in sorted_table:
                if proc['user'] == system_info['user']:
                    temp_list.append("{0: <30} {1: >5}{5}{2: <10}{5}{3: <8}{5}{4: <4} % \
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
            pass

    def main(self):
        npyscreen.setTheme(self.get_theme())

        # time(ms) to wait for user interactions
        self.keypress_timeout_default = 10

        # setting the main window form
        self.window = WindowForm(parentApp=self,
                                 name="ptop ( http://github.com/black-perl/ptop) ")

        self.logger.info(self.window.curses_pad.getmaxyx())

        max_y,max_x = self.window.curses_pad.getmaxyx()

        self.Y_SCALING_FACTOR = float(max_y)/27
        self.X_SCALING_FACTOR = float(max_x)/104

        self.basic_stats = self.window.add(MultiLineWidget,
                                           name="Overview",
                                           relx=1,
                                           rely=1,
                                           max_height=int(math.ceil(5*self.Y_SCALING_FACTOR)),
                                           max_width=int(100*self.X_SCALING_FACTOR)
                                           )
        self.basic_stats.value = ""
        self.basic_stats.entry_widget.editable = False


        self.memory_chart = self.window.add(MultiLineWidget,
                                            name="Memory Usage",
                                            relx=1,
                                            rely=int(math.ceil(5*self.Y_SCALING_FACTOR)+1),
                                            max_height=int(10*self.Y_SCALING_FACTOR),
                                            max_width=int(50*self.X_SCALING_FACTOR)
                                            )
        self.memory_chart.value = ""
        self.memory_chart.entry_widget.editable = False

        self.cpu_chart = self.window.add(MultiLineWidget,
                                         name="CPU Usage",
                                         relx=int(52*self.X_SCALING_FACTOR),
                                         rely=int(math.ceil(5*self.Y_SCALING_FACTOR)+1),
                                         max_height=int(10*self.Y_SCALING_FACTOR),
                                         max_width=int(49*self.X_SCALING_FACTOR)
                                         )
        self.cpu_chart.value = ""
        self.cpu_chart.entry_widget.editable = False

        self.processes_table = self.window.add(MultiLineActionWidget,
                                               name="Processes",
                                               relx=1,
                                               rely=int(16*self.Y_SCALING_FACTOR),
                                               max_height=int(8*self.Y_SCALING_FACTOR),
                                               max_width=int(100*self.X_SCALING_FACTOR)
                                               )

        self.processes_table.entry_widget.values = []
        self.processes_table.entry_widget.scroll_exit = False

        self.actions = self.window.add(npyscreen.FixedText,
                                       relx=1,
                                       rely=int(24*self.Y_SCALING_FACTOR)
                                       )
        self.actions.value = "^K : Kill     ^N : Sort by Memory     ^H : Sort by Time      g : top    q : quit "
        self.actions.display()
        self.actions.editable = False

        self.CHART_LENGTH = int(self.CHART_LENGTH*self.X_SCALING_FACTOR)
        self.CHART_HEIGHT = int(self.CHART_HEIGHT*self.Y_SCALING_FACTOR)

        # fix for index error
        self.cpu_array = [0]*self.CHART_LENGTH
        self.memory_array = [0]*self.CHART_LENGTH

        # add subwidgets to the parent widget
        self.window.edit()


