__all__ = ['Image', 'display', 'panic']

from time import sleep as _sleep
from turtle import Screen as _Screen
from threading import Thread as _Thread

# initialize screen and canvas
_screen = _Screen()
_screen.tracer(0)
_screen._root.geometry('500x500')
_screen._root.resizable(0, 0)
_cv = _screen.cv
_cv.config(bg='black')


# error code
def panic(error_code=None):
    if error_code == None:
        error_code = Image.SAD
    display.show(error_code, loop=True)


# simulated LED class
class _led:
    pool = [[None] * 5 for i in range(5)]

    @staticmethod
    def _colortext(fr, to, val):
        return '#%02x%02x%02x' % tuple(
            min(max(int(fr[i] + (to[i] - fr[i]) * val / 9), 0), 255)
            for i in range(3))

    def __init__(self, x, y):
        _led.pool[x][y] = self
        center = (100 * (x - 2), 100 * (y - 2))
        self.outer = _cv.create_rectangle(
            center[0] - 45,
            center[1] - 45,
            center[0] + 45,
            center[1] + 45,
            fill='#%02x%02x%02x' % (10, 15, 10),
            outline='')
        self.inner = _cv.create_rectangle(
            center[0] - 35,
            center[1] - 35,
            center[0] + 35,
            center[1] + 35,
            fill='#%02x%02x%02x' % (0, 0, 0),
            outline='')
        self.level = 0

    def set_lightness(self, level):
        self.level = int(max(0, (min(9, level))))
        _cv.itemconfig(
            self.inner,
            fill=_led._colortext((0, 0, 0), (750, 140, 120),
                                 self.level))  # fake HDR
        _cv.itemconfig(
            self.outer,
            fill=_led._colortext((10, 15, 10), (255, 30, 30), self.level))


class display:

    # background thread
    # wait=False implement
    # TODO
    _display_thread = _Thread()

    # initialize the screen
    @staticmethod
    def _init_led():
        for x in range(5):
            for y in range(5):
                _led(x, y)

    # toggle screen on/off
    _is_on = True

    @staticmethod
    def on():
        display._is_on = True

    @staticmethod
    def off():
        display._is_on = False
        if _display_thread.is_alive():
            _display_thread._stop()
        display.clear()

    @staticmethod
    def is_on():
        return display._is_on

    # get lightness level of certain pixel
    @staticmethod
    def get_pixel(x, y):
        return _led.pool[x][y].level

    # set lightness level of certain pixel
    @staticmethod
    def set_pixel(x, y, val):
        if not display._is_on:
            return
        _led.pool[x][y].set_lightness(val)
        _cv.update()

    # clear the screen
    @staticmethod
    def clear():
        for col in _led.pool:
            for led in col:
                led.set_lightness(0)
        _cv.update()

    # display something on screen
    # distributed by input type
    @staticmethod
    def show(item, delay=None, **kwargs):  # wait=True, loop=False, clear=False
        # make sure screen is on
        if not display._is_on:
            return

        # grab arguments
        wait = kwargs.get('wait', True)
        loop = kwargs.get('loop', False)
        clear = kwargs.get('clear', False)

        # distribute by types
        if isinstance(item, Image):
            # small image
            if item._width <= 5:
                display._show_image(item, delay or 0, loop)

            # long image splitted into list
            # TODO
            else:
                pass
        elif isinstance(item, list) or isinstance(item, tuple):
            display._show_sequence(item, delay or 400, loop)
        elif isinstance(item, int) or isinstance(item, float) or isinstance(
                item, str):
            display.scroll(str(item), delay=delay or 150, **kwargs)
        else:
            panic()

        # clear if needed
        if clear:
            display.clear()

    # show an image (first 5 columns)
    @staticmethod
    def _show_image(item, delay, loop):
        # enter loop for once/forever
        while True:
            # clear first
            for col in _led.pool:
                for led in col:
                    led.set_lightness(0)

            # set all pixels
            for x in range(min(5, item._width)):
                for y in range(min(5, item._height)):
                    _led.pool[x][y].set_lightness(item._data[x][y])
            _cv.update()

            # delay between frames
            if delay:
                _sleep(delay / 1000)

            # if not loop, then break
            if not loop:
                break

    # show the character's font
    @staticmethod
    def _show_char(string, delay, loop):
        char_img = _font.get(string, _font['?'])
        display._show_image(char_img, delay, loop)

    # show a sequence of iterables
    @staticmethod
    def _show_sequence(lst, delay, loop):
        # enter loop for once/forever
        while 1:
            # show each item
            for item in lst:
                if isinstance(item, Image):
                    display._show_image(item, delay, False)
                elif isinstance(item, str):
                    display.scroll(item, 150)

            # if not loop, then break
            if not loop:
                break

    @staticmethod
    def scroll(string, delay=150,
               **kwargs):  # wait=True, loop=False, monospace=False
        # make sure screen is on
        if not display._is_on:
            return

        # grab arguments
        wait = kwargs.get('wait', True)
        loop = kwargs.get('loop', False)
        monospace = kwargs.get('monospace', False)

        # enter loop for once/forever
        while 1:
            # display single character if len==1
            if len(string) == 1:
                display._show_char(string, delay, loop)

            # generate long image
            img_start = Image()
            for i in string:
                if not monospace:
                    img_start = img_start._join(Image(1, 5))
                img_start = img_start._join(_font.get(i, _font['?']))

            # scroll string image
            while img_start._width:
                # draw current image & delay
                display._show_image(img_start, delay, False)

                # scroll 1 block
                img_start = img_start.shift_left(1)

            # break if not in loop
            if not loop:
                break


class Image:

    # compile ascii font strings into Image
    @staticmethod
    def _init_font():
        for chr in _font:
            _font[chr] = Image(_font[chr])

    # compile inner images
    @staticmethod
    def _inner_image(s):
        img = Image(s)
        for fun in ['set_pixel', 'fill', 'blit']:
            img.__setattr__(fun, Image._inner_attempt_modify)

        return img

    # try to modify inner images
    def _inner_attempt_modify(self, *args, **kwargs):
        panic()

    def __init__(self, *args):  # ._data format as lightness[x][y]
        # empty 5x5
        if len(args) == 0:
            self._width = self._height = 5
            self._data = [[0] * 5 for i in range(5)]

        # from string
        elif len(args) == 1:  # from string
            s = args[0].replace(' ', '').replace('\t', '').replace('\n', ':')
            sl = [i for i in s.split(':') if i]
            self._width, self._height = len(sl[0]), len(sl)
            self._data = [[int(sl[y][x]) for y in range(self._height)]
                          for x in range(self._width)]

        # with specific width and height
        else:
            self._width, self._height = args[:2]
            self._data = [[0] * self._height for i in range(self._width)]
            if len(args) > 2:
                s = args[2].replace(':', '').replace(' ', '').replace(
                    '\t', '').replace('\n', '')
                for i in range(min(len(s), self._width * self._height)):
                    self._data[i % self._width][i // self._width] = int(s[i])

    def fill(self, value):
        for x in range(self._width):
            for y in range(self._height):
                self._data[x][y] = value

    def width(self):
        return self._width

    def height(self):
        return self._height

    def copy(self):
        new_image = Image(0, self._height)
        new_image._data = [col.copy() for col in self._data]
        new_image._width = self._width
        return new_image

    def invert(self):
        new_image = self.copy()
        for x in range(new_image._width):
            for y in range(new_image._height):
                new_image._data[x][y] = 9 - new_image._data[x][y]
        return new_image

    def set_pixel(self, x, y, value):
        self._data[x][y] = value

    def get_pixel(self, x, y):
        return self._data[x][y]

    def blit(self, src, x, y, w, h, xdest=0, ydest=0):
        for cx in range(min(w, self._width - xdest)):
            for cy in range(min(h, self._height - ydest)):
                if x + cx >= src._width or y + cy >= src._height:
                    l = 0
                else:
                    l = src._data[x + cx][y + cy]
                self._data[xdest + cx][ydest + cy] = l

    def crop(self, x, y, w, h):
        new_img = Image(w, h)
        new_img.blit(self, x, y, w, h)
        return new_img

    def shift_left(self, n):
        if n < 0:
            return self.shift_right(-n)
        new_image = Image(0, self._height)
        new_image._data = [x.copy() for x in self._data[n:]]
        new_image._width = max(self._width - n, 0)
        return new_image

    def shift_right(self, n):
        if n < 0:
            return self.shift_left(-n)
        new_image = Image(0, self._height)
        new_image._data = [x.copy() for x in self._data[:-n]]
        new_image._width = max(self._width - n, 0)
        return new_image

    def shift_up(self, n):
        if n < 0:
            return self.shift_down(-n)
        new_image = Image(self._width, 0)
        new_image._data = [x[n:] for x in self._data]
        new_image._height = max(self._height - n, 0)
        return new_image

    def shift_down(self, n):
        if n < 0:
            return self.shift_up(-n)
        new_image = Image(self._width, 0)
        new_image._data = [x[:-n] for x in self._data]
        new_image._height = max(self._height - n, 0)
        return new_image

    def _join(self, other):  # on right
        if self._height != other._height:
            panic()
        new_image = self.copy()
        new_image._data.extend(x.copy() for x in other._data)
        new_image._width += other._width
        return new_image

    def __repr__(self):
        return ':'.join(''.join(
            str(self._data[x][y]) for x in range(self._width))
                        for y in range(self._height))

    def __str__(self):
        return '\n'.join(''.join(
            str(self._data[x][y]) for x in range(self._width))
                         for y in range(self._height))

    def __add__(self, other):
        res = Image(
            max(self._width, other._width), max(self._height, other._height))
        for x in range(self._width):
            for y in range(self._height):
                res[x][y] = self[x][y]
        for x in range(other._width):
            for y in range(other._height):
                res[x][y] = min(res[x][y] + other[x][y], 9)
        return res

    def __mul__(self, n):
        res = Image(self._width, self._height)
        for x in range(self._width):
            for y in range(self._height):
                res[x][y] = min(self._data[x][y] * n, 9)
        return res


# all static images
if 1:
    Image.HEART = Image._inner_image('01010:11111:11111:01110:00100:')
    Image.HEART_SMALL = Image._inner_image('00000:01010:01110:00100:00000:')
    Image.HAPPY = Image._inner_image('00000:01010:00000:10001:01110:')
    Image.SMILE = Image._inner_image('00000:00000:00000:10001:01110:')
    Image.SAD = Image._inner_image('00000:01010:00000:01110:10001:')
    Image.CONFUSED = Image._inner_image('00000:01010:00000:01010:10101:')
    Image.ANGRY = Image._inner_image('10001:01010:00000:11111:10101:')
    Image.ASLEEP = Image._inner_image('00000:11011:00000:01110:00000:')
    Image.SURPRISED = Image._inner_image('01010:00000:00100:01010:00100:')
    Image.SILLY = Image._inner_image('10001:00000:11111:00101:00111:')
    Image.FABULOUS = Image._inner_image('11111:11011:00000:01010:01110:')
    Image.MEH = Image._inner_image('01010:00000:00010:00100:01000:')
    Image.YES = Image._inner_image('00000:00001:00010:10100:01000:')
    Image.NO = Image._inner_image('10001:01010:00100:01010:10001:')
    Image.CLOCK12 = Image._inner_image('00100:00100:00100:00000:00000:')
    Image.CLOCK1 = Image._inner_image('00010:00010:00100:00000:00000:')
    Image.CLOCK2 = Image._inner_image('00000:00011:00100:00000:00000:')
    Image.CLOCK3 = Image._inner_image('00000:00000:00111:00000:00000:')
    Image.CLOCK4 = Image._inner_image('00000:00000:00100:00011:00000:')
    Image.CLOCK5 = Image._inner_image('00000:00000:00100:00010:00010:')
    Image.CLOCK6 = Image._inner_image('00000:00000:00100:00100:00100:')
    Image.CLOCK7 = Image._inner_image('00000:00000:00100:01000:01000:')
    Image.CLOCK8 = Image._inner_image('00000:00000:00100:11000:00000:')
    Image.CLOCK9 = Image._inner_image('00000:00000:11100:00000:00000:')
    Image.CLOCK10 = Image._inner_image('00000:11000:00100:00000:00000:')
    Image.CLOCK11 = Image._inner_image('01000:01000:00100:00000:00000:')
    Image.ARROW_N = Image._inner_image('00100:01110:10101:00100:00100:')
    Image.ARROW_NE = Image._inner_image('00111:00011:00101:01000:10000:')
    Image.ARROW_E = Image._inner_image('00100:00010:11111:00010:00100:')
    Image.ARROW_SE = Image._inner_image('10000:01000:00101:00011:00111:')
    Image.ARROW_S = Image._inner_image('00100:00100:10101:01110:00100:')
    Image.ARROW_SW = Image._inner_image('00001:00010:10100:11000:11100:')
    Image.ARROW_W = Image._inner_image('00100:01000:11111:01000:00100:')
    Image.ARROW_NW = Image._inner_image('11100:11000:10100:00010:00001:')
    Image.TRIANGLE = Image._inner_image('00000:00100:01010:11111:00000:')
    Image.TRIANGLE_LEFT = Image._inner_image('10000:11000:10100:10010:11111:')
    Image.CHESSBOARD = Image._inner_image('01010:10101:01010:10101:01010:')
    Image.DIAMOND = Image._inner_image('00100:01010:10001:01010:00100:')
    Image.DIAMOND_SMALL = Image._inner_image('00000:00100:01010:00100:00000:')
    Image.SQUARE = Image._inner_image('11111:10001:10001:10001:11111:')
    Image.SQUARE_SMALL = Image._inner_image('00000:01110:01010:01110:00000:')
    Image.RABBIT = Image._inner_image('10100:10100:11110:11010:11110:')
    Image.COW = Image._inner_image('10001:10001:11111:01110:00100:')
    Image.MUSIC_CROTCHET = Image._inner_image('00100:00100:00100:11100:11100:')
    Image.MUSIC_QUAVER = Image._inner_image('00100:00110:00101:11100:11100:')
    Image.MUSIC_QUAVERS = Image._inner_image('01111:01001:01001:11011:11011:')
    Image.PITCHFORK = Image._inner_image('10101:10101:11111:00100:00100:')
    Image.XMAS = Image._inner_image('00100:01110:00100:01110:11111:')
    Image.PACMAN = Image._inner_image('01111:11010:11100:11110:01111:')
    Image.TARGET = Image._inner_image('00100:01110:11011:01110:00100:')
    Image.TSHIRT = Image._inner_image('11011:11111:01110:01110:01110:')
    Image.ROLLERSKATE = Image._inner_image('00011:00011:11111:11111:01010:')
    Image.DUCK = Image._inner_image('01100:11100:01111:01110:00000:')
    Image.HOUSE = Image._inner_image('00100:01110:11111:01110:01010:')
    Image.TORTOISE = Image._inner_image('00000:01110:11111:01010:00000:')
    Image.BUTTERFLY = Image._inner_image('11011:11111:00100:11111:11011:')
    Image.STICKFIGURE = Image._inner_image('00100:11111:00100:01010:10001:')
    Image.GHOST = Image._inner_image('11111:10101:11111:11111:10101:')
    Image.SWORD = Image._inner_image('00100:00100:00100:01110:00100:')
    Image.GIRAFFE = Image._inner_image('11000:01000:01000:01110:01010:')
    Image.SKULL = Image._inner_image('01110:10101:11111:01110:01110:')
    Image.UMBRELLA = Image._inner_image('01110:11111:00100:10100:01100:')
    Image.SNAKE = Image._inner_image('11000:11011:01010:01110:00000:')
    Image.ALL_CLOCKS = [eval('Image.CLOCK%d' % i) for i in range(1, 13)]
    Image.ALL_ARROWS = [
        eval('Image.ARROW_%s' % i)
        for i in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    ]

# ascii font before compiled into Image
_font = {
    ' ': '00000:00000:00000:00000:00000',
    '!': '09000:09000:09000:00000:09000',
    '"': '09090:09090:00000:00000:00000',
    '#': '09090:99999:09090:99999:09090',
    '$': '09990:99009:09990:90099:09990',
    '%': '99009:90090:00900:09009:90099',
    '&': '09900:90090:09900:90090:09909',
    "'": '09000:09000:00000:00000:00000',
    '(': '00900:09000:09000:09000:00900',
    ')': '09000:00900:00900:00900:09000',
    '*': '00000:09090:00900:09090:00000',
    '+': '00000:00900:09990:00900:00000',
    ',': '00000:00000:00000:00900:09000',
    '-': '00000:00000:09990:00000:00000',
    '.': '00000:00000:00000:09000:00000',
    '/': '00009:00090:00900:09000:90000',
    '0': '09900:90090:90090:90090:09900',
    '1': '00900:09900:00900:00900:09990',
    '2': '99900:00090:09900:90000:99990',
    '3': '99990:00090:00900:90090:09900',
    '4': '00990:09090:90090:99999:00090',
    '5': '99999:90000:99990:00009:99990',
    '6': '00090:00900:09990:90009:09990',
    '7': '99999:00090:00900:09000:90000',
    '8': '09990:90009:09990:90009:09990',
    '9': '09990:90009:09990:00900:09000',
    ':': '00000:09000:00000:09000:00000',
    ';': '00000:00900:00000:00900:09000',
    '<': '00090:00900:09000:00900:00090',
    '=': '00000:09990:00000:09990:00000',
    '>': '09000:00900:00090:00900:09000',
    '?': '09990:90009:00990:00000:00900',
    '@': '09990:90009:90909:90099:09900',
    'A': '09900:90090:99990:90090:90090',
    'B': '99900:90090:99900:90090:99900',
    'C': '09990:90000:90000:90000:09990',
    'D': '99900:90090:90090:90090:99900',
    'E': '99990:90000:99900:90000:99990',
    'F': '99990:90000:99900:90000:90000',
    'G': '09990:90000:90099:90009:09990',
    'H': '90090:90090:99990:90090:90090',
    'I': '99900:09000:09000:09000:99900',
    'J': '99999:00090:00090:90090:09900',
    'K': '90090:90900:99000:90900:90090',
    'L': '90000:90000:90000:90000:99990',
    'M': '90009:99099:90909:90009:90009',
    'N': '90009:99009:90909:90099:90009',
    'O': '09900:90090:90090:90090:09900',
    'P': '99900:90090:99900:90000:90000',
    'Q': '09900:90090:90090:09900:00990',
    'R': '99900:90090:99900:90090:90009',
    'S': '09990:90000:09900:00090:99900',
    'T': '99999:00900:00900:00900:00900',
    'U': '90090:90090:90090:90090:09900',
    'V': '90009:90009:90009:09090:00900',
    'W': '90009:90009:90909:99099:90009',
    'X': '90090:90090:09900:90090:90090',
    'Y': '90009:09090:00900:00900:00900',
    'Z': '99990:00900:09000:90000:99990',
    '[': '09990:09000:09000:09000:09990',
    '\\': '90000:09000:00900:00090:00009',
    ']': '09990:00090:00090:00090:09990',
    '^': '00900:09090:00000:00000:00000',
    '_': '00000:00000:00000:00000:99999',
    '`': '09000:00900:00000:00000:00000',
    'a': '00000:09990:90090:90090:09999',
    'b': '90000:90000:99900:90090:99900',
    'c': '00000:09990:90000:90000:09990',
    'd': '00090:00090:09990:90090:09990',
    'e': '09900:90090:99900:90000:09990',
    'f': '00990:09000:99900:09000:09000',
    'g': '09990:90090:09990:00090:09900',
    'h': '90000:90000:99900:90090:90090',
    'i': '09000:00000:09000:09000:09000',
    'j': '00090:00000:00090:00090:09900',
    'k': '90000:90900:99000:90900:90090',
    'l': '09000:09000:09000:09000:00990',
    'm': '00000:99099:90909:90009:90009',
    'n': '00000:99900:90090:90090:90090',
    'o': '00000:09900:90090:90090:09900',
    'p': '00000:99900:90090:99900:90000',
    'q': '00000:09990:90090:09990:00090',
    'r': '00000:09990:90000:90000:90000',
    's': '00000:00990:09000:00900:99000',
    't': '09000:09000:09990:09000:00999',
    'u': '00000:90090:90090:90090:09999',
    'v': '00000:90009:90009:09090:00900',
    'w': '00000:90009:90009:90909:99099',
    'x': '00000:90090:09900:09900:90090',
    'y': '00000:90009:09090:00900:99000',
    'z': '00000:99990:00900:09000:99990',
    '{': '00990:00900:09900:00900:00990',
    '|': '09000:09000:09000:09000:09000',
    '}': '99000:09000:09900:09000:99000',
    '~': '00000:00000:09900:00099:00000'
}

# ============ post-import ============

display._init_led()
Image._init_font()