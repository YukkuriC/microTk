from turtle import Screen as _Screen

_screen = _Screen()
_tk = _screen._root

__all__ = ['button_a', 'button_b','accelerometer']


# ============ button input ============
class _button:
    def _press(self, event):
        self._button_down = True
        self._count += 1

    def _release(self, event):
        self._button_down = False

    def __init__(self, bind):
        self._count = 0
        self._button_down = False
        _tk.bind("<Button-%d>" % bind, self._press)
        _tk.bind("<ButtonRelease-%d>" % bind, self._release)

    def is_pressed(self):
        _tk.update()  # update tkinter for latest mouse status
        return self._button_down

    def was_pressed(self):
        return self._count > 0

    def get_presses(self):
        res, self._count = self._count, 0
        return res


button_a = _button(1)  # left mouse button
button_b = _button(3)  # right

# ============ accelerometer ============
class accelerometer:
    pass