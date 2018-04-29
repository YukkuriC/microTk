__doc__ = '''accelerometer module
simulates gravity and gestures saparately

Containment:
- method
-- microbit.accelerometer.get_x
-- microbit.accelerometer.get_y
-- microbit.accelerometer.get_z
-- microbit.accelerometer.get_values
-- microbit.accelerometer.current_gesture
-- microbit.accelerometer.is_gesture
-- microbit.accelerometer.was_gesture
-- microbit.accelerometer.get_gestures
'''

from ._hardware import spatial, gesture

if 'numeric value':
    _g = 1024

    def get_x():
        return -int(_g * spatial.r_matrix[0][2])

    def get_y():
        return -int(_g * spatial.r_matrix[1][2])

    def get_z():
        return -int(_g * spatial.r_matrix[2][2])

    def get_values():
        return get_x(), get_y(), get_z()


if 'gesture':

    def current_gesture():
        return gesture.curr

    def is_gesture(name):
        return gesture.curr == name

    def was_gesture(name):
        res = gesture.appeared[name]
        for g in gesture.all:
            gesture.appeared[g] = False
        gesture.curr = "face up"
        return res

    def get_gestures():
        res = tuple(gesture.sequence)
        gesture.sequence = []
        return res