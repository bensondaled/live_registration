from cameras import Camera
from mp285 import MP285
import itertools as it
import numpy as np
import pylab as pl
from scipy.stats import linregress

calib_path = r'C:\\WF\\calibration.npy'
mp285 = MP285()
cam = Camera()
mp285.zero(warn=False)
img0 = cam.get(n=5)

ims_x = []
ims_y = []
step = 50
pos = np.arange(-150,151,step)
for p in pos:
    mp285.goto([p,0,0]) #X
    ims_x.append(cam.get(n=5))
    mp285.goto([0,p,0]) #Y
    ims_y.append(cam.get(n=5))

mp285.goto([0,0,0])    
cam.end()
mp285.end()

# determine best shifts
pad = 30
templ = img0[pad:-pad, pad:-pad]
mt_x = [cv2.matchTemplate(i, templ, cv2.TM_CCORR_NORMED) for i in ims_x]
mt_y = [cv2.matchTemplate(i, templ, cv2.TM_CCORR_NORMED) for i in ims_y]
best_x = [np.unravel_index(np.argmax(m), m.shape) for m in mt_x]
best_y = [np.unravel_index(np.argmax(m), m.shape) for m in mt_y]
print 'these should be exactly {}:'.format(pad)
print [b[0] for b in best_x]
print 'these should also be exactly {}:'.format(pad)
print [b[1] for b in best_y]
pl.scatter(pos, [b[1] for b in best_x], color='b')
pl.scatter(pos, [b[0] for b in best_y], color='g')
pl.title('There should be some decent-looking relationship')
# some checks for consistency, for example r^2 of line if it's linear, which it clearly should be
regx = np.append(pos,pos)
regy = np.append([b[1] for b in best_x], [b[0] for b in best_y])
m,yint,r,p,err = linregress(regx, regy)
calib = m
print 'Calibration complete: {:0.3f} pixels per micrometer.'.format(calib)

np.save(calib_path, calib)