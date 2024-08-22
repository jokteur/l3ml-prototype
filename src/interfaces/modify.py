import os
import imageio
import numpy as np
from PIL import Image, ImageDraw
from bokeh import events
from skimage import filters
from bokeh.models.widgets import PreText, TextInput, Div, RadioButtonGroup, Select, AutocompleteInput, Button
from bokeh.layouts import column, row, layout, gridplot, GridSpec
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.tools import WheelZoomTool, PanTool, LassoSelectTool, SaveTool, ResetTool, HoverTool

from src.workspace import Workspace
from src.constants import page_width
from src.interfaces.AbstractPanel import AbstractPanel
from src.image_processing import apply_mask_on_im, muscle_mask, measurements
from src.constants import page_width

wksp = Workspace()
thumb_size = 128

translation = {'modified': '(modifié)', 'validated': '(validé)', 'non_modified': '(non modifié)'}

class Modify(AbstractPanel):
    """"""
    def __init__(self, title='Start', data=None):
        """"""

        AbstractPanel.__init__(self, title=title)

        wksp.update()

        if data == None:
            data = wksp.ids_list[0]
        
        c_select = Div(text="""Cliquer sur une image pour l'ouvrir""")
        self.title2 = Div(text=f"<h2>Cas n° {data} {translation[wksp.ids[data]]}</h2>")
        select = Div(text=f'Selectionner cas :')

        text1 = Div(text="<h2>Actions</h2>")
        text2 = Div(text="Masque :")
        text3 = Div(text="Actions sur le cas :")
        text4 = Div(text="<h2>Mesures</h2>")
        self.text5 = Div(text=f"(cm^2)")
        self.text6 = Div(text=f"(HU)")

        self.ipps_ids = dict({})
        self.ipp = data

        self.toggle_b = RadioButtonGroup(
        name='Mode', labels=['Ajouter', 'Supprimer'], button_type='primary')
        self.toggle_b.on_click(self.toggle_callback)

        back_b = Button(label="Retour menu principal")
        back_b.on_click(self.back_callback)
        prev_b = Button(label="Précédent")
        prev_b.on_click(self.prev_callback)
        next_b = Button(label="Suivant")
        next_b.on_click(self.next_callback)

        reset = Button(label="Effacer modifications", button_type='danger')
        reset.on_click(self.reset_callback)
        self.validate = Button(label="Valider cas", button_type='success')
        self.validate.on_click(self.validate_callback)

        self.toggle = False
        
        # Grid layout for non-modified
        c_select = self.c_select()
        p_im, p_seg, p_masked = self.edit_image(self.ipp)

        self.panel = row(
            column(
                row(self.title2),
                row(column(p_masked, row(p_im, p_seg), css_classes=['overflow_h']))
                ),
            column(text1, back_b, select, c_select, 
                    row(prev_b, next_b, width=300), text2, self.toggle_b,
                    text3, row(reset, self.validate, width=300),
                    text4, row(self.text5, self.text6), width=300
                )
        )

        self.make_measurements()
                    
    def back_callback(self, *events):
        self.goto = 'main_interface'
    def prev_callback(self, *events):
        j = 0
        for i, ipp in enumerate(wksp.ids_list):
            if self.ipp == ipp:
                j = i
                break
        self.reload_data(wksp.ids_list[j - 1])
    def next_callback(self, *events):
        j = 0
        for i, ipp in enumerate(wksp.ids_list):
            if self.ipp == ipp:
                j = i
                break
        if j == len(wksp.ids_list) - 1:
            self.reload_data(wksp.ids_list[0])
        else:
            self.reload_data(wksp.ids_list[j + 1])
    def reset_callback(self, *events):
        self.validate.label = 'Valider cas'
        self.validate.button_type = 'success'
        wksp.erase_modifications(self.ipp)
        self.reload_data(self.ipp)

    def validate_callback(self, *events):
        if wksp.ids[self.ipp] == 'validated':
            self.validate.label = 'Valider cas'
            self.validate.button_type = 'success'
            wksp.devalidate(self.ipp)
            self.reload_data(self.ipp)
        else:
            self.validate.label = 'Dévalider cas'
            self.validate.button_type = 'warning'
            wksp.validate(self.ipp, self.masked)
            self.reload_data(self.ipp)
    def c_select(self):
        # ==============
        # Selection of case
        # ==============
        selected = Select(name='Selectionner cas', options=list(wksp.ids.keys()), width=100)
        autocomplet = AutocompleteInput(name='ou taper l\'id :', completions=list(wksp.ids.keys()), placeholder='N° ipp', width=100)

        selected.on_change('value', self.select_callback)
        autocomplet.on_change('value', self.select_callback)

        plots = []
        """for ipp in wksp.ids:
            plots.append(self.thumbnail_widget(ipp))
        size = 256
        layout = row(gridplot(plots, ncols=1, plot_width=size, plot_height=size, toolbar_location=None), css_classes=['viewer2'])
        if len(plots) == 0:
            layout = Div(text="<h3>Rien à lister</h3>")"""

        return row(selected, autocomplet)

    def toggle_callback(self, *events):
        self.toggle = bool(events[0])
    
    def draw_callback(self, event):
        if event.final:
            x_length = self.masked.shape[0]
            y_length = self.masked.shape[1]

            # Extract polygon drawn
            x = list(event.geometry['x'].values())
            y = list(event.geometry['y'].values())
            polygon = list(zip(x, y))

            mask = Image.new('L', (x_length, y_length), 0)
            ImageDraw.Draw(mask).polygon(polygon, outline=1, fill=1)

            mask = np.array(mask)
            if self.toggle:
                self.ml_pred = np.logical_xor(np.logical_and(self.ml_pred, mask), self.ml_pred)
            else:
                mask = np.logical_and(mask, ~self.muscle_mask)
                self.ml_pred = np.logical_or(self.ml_pred, mask)

            self.masked = apply_mask_on_im(self.im, self.ml_pred)
            self.ds_ml_segm.data = dict(image=[self.ml_pred[::-1,:]],
                x=[0], y=[y_length], dh=[y_length], dw=[x_length])
            self.ds_finalImg.data = dict(image=[self.masked[::-1,:]],
                x=[0], y=[y_length], dh=[y_length], dw=[x_length])

            if wksp.ids[self.ipp] == 'validated':
                np.save(os.path.join(wksp.validated_masks_dir, self.ipp), self.ml_pred)
                imageio.imsave(os.path.join(wksp.validated_images_dir, self.ipp + '.png'), self.masked)
            else:
                np.save(os.path.join(wksp.temp_masks_dir, self.ipp), self.ml_pred)
                wksp.ids[self.ipp] = 'modified'
                self.title2.text = f"<h2>Cas n° {self.ipp} {translation[wksp.ids[self.ipp]]}</h2>"

            wksp.make_thumbnail(self.ipp)
            self.make_measurements()
    
    def make_measurements(self):
        values = measurements(self.hu_image, self.ml_pred, self.pixel_spacing)
        wksp.measurements[self.ipp] = values

        self.text5.text = f"SMA : {values['SMA']:.2f} (cm^2)"
        self.text6.text = f"SMRA : {values['SMRA']:.2f} (HU)"


    def callback(self, event):
        self.ipp = self.ipps_ids[event._model_id]
        self.reload_data(self.ipp)

    def thumbnail_widget(self, ipp):
        thumbnail = wksp.thumbnails[ipp]

        p = figure(title=f"Cas n° {ipp}", tools=[], css_classes=['thumb_focus'])
        p.axis.visible = False
        p.image_rgba(image=[thumbnail[::-1,:,:]], x=[0], y=[0], dh=[1], dw=[1])
        p.on_event(events.Tap, self.callback)
        self.ipps_ids[p._id] = ipp
        
        return p

    def load_data(self, ipp):
        seg_path_folder = wksp.masks_dir
        if wksp.ids[ipp] == 'modified':
            self.validate.label = 'Valider cas'
            self.validate.button_type = 'success'
            seg_path_folder = wksp.temp_masks_dir
        elif wksp.ids[ipp] == 'validated':
            self.validate.label = 'Dévalider cas'
            self.validate.button_type = 'warning'
            seg_path_folder = wksp.validated_masks_dir
        else:
            self.validate.label = 'Valider cas'
            self.validate.button_type = 'success'

        segmentation = np.load(os.path.join(seg_path_folder, ipp + '.npy'), allow_pickle=True)
        image = imageio.imread(os.path.join(wksp.images_dir, ipp + '.png'))[:,:,0]
        data = np.load(os.path.join(wksp.npy_dir, ipp + '.npy'), allow_pickle=True)
        self.hu_image = data[0]
        self.pixel_spacing = data[1]

        masked = apply_mask_on_im(image, segmentation)

        muscl_mask = muscle_mask(self.hu_image)
        muscle_im = np.copy(image)
        muscle_im[muscl_mask] = 0

        #Segmentation
        block_size = 21
        local_thresh = filters.threshold_sauvola(muscle_im, block_size)#filters.threshold_local(muscle_im, block_size, offset=10)
        binary_local = muscle_im > local_thresh

        self.im, self.ml_pred, self.masked, self.muscle_mask = image, segmentation, masked, muscl_mask

    def reload_data(self, ipp):
        self.ipp = ipp
        self.load_data(ipp)
        self.title2.text = f"<h2>Cas n° {ipp} {translation[wksp.ids[ipp]]}</h2>"

        x_length = self.masked.shape[0]
        y_length = self.masked.shape[1]

        self.ds_im.data = dict(image=[self.im[::-1,:]],
            x=[0], y=[y_length], dh=[y_length], dw=[x_length])
        self.ds_ml_segm.data = dict(image=[self.ml_pred[::-1,:]],
            x=[0], y=[y_length], dh=[y_length], dw=[x_length])
        self.ds_finalImg.data = dict(image=[self.masked[::-1,:]],
            x=[0], y=[y_length], dh=[y_length], dw=[x_length])

        self.make_measurements()

    def select_callback(self, attr, old, new):
        self.reload_data(new)

    def edit_image(self, ipp):

        width = 600
        halfwidth = int(width/2)
        self.load_data(ipp)

        x_length = self.masked.shape[0]
        y_length = self.masked.shape[1]
        
        self.ds_im = ColumnDataSource(dict(image=[self.im[::-1,:]],
            x=[0], y=[y_length], dh=[y_length], dw=[x_length]))

        self.ds_ml_segm = ColumnDataSource(dict(image=[self.ml_pred[::-1,:]],
            x=[0], y=[y_length], dh=[y_length], dw=[x_length]))

        self.ds_finalImg = ColumnDataSource(dict(image=[self.masked[::-1,:,:]],
            x=[0], y=[y_length], dh=[y_length], dw=[x_length]))

        p_im = figure(title='CT',x_range=(0, x_length), y_range=(y_length, 0),
            width=halfwidth, height=halfwidth)
        p_im.image(source=self.ds_im, image='image', x='x', y='y', dh='dh', dw='dw')

        p_seg = figure(title='Masque', x_range=(0, x_length), y_range=(y_length, 0),
            width=halfwidth, height=halfwidth)
        p_seg.image(source=self.ds_ml_segm, image='image', x='x', y='y', dh='dh', dw='dw')

        lasso_select = LassoSelectTool()
        wheel_zoom = WheelZoomTool()
        pan_tool = PanTool()
        lasso_select = LassoSelectTool()
        save_tool = SaveTool()
        reset_tool = ResetTool()

        TOOLTIPS = [
            ("(x, y)", "($x{0}, $y{0})"),
            ("value", "@image")]
        hover = HoverTool(tooltips=TOOLTIPS)

        p_masked = figure(title=f'CT + masque', x_range=[0, x_length], y_range=[y_length, 0],
            width=width, height=width,
            tools=[lasso_select, wheel_zoom, pan_tool, save_tool, reset_tool])
        p_masked.image_rgba(source=self.ds_finalImg, image='image', x='x', y='y', dh='dh', dw='dw')

        p_masked.toolbar.active_drag = None
        p_masked.on_event(events.SelectionGeometry, self.draw_callback)

        return p_im, p_seg, p_masked