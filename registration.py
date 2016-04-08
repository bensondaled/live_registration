import numpy as np
import cv2, time
import pylab as pl

def cut_black(im):
    imb = cv2.medianBlur(im, 9)
    nonzero_y,nonzero_x = np.where(imb>30)
    return im[nonzero_y.min():nonzero_y.max(), nonzero_x.min():nonzero_x.max()]

def register_imgs(tmp, cam):
    pad = 200
    #tmp = cut_black(tmp)
    tmp = tmp[pad:-pad,pad:-pad]
    #fr = cut_black(cam.get())
    fr = cam.get(n=5)
    corr = cv2.matchTemplate(fr, tmp, cv2.TM_CCORR_NORMED)
    #pl.subplot(2,2,1)
    #pl.imshow(corr)
    #pl.subplot(2,2,2)
    #pl.imshow(fr)
    #pl.subplot(2,2,3)
    #pl.imshow(tmp)
    best_idx = np.unravel_index(np.argmax(corr), corr.shape)
    best_idx = np.asarray(best_idx)
    best_idx -= pad
    return -best_idx, np.max(corr)
    
def apply_registration(r, ctrl, calib):
    # calib is in pixels per micron
    ctrl.zero(warn=False)
    #print ctrl.get_pos()
    #print calib
    pos = r/calib
    if len(pos)==2:
        pos = np.append(pos,0)
    ctrl.goto(pos)
    #print ctrl.get_pos()
    ctrl.zero(warn=True)