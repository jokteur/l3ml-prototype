import os
import csv
import imageio
import numpy as np
from bokeh.models.widgets import PreText, TextInput, Div, Button
from bokeh.layouts import column, row
from bokeh.layouts import gridplot
from bokeh.plotting import figure
from bokeh import events

from l3ml.workspace import Workspace
from l3ml.constants import page_width
from l3ml.interfaces.AbstractPanel import AbstractPanel
from l3ml.image_processing import measurements

wksp = Workspace()
thumb_size = 128

class MainInterface(AbstractPanel):
    """"""
    def __init__(self, title='Start', data=None):
        """"""

        AbstractPanel.__init__(self, title=title)

        wksp.update()
        
        preamble = Div(text="""Cliquer sur une image pour l'ouvrir""")

        title1 = Div(text="""<h2>Cas non-modifiés</h2>""")
        title2 = Div(text="""<h2>Cas retouchés</h2>""")
        title3 = Div(text="""<h2>Cas validés</h2>""")

        self.ipps_ids = dict({})
        
        # Grid layout for non-modified
        non_modified_layout = self.list_cases('non_modified')
        # Grid layout for non-modified
        modified_layout = self.list_cases('modified')
        # Grid layout for non-modified
        validated_layout = self.list_cases('validated')

        export_b = Button(label="Exporter les mesures validées en csv", button_type="success", width=300)
        export_b.on_click(self.export_csv)

        self.panel = column(preamble, title1, non_modified_layout,
            title2, modified_layout,
            title3, export_b, validated_layout, width=page_width)

    def export_csv(self, *events):
        with open(os.path.join(wksp.path, 'validation', 'mesures_valides.csv'), 'w') as csvfile:
            csv_write = csv.writer(csvfile, delimiter=',', quotechar='"')
            csv_write.writerow(['IPP', 'SMA (cm^2)', 'SMRA (HU)'])
            for ipp in wksp.ids_list:
                if wksp.ids[ipp] == 'validated':
                    ml_pred = np.load(os.path.join(wksp.validated_masks_dir, ipp + '.npy'), allow_pickle=True)
                    image = imageio.imread(os.path.join(wksp.images_dir, ipp + '.png'))[:,:,0]
                    data = np.load(os.path.join(wksp.npy_dir, ipp + '.npy'), allow_pickle=True)
                    hu_image = data[0]
                    pixel_spacing = data[1]
                    values = measurements(hu_image, ml_pred, pixel_spacing)
                    csv_write.writerow([ipp, np.round(values['SMA'], 2), np.round(values['SMRA'], 2)])
        
        self.message = "Les données ont été exportées dans validation/mesures_valides.csv"

    def list_cases(self, ctype):
        
        clist = [ipp for ipp in wksp.ids if wksp.ids[ipp] == ctype]
        plots = []
        for ipp in clist:
            plots.append(self.thumbnail_widget(ipp))
        layout = row(gridplot(plots, ncols=len(plots), plot_width=256, plot_height=256, toolbar_location=None), css_classes=['viewer'], width=page_width, height=305)
        if len(plots) == 0:
            layout = Div(text="<h3>Rien à lister</h3>")

        return layout

    def callback(self, event):
        self.future_data =  self.ipps_ids[event._model_id]
        self._ready_observers[0]() #Hack
        self._is_ready = True

    def thumbnail_widget(self, ipp):
        thumbnail = wksp.thumbnails[ipp]

        p = figure(title=f"Cas n° {ipp}", tools=[], css_classes=['thumb_focus'])
        p.axis.visible = False
        p.image_rgba(image=[thumbnail[::-1,:,:]], x=[0], y=[0], dh=[1], dw=[1])
        p.on_event(events.Tap, self.callback)
        self.ipps_ids[p._id] = ipp
        
        return p