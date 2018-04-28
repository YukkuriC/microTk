__doc__ = '''Module entry
initialize display and load all sub-modules

Containment:
- method
-- microbit.running_time
-- microbit.sleep
-- microbit.temperature
- module
-- microbit.display
-- microbit.accelerometer
- object
-- microbit.button_a
-- microbit.button_b
-- microbit.pin0-19 (without 17,18)
'''

# root functions & classes
from .display import Image, panic
from ._timebase import *
from ._hardware import *

# sub modules
from . import display
from . import accelerometer
from . import compass

# add links
from os.path import abspath, split
from sys import path

curr_path = split(__file__)[0]
pkg_path = curr_path + '\\_external_modules'
path.append(pkg_path)  # make 'music' an importable module
path.append(split(curr_path)[0])  # make this an importable package

__all__ = [
    'display', 'accelerometer','compass', 'Image', 'button_a', 'button_b', 'panic',
    'pin0', 'pin1', 'pin2', 'pin3', 'pin4', 'pin5', 'pin6', 'pin7', 'pin8',
    'pin9', 'pin10', 'pin11', 'pin12', 'pin13', 'pin14', 'pin15', 'pin16',
    'pin19', 'pin20', 'running_time', 'sleep', 'temperature'
]
