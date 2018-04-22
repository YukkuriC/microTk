__doc__ = '''microbit.display module

Containment:
- method:
-- microbit.display.on
-- microbit.display.off
-- microbit.display.is_on
-- microbit.display.get_pixel
-- microbit.display.set_pixel
-- microbit.display.clear
-- microbit.display.show
-- microbit.display.scroll

Extension of microbit:
- class:
-- microbit.Image
- method:
-- microbit.panic
'''
__all__ = [
    'on', 'off', 'is_on', 'get_pixel', 'set_pixel', 'clear', 'show', 'scroll'
]

from threading import Thread as _Thread
from ._timebase import sleep as _sleep
from ._screen import LED
from ._hardware import _pin


# ============ root content ============
# error code
def panic(error_code=0):
    while 1:
        display.show(str(error_code))
        sleep(400)
        display.show(Image.SAD)
        sleep(400)


# Image class defination
class Image:
    # compile inner images
    @staticmethod
    def _inner_image(s):
        img = Image(s)
        for fun in ['set_pixel', 'fill', 'blit']:
            img.__setattr__(fun, Image._inner_attempt_modify)

        return img

    # try to modify inner images
    def _inner_attempt_modify(self, *args, **kwargs):
        raise AttributeError('read only')

    def __init__(self, *args):  # ._data format as lightness[x][y]
        # empty read-only 5x5
        if len(args) == 0:
            self._width = self._height = 5
            self._data = [[0] * 5 for i in range(5)]
            for fun in ['set_pixel', 'fill', 'blit']:
                self.__setattr__(fun, Image._inner_attempt_modify)

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
        assert isinstance(value, int) and 0 <= value <= 9
        self._data[x][y] = value

    def get_pixel(self, x, y):
        return self._data[x][y]

    def blit(self, src, x, y, w, h, xdest=0, ydest=0):
        for cx in range(min(w, self._width - xdest)):
            for cy in range(min(h, self._height - ydest)):
                if 0 <= x + cx < src._width and 0 <= y + cy < src._height:
                    l = src._data[x + cx][y + cy]
                else:
                    l = 0
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
                res._data[x][y] = self._data[x][y]
        for x in range(other._width):
            for y in range(other._height):
                res._data[x][y] = min(res._data[x][y] + other._data[x][y], 9)
        return res

    def __sub__(self, other):
        res = Image(
            max(self._width, other._width), max(self._height, other._height))
        for x in range(self._width):
            for y in range(self._height):
                res._data[x][y] = self._data[x][y]
        for x in range(other._width):
            for y in range(other._height):
                res._data[x][y] = max(res._data[x][y] - other._data[x][y], 0)
        return res

    def __mul__(self, n):
        res = Image(self._width, self._height)
        for x in range(self._width):
            for y in range(self._height):
                res._data[x][y] = max(0, min(self._data[x][y] * n, 9))
        return res


if 'builtin images':
    Image.HEART = Image._inner_image('09090:99999:99999:09990:00900:')
    Image.HEART_SMALL = Image._inner_image('00000:09090:09990:00900:00000:')
    Image.HAPPY = Image._inner_image('00000:09090:00000:90009:09990:')
    Image.SMILE = Image._inner_image('00000:00000:00000:90009:09990:')
    Image.SAD = Image._inner_image('00000:09090:00000:09990:90009:')
    Image.CONFUSED = Image._inner_image('00000:09090:00000:09090:90909:')
    Image.ANGRY = Image._inner_image('90009:09090:00000:99999:90909:')
    Image.ASLEEP = Image._inner_image('00000:99099:00000:09990:00000:')
    Image.SURPRISED = Image._inner_image('09090:00000:00900:09090:00900:')
    Image.SILLY = Image._inner_image('90009:00000:99999:00909:00999:')
    Image.FABULOUS = Image._inner_image('99999:99099:00000:09090:09990:')
    Image.MEH = Image._inner_image('09090:00000:00090:00900:09000:')
    Image.YES = Image._inner_image('00000:00009:00090:90900:09000:')
    Image.NO = Image._inner_image('90009:09090:00900:09090:90009:')
    Image.CLOCK12 = Image._inner_image('00900:00900:00900:00000:00000:')
    Image.CLOCK1 = Image._inner_image('00090:00090:00900:00000:00000:')
    Image.CLOCK2 = Image._inner_image('00000:00099:00900:00000:00000:')
    Image.CLOCK3 = Image._inner_image('00000:00000:00999:00000:00000:')
    Image.CLOCK4 = Image._inner_image('00000:00000:00900:00099:00000:')
    Image.CLOCK5 = Image._inner_image('00000:00000:00900:00090:00090:')
    Image.CLOCK6 = Image._inner_image('00000:00000:00900:00900:00900:')
    Image.CLOCK7 = Image._inner_image('00000:00000:00900:09000:09000:')
    Image.CLOCK8 = Image._inner_image('00000:00000:00900:99000:00000:')
    Image.CLOCK9 = Image._inner_image('00000:00000:99900:00000:00000:')
    Image.CLOCK10 = Image._inner_image('00000:99000:00900:00000:00000:')
    Image.CLOCK11 = Image._inner_image('09000:09000:00900:00000:00000:')
    Image.ARROW_N = Image._inner_image('00900:09990:90909:00900:00900:')
    Image.ARROW_NE = Image._inner_image('00999:00099:00909:09000:90000:')
    Image.ARROW_E = Image._inner_image('00900:00090:99999:00090:00900:')
    Image.ARROW_SE = Image._inner_image('90000:09000:00909:00099:00999:')
    Image.ARROW_S = Image._inner_image('00900:00900:90909:09990:00900:')
    Image.ARROW_SW = Image._inner_image('00009:00090:90900:99000:99900:')
    Image.ARROW_W = Image._inner_image('00900:09000:99999:09000:00900:')
    Image.ARROW_NW = Image._inner_image('99900:99000:90900:00090:00009:')
    Image.TRIANGLE = Image._inner_image('00000:00900:09090:99999:00000:')
    Image.TRIANGLE_LEFT = Image._inner_image('90000:99000:90900:90090:99999:')
    Image.CHESSBOARD = Image._inner_image('09090:90909:09090:90909:09090:')
    Image.DIAMOND = Image._inner_image('00900:09090:90009:09090:00900:')
    Image.DIAMOND_SMALL = Image._inner_image('00000:00900:09090:00900:00000:')
    Image.SQUARE = Image._inner_image('99999:90009:90009:90009:99999:')
    Image.SQUARE_SMALL = Image._inner_image('00000:09990:09090:09990:00000:')
    Image.RABBIT = Image._inner_image('90900:90900:99990:99090:99990:')
    Image.COW = Image._inner_image('90009:90009:99999:09990:00900:')
    Image.MUSIC_CROTCHET = Image._inner_image('00900:00900:00900:99900:99900:')
    Image.MUSIC_QUAVER = Image._inner_image('00900:00990:00909:99900:99900:')
    Image.MUSIC_QUAVERS = Image._inner_image('09999:09009:09009:99099:99099:')
    Image.PITCHFORK = Image._inner_image('90909:90909:99999:00900:00900:')
    Image.XMAS = Image._inner_image('00900:09990:00900:09990:99999:')
    Image.PACMAN = Image._inner_image('09999:99090:99900:99990:09999:')
    Image.TARGET = Image._inner_image('00900:09990:99099:09990:00900:')
    Image.TSHIRT = Image._inner_image('99099:99999:09990:09990:09990:')
    Image.ROLLERSKATE = Image._inner_image('00099:00099:99999:99999:09090:')
    Image.DUCK = Image._inner_image('09900:99900:09999:09990:00000:')
    Image.HOUSE = Image._inner_image('00900:09990:99999:09990:09090:')
    Image.TORTOISE = Image._inner_image('00000:09990:99999:09090:00000:')
    Image.BUTTERFLY = Image._inner_image('99099:99999:00900:99999:99099:')
    Image.STICKFIGURE = Image._inner_image('00900:99999:00900:09090:90009:')
    Image.GHOST = Image._inner_image('99999:90909:99999:99999:90909:')
    Image.SWORD = Image._inner_image('00900:00900:00900:09990:00900:')
    Image.GIRAFFE = Image._inner_image('99000:09000:09000:09990:09090:')
    Image.SKULL = Image._inner_image('09990:90909:99999:09990:09990:')
    Image.UMBRELLA = Image._inner_image('09990:99999:00900:90900:09900:')
    Image.SNAKE = Image._inner_image('99000:99099:09090:09990:00000:')
    Image.ALL_CLOCKS = [eval('Image.CLOCK%d' % i) for i in range(1, 13)]
    Image.ALL_ARROWS = [
        eval('Image.ARROW_%s' % i)
        for i in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    ]

# ============ display module ============
if 'display':

    def on():
        _pin.screen_mode = True

    def off():
        _pin.screen_mode = False
        clear()

    is_on = lambda: _pin.screen_mode

    # get lightness level of certain pixel
    def get_pixel(x, y):
        return LED.pool[x][y].level

    # set lightness level of certain pixel
    def set_pixel(x, y, val):
        if not _pin.screen_mode:
            return
        LED.pool[x][y].set_lightness(val)

    # clear the screen
    def clear():
        _stop_bg_run()

        for col in LED.pool:
            for led in col:
                led.set_lightness(0)

    # display something on screen
    # distributed by input type
    def show(item, delay=None, **kwargs):  # wait=True, loop=False, clear=False
        assert type(item) in [str, Image, tuple, list]

        # stop background thread
        _stop_bg_run()

        # make sure screen is on
        if not _pin.screen_mode:
            return

        # grab arguments
        wait = kwargs.get('wait', True)
        loop = kwargs.get('loop', False)
        clear = kwargs.get('clear', False)

        # single-image display
        if isinstance(item, Image) or isinstance(item, str) and len(item) == 1:
            _show_image(item)
            if loop and not wait:  # stop here
                while 1:
                    _sleep(1000)

        # show sequence in main thread
        elif wait:
            _show_sequence(item, delay or 400, loop, clear)

        # show sequence in background
        else:
            _run_bg(_show_sequence, item, delay or 400, loop, clear)

    # show an image (first 5 columns)
    def _show_image(item, delay=0):
        # turn char into image
        if isinstance(item, str):
            item = _font.get(item, _font['?'])

        # clear first
        for col in LED.pool:
            for led in col:
                led.set_lightness(0)

        # set all pixels
        for x in range(min(5, item._width)):
            for y in range(min(5, item._height)):
                LED.pool[x][y].set_lightness(item._data[x][y])

        # delay between frames
        if delay:
            _sleep(delay)

    # show a sequence of iterables
    def _show_sequence(lst, delay, loop, clear):
        # enter loop for once/forever
        while 1:
            # show each item until meeting illegal
            for item in lst:
                if isinstance(
                        item,
                        Image) or isinstance(item, str) and len(item) == 1:
                    _show_image(item, delay)
                else:
                    return

            # if not loop, then break
            if not loop:
                break

        # clear if needed
        if clear:
            clear()

    # scroll string
    def scroll(string, delay=150, **kwargs):
        # wait=True, loop=False, monospace=False

        # stop background thread
        _stop_bg_run()

        # make sure screen is on
        if not _pin.screen_mode:
            return

        # grab arguments
        wait = kwargs.get('wait', True)
        loop = kwargs.get('loop', False)
        monospace = kwargs.get('monospace', False)

        # turn background if wait=False
        if not wait:
            kwargs['wait'] = False
            return _run_bg(show, delay, kwargs)

        # display single character if len==1
        if len(string) == 1:
            return _show_char(string, delay, loop)

        # enter loop for once/forever
        while 1:
            # generate long image
            img_start = Image()
            for i in string:
                if not monospace:
                    img_start = img_start._join(Image(1, 5))
                img_start = img_start._join(_font.get(i, _font['?']))

            # scroll string image
            while img_start._width:
                # draw current image & delay
                _show_image(img_start, delay)

                # scroll 1 block
                img_start = img_start.shift_left(1)

            # break if not in loop
            if not loop:
                break

        # clear afterwards
        clear()


if 'background display':
    _display_thread = _Thread()

    def _stop_bg_run():
        if not _display_thread.is_alive() or id == _display_thread_id:
            return
        _display_thread._stop()

    def _run_bg(fun, lst, delay, loop, clear):
        _display_thread = _Thread(target=fun, args=(lst, delay, loop, clear))
        _display_thread.start()


# ascii font before compiled into Image
_font = {
    ' ': Image('00000:00000:00000:00000:00000'),
    '!': Image('09000:09000:09000:00000:09000'),
    '"': Image('09090:09090:00000:00000:00000'),
    '#': Image('09090:99999:09090:99999:09090'),
    '$': Image('09990:99009:09990:90099:09990'),
    '%': Image('99009:90090:00900:09009:90099'),
    '&': Image('09900:90090:09900:90090:09909'),
    "'": Image('09000:09000:00000:00000:00000'),
    '(': Image('00900:09000:09000:09000:00900'),
    ')': Image('09000:00900:00900:00900:09000'),
    '*': Image('00000:09090:00900:09090:00000'),
    '+': Image('00000:00900:09990:00900:00000'),
    ',': Image('00000:00000:00000:00900:09000'),
    '-': Image('00000:00000:09990:00000:00000'),
    '.': Image('00000:00000:00000:09000:00000'),
    '/': Image('00009:00090:00900:09000:90000'),
    '0': Image('09900:90090:90090:90090:09900'),
    '1': Image('00900:09900:00900:00900:09990'),
    '2': Image('99900:00090:09900:90000:99990'),
    '3': Image('99990:00090:00900:90090:09900'),
    '4': Image('00990:09090:90090:99999:00090'),
    '5': Image('99999:90000:99990:00009:99990'),
    '6': Image('00090:00900:09990:90009:09990'),
    '7': Image('99999:00090:00900:09000:90000'),
    '8': Image('09990:90009:09990:90009:09990'),
    '9': Image('09990:90009:09990:00900:09000'),
    ':': Image('00000:09000:00000:09000:00000'),
    ';': Image('00000:00900:00000:00900:09000'),
    '<': Image('00090:00900:09000:00900:00090'),
    '=': Image('00000:09990:00000:09990:00000'),
    '>': Image('09000:00900:00090:00900:09000'),
    '?': Image('09990:90009:00990:00000:00900'),
    '@': Image('09990:90009:90909:90099:09900'),
    'A': Image('09900:90090:99990:90090:90090'),
    'B': Image('99900:90090:99900:90090:99900'),
    'C': Image('09990:90000:90000:90000:09990'),
    'D': Image('99900:90090:90090:90090:99900'),
    'E': Image('99990:90000:99900:90000:99990'),
    'F': Image('99990:90000:99900:90000:90000'),
    'G': Image('09990:90000:90099:90009:09990'),
    'H': Image('90090:90090:99990:90090:90090'),
    'I': Image('99900:09000:09000:09000:99900'),
    'J': Image('99999:00090:00090:90090:09900'),
    'K': Image('90090:90900:99000:90900:90090'),
    'L': Image('90000:90000:90000:90000:99990'),
    'M': Image('90009:99099:90909:90009:90009'),
    'N': Image('90009:99009:90909:90099:90009'),
    'O': Image('09900:90090:90090:90090:09900'),
    'P': Image('99900:90090:99900:90000:90000'),
    'Q': Image('09900:90090:90090:09900:00990'),
    'R': Image('99900:90090:99900:90090:90009'),
    'S': Image('09990:90000:09900:00090:99900'),
    'T': Image('99999:00900:00900:00900:00900'),
    'U': Image('90090:90090:90090:90090:09900'),
    'V': Image('90009:90009:90009:09090:00900'),
    'W': Image('90009:90009:90909:99099:90009'),
    'X': Image('90090:90090:09900:90090:90090'),
    'Y': Image('90009:09090:00900:00900:00900'),
    'Z': Image('99990:00900:09000:90000:99990'),
    '[': Image('09990:09000:09000:09000:09990'),
    '\\': Image('90000:09000:00900:00090:00009'),
    ']': Image('09990:00090:00090:00090:09990'),
    '^': Image('00900:09090:00000:00000:00000'),
    '_': Image('00000:00000:00000:00000:99999'),
    '`': Image('09000:00900:00000:00000:00000'),
    'a': Image('00000:09990:90090:90090:09999'),
    'b': Image('90000:90000:99900:90090:99900'),
    'c': Image('00000:09990:90000:90000:09990'),
    'd': Image('00090:00090:09990:90090:09990'),
    'e': Image('09900:90090:99900:90000:09990'),
    'f': Image('00990:09000:99900:09000:09000'),
    'g': Image('09990:90090:09990:00090:09900'),
    'h': Image('90000:90000:99900:90090:90090'),
    'i': Image('09000:00000:09000:09000:09000'),
    'j': Image('00090:00000:00090:00090:09900'),
    'k': Image('90000:90900:99000:90900:90090'),
    'l': Image('09000:09000:09000:09000:00990'),
    'm': Image('00000:99099:90909:90009:90009'),
    'n': Image('00000:99900:90090:90090:90090'),
    'o': Image('00000:09900:90090:90090:09900'),
    'p': Image('00000:99900:90090:99900:90000'),
    'q': Image('00000:09990:90090:09990:00090'),
    'r': Image('00000:09990:90000:90000:90000'),
    's': Image('00000:00990:09000:00900:99000'),
    't': Image('09000:09000:09990:09000:00999'),
    'u': Image('00000:90090:90090:90090:09999'),
    'v': Image('00000:90009:90009:09090:00900'),
    'w': Image('00000:90009:90009:90909:99099'),
    'x': Image('00000:90090:09900:09900:90090'),
    'y': Image('00000:90009:09090:00900:99000'),
    'z': Image('00000:99990:00900:09000:99990'),
    '{': Image('00990:00900:09900:00900:00990'),
    '|': Image('09000:09000:09000:09000:09000'),
    '}': Image('99000:09000:09900:09000:99000'),
    '~': Image('00000:00000:09900:00099:00000')
}