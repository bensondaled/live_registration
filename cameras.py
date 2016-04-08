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
        self.frame_shape = np.asarray(self.img).shape
        self.on = True
        self.complete = False
        self.lock = threading.Lock()
        threading.Thread(target=self._continuous).start()
    def _continuous(self):
        while self.on:
            with self.lock:
                self.c.retrieve_buffer(self.img)
        self.complete = True
    def get(self, n=3, sleep=0.050):
        with self.lock:
            ims = []
            for i in range(n):
                self.c.retrieve_buffer(self.img)
                ims.append(np.asarray(self.img))
                time.sleep(sleep)
            return np.mean(ims, axis=0).astype(np.uint8)
    def end(self):
        self.on = False
        while not self.complete:
            pass
        self.c.stop_capture()
        self.c.disconnect()
