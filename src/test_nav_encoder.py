# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
CircuitPython ANO Rotary Encoder and NeoPixel Ring example.
"""
import board
import digitalio
import rotaryio

# The pin assignments for the breakout pins. Update this is you are not using a Feather.

# ENCA = board.SDA
# ENCB = board.SCL
# COMA = board.D5
# SW1 = board.D6
# SW2 = board.D9
# SW3 = board.D10
# SW4 = board.D11
# SW5 = board.D12
# COMB = board.D13

ENCA = board.D13
ENCB = board.D12
COMA = board.D11
SW1 = board.D10
SW2 = board.D9
SW3 = board.D6
SW4 = board.D5
SW5 = board.SCL
COMB = board.SDA

# Rotary encoder setup
encoder = rotaryio.IncrementalEncoder(ENCA, ENCB)
last_position = None

# Set the COMA and COMB pins LOW. This is only necessary when using the direct-to-Feather or other
# GPIO-based wiring method. If connecting COMA and COMB to ground, you do not need to include this.
com_a = digitalio.DigitalInOut(COMA)
com_a.switch_to_output()
com_a = False
com_b = digitalio.DigitalInOut(COMB)
com_b.switch_to_output()
com_b = False

# Button pin setup
button_pins = (SW1, SW2, SW3, SW4, SW5)
buttons = []
for button_pin in button_pins:
    pin = digitalio.DigitalInOut(button_pin)
    pin.switch_to_input(digitalio.Pull.UP)
    buttons.append(pin)

while True:
    position = encoder.position
    if last_position is None or position != last_position:
        print("Position: {}".format(position))
        last_position = position

    if not buttons[0].value:
        print("Center button!")

    if not buttons[1].value:
        print("Up button!")

    if not buttons[2].value:
        print("Left button!")

    if not buttons[3].value:
        print("Down button!")

    if not buttons[4].value:
        print("Right button!")
