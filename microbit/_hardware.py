__doc__ = '''Extend of microbit module
simmulation of buttons with mouse

Extension of microbit:
- method
-- microbit.temperature
- object
-- microbit.button_a
-- microbit.button_b
'''
__all__ = ['button_a', 'button_b','temperature']


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

# temperature controlled by mouse wheel
def temperature():
    return temperature.temp
temperature.temp=26