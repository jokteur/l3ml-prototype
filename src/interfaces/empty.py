from bokeh.layouts import column

from src.interfaces.AbstractPanel import AbstractPanel

class Empty(AbstractPanel):
    """"""
    def __init__(self, title='working', data=None):
        """"""

        AbstractPanel.__init__(self, title=title)

        self.panel = column()
