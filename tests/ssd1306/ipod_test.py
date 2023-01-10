"""
This script is the entry point of all scripts.
Please check the .url files for more help

Github: https://github.com/urfdvw/Password-Keeper/

Platform: Password Keeper Xiao 2040
CircuitPython: 7.2.5

Author: River Wang
Contact: urfdvw@gmail.com
License: GPL3
Date updated: 2022/06/21 (YYYY/MM/DD)
"""
import board

#%% buzzer
from driver import Buzzer
buzzer = Buzzer(board.D10)

#%% clickwheel
from touchwheel import TouchWheelPhysics, TouchWheelEvents
wheel_phy = TouchWheelPhysics(
    up=board.D7,
    down=board.D0,
    left=board.D6,
    right=board.D9,
    center=board.D8,
    # comment the following 2 lines to enter range measuring mode
    pad_max = [2160, 2345, 2160, 1896, 2602] ,
    pad_min = [904, 1239, 862, 879, 910]
)
wheel_events = TouchWheelEvents(
    wheel_phy,
    N=10,
)

#%% define screen
import busio
import displayio
import adafruit_displayio_ssd1306

displayio.release_displays()
oled_reset = None
i2c = busio.I2C(board.SCL, board.SDA, frequency=int(1e6))
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C, reset=oled_reset)
WIDTH = 128
HEIGHT = 64
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT, rotation=180)

#%% USB HID
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse

while True:
    try:
        # Keep trying connect to USB untill success
        # This useful for computer log in after boot.
        mouse = Mouse(usb_hid.devices)
        keyboard = Keyboard(usb_hid.devices)
        break
    except:
        print('\n' * 10 + 'USB not ready\nPlease Wait')

#%% Background apps
from background import FpsControl, FpsMonitor

frame_app = FpsControl(fps=30)
fpsMonitor_app = FpsMonitor(period=10, fps_app=frame_app)

#%% apps
from iPodApp import iPod
app_ipod = iPod()

app = app_ipod # app to start from

#%% Main logic
print('init done')
memo = {}
while True:
    # Background procedures
    fpsMonitor_app()

    # # FPS control
    # if not frame_app():
    #     continue

    # logic
    shift, message, broadcast = app.update(wheel_events.get())
    memo.update(broadcast)
    if shift:
        app.receive(message, memo)

    # display changes
    app.display(display, buzzer)
