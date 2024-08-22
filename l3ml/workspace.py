import os
import shutil
import numpy as np
from PIL import Image
import imageio

from l3ml.singleton import Singleton
from l3ml.image_processing import apply_mask_on_im, measurements


def verify(path):
    """"""
    data_dir = os.path.join(path, 'data')
    images_dir = os.path.join(data_dir, 'images')
    masks_dir = os.path.join(data_dir, 'masks')
    npy_dir = os.path.join(data_dir, 'npy')

    return os.path.isdir(images_dir) and os.path.isdir(npy_dir) and os.path.isdir(masks_dir)

class Workspace(metaclass=Singleton):
    """Manages the workspace"""
    def __init__(self):
        1

    def make_thumbnail(self, ipp):
        """"""
        image = imageio.imread(os.path.join(self.images_dir, ipp + '.png'))[:,:,0]
        seg_path_folder = self.masks_dir
        if self.ids[ipp] == 'validated':
            seg_path_folder = self.validated_masks_dir
        elif self.ids[ipp] == 'modified':
            seg_path_folder = self.temp_masks_dir

        mask = np.load(os.path.join(seg_path_folder, ipp + '.npy'))
        image = apply_mask_on_im(image, mask)

        self.thumbnails[ipp] = image
        image = Image.fromarray(image)
        image.thumbnail((256, 256))
        image.save(os.path.join(self.thumb_dir, ipp + '.png'))

    def update(self):
        """"""
        modified = [name[:-4] for name in os.listdir(self.temp_masks_dir)]
        validated = [name[:-4] for name in os.listdir(self.validated_images_dir)]

        for ipp in self.ids:
            if ipp in modified:
                self.ids[ipp] = 'modified'
            if ipp in validated:
                self.ids[ipp] = 'validated'
            if not ipp in self.thumbnails:
                self.thumbnails[ipp] = imageio.imread(os.path.join(self.thumb_dir, ipp + '.png'))

    def validate(self, ipp, image):
        if not self.ids[ipp] == 'validated':
            imageio.imsave(os.path.join(self.validated_images_dir, ipp + '.png'), image)
            if self.ids[ipp] == 'non_modified':
                shutil.copy2(os.path.join(self.masks_dir, ipp + '.npy'), os.path.join(self.validated_masks_dir, ipp + '.npy'))
            else:
                shutil.move(os.path.join(self.temp_masks_dir, ipp + '.npy'), os.path.join(self.validated_masks_dir, ipp + '.npy'))
            self.ids[ipp] = 'validated'

    def devalidate(self, ipp):
        if self.ids[ipp] == 'validated':
            shutil.move(os.path.join(self.validated_masks_dir, ipp + '.npy'), os.path.join(self.temp_masks_dir, ipp + '.npy'))
            os.remove(os.path.join(self.validated_images_dir, ipp + '.png'))
            self.ids[ipp] = 'modified'

    def erase_modifications(self, ipp):
        if self.ids[ipp] == 'validated':
            os.remove(os.path.join(self.validated_images_dir, ipp + '.png'))
            os.remove(os.path.join(self.validated_masks_dir, ipp + '.npy'))
        elif self.ids[ipp] == 'modified':
            os.remove(os.path.join(self.temp_masks_dir, ipp + '.npy'))
        self.ids[ipp] = 'non_modified'
        self.make_thumbnail(ipp)

    def prepare_workspace(self, path):
        """"""
        self.path = path
        self.data_dir = os.path.join(path, 'data')
        self.images_dir = os.path.join(self.data_dir, 'images')
        self.masks_dir = os.path.join(self.data_dir, 'masks')
        self.npy_dir = os.path.join(self.data_dir, 'npy')

        self.misc_dir = os.path.join(path, 'misc')
        self.thumb_dir = os.path.join(path, 'misc', 'thumbnails')
        self.temp_masks_dir = os.path.join(path, 'misc', 'temp')
        self.validated_masks_dir = os.path.join(path, 'validation', 'masks')
        self.validated_images_dir = os.path.join(path, 'validation', 'images')

        os.makedirs(self.misc_dir, exist_ok=True)
        os.makedirs(self.thumb_dir, exist_ok=True)
        os.makedirs(self.temp_masks_dir, exist_ok=True)
        os.makedirs(self.validated_masks_dir, exist_ok=True)
        os.makedirs(self.validated_images_dir, exist_ok=True)

        self.ids_list = [int(name[:-4]) for name in os.listdir(self.images_dir)][:20]
        self.ids_list.sort()
        self.ids_list = [str(ids) for ids in self.ids_list]
        self.ids = {str(i) :'non_modified' for i in self.ids_list}
        self.measurements = {}
        self.thumbnails = {}
