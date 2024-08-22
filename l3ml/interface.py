"""@package docstring

Module for making the interaction between the GUI and the MCS class possible.

Basically, the Interface defines a "state", which is the combination of the
function of the MCS class and a GUI panel from the gui_panels folder.

Interface produces a loop (Interface.proceed()) which executes the states one
after the other. Sometimes, there is a need for user interaction. Interface will
observe the current GUI panel to see if the user is ready to continue the
algorithm. The GUI can also request to go to any state that is defined in this
class.

Data that is produced by the MCS function and should be transferred to the GUI
panel should be stored in MCS.plotting_data. Data that comes from the GUI and
should be transferred to the next MCS function should be stored into
AbstractPanel.future_data.
"""
import sys
from collections import OrderedDict
import time
import traceback
import queue
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.layouts import column, row
from bokeh.server.server import Server
from bokeh.plotting import curdoc
from bokeh.models.widgets import Paragraph, Div

from l3ml.interfaces.empty import Empty
from l3ml.interfaces.start import Start
from l3ml.constants import page_width
from l3ml.interfaces.main_interface import MainInterface
from l3ml.interfaces.modify import Modify
from l3ml.exceptions import ProgramInterrupt, StateError

class Interface:
    """Class which does the interface between the MCS algorithm and the different
    GUI panels associated to the MCS algorithm"""

    def __init__(self):
        """Defines the order in which the algorithm should proceed"""

        self.state = OrderedDict()
        self.active_state = 'start'
        self.active_panel = Empty(title='start')
        self.data = None

        self.is_instanciated = False

        # Want to avoid launching MCS functions from the Bokeh thread
        # otherwise the MCS functions will block the GUI
        # This means that self._load_state() should always be launched in the
        # main thread. queue is the perfect module for this task
        self.callback_queue = queue.Queue()

        self.state['start'] = {'gui_panel': Empty}
        self.state['open_file'] = {'gui_panel': Start}
        self.state['main_interface'] = {'gui_panel': MainInterface}
        self.state['modifiy'] = {'gui_panel': Modify}

    def instanciate(self):
        """Launches the Bokeh/Panel server on a local address
        (i.e. localhost:5006)
        """
        if not self.is_instanciated:
            self.app = Application(FunctionHandler(self.create_app))
            self.server = Server({'/': self.app}, port=5006)

            print(f"Creating app on http://localhost:5006")

            is_instanciated = True

            self.server.start()
            self.server.show('/')
            from tornado.ioloop import IOLoop
            loop = IOLoop.current()
            loop.start()


    def create_app(self, doc):
        """Core of the app"""
        self.message = row(Paragraph(text=""))
        self.panel = row(Paragraph(text=""))
        self.root_doc = column(self.message, self.panel, width=page_width)
        from l3ml.template import template
        doc.template = template
        doc.add_root(self.root_doc)
        doc.title = "L3ML"

        self._next_state()

    def next(self, is_ready=True):
        """Proceeds to the next step/state of the algorithm (called by observers)"""
        if(is_ready):
            self._next_state()

    def goto(self, goto=''):
        """Goes to the specified state of the algorithm (called by observers)"""
        if goto not in self.state.keys():
            raise StateError()

        self._load_state(goto)

    def _load_from_main_thread(self, state=''):
        """Loads and launches the state from the main thread to avoid
        blocking in the GUI"""
        self.callback_queue.put(lambda: self._load_state(state))

    def _quit(self):
        """Quits the main loop"""
        from tornado.ioloop import IOLoop
        IOLoop.current().stop()
        self.server.stop()

    def _next_state(self):
        """Selects the next step in the algorithm, execute the MCS and the
        optional GUI"""
        key_list = list(self.state.keys())
        next_state_found = False
        next_state = ''
        for i, key in enumerate(key_list):
            if key == self.active_state and i < len(key_list) - 1:
                next_state_found = True
                next_state = key_list[i+1]
                break

        if next_state_found:
            self._load_state(next_state)
        else:
            self._load_panel(Empty(title="Le programme a été quitté."))

            self._quit()

    def _load_state(self, state):
        """Loads the specified MCS state

        Returns True if ready to go the next state, False if Interface should
        wait and listen to the GUI panel."""
        data = self.active_panel.future_data
        self.state[self.active_state]['gui_panel']()
        self.active_state = state

        # Load empty panel when mcs is working
        self._load_panel(Empty())

        # Load relevant panel of the step
        self.active_panel = self.state[self.active_state]['gui_panel'](data=data)
        # Bind the current panel for observing when it is ready to proceed
        self.active_panel.ready_bind_to(self.next)
        self.active_panel.goto_bind_to(self.goto)
        self.active_panel.message_bind_to(self._send_message)

        self._load_panel(self.active_panel)

        return False

    def _send_message(self, message):
        """"""
        style = f'background:#efefef;color:red;font-size:16px;padding:10px;border-radius=5px;border:1px gray dashed;width=99%;display:block;'
        flush = 'clear:both;'
        if not message == '':
            disp = Div(text=f'<span style="{style}">{message}</span><span style="clear:both"></span>', width=page_width)
        else:
            disp = Paragraph(text="")
        self.root_doc.children[0].children[0] = disp

    def _load_panel(self, panel):
        """"""
        self.root_doc.children[1].children[0] = panel.view()