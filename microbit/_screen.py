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
from time import perf_counter, sleep
from ._hardware import button_a, button_b, temperature, _pin
from ._sub_window import *


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

    def bind_to_cv(self, cv, x, y, outer_size, inner_size):
        self.outer = cv.create_rectangle(
            x - outer_size[0],
            y - outer_size[1],
            x + outer_size[0],
            y + outer_size[1],
            outline='')
        self.inner = cv.create_rectangle(
            x - inner_size[0],
            y - inner_size[1],
            x + inner_size[0],
            y + inner_size[1],
            outline='')
        self.update_color(cv)

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


# ============ functions in main thread ============
def init_interface(cv, width, height):
    main_color = '#ff3871'
    bg_color = '#111111'
    cv.config(bg=bg_color)

    if 'upleft decoration':
        deco_pos, deco_size = 0, 200
        for i in range(3):
            cv.create_polygon(
                (deco_pos, 0), (deco_pos + deco_size, 0),
                (deco_pos, deco_size),
                outline='',
                fill=main_color)
            deco_pos += deco_size
            deco_size /= 2

    if 'logo':
        logo_center, logo_size = (500, 100), 50
        for step in [5, 3, 1]:
            for center in [
                    logo_center[0] - logo_size, logo_center[0] + logo_size
            ]:
                cv.create_oval(
                    center - logo_size * step / 5,
                    logo_center[1] - logo_size * step / 5,
                    center + logo_size * step / 5,
                    logo_center[1] + logo_size * step / 5,
                    fill=bg_color if step == 3 else main_color,
                    outline='')
            if step > 1:
                cv.create_rectangle(
                    logo_center[0] - logo_size,
                    logo_center[1] - logo_size * step / 5,
                    logo_center[0] + logo_size,
                    logo_center[1] + logo_size * step / 5 + 1,
                    fill=bg_color if step == 3 else main_color,
                    outline='')

    if 'LED screen':
        screen_pos = (300, 200)
        led_size = 80
        cv.create_rectangle(
            screen_pos[0] - 20,
            screen_pos[1] - 20,
            screen_pos[0] + 20 + led_size * 5,
            screen_pos[1] + 20 + led_size * 5,
            fill='black',
            outline='#151515',
            width=5)
        for x in range(5):
            for y in range(5):
                center = (screen_pos[0] + led_size * x + led_size // 2,
                          screen_pos[1] + led_size * y + led_size // 2)
                LED.pool[x][y].bind_to_cv(cv, *center, (40, 40), (30, 30))

    if 'buttons':
        button_y = 400
        button_xs = (150, 850)
        button_size = 60
        deco_size = 100
        for button_x in button_xs:
            # base
            cv.create_rectangle(
                button_x - button_size,
                button_y - button_size,
                button_x + button_size,
                button_y + button_size,
                outline='',
                fill='#b7b7b7')
            d = 45
            for dx in [-d, d]:
                for dy in [-d, d]:
                    cv.create_oval(
                        button_x + dx - button_size * 0.2,
                        button_y + dy - button_size * 0.2,
                        button_x + dx + button_size * 0.2,
                        button_y + dy + button_size * 0.2,
                        outline='',
                        fill='#7f3b05')

            # button
            side = -1 if button_x < 500 else 1
            btn = cv.create_oval(
                button_x - button_size * 0.6,
                button_y - button_size * 0.6,
                button_x + button_size * 0.6,
                button_y + button_size * 0.6,
                outline='',
                fill='black')
            if side == -1:
                button_a._cv = btn
            else:
                button_b._cv = btn

            # decoration text
            cv.create_polygon(
                (button_x, button_y - side * deco_size),
                (button_x, button_y - side * deco_size * 2),
                (button_x + side * deco_size, button_y - side * deco_size * 2),
                outline='',
                fill=main_color)
            cv.create_text(
                (button_x + side * deco_size * 0.3,
                 button_y - side * deco_size * 1.7),
                text='AB' [side > 0],
                font=('arial', 35, 'bold'),
                anchor='center')

    if 'pins':
        pin_y = 750
        pin_x = 2
        pin_step = 25
        pin_width = (21, 96)
        large_pins = (1, 9, 18, 27, 35)
        small_pins = tuple(
            i for i in range(40)
            if all(i < x or i - x >= 4 for x in large_pins))
        pin_color = '#ffa900'
        cv_small = []
        cv_large = []

        if 'generate canvas':
            # label on pins
            text_list = [list(range(3, 23)), ['0', '1', '2', '3V', 'GND']]
            text_list[0][14:16] = '', ''
            text_list[0][18:20] = '', ''

            # small ones
            for i, text in zip(small_pins, text_list[0]):
                # body
                pin = cv.create_rectangle(
                    (pin_x + i * pin_step, pin_y),
                    (pin_x + i * pin_step + pin_width[0], height + 10),
                    fill='red' if i in (26, 31) else pin_color,
                    outline='')
                cv_small.append(pin)

                # deco
                cv.create_text(
                    pin_x + i * pin_step + 10,
                    height - 15,
                    text=text,
                    font=('arial', 10, 'bold'),
                    anchor='center')

            # large ones
            for i, text in zip(large_pins, text_list[1]):
                # body
                pin = cv.create_rectangle(
                    (pin_x + i * pin_step, pin_y - pin_step),
                    (pin_x + i * pin_step + pin_width[1], height + 10),
                    fill='red' if i == 27 else pin_color,
                    outline='')
                pin2 = cv.create_oval(
                    (pin_x + i * pin_step,
                     pin_y - pin_step - pin_width[1] / 2),
                    (pin_x + i * pin_step + pin_width[1] - 1,
                     pin_y - pin_step + pin_width[1] / 2 - 1),
                    fill='red' if i == 27 else pin_color,
                    outline='')
                cv_large.append((pin, pin2))

                # deco
                cv.create_oval(
                    (pin_x + i * pin_step + 9,
                     pin_y - pin_step - pin_width[1] / 2 + 9),
                    (pin_x + i * pin_step + pin_width[1] - 10,
                     pin_y - pin_step + pin_width[1] / 2 - 10),
                    fill=bg_color,
                    outline='')
                cv.create_text(
                    pin_x + i * pin_step + pin_width[1] / 2,
                    height - 15,
                    text=text,
                    font=('arial', 20, 'bold'),
                    anchor='center')

        if 'bind canvas to object':
            # large ones
            for i in range(3):
                _pin.pins[i]._cv_hook = cv_large[i]

            # small ones
            for pin, i in zip([p for p in _pin.pins[3:] if p],
                              cv_small[:14] + cv_small[16:]):
                pin._cv_hook = (i, )


def bind_input_callback(tk, cv):
    # buttons & temperature control
    if 'mouse':
        # control buttons
        def bt_down(button):
            button._button_down = True
            button._pressed = True
            button._count += 1
            cv.itemconfig(button._cv, fill='yellow')

        def bt_up(button):
            button._button_down = False
            cv.itemconfig(button._cv, fill='black')

        def modify_temp(dt):
            temperature.temp = min(100, max(0, temperature.temp + dt))

        cv.bind('<Button-1>', lambda e: bt_down(button_a))
        cv.bind('<ButtonRelease-1>', lambda e: bt_up(button_a))
        cv.bind('<Button-3>', lambda e: bt_down(button_b))
        cv.bind('<ButtonRelease-3>', lambda e: bt_up(button_b))

        # control temperature
        cv.bind('<Button-2>', lambda e: temperature.__setattr__('temp', 26))
        cv.bind('<MouseWheel>',
                lambda e: modify_temp(1 if e.delta > 0 else -1))

    # pop information windows
    if 'keyboard':

        def key_down(event):
            event_pool = {
                80: pin_info,  # P calls pin information window
                66: beeper,  # B calls a beeper window playing sound
                82: rotation,  # R calls spatial rotation window
                71: gesture_info,  # G calls gesture window
                67: compass_control  # C calls magnetic field direction window
            }
            if event.keycode in event_pool:
                sub = event_pool[event.keycode]
                try:
                    if sub.running and sub.window.is_alive():
                        sub.running = False
                    else:
                        raise
                except Exception as e:
                    sub.window = Thread(target=sub)
                    sub.running = True
                    sub.window.start()

        tk.bind('<KeyPress>', key_down)


# ============ main screen thread ============
def run_screen():
    try:
        # initialize tkinter window
        width, height = 1000, 800
        tk = Tk(className='micro:bit Simulator')
        tk.geometry('+%d+%d' % (int(tk.winfo_screenwidth() - width) // 2, 10))
        tk.resizable(0, 0)

        # initialize canvas
        cv = Canvas(width=width, height=height, highlightthickness=0)
        cv.pack()

        # initialize layout
        init_interface(cv, width, height)

        # bind mouse & keyboard input
        bind_input_callback(tk, cv)

        # initialize information bar
        info_left = StringVar()
        info_right = StringVar()
        Label(tk, textvariable=info_left).pack(side=LEFT)
        Label(tk, textvariable=info_right, justify=RIGHT).pack(side=RIGHT)

        # main loop
        while 1:
            if 'update LED color':
                for x in range(5):
                    for y in range(5):
                        if not LED.pool[x][y].uptodate:
                            LED.pool[x][y].update_color(cv)

            if 'update pins':
                for p in _pin.pins:
                    if p:
                        p._update_color(cv)

            if 'update information bar':
                # left shows LED lightness
                left_text = ''

                mouse_x = tk.winfo_pointerx() - tk.winfo_rootx()
                mouse_y = tk.winfo_pointery() - tk.winfo_rooty()

                screen_pos = (300, 200)
                led_size = 80
                led_x, led_y = (mouse_x - screen_pos[0]) // led_size, (
                    mouse_y - screen_pos[1]) // led_size
                if 0 <= led_x < 5 and 0 <= led_y < 5:
                    left_text = 'LED screen (%d, %d) at lightness %d.' % (
                        led_x, led_y, LED.pool[led_x][led_y].level)
                info_left.set(left_text)

                # right shows temperature
                info_right.set('Temperature: %d℃' % temperature.temp)

            # update display
            tk.update()

    # exit when main window terminated
    except Exception as e:
        print(e)
        _exit(0)


# initialize LED screen
for x in range(5):
    for y in range(5):
        LED.pool[x][y] = LED()

# run screen
_screen_thread = Thread(target=run_screen)
_screen_thread.start()

# ============ beeper thread ============


def run_beeper():
    # load beeper
    try:
        from ctypes import windll
        bp = windll.LoadLibrary('kernel32.dll')
        beep = bp.Beep  # frequency, duration
        # raise
    except:
        print('loading Windows beeper failed')

        def beep(freq, dur):
            print('beep %.1fHz for %dms' % (freq, dur))

    while 1:
        if _pin.tones:
            tone = _pin.tones.pop()
        else:
            sleep(0.005)
            continue
        if tone[0] != _pin.music_pin:
            continue

        dur = int((tone[2] - perf_counter()) * 1000) - 30
        if dur > 0:
            beep(tone[1], dur)


# run beeper
_beeper_thread = Thread(target=run_beeper)
_beeper_thread.start()
