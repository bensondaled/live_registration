import numpy as np
import serial, struct, warnings
import win32api

class MP285():
    ABS,REL = 0,1
    def __init__(self, port='COM1', baudrate=9600, timeout=60, vel=200):
        self.vel = vel
        self.ser = serial.Serial(port=port, baudrate=baudrate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, timeout=timeout)
        self.setup()
    
    def word_to_val(self, w):
        return w[1]*256 + float(w[0])
        
    def setup(self):
        stat = self.get_status()
        self.step_mult = self.word_to_val(stat['step_mult'])
        self.step_div = self.word_to_val(stat['step_div'])
        self.uoffset = self.word_to_val(stat['uoffset'])
        
        self.set_mode(self.REL)
        self.set_velocity(self.vel)
    def get_status(self):
        self.ser.write('s\r')
        stat = self.ser.read(32)
        self._wait()
        stat = struct.unpack(32*'B', stat)
        
        FLAGS,UDIRX,UDIRY,UDIRZ = stat[0:4]
        ROE_VARI = stat[4:6]
        UOFFSET = stat[6:8]
        URANGE = stat[8:10]
        PULSE = stat[10:12]
        USPEED = stat[12:14]
        INDEVICE = stat[14]
        FLAGS_2 = stat[15]
        JUMPS_PD = stat[16:18]
        HIGHSPD = stat[18:20]
        DEAD = stat[20:22]
        WATCH_DOG = stat[22:24]
        STEP_DIV = stat[24:26]
        STEP_MULT = stat[26:28]
        XSPEED = stat[28:30]
        VERSION = stat[30:32]
        
        return dict(step_div=STEP_DIV, step_mult=STEP_MULT, uoffset=UOFFSET)
        
    def get_pos(self):
        self.ser.write('c\r')
        pos = self.ser.read(13)
        pos = np.array(struct.unpack('lll', pos[:12]))
        return pos/self.step_div

    def goto(self, pos):
        assert len(pos)==3
        pos = np.array(pos) * self.step_div
        pos = struct.pack('lll', *pos)
        self.ser.write('m'+pos+'\r')
        self._wait()
        self.refresh()
        
    def set_velocity(self, vel, ustep_resolution=50):
        vel = struct.pack('H', int(vel))
        if ustep_resolution == 50:
            b2 = float(struct.unpack('B', vel[1])[0]) + 128
            vel = vel[0] + struct.pack('B', b2)
        self.ser.write('V'+vel+'\r')
        self._wait()
        self.refresh()
    def set_mode(self, mode):
        # MP285.ABS or MP285.REL
        ch = {self.ABS:'a', self.REL:'b'} 
        self.ser.write(ch[mode]+'\r')
        self._wait()
        self.refresh()

    def zero(self, warn=True):
        self.ser.write('o\r')
        self._wait()
        self.refresh()
        if warn:
            win32api.MessageBox(0, 'Zero MP285 manually now for smoother experience.', 'MP285', 0x00001000) 

    def refresh(self):
        self.ser.write('n\r')
        self._wait()

    def _wait(self):
        ret = self.ser.read(1)
        if ret != '\r':
            warnings.warn('Failure to receive reply from device.')
        assert self.ser.inWaiting()==0

    def reset(self):
        self.ser.write('r\r')

    def end(self):
        self.ser.close()
