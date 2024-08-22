__GPU__ = False
import os
if not __GPU__:
    os.environ['CUDA_VISIBLE_DEVICES']='-1'
from keras.optimizers import Adam, SGD
from keras.models import model_from_json
import keras.backend as K

smooth = 1e-5
def dice_coef(y_true, y_pred):
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)
def dice_coef_loss(y_true, y_pred):
    return dice_coef(y_true, y_pred)

def load_trained_model(model_json, model_weights):
    """
    """

    json_file = open(model_json, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.compile(loss='binary_crossentropy',  optimizer=Adam(lr=1e-4), metrics=['acc', dice_coef_loss])
    model.load_weights(model_weights)
    return model
