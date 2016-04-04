import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import cv2, logging, wx


### Wx ###
class View(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Live Registration")
        
        self.sub_names = []
        
        # Leftmost panel
        self.panel_left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.add_sub_button = wx.Button(self, label='Add Subject')
        self.but_load = wx.Button(self, label='Load Subject')
        self.but_reg = wx.Button(self, label='Register')
        self.sub_box = wx.ListBox(self)
        self.panel_left_sizer.Add(self.but_load)
        self.panel_left_sizer.Add(self.but_reg)
        self.panel_left_sizer.Add(self.add_sub_button)
        self.panel_left_sizer.Add(self.sub_box, flag=wx.EXPAND|wx.ALL, proportion=1)
        
        # main view sizers
        self.sizer_main = wx.BoxSizer(wx.HORIZONTAL)

        self.sizer_main.Add(self.panel_left_sizer, flag=wx.EXPAND|wx.ALL, proportion=1)

        self.SetSizer(self.sizer_main)

        self.Show()
        self.Layout()
    def add_sub(self, s):
        if not isinstance(s, list):
            s = [s]
        self.sub_names += s
        self.sub_names = sorted(self.sub_names)
        self.sub_box.Clear()
        if self.sub_names:
            self.sub_box.InsertItems(items=self.sub_names, pos=0)

