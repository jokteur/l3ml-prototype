import numpy as np

def apply_mask_on_im(im, mask):
    im = im.astype(np.float)
    ret_im = np.stack((im + 60*mask, im, im, np.ones(im.shape)*255), axis=2)
    ret_im = np.clip(ret_im, 0, 255)
    return ret_im.astype(np.uint8)

def muscle_mask(hu_image):
    #Shift the values such that 0 is equal to no data
    min_value = np.min(hu_image)
    hu_image = hu_image - min_value

    mask = (hu_image < -29 - min_value) | (hu_image > 150 - min_value)

    return mask

def measurements(hu_image, prediction, pixel_spacing):
    #Shift the values such that 0 is equal to no data
    min_value = np.min(hu_image)
    hu_image = hu_image - min_value
    thresholded_image = prediction.astype(float)*hu_image

    mask = (thresholded_image < -29 - min_value) | (thresholded_image > 150 - min_value)

    SMRA = np.mean(thresholded_image[~mask] + min_value)

    thresholded_image[~mask] = 1
    thresholded_image[mask] = 0


    #Calculate the resulting coefficient to measure
    average_pixel_spacing = .5*(pixel_spacing[0]+pixel_spacing[1])
    SMA = np.count_nonzero(thresholded_image)*pixel_spacing[0]*pixel_spacing[1]

    measurements = dict({
        'SMA': SMA/100,
        'SMRA': SMRA,
        'Pixel spacing': pixel_spacing
    })
    return measurements