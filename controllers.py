import threading, wx, time, sys, logging, Queue, os, cv2, re
import numpy as np
from cameras import Camera
from mp285 import MP285
from views import View
from registration import register_imgs, apply_registration
import pylab as pl
pl.ion()

class Controller:

    REFRESH_INTERVAL = 100 #ms
    NEW,EXISTS = 0,1

    def __init__(self, data_dir=r'D:\\deverett', wf_calib_path=r'C:\\WF\\calibration.npz'):
        # Make app
        self.app = wx.App(False) 

        self.view = View(None)

        self.view.Bind(wx.EVT_CLOSE, self.evt_close)
        
        # Button bindings
        self.view.add_sub_button.Bind(wx.EVT_BUTTON, self.evt_addsub)
        self.view.but_load.Bind(wx.EVT_BUTTON, self.evt_load)
        self.view.but_reg.Bind(wx.EVT_BUTTON, self.evt_reg)
        self.view.but_freg.Bind(wx.EVT_BUTTON, self.evt_freg)
        self.view.but_save.Bind(wx.EVT_BUTTON, self.evt_save)
        
        # load initial info
        self.data_dir = data_dir
        subs = os.listdir(self.data_dir)
        self.view.add_sub(subs)
        try:
            with np.load(wf_calib_path) as cf:
                self.ppm_y = cf['pix_per_micron_y']
                self.ppm_x = cf['pix_per_micron_x']
        except FileNotFoundError:
            raise Exception('Calibration file not found. Please calibrate before registering.')
        
        # runtime
        self.cam = Camera()
        self.mp285 = MP285()
        self.current_sub = None
        self.register_mode = None
        self.result = None
        self.update()

        # Run
        self.app.MainLoop()
    
    def evt_close(self, evt):
        self.update_timer.Stop()
        self.cam.end()
        self.mp285.end()
        cv2.destroyAllWindows()
        pl.close('all')
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
            idx = max([int(i.groups()[0]) for i in fov_files])
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
        self.result = None
    def evt_reg(self, evt):
        if self.register_mode is None:
            return
        if self.register_mode == self.NEW:
            before_reg = self.cam.get(n=5)
            result = self.cam.get(n=5)
            score = 1.0
        elif self.register_mode == self.EXISTS:
            before_reg = self.cam.get(n=5)
            self.update_timer.Stop()
            reg,score = register_imgs(self.template, self.cam)
            apply_registration(reg, self.mp285, np.array([self.ppm_x,self.ppm_y]))
            result = self.cam.get(n=5)
            self.update_timer = wx.CallLater(self.REFRESH_INTERVAL, self.update)
        pl.subplot(2,2,1)
        self.plshow('Loaded Template: {}'.format(self.current_sub), self.template)
        pl.subplot(2,2,2)
        self.plshow('Original FOV today: {}'.format(self.current_sub), before_reg)
        pl.subplot(2,2,3)
        self.plshow('Adjusted FOV (and new template): {}'.format(self.current_sub), result)
        pl.subplot(2,2,4)
        diff = np.abs(result-self.template)
        diff = diff.astype(float)
        self.plshow('Difference b/t old and new fov\nScore: {:0.3f}'.format(score), diff)
        self.register_mode = None
        self.result = result
        dlg = wx.MessageDialog(self.view, 'Remember to save.', 'Registered.', wx.OK)
        _ = dlg.ShowModal()
        dlg.Destroy()
    def evt_save(self, evt):
        if self.result is None:
            return
        np.save(self.next_path, self.result)
    def evt_freg(self, evt):
        if self.register_mode is None:
            return
        if self.register_mode == self.NEW:
            before_reg = self.cam.get(n=5)
            result = self.cam.get(n=5)
            score = 1.0
        elif self.register_mode == self.EXISTS:
            before_reg = self.cam.get(n=5)
            self.update_timer.Stop()
            # note no registration process occurs here; this is forced registration
            result = self.cam.get(n=5)
            self.update_timer = wx.CallLater(self.REFRESH_INTERVAL, self.update)
        pl.subplot(2,2,1)
        self.plshow('Loaded Template: {}'.format(self.current_sub), self.template)
        pl.subplot(2,2,2)
        self.plshow('Original FOV today: {}'.format(self.current_sub), before_reg)
        pl.subplot(2,2,3)
        self.plshow('Adjusted FOV (and new template): {}'.format(self.current_sub), result)
        pl.subplot(2,2,4)
        diff = np.abs(result-self.template)
        diff = diff.astype(float)
        self.plshow('Difference b/t old and new fov', diff)
        self.register_mode = None
        self.result = result

    def evt_addsub(self, evt):
        dlg = wx.TextEntryDialog(self.view, message='Enter new subject name:')
        ret = dlg.ShowModal()
        if ret == wx.ID_OK:
            self.view.add_sub(dlg.GetValue().strip().lower())
        else:
            pass
            
    def imshow(self, win, im):
        im = cv2.resize(im, tuple(np.array(im.shape[::-1])/3))
        cv2.imshow(win, im)
    def plshow(self, txt, im):
        pl.imshow(im, cmap='gray')
        pl.axis('off')
        pl.title(txt)
