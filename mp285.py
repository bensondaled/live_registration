import numpy as np
import serial, struct, warnings

class MP285():
    ABS,REL = 0,1
    def __init__(self, port='COM1', baudrate=9600, timeout=60):
        self.ser = serial.Serial(port=port, baudrate=baudrate, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=timeout)

	def get_pos(self):
		self.ser.write('c\r')
		pos = self.ser.read(13)
		pos = np.array(struct.unpack('lll', pos[:12]))
		return pos

    def goto(self, pos):
        assert len(pos)==3
		pos = struct.pack('lll', *pos)
		self.ser.write('m'+pos+'\r')
        self._wait()

    def set_mode(self, mode):
        # MP285.ABS or MP285.REL
        ch = {self.ABS:'a', self.REL:'b'} 
        self.ser.write(ch[mode]+'\r')
        self._wait()

    def zero(self):
        self.ser.write('o\r')
        self._wait()

    def refresh(self):
        self.ser.write('n\r')
        self._wait()

    def _wait(self):
        ret = self.ser.read(1)
        if ret != '\r':
            warnings.warn('Failure to receive reply from device.')

    def reset(self):
        self.ser.write('r\r')

    def end(self):
        self.ser.close()
