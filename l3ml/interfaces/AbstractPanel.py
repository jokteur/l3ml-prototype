from abc import ABC, abstractmethod


class AbstractPanel(ABC):
    """Defines an abstract panel that will be displayed in the Bokeh server

    Every GUI panel should inherit from this Abstract Panel.

    Parameters
    ----------
    panel : Panel object
        panel that will be fetched by the GUI and displayed in the tab
    title : str, optional
        title of the panel (will be showed in the Tab)
    _is_ready : bool
        internal variable that will be observed for knowning if the panel is
        ready to finish
    _observers : list of functions
        internal variable that stores the observers to the _is_ready variable
        if this _is_ready is changed, the observers will be notified
    """
    @abstractmethod
    def __init__(self, title='', data=None):
        """An abstract panel has at least a panel object (could be holoviews,
        panel or bokeh) and maybe plotting data.
        """
        self.panel = None
        self.future_data = None
        self.incoming_data = None
        self.title = title

        # We want to know from the outside if the panel is ready to continue
        # (go to next panel or next mcs step). Here, Observers can be added
        # such that if self.continue changes to True, then it will call the
        # observers
        self._is_ready = False
        self._ready_observers = []

        # It is also possible to trigger a goto event (to any state of the MCS)
        self._goto = ''
        self._goto_observers = []

        # Send message to the GUI
        self._message = ''
        self._message_observers = []

    def view(self):
        """Returns the panel object"""
        return self.panel

    @property
    def is_ready(self):
        """Transform function is_ready in attribute-like"""
        return self._is_ready

    @is_ready.setter
    def is_ready(self, value):
        """This function is called whenever is_ready is modified.
        All observers will be called upon setting is_ready."""
        self._is_ready = value
        for callback in self._ready_observers:
            callback(self._is_ready)

    def ready_bind_to(self, callback):
        """Binds a new observer to the is_ready attribute"""
        self._ready_observers.append(callback)


    @property
    def goto(self):
        """Transform function is_ready in attribute-like"""
        return self._goto

    @is_ready.setter
    def goto(self, value):
        """This function is called whenever is_ready is modified.
        All observers will be called upon setting is_ready."""
        self._goto = value
        for callback in self._goto_observers:
            callback(self._goto)

    def goto_bind_to(self, callback):
        """Binds a new observer to the is_ready attribute"""
        self._goto_observers.append(callback)


    def next(self):
        """Function is called when the next button is pressed"""
        pass
    
    @property
    def message(self):
        """Transform function is_ready in attribute-like"""
        return self._message

    @is_ready.setter
    def message(self, value):
        """This function is called whenever is_ready is modified.
        All observers will be called upon setting a message."""
        self._message = value
        for callback in self._message_observers:
            callback(self._message)

    def message_bind_to(self, callback):
        """Binds a new observer to the is_ready attribute"""
        self._message_observers.append(callback)
