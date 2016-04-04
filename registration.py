import numpy as np
import cv2, time
import itertools as it
import pylab as pl

def cut_black(im):
    imb = cv2.medianBlur(im, 9)
    nonzero_y,nonzero_x = np.where(imb>30)
    return im[nonzero_y.min():nonzero_y.max(), nonzero_x.min():nonzero_x.max()]

def register_imgs(tmp, cam, ctrl):
    pad = 130
    tmp = cut_black(tmp)
    tmp = tmp[pad:-pad,pad:-pad]
    fr = cut_black(cam.get())
    corr = cv2.matchTemplate(fr, tmp, cv2.TM_CCORR_NORMED)
    pl.subplot(2,2,1)
    pl.imshow(corr)
    pl.subplot(2,2,2)
    pl.imshow(fr)
    pl.subplot(2,2,3)
    pl.imshow(tmp)