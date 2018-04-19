__doc__='''Module entry
initialize display and load all sub-modules

Containment:
- method
-- microbit.running_time
-- microbit.sleep
-- microbit.temperature
- module
-- microbit.display
- object
-- microbit.button_a
-- microbit.button_b
'''

# root functions & classes
from ._timebase import *
from ._hardware import *
from .display import Image, panic

# display module
from . import display
