
# CircuitPython
import displayio
from terminalio import FONT
from vectorio import Rectangle
palette = displayio.Palette(1)
palette[0] = 0xFFFFFF
palette_hidden = displayio.Palette(1)
palette_hidden[0] = 0x000000

# check out https://digital-maker.co.uk/tag/circuitpython
# cheng to vector.io
# Adafruit
from adafruit_display_text import label, wrap_text_to_lines
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.polygon import Polygon
# Mine
from application import Application

class iPod(Application):
    def __init__(self):
        # States
        # buzzer
        self.freq = 0
        # disp
        self.disp_playing = True
        self.disp_cursor = True
        self.disp_bar = 0.5
        
        # display
        self.splash = displayio.Group()
        
        # Title
        self.name_text = label.Label(
            FONT,
            anchor_point = (0.5, 0), # top left
            anchored_position = (64, -3), # position
            text='Now Playing',
            color=0xFFFFFF,
        )
        self.splash.append(self.name_text)
        
        # line under the title
        self.splash.append(Line(0, 15 - 3, 127, 15 - 3, 0xFFFFFF))
        
        # Battery outline
        BAT_W = 15
        BAT_H = 10
        BAT_HEAD = 2
        self.splash.append(Rect(
            x=128 - BAT_W,
            y=0,
            width=BAT_W - 1,
            height=BAT_H,
            fill=0x000000,
            outline=0xFFFFFF,
            stroke=1
        ))
        self.splash.append(Line(126, (BAT_H - BAT_HEAD) // 2, 126, (BAT_H + BAT_HEAD) // 2, 0x000000))
        self.splash.append(Line(127, (BAT_H - BAT_HEAD) // 2 - 1, 127, (BAT_H + BAT_HEAD) // 2 + 1, 0xFFFFFF))
        
        # Battery Level
        BAT_LEVEL = 100
        self.splash.append(Rect(
            x=128 - BAT_W + 1,
            y=1,
            width=(BAT_W - 1 - 2) * BAT_LEVEL // 100,
            height=BAT_H - 2,
            fill=0xFFFFFF,
            outline=0x000000,
            stroke=1
        ))
        
        # Playing
        self.play = Triangle(
            0, 0,
            8, 4,
            0, 8,
            fill=0xFFFFFF,
            outline=0xFFFFFF,
        )
        self.splash.append(self.play)
        
        # Pause
        self.pause = displayio.Group()
        self.pause.append(Rect(
            x=0,
            y=0,
            width=3,
            height=9,
            fill=0xFFFFFF,
            outline=0xFFFFFF,
            stroke=1
        ))
        
        self.pause.append(Rect(
            x=6,
            y=0,
            width=3,
            height=9,
            fill=0xFFFFFF,
            outline=0xFFFFFF,
            stroke=1
        ))
        self.splash.append(self.pause)
        
        # Info
        self.songinfo = label.Label(
            font=FONT,
            line_spacing=0.7,
            text='\n'.join(wrap_text_to_lines(
                # 'Song, Artist, Year, Album if any bla bla bla bla bla bla bla bla bla bla bla bla',
                'hi',
                128 // 6
            )[:4]),
            anchor_point = (0, 0), # top left
            anchored_position = (0, 10), # position
            color=0xFFFFFF,
        )
        self.splash.append(self.songinfo)
        
        # progress bar
        PRO = self.disp_bar
        PRO_Y = 51
        self.splash.append(Rect(
            x=0,
            y=PRO_Y,
            width=128,
            height=3,
            fill=0x000000,
            outline=0xFFFFFF,
            stroke=1
        ))
        self.progress_bar = Rectangle(
            pixel_shader=palette,
            width=int(126 * self.disp_bar),
            height=1,
            x=1,
            y=PRO_Y + 2) # no sure why + 2
        self.splash.append(self.progress_bar)
        
        # Cursor
        self.cursor = Rect(
            x=int(126 * PRO),
            y=PRO_Y - 1,
            width=3,
            height=5,
            fill=0xFFFFFF,
            outline=0xFFFFFF,
            stroke=1
        )
        self.splash.append(self.cursor)
        
        # Time played
        self.note_text = label.Label(
            FONT,
            text='12:34',
            anchor_point = (0, 1), # bottom left
            anchored_position = (0, 63 + 3), # position
            color=0xFFFFFF,
        )
        self.splash.append(self.note_text)
        
        # Time remaining
        self.note_text = label.Label(
            FONT,
            text='01:20:18',
            anchor_point = (1, 1), # bottom right
            anchored_position = (127, 63 + 3), # position
            color=0xFFFFFF,
        )
        self.splash.append(self.note_text)

    def update(self, event):
        if event is None:
            return 0, {}, {}
        # buzzer
        if event.name == 'press':
            # if press
            self.freq = 800
        if event.name == 'release':
            self.freq = 1000
            if event.val == 'down':
                self.disp_playing ^= True
            if event.val == 'center':
                self.disp_cursor ^= True
        if event.name == 'dial':
            self.freq = 10
            self.disp_bar += event.val * 0.02
            self.disp_bar = min(self.disp_bar, 1)
            self.disp_bar = max(self.disp_bar, 0)
        return 0, {}, {}

    def display(self, display, buzzer):
        # OLED
        display.show(self.splash)
        self.play.hidden = not self.disp_playing
        self.pause.hidden = self.disp_playing
        self.cursor.hidden = not self.disp_cursor
        self.progress_bar.pixel_shader = palette_hidden if self.disp_cursor else palette
        self.progress_bar.width=int(126 * self.disp_bar)
        self.cursor.x = int(126 * self.disp_bar) - 1
        # buzzer
        buzzer.beep(freq=self.freq)
        self.freq = 0
        return

    def receive(self, message, memo):
        print("Entered the Item app")
        self.after_name = False
        self.freq = 1200
        self.data = message['data']
        self.key = memo['key']
        return