__doc__ = '''Extend of microbit module
simmulation of buttons with mouse

Extension of microbit:
- method
-- microbit.temperature
- object
-- microbit.button_a
-- microbit.button_b
-- microbit.pin0-19 (without 17,18)
'''
__all__ = ['button_a', 'button_b', 'temperature']
__all__ += ['pin%d' % i for i in range(21) if not i in (17, 18)]


# temperature controlled by mouse wheel
def temperature():
    return temperature.temp


temperature.temp = 26


# button class (hook of display thread)
class _button:
    def __init__(self, bind):
        self._count = 0
        self._button_down = False

    def is_pressed(self):
        return self._button_down

    def was_pressed(self):
        return self._count > 0

    def get_presses(self):
        res, self._count = self._count, 0
        return res


button_a = _button(1)  # left mouse button
button_b = _button(3)  # right


# pins
class _pin:
    pins = [None] * 21  # all pins
    screen_mode = True  # whether LED screen is on

    # update display color
    def _update_color(self, cv):
        self._uptodate = True
        new_color = '#FF%02x00' % int(169 * (1 - self.volt / 1023))
        for i in self._cv_hook:
            cv.itemconfig(i, fill=new_color)

    def __init__(self, id):
        _pin.pins[id] = self
        self.id = id
        self.volt, self.period = 0, 1000  # write output
        self.volt_r, self.period_r = 0, 1000  # read_input

        self._cv_hook = None
        self._uptodate = False

    def __check_occupied(self):
        if self.id in (5, 11):
            raise ValueError('pin in button mode')
        elif self.id in (3, 4, 6, 7, 9, 10) and is_on():
            raise ValueError('pin in display mode')
        elif self.id == 12:
            raise ValueError('pin reserved')

    def read_digital(self):
        self.__check_occupied()
        self.volt = 0
        return self.volt_r > 0

    def write_digital(self, value):
        self.__check_occupied()
        assert value in (0, 1)
        self.volt = value and 1023
        self._uptodate = False

    def set_pull(self, value):  # what's this?
        pass

    def read_analog(self):
        self.__check_occupied()
        if (self.id > 4 and self.id != 10):
            raise AttributeError("digital pins don't support analog input")
        self.volt = 0
        return self.volt_r > 0

    def write_analog(self, value):
        self.__check_occupied()
        assert isinstance(value, int) and 0 <= value < 1024
        self.volt = value
        self._uptodate = False

    def set_analog_period(self, period):
        self.__check_occupied()
        assert isinstance(period, int) and period >= 1
        self.period_r = period * 1000

    def set_analog_period_microseconds(self, period):
        self.__check_occupied()
        assert isinstance(period, int) and period >= 256
        self.period_r = period

    def is_touched(self):
        if self.id > 2:
            raise AttributeError('not a touch pin')
        return self.touched


# initialize pins
for i in range(21):
    if not i in (17, 18):
        exec('pin%d = _pin(i)' % i)