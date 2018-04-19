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
    _sleep(ms / 1000)  # turn into seconds


_init_time = _time()


def running_time():
    return (_time() - _init_time) * 1000
