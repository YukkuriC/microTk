__doc__ = '''Tkinter layout module
Initialize window with tkinter and a virtual LED class
also export mouse actions to buttons and temperature

Containment:
- class:
-- LED
'''

from tkinter import *
from threading import Thread
from os import _exit
from ._hardware import button_a, button_b, temperature


# simulated LED class
class LED:
    pool = [[None] * 5 for i in range(5)]

    @staticmethod
    def colortext(fr, to, val):
        return '#%02x%02x%02x' % tuple(
            min(max(int(fr[i] + (to[i] - fr[i]) * val / 9), 0), 255)
            for i in range(3))

    def __init__(self):
        self.level = 0
        self.uptodate = True

    def bind_to_cv(self, x, y, cv):
        center = (100 * x + 50, 100 * y + 50)
        self.outer = cv.create_rectangle(
            center[0] - 45,
            center[1] - 45,
            center[0] + 45,
            center[1] + 45,
            fill='#%02x%02x%02x' % (10, 15, 10),
            outline='')
        self.inner = cv.create_rectangle(
            center[0] - 35,
            center[1] - 35,
            center[0] + 35,
            center[1] + 35,
            fill='#%02x%02x%02x' % (0, 0, 0),
            outline='')

    def set_lightness(self, level):
        self.level = max(0, (min(9, level)))
        self.uptodate = False

    def update_color(self, cv):
        self.uptodate = True
        cv.itemconfig(
            self.inner,
            fill=LED.colortext((0, 0, 0), (750, 140, 120),
                               self.level))  # fake HDR
        cv.itemconfig(
            self.outer,
            fill=LED.colortext((10, 15, 10), (255, 30, 30), self.level))


# main display thread
def run_screen():
    try:
        # initialize tkinter window
        width, height = 500, 500
        tk = Tk(className='micro:bit simulator')
        tk.geometry('+%d+%d' % (int(tk.winfo_screenwidth() - width) // 2, 10))
        tk.resizable(0, 0)
        bind_button(tk)

        # initialize canvas
        cv = Canvas(width=width, height=height, bg='black')
        cv.pack()
        init_interface(cv)

        # information bar
        info_left = StringVar()
        info_right = StringVar()
        Label(tk, textvariable=info_left).pack(side=LEFT)
        Label(tk, textvariable=info_right, justify=RIGHT).pack(side=RIGHT)

        # run LED screen
        while 1:
            # update LED color
            for x in range(5):
                for y in range(5):
                    if not LED.pool[x][y].uptodate:
                        LED.pool[x][y].update_color(cv)

            # update information bar
            update_info(info_left, info_right)

            # update display
            tk.update()

    # exit when main window terminated
    except:
        _exit(0)


# update information bar
def update_info(info_left, info_right):
    button_state = ['none', 'A', 'B',
                    'A&B'][button_a._button_down + button_b._button_down * 2]
    info_left.set('Pressed button: ' + button_state)
    info_right.set('Temperature: %d℃' % temperature.temp)


# bind left/right mouse button to button_a/button_b/temperature
def bind_button(tk):
    # control buttons
    def bt_down(button):
        button._button_down = True
        button._count += 1

    def bt_up(button):
        button._button_down = False

    def modify_temp(dt):
        temperature.temp = min(100, max(0, temperature.temp + dt))

    tk.bind('<Button-1>', lambda e: bt_down(button_a))
    tk.bind('<ButtonRelease-1>', lambda e: bt_up(button_a))
    tk.bind('<Button-3>', lambda e: bt_down(button_b))
    tk.bind('<ButtonRelease-3>', lambda e: bt_up(button_b))

    # control temperature
    tk.bind('<Button-2>', lambda e: temperature.__setattr__('temp', 26))
    tk.bind('<MouseWheel>', lambda e: modify_temp(1 if e.delta > 0 else -1))


# draw interface
def init_interface(cv):
    # initialize LED screen
    for x in range(5):
        for y in range(5):
            LED.pool[x][y].bind_to_cv(x, y, cv)


# ============ post import ============
# initialize LED screen
for x in range(5):
    for y in range(5):
        LED.pool[x][y] = LED()

# run screen
_screen_thread = Thread(target=run_screen)
_screen_thread.start()