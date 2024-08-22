import os
import csv
import imageio
import numpy as np
from bokeh.models.widgets import PreText, TextInput, Div, Button
from bokeh.layouts import column, row
from bokeh.layouts import gridplot
from bokeh.plotting import figure
from bokeh import events

from src.workspace import Workspace
from src.constants import page_width
from src.interfaces.AbstractPanel import AbstractPanel
from src.image_processing import measurements

wksp = Workspace()
thumb_size = 128
num_cases_per_layout = 4

class MainInterface(AbstractPanel):
    """"""
    def __init__(self, title='Start', data=None):
        """"""

        AbstractPanel.__init__(self, title=title)

        wksp.update()
        
        self.cases_infos = {
            'n': [[ipp for ipp in wksp.ids if wksp.ids[ipp] == 'non_modified'], 0],
            'm': [[ipp for ipp in wksp.ids if wksp.ids[ipp] == 'modified'], 0],
            'v': [[ipp for ipp in wksp.ids if wksp.ids[ipp] == 'validated'], 0],
        }
        
        preamble = Div(text="""Cliquer sur une image pour l'ouvrir""")

        self.n_len = len(self.cases_infos['n'][0])
        self.m_len = len(self.cases_infos['m'][0])
        self.v_len = len(self.cases_infos['v'][0])

        title1 = Div(text=f"<h2>Cas non-modifiés ({self.n_len})</h2>")
        title2 = Div(text=f"<h2>Cas retouchés ({self.m_len})</h2>")
        title3 = Div(text=f"<h2>Cas validés ({self.v_len})</h2>")

        self.ipps_ids = dict({})

        self.buttons_ids = {}

        self.button_dict = {}
        
        # Grid layout for non-modified
        non_modified_plots = self.list_cases('n', 0)

        self.button_dict['n_n'] = Button(label=f"Cas suivants ({np.max([self.n_len - num_cases_per_layout, 0])})", width=200)
        self.button_dict['n_p'] = Button(label="Cas précédents (0)", width=200)
        self.button_dict['n_jn'] = Button(label="+ 40", width=50)
        self.button_dict['n_jp'] = Button(label="- 40", width=50)

        non_modified_layout = column(row(self.button_dict['n_jp'], self.button_dict['n_p'], self.button_dict['n_n'], self.button_dict['n_jn']), non_modified_plots)

        # Grid layout for non-modified
        modified_plots = self.list_cases('m', 0)
        self.button_dict['m_n'] = Button(label=f"Cas suivants ({np.max([self.m_len - num_cases_per_layout, 0])})", width=200)
        self.button_dict['m_p'] = Button(label="Cas précédents (0)", width=200)
        self.button_dict['m_jn'] = Button(label="+ 40", width=50)
        self.button_dict['m_jp'] = Button(label="- 40", width=50)

        modified_layout = column(row(self.button_dict['m_jp'], self.button_dict['m_p'], self.button_dict['m_n'], self.button_dict['m_jn']), modified_plots)

        # Grid layout for non-modified
        validated_plots = self.list_cases('v', 0)
        self.button_dict['v_n'] = Button(label=f"Cas suivants ({np.max([self.v_len - num_cases_per_layout, 0])})", width=200)
        self.button_dict['v_p'] = Button(label="Cas précédents (0)", width=200)
        self.button_dict['v_jn'] = Button(label="+ 40", width=50)
        self.button_dict['v_jp'] = Button(label="- 40", width=50)

        validated_layout = column(row(self.button_dict['v_jp'], self.button_dict['v_p'], self.button_dict['v_n'], self.button_dict['v_jn']), validated_plots)


        # Assign actions and ids to buttons
        for key in self.button_dict:
            self.buttons_ids[self.button_dict[key].id] = key

        for button in self.button_dict.values():
            button.on_click(self.button_event)

        export_b = Button(label="Exporter les mesures validées en csv", button_type="success", width=300)
        export_b.on_click(self.export_csv)

        self.panel = column(preamble, title1, non_modified_layout,
            title2, modified_layout,
            title3, export_b, validated_layout, width=page_width)

    def change_idx(self, ctype, action, num=num_cases_per_layout):
        clen = len(self.cases_infos[ctype][0])
        idx = self.cases_infos[ctype][1]
        
        if action[-1] == 'n':
            if idx + num < clen:
                self.cases_infos[ctype][1] += num
        else:
            self.cases_infos[ctype][1] = np.max([idx - num, 0])

    def button_event(self, *events):
        action_desc = self.buttons_ids[events[0]._model_id]
        ctype = action_desc[0]
        if action_desc[-2] == 'j':
            self.change_idx(ctype, action_desc[-1], 40)
        else:
            self.change_idx(ctype, action_desc[-1])

        idx = self.cases_infos[ctype][1]
        layout = self.list_cases(ctype, idx)

        layout_index = 7
        self.button_dict[ctype+'_p'].label = f"Cas précédents ({idx})"
        self.button_dict[ctype+'_n'].label = f"Cas suivants ({np.max([len(self.cases_infos[ctype][0]) - num_cases_per_layout - idx, 0])})"
        if ctype == 'n':
            layout_index = 2
        elif ctype == 'm':
            layout_index = 4
        
        self.panel.children[layout_index].children[1] = layout

    def export_csv(self, *events):
        with open(os.path.join(wksp.path, 'validation', 'mesures_valides.csv'), 'w', newline='') as csvfile:
            csv_write = csv.writer(csvfile, delimiter=';', quotechar='"')
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

    def list_cases(self, ctype, b_idx):
        clist = self.cases_infos[ctype][0]

        if len(clist) == 0:
            return Div(text="<h3>Rien à lister</h3>")

        plots = []

        slide_idx = np.min([len(clist), b_idx + num_cases_per_layout])
        for ipp in clist[b_idx:slide_idx]:
            plots.append(self.thumbnail_widget(ipp))
        layout = row(gridplot(plots, ncols=len(plots), plot_width=256, plot_height=256, toolbar_location=None), css_classes=['viewer'], width=page_width, height=305)

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