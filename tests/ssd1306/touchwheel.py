#%% clickwheel
import touchio
from math import sqrt, atan2, pi
import time
from timetrigger import Timer
from time import monotonic, sleep

class Dict2Obj(object):
    """https://stackoverflow.com/a/1305682"""
    def __init__(self, d):
        for k, v in d.items():
            if isinstance(k, (list, tuple)):
                setattr(self, k, [obj(x) if isinstance(x, dict) else x for x in v])
            else:
                setattr(self, k, obj(v) if isinstance(v, dict) else v)

class Relay:
    def __init__(self, thr):
        self.thr = thr
        self.remain = 0
    # on theta
    def __call__(self, x):
        self.remain += x
        if self.remain > self.thr:
            y = self.remain - self.thr
        elif self.remain < -self.thr:
            y = self.remain + self.thr
        else:
            self.remain *= 0.95
            y = 0
        self.remain = self.remain - y
        return y

def theta_diff(a, b):
    c = a - b
    if c >= pi:
        c -= 2 * pi
    if c < - pi:
        c += 2 * pi
    return c
    
class State:
    def __init__(
        self,
        filter_level=None,  # smoother
        relay_thr=None,  # less shaking
        id=None
    ):
        self.id = id
        self._now = 0
        self.last = 0
        if filter_level is not None:
            self.use_filter = True
            self.alpha = 1 / 2 ** filter_level
        else:
            self.use_filter = False
        if relay_thr is not None:
            self.use_relay = True
            self.relay = Relay(relay_thr)
        else:
            self.use_relay = False
    @property
    def now(self):
        return self._now
        
    @now.setter
    def now(self, new):
        self.last = self._now # _now is the old value now
        # low pass filter
        if self.use_filter:
            new = new * self.alpha \
                      + self._now * (1 - self.alpha)
        # Relay
        diff = new - self.last
        new = self.last + (
            self.relay(diff)
            if self.use_relay else
            diff
        )
        self._now = new
        
    @property
    def diff(self):
        return self._now - self.last
        
class EventQueue:
    def __init__(self):
        self.data = []

    def append(self, given):
        self.data.append(given)

    def get(self):
        if self.data:
            return self.data.pop(0)

    def clear(self):
        self.data = []

    def __len__(self):
        return len(self.data)

    def __bool__(self):
        return bool(self.data)
        
class Event:
    def __init__(self, name, val):
        if name in [
            'press',
            'release',
            'dial',
            'long'
        ]:
            self.name = name
        else:
            raise Exception('bad event ID')
        self.val = val
    def __str__(self):
        return self.name + ' event with value ' + str(self.val)
        
class Dial:
    def __init__(self, N):
        self.N = N
        self.dial_changed = False
        self.last_dial_time = monotonic()
        
    def reset(self, theta):
        self.theta_residual = 0
        self.theta_d = 0
        self.theta_last = theta
        self.dial_changed = False
        
    def update(self, theta):
        self.theta_d = theta_diff(theta, self.theta_last)
        self.theta_residual += self.theta_d
        dial = 0
        while self.theta_residual > pi / self.N:
            self.theta_residual -= 2 * pi / self.N
            dial -= 1
        while self.theta_residual < -pi / self.N:
            self.theta_residual += 2 * pi / self.N
            dial += 1
        if dial:
            self.dial_changed = True
        self.theta_last = theta
        return dial

class TouchWheelPhysics:
    def __init__(
        self,
        up,
        down,
        left,
        right,
        center,
        pad_max = None,
        pad_min = None,
        n_sec = 8,
    ):
        # touch pads
        self.pads = [touchio.TouchIn(p) for p in [
            up,
            down,
            left,
            right,
            center
        ]]
        # range of touch pads
        if pad_max is None or pad_min is None:
            start_time = monotonic()
            pad_max = [0] * 5
            pad_min = [100000] * 5
            while monotonic() - start_time < 5:
                # run the test for 5s
                # in the mean time, slide on the ring for multiple cycles.
                for i in range(5):
                    value = self.pads[i].raw_value
                    pad_max[i] = max(pad_max[i], value)
                    pad_min[i] = min(pad_min[i], value)
                    # print(ring_max, ring_min)
                    sleep(0.1)
            print('pad_max =', pad_max, ',')
            print('pad_min =', pad_min)
            # cancel running the original script
            import sys
            sys.exit()
        else: 
            self.pad_max, self.pad_min = pad_max, pad_min
        # direction constants
        self.alter_x = [0, 0, -1, 1, 0]
        self.alter_y = [1, -1, 0, 0, 0]
        self.alter_z = [0, 0, 0, 0, 1]
        
        # states
        self.filter_level = 1 # not more than 2
        self.relay_thr = 0.5
        self.x = State(filter_level=self.filter_level, relay_thr=self.relay_thr)
        self.y= State(filter_level=self.filter_level, relay_thr=self.relay_thr)
        self.z = State(filter_level=self.filter_level, relay_thr=self.relay_thr)
        
        self.r = State()  # amplitude on the plane
        self.l = State()  # amplitude in the space
        self.theta = State()  # angle on the plane
        self.phi = State()  # angle raised
    
    def get(self):
        # read sensor
        pads_now = [r.raw_value for r in self.pads]
        # conver sensor to weights
        w = [
            (pads_now[i] - self.pad_min[i]) / (self.pad_max[i] - self.pad_min[i])
            for i in range(5)
        ]
        # computer vector sum
        self.x.now = sum([w[i] * self.alter_x[i] for i in range(5)])
        self.y.now = sum([w[i] * self.alter_y[i] for i in range(5)])
        self.z.now = sum([w[i] * self.alter_z[i] for i in range(5)])
        # conver to polar axis
        self.r.now = sqrt(
            self.x.now ** 2 + 
            self.y.now ** 2
        )
        self.l.now = sqrt(
            self.r.now ** 2 +
            self.z.now ** 2
        )
        self.theta.now = atan2(self.y.now, self.x.now)
        self.phi.now = atan2(self.z.now, self.r.now)
        
        return Dict2Obj({
            'x': self.x.now,
            'y': self.y.now,
            'z': self.z.now,
            'r': self.r.now,
            'theta': self.theta.now,
            'l': self.l.now,
            'phi': self.phi.now
        })
        
class TouchWheelEvents:
    def __init__(
        self, 
        wheel,
        N=8,
        thr_upper=0.8,
        thr_lower=0.5,
        thr_deg=20,
    ):
        self.wheel = wheel
        
        self.thr_upper = thr_upper
        self.thr_lower = thr_lower
        self.thr = self.thr_upper
        self.thr_rad = thr_deg / 180 * pi
        
        self.any = State(id='any')
        self.ring = State()
        self.up = State(id='up')
        self.down = State(id='down')
        self.left = State(id='left')
        self.right = State(id='right')
        self.center = State(id='center')
        
        self.dial = Dial(N)
        self.hold_timer = Timer()
        
        self.events = EventQueue()
    
    def get(self):
        # get physical value
        phy = self.wheel.get()
        # touch detect
        self.any.now = int(phy.l > self.thr)
        self.ring.now = int(phy.r > self.thr)
        self.center.now = int(abs(theta_diff(pi / 2, phy.phi)) < self.thr_rad) & self.any.now
        self.up.now = int(abs(theta_diff(pi / 2, phy.theta)) < self.thr_rad) & self.ring.now
        self.down.now = int(abs(theta_diff(-pi / 2, phy.theta)) < self.thr_rad)& self.ring.now
        self.left.now = int(abs(theta_diff(pi, phy.theta)) < self.thr_rad)& self.ring.now
        self.right.now = int(abs(theta_diff(0, phy.theta)) < self.thr_rad)& self.ring.now
        
        # adaptive thr
        if self.any.diff == 1:
            self.thr = self.thr_lower
        if self.any.diff == -1:
            self.thr = self.thr_upper
        
        # press
        if self.any.diff == 1:
            self.events.append(Event(
                name='press',
                val=self.any.id
            ))
        if self.ring.diff == 1:
            self.dial.reset(phy.theta)
        # release
        if self.any.diff == -1 and not self.dial.dial_changed:
            for state in [
                self.center,
                self.up,
                self.down,
                self.left,
                self.right,
            ]:
                if state.diff == -1:
                    self.events.append(Event(
                        name='release',
                        val=state.id
                    ))
        # dial
        if self.ring.now == 1:
            dial = self.dial.update(phy.theta)
            if dial:
                self.events.append(Event(
                    name='dial',
                    val=dial
                ))
                
        # long press
        if self.any.diff == 1:
            self.hold_timer.start(1)
        if (self.any.now == 1 
        and self.hold_timer.over()
        and not self.dial.dial_changed):
            self.dial.dial_changed = True
            for state in [
                self.center,
                self.up,
                self.down,
                self.left,
                self.right,
            ]:
                if state.now == 1:
                    self.events.append(Event(
                        name='long',
                        val=state.id
                    ))
        if self.any.diff == -1:
            self.dial.dial_changed = False
            
        return self.events.get()