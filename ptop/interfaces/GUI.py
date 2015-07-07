'''
    Graphical User Interface for ptop
'''

import npyscreen, math
from drawille import Canvas
from utils import ThreadJob
import os, psutil

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
            "^K": self.kill_process
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
    def __init__(self,statistics,stop_event):
        self.statistics = statistics
        # main form
        self.window = None 
        # thread for updating
        self.update_thread = None
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
        self.cpu_array = [0]*self.CHART_LENGTH
        self.memory_array = [0]*self.CHART_LENGTH
        # Global stop event
        self.stop_event = stop_event

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
            row1 = "Disk Usage (/)    {0: <6}/{1: >6} MB     {2: >2} % \
                    Processes         {3: >8}".format(disk_info["used"],
                                                      disk_info["total"],
                                                      disk_info["percentage"],
                                                      processes_info["running_processes"])

            row2 = "Swap Memory       {0: <6}/{1: >6} MB     {2: >2} % \
                    Threads           {3: >8}".format(swap_info["active"],
                                                      swap_info["total"],
                                                      swap_info["percentage"],
                                                      processes_info["running_threads"])

            row3 = "Main memory       {0: <6}/{1: >6} MB     {2: >2} % \
                    Boot Time         {3: >8}".format(memory_info["active"],
                                                      memory_info["total"],
                                                      memory_info["percentage"],
                                                      system_info['running_time'])

            self.basic_stats.value = row1 + '\n' + row2 + '\n' + row3
            self.basic_stats.display()

            ### cpu_usage chart
            cpu_canvas = Canvas()
            next_peak_height = int(math.ceil((float(cpu_info['percentage'])/100)*self.CHART_HEIGHT))
            self.cpu_chart.value = self.draw_chart(cpu_canvas,next_peak_height,'cpu')
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
                    temp_list.append("{0: <30} {1: >5}       {2: <10}        {3: <8}         {4: <4} % \
                    ".format( (proc['name'][:25] + '...') if len(proc['name']) > 25 else proc['name'],
                               proc['id'],
                               proc['user'],
                               proc['time'],
                               proc['memory'])
                    )
            self.processes_table.entry_widget.values = temp_list
            self.processes_table.display()

        # catch the fucking KeyError caused to c
        # cumbersome point of reading the stats data structures
        except KeyError:
            pass

    def main(self):
        os.system('clear')

        # npyscreen.setTheme(npyscreen.Themes.TransparentThemeDarkText)
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)

        # time(ms) to wait for user interactions
        self.keypress_timeout_default = 10

        # setting the main window form
        self.window = WindowForm(parentApp=self,name="ptop")
        # use gridss
        self.basic_stats = self.window.add(MultiLineWidget,name="Overview",relx=1,rely=1,max_height=5,max_width=100)
        self.basic_stats.value = ""
        self.basic_stats.entry_widget.editable = False


        self.memory_chart = self.window.add(MultiLineWidget,name="Memory Usage",relx=1,rely=6,max_height=10,max_width=50)
        self.memory_chart.value = ""
        self.memory_chart.entry_widget.editable = False

        self.cpu_chart = self.window.add(MultiLineWidget,name="CPU Usage",relx=52,rely=6,max_height=10,max_width=49)
        self.cpu_chart.value = ""
        self.cpu_chart.entry_widget.editable = False

        self.processes_table = self.window.add(MultiLineActionWidget,name="Processes",relx=1,rely=16,max_height=8,max_width=100)
        self.processes_table.entry_widget.values = []
        self.processes_table.entry_widget.scroll_exit = False

        self.actions = self.window.add(npyscreen.FixedText,relx=1,rely=24)
        self.actions.value = "^K : Kill     ^N : Sort by Memory     ^H : Sort by Time      g : top "
        self.actions.display()
        self.actions.editable = False


        # add subwidgets to the parent widget
        self.window.edit()


