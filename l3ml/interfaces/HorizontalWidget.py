from bokeh.core.properties import String, Instance
from bokeh.models import HTMLBox, Slider

class CustomViewer(HTMLBox):
    __implementation__ = "custom.ts"

    text = String(default="Viewer")
