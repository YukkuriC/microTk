__doc__ = '''Compass module
calibration part ignored

Containment:
-- microbit.compass.calibrate
-- microbit.compass.clear_calibration
-- microbit.compass.get_field_strength
-- microbit.compass.get_x
-- microbit.compass.get_y
-- microbit.compass.get_z
-- microbit.compass.heading
-- microbit.compass.is_calibrated
'''
__all__ = [
    'calibrate', 'clear_calibration', 'get_field_strength', 'get_x', 'get_y',
    'get_z', 'heading', 'is_calibrated'
]

from ._hardware import spatial, magnetic
from .display import show, Image
from math import atan2, pi

_done = False


def calibrate():
    show([Image('09090:09090:00000:90009:09990')], 1000)
    global _done
    _done = True


def is_calibrated():
    return _done


def clear_calibration():
    global _done
    _done = False


def get_x():
    assert _done
    return int(magnetic.str_x * spatial.r_matrix[0][0] +
               magnetic.str_y * spatial.r_matrix[0][1])


def get_y():
    assert _done
    return int(magnetic.str_x * spatial.r_matrix[1][0] +
               magnetic.str_y * spatial.r_matrix[1][1])


def get_z():
    assert _done
    return int(magnetic.str_x * spatial.r_matrix[2][0] +
               magnetic.str_y * spatial.r_matrix[2][1])


def heading():
    assert _done
    return (int(-90 - atan2(get_y(), get_x()) * 180 / pi) + 360) % 360


def get_field_strength():
    assert _done
    return magnetic.strength