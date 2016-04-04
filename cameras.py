import flycapture2 as fc2
import threading, time, os, sys
import numpy as np

class Camera():
    def __init__(self):
        self.c = fc2.Context()
        self.c.connect(*self.c.get_camera_from_index(0))
        self.c.start_capture()
        self.img = fc2.Image()
        self.c.retrieve_buffer(self.img)
    def get(self, n=3):
        ims = []
        for i in range(n):
            self.c.retrieve_buffer(self.img)
            ims.append(np.asarray(self.img))
            time.sleep(0.030)
        return np.mean(ims, axis=0).astype(np.uint8)
    def end(self):
        self.c.stop_capture()
        self.c.disconnect()
