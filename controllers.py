import threading, wx, time, sys, logging, Queue, os, cv2, re
import numpy as np
from cameras import Camera
from mp285 import MP285
from views import View
from registration import register_imgs, apply_registration

class Controller:

    REFRESH_INTERVAL = 100 #ms
    NEW,EXISTS = 0,1

    def __init__(self, data_dir=r'D:\\deverett', wf_calib_path=r'C:\\WF\\calibration.npy'):
        # Make app
        self.app = wx.App(False) 

        self.view = View(None)

        self.view.Bind(wx.EVT_CLOSE, self.evt_close)
        
        # Button bindings
        self.view.add_sub_button.Bind(wx.EVT_BUTTON, self.evt_addsub)
        self.view.but_load.Bind(wx.EVT_BUTTON, self.evt_load)
        self.view.but_reg.Bind(wx.EVT_BUTTON, self.evt_reg)
        self.view.but_freg.Bind(wx.EVT_BUTTON, self.evt_freg)
        
        # load initial info
        self.data_dir = data_dir
        subs = os.listdir(self.data_dir)
        self.view.add_sub(subs)
        try:
            self.calibration = np.load(wf_calib_path)
        except FileNotFoundError:
            raise Exception('Calibration file not found. Please calibrate before registering.')
        
        # runtime
        self.cam = Camera()
        self.mp285 = MP285()
        self.current_sub = None
        self.register_mode = None
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
    def get_paths(self, sub):
        if not os.path.exists(os.path.join(self.data_dir, self.current_sub)):
            os.mkdir(os.path.join(self.data_dir, self.current_sub))
        subdir = os.path.join(self.data_dir, self.current_sub)
        fov_files = [re.match('fov_(\d*)_.*.npy',f) for f in os.listdir(subdir)]
        date = time.strftime('%Y%m%d')
        if not any(fov_files):
            idx = -1
            cpath = None
        else:
            idx = max([int(i) for i in fov_files])
            cpath = os.path.join(self.data_dir,self.current_sub,'fov_{:03d}_{}.npy'.format(idx, date))
        npath = os.path.join(self.data_dir,self.current_sub,'fov_{:03d}_{}.npy'.format(idx+1, date))
        return cpath,npath
    def evt_load(self, evt):
        sub = self.view.sub_box.GetSelection()
        if sub == wx.NOT_FOUND:
            return
        self.current_sub = self.view.sub_names[sub]
        self.current_path,self.next_path = self.get_paths(self.current_sub)
        if self.current_path:
            self.register_mode = self.EXISTS
            self.template = np.load(self.current_path)
        elif not self.current_path:
            self.register_mode = self.NEW
            self.template = np.zeros(self.cam.frame_shape)
        self.imshow('Existing Template: {}'.format(self.current_sub),self.template)
    def evt_reg(self, evt):
        if self.register_mode is None:
            return
        if self.register_mode == self.NEW:
            result = self.cam.get(n=5)
            np.save(self.next_path, result)
        elif self.register_mode == self.EXISTS:
            self.update_timer.Stop()
            reg = register_imgs(self.template, self.cam)
            apply_registration(reg, self.mp285, self.calibration)
            result = self.cam.get(n=5)
            np.save(self.next_path, result)
            self.update_timer = wx.CallLater(self.REFRESH_INTERVAL, self.update)
        self.imshow('New Template: {}'.format(self.current_sub), result)
        diff = np.abs(result-self.template)
        diff = diff/diff.max()
        self.imshow('Diff: {} (normalized)'.format(self.current_sub), diff)
        self.register_mode = None
    def evt_freg(self, evt):
        if self.register_mode is None:
            return
        if self.register_mode == self.NEW:
            result = self.cam.get(n=5)
            np.save(self.next_path, result)
        elif self.register_mode == self.EXISTS:
            self.update_timer.Stop()
            # note no registration process occurs here; this is forced registration
            result = self.cam.get(n=5)
            np.save(self.next_path, result)
            self.update_timer = wx.CallLater(self.REFRESH_INTERVAL, self.update)
        self.imshow('New Template: {}'.format(self.current_sub), result)
        diff = np.abs(result-self.template)
        diff = diff/diff.max()
        self.imshow('Diff: {} (normalized)'.format(self.current_sub), diff)
        self.register_mode = None

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
