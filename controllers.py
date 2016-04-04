import threading, wx, time, sys, logging, Queue, os, cv2
import numpy as np
from cameras import Camera
from mp285 import MP285
from views import View
from registration import register_imgs

class Controller:

    REFRESH_INTERVAL = 100 #ms
    NEW,EXISTS = 0,1

    def __init__(self, data_dir='D:\deverett'):
        # Make app
        self.app = wx.App(False) 

        self.view = View(None)

        self.view.Bind(wx.EVT_CLOSE, self.evt_close)
        
        # Button bindings
        self.view.add_sub_button.Bind(wx.EVT_BUTTON, self.evt_addsub)
        self.view.but_load.Bind(wx.EVT_BUTTON, self.evt_load)
        self.view.but_reg.Bind(wx.EVT_BUTTON, self.evt_reg)
        
        # load initial info
        self.data_dir = data_dir
        subs = os.listdir(self.data_dir)
        self.view.add_sub(subs)
        
        # runtime
        self.cam = Camera()
        self.mp285 = MP285()
        self.current_sub = None
        self.register_mode = self.NEW
        self.update()

        # Run
        self.app.MainLoop()
    
    def evt_close(self, evt):
        self.update_timer.Stop()
        self.cam.end()
        self.mp285.end()
        cv2.destroyAllWindows()
        self.view.Destroy()
    def update(self):
        self.imshow('Live Camera',self.cam.get())
        self.update_timer = wx.CallLater(self.REFRESH_INTERVAL, self.update)
    def evt_load(self, evt):
        sub = self.view.sub_box.GetSelection()
        self.current_sub = self.view.sub_names[sub]
        self.current_path = os.path.join(self.data_dir,self.current_sub,'fov_00.npy')
        if os.path.exists(self.current_path):
            self.register_mode = self.EXISTS
            self.template = np.load(self.current_path)
            self.imshow('Template: {}'.format(self.current_sub),self.template)
        elif not os.path.exists(self.current_path):
            self.register_mode = self.NEW
            if not os.path.exists(os.path.join(*os.path.split(self.current_path)[:-1])):
                os.mkdir(os.path.join(*os.path.split(self.current_path)[:-1]))
    def evt_reg(self, evt):
        if self.register_mode == self.NEW:
            np.save(self.current_path, self.cam.get())
        elif self.register_mode == self.EXISTS:
            self.update_timer.Stop()
            register_imgs(self.template, self.cam, self.mp285)
            self.update_timer = wx.CallLater(self.REFRESH_INTERVAL, self.update)

    def evt_addsub(self, evt):
        dlg = wx.TextEntryDialog(self.view, message='Enter new subject name:')
        ret = dlg.ShowModal()
        if ret == wx.ID_OK:
            self.view.add_sub(dlg.GetValue().strip().lower())
        else:
            pass
            
    def imshow(self, win, im):
        im = cv2.resize(im, tuple(np.array(im.shape[::-1])/2))
        cv2.imshow(win, im)
