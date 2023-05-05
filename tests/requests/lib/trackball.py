"""
Trackball Driver

Trackball:
    https://shop.pimoroni.com/products/trackball-breakout
Code reference:
    https://github.com/jspinella/pimoroni-trackball-circuitpy
"""
from adafruit_bus_device.i2c_device import I2CDevice

I2C_ADDRESS = 0x0A

REG_LED_RED = 0x00
REG_LED_GRN = 0x01
REG_LED_BLU = 0x02
REG_LED_WHT = 0x03

REG_LEFT = 0x04
REG_RIGHT = 0x05
REG_UP = 0x06
REG_DOWN = 0x07

class TrackBall(I2CDevice):
    def __init__(self, i2c_bus, address=I2C_ADDRESS):
        super().__init__(i2c_bus, address)

    def set_leds(self, r,g,b,w):
        self.write(bytes([REG_LED_RED, r & 0xff]))
        self.write(bytes([REG_LED_GRN, g & 0xff]))
        self.write(bytes([REG_LED_BLU, b & 0xff]))
        self.write(bytes([REG_LED_WHT, w & 0xff]))
    
    def set_leds_purple(self): self.set_leds(60,0,90,20)
    def set_leds_orange(self): self.set_leds(99,63,8,0)
    def set_leds_yellow(self): self.set_leds(100,85,6,0)
    def set_leds_white(self): self.set_leds(0,0,0,100)
    
    def i2c_rdwr(self, data, length=0):
        """Write and optionally read I2C data."""
        
        self.i2c.try_lock()
        self.write(bytes(data))
    
        if length > 0:
            msg_r = bytearray(length)
            self.readinto(msg_r)
            result = list(msg_r)
        else:
            result = []
            
        self.i2c.unlock()
        return result
    
    def read(self):
        """Read up, down, left, right and switch data from trackball."""
        left, right, up, down, switch = self.i2c_rdwr([REG_LEFT], 5)
    
        switch = 129 == switch
    
        return up, down, left, right, switch
