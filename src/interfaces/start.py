import os
from bokeh.models.widgets import PreText, TextInput, Div
from bokeh.layouts import column

from src.workspace import Workspace, verify
from src.interfaces.AbstractPanel import AbstractPanel
class Start(AbstractPanel):
    """"""
    def __init__(self, title='Start', data=None):
        """"""

        AbstractPanel.__init__(self, title=title)

        title = Div(text="""<h1>Charger des données</h1>""")
        text = PreText(text="""Pour commencer, veuillez entrer le chemin du dossier vers les données.

Le dossier devrait contenir au minimum les dossiers suivants :
data/
|...images/
|...npy/
|...masks/""")
        file = TextInput(title="Chemin", value='')

        file.on_change('value', self.verify_workspace)

        self.panel = column(title, text, file)
        
        self._is_ready = True

    def verify_workspace(self, attr, new, old):
        folder = None
        
        if verify(new):
            folder = new
        elif verify(old):
            folder = old
        
        if folder:
            wksp = Workspace()
            wksp.prepare_workspace(folder)
            self.message = ""

            correct_ids = {}
            incorrect_ids = []
            for i, ipp in enumerate(wksp.ids):
                self.message = f"Vérification des données ({i}/{len(wksp.ids)})"

                if os.path.isfile(os.path.join(wksp.masks_dir, ipp + '.npy')) and os.path.isfile(os.path.join(wksp.npy_dir, ipp + '.npy')):
                    correct_ids[ipp] = 'non_modified'
                    
                    if not os.path.isfile(os.path.join(wksp.thumb_dir, ipp + '.png')):
                        wksp.make_thumbnail(ipp)
                else:
                    incorrect_ids.append(ipp)

            self.message = f"Vérification des données ({len(wksp.ids)}/{len(wksp.ids)})"

            if len(incorrect_ids) > 0:
                self.message = f"Certaines données manquaient dans le dossier 'npy' ou 'masks'. <br />Les ids suivantes ont été ignorées :<br /><em>{incorrect_ids}</em>"
            else:
                self.message = ""

            wksp.ids = correct_ids
            self.is_ready = True
        else:
            self.message = "Chemin invalide ou dossier incomplet."
