__doc__ = '''Extend of microbit module
several timing functions

Extension of microbit:
- method
-- microbit.running_time
-- microbit.sleep
'''
__all__ = ['sleep', 'running_time']

from time import sleep as _sleep, perf_counter as _time


def sleep(ms):
    '''Wait for n milliseconds.'''
    _sleep(ms / 1000)  # turn into seconds


_init_time = _time()


def running_time():
    '''Return the number of milliseconds since the board was switched on or
    restarted.'''
    return (_time() - _init_time) * 1000
