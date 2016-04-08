from cameras import Camera
from mp285 import MP285
import itertools as it
import numpy as np
import pylab as pl
import cv2
from scipy.stats import linregress

calib_path = r'C:\\WF\\calibration.npz'
mp285 = MP285()
cam = Camera()
mp285.zero(warn=False)
img0 = cam.get(n=5)

ims_x = []
ims_y = []
step = 50
pos = np.arange(-5*step,5*step+1,step)
for i,p in enumerate(pos):
    mp285.goto([p,0,0]) #X
    ims_x.append(cam.get(n=5))
    pl.subplot(4,4,i+1)
    pl.imshow(cam.get(n=5))
for i,p in enumerate(pos):
    mp285.goto([0,p,0]) #Y
    ims_y.append(cam.get(n=5))

mp285.goto([0,0,0])    
cam.end()
mp285.end()

pl.figure()
# determine best shifts
pad = 250
templ = img0[pad:-pad, pad:-pad]
mt_x = [cv2.matchTemplate(i, templ, cv2.TM_CCORR_NORMED) for i in ims_x]
mt_y = [cv2.matchTemplate(i, templ, cv2.TM_CCORR_NORMED) for i in ims_y]
best_x = [np.unravel_index(np.argmax(m), m.shape) for m in mt_x]
best_y = [np.unravel_index(np.argmax(m), m.shape) for m in mt_y]
print np.diff([b[0] for b in best_x])
print np.diff([b[1] for b in best_y])
pl.scatter(pos, [b[0] for b in best_x], color='b', marker='x')
pl.scatter(pos, [b[1] for b in best_y], color='g', alpha=0.3)
pl.title('There should be some decent-looking relationship')
# some checks for consistency, for example r^2 of line if it's linear, which it clearly should be
m_x,yint,r,p,err = linregress(pos, [b[0] for b in best_x])
m_y,yint,r,p,err = linregress(pos, [b[1] for b in best_y])
print 'Calibration complete: {:0.3f} pixels per micrometer in X.'.format(m_x)
print 'Calibration complete: {:0.3f} pixels per micrometer in Y.'.format(m_y)

np.savez(calib_path, pix_per_micron_x=m_x, pix_per_micron_y=m_y)