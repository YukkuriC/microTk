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

from ._hardware import spatial

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
        pass

    # .. note::

    #     MicroPython understands the following gesture names: ``"up"``, ``"down"``,
    #     ``"left"``, ``"right"``, ``"face up"``, ``"face down"``, ``"freefall"``,
    #     ``"3g"``, ``"6g"``, ``"8g"``, ``"shake"``. Gestures are always
    #     represented as strings.

    def is_gesture(name):
        '''Return True or False to indicate if the named gesture is currently active.'''

    def was_gesture(name):
        '''Return True or False to indicate if the named gesture was active since the
        last call.'''

    def get_gestures():
        '''Return a tuple of the gesture history. The most recent is listed last.
        Also clears the gesture history before returning.'''