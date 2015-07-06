'''
    Graphical User Interface for ptop
'''

import npyscreen, math, threading
from drawille import Canvas
from utils import ThreadJob


class MultiLineWidget(npyscreen.BoxTitle):
    '''
        A framed widget containing multiline text
    '''
    _contained_widget = npyscreen.MultiLineEdit


class MultiLineActionWidget(npyscreen.BoxTitle):
    '''
        A framed widget containing multiline text
    '''
    _contained_widget = npyscreen.MultiLineAction


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
    def __init__(self,statistics):
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
            for i in xrange(32,end_point,-1):
                canvas.set(ctr,i)

        return canvas.frame(0,0,self.CHART_LENGTH,self.CHART_HEIGHT)

    def while_waiting(self):
        '''
            called periodically when user is not pressing any key
        '''
        if not self.update_thread:
            self.stop_event = threading.Event()
            t = ThreadJob(self.update,self.stop_event,1)
            self.update_thread = t
            self.update_thread.start()

    def update(self):
        '''
            Update the form in background
        '''
                # get the information
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
        for proc in processes_table:
            if proc['user'] == system_info['user']:
                self.processes_table.entry_widget.values.append("{0: <30} {1: >4}       {2: <10}        {3: <4} %         {4: <4} % \
                ".format( (proc['name'][:25] + '...') if len(proc['name']) > 25 else proc['name'],
                           proc['id'],
                           proc['user'],
                           proc['cpu'],
                           proc['memory'])
                )

        self.processes_table.display()

    def main(self):
        npyscreen.setTheme(npyscreen.Themes.TransparentThemeDarkText)

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
        self.actions.value = ""
        self.actions.editable = False


        # add subwidgets to the parent widget
        self.window.edit()


