from time import sleep as _sleep, perf_counter as _time

def sleep(ms):
    _sleep(ms / 1000)  # turn into seconds


_init_time = _time()


def running_time():
    return (_time() - _init_time) * 1000
