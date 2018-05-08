__doc__ = '''micro:bit music module
output analog to pins with different period for notes
'''

from threading import Thread as _Thread
from time import sleep as _sleep, perf_counter as _perf
import microbit

pin_class = microbit.pin0.__class__

if 'music':
    _tick = 4
    _bpm = 120
    _octave = 4
    _duration = 4
    _tick_l = 125

    # output frequency to pin
    def _play_freq(pin, freq, duration):
        pin.set_analog_period_microseconds(int(1000000 / freq))
        pin.write_analog(511)
        # with pin_class.tlock:
        pin_class.tones.appendleft((pin, int(freq), _perf() + duration / 1000))
        _sleep(duration / 1000)

    # read note
    _note_offset = {
        'C': -9,
        'D': -7,
        'E': -5,
        'F': -4,
        'G': -2,
        'A': 0,
        'B': 2
    }

    def _parse_music_note(note, pin, curr_octave, curr_duration):
        print(note)
        try:
            tmp = note.split(':')
            assert len(tmp) in (1, 2)

            # parse duration
            if len(tmp) == 2:
                curr_duration = int(tmp[1])
            tmp = tmp[0]

            # parse octave
            if tmp[-1].isdigit():
                curr_octave = int(tmp[-1])
                tmp = tmp[:-1]

            # parse frequency
            assert len(tmp) <= 2
            tmp = tmp.capitalize()
            if tmp == 'R':  # rest
                pin.volt = 0
                _sleep(_tick_l * curr_duration * 0.001)
                return curr_octave, curr_duration
            elif 'A' <= tmp[0] <= 'G':  # note
                offset = _note_offset[tmp[0]]
                if len(tmp) == 2:
                    if tmp[1] == '#':
                        offset += 1
                    elif tmp[1] == 'b':
                        offset -= 1
                    else:
                        raise
            else:  # illegal
                raise

        except:
            raise ValueError('%r is not a valid note' % note)

        freq = 2**(curr_octave - 4 + offset / 12) * 440
        _play_freq(pin, freq, _tick_l * curr_duration)
        return curr_octave, curr_duration

    # read note sequence
    def _parse_music_seq(music, pin, loop, in_thread=False):
        if not music:
            return

        # enter loop once/forever
        while 1:
            # play
            curr_octave, curr_duration = _octave, _duration
            for i in music:
                if in_thread and _thread_running[pin] != in_thread:
                    return
                curr_octave, curr_duration = _parse_music_note(
                    i, pin, curr_octave, curr_duration)

            # break if not loop
            if not loop:
                break

        # clear afterwards
        stop(pin)

    def set_tempo(ticks=4, bpm=120):
        assert isinstance(ticks, int) and isinstance(
            bpm, int) and ticks > 0 and bpm > 0

        global _tick, _bpm, _tick_l
        _tick = ticks
        _bpm = bpm
        _tick_l = 60000 / ticks / bpm

    def get_tempo():
        return (_tick, _bpm)

    def play(music, pin=microbit.pin0, wait=True, loop=False):
        if isinstance(music, str):
            music = [music]

        _thread_running[pin] = False
        if wait:
            _parse_music_seq(music, pin, loop)
        else:
            _play_bgm(_parse_music_seq, (music, pin, loop), pin)

    def _pitch(freq, duration, pin, in_thread=False):
        if duration < 0:
            while 1:
                if in_thread and _thread_running[pin] != in_thread:
                    return
                _play_freq(pin, freq, 100)
        else:
            _play_freq(pin, freq, duration)

        # clear afterwards
        stop(pin)

    def pitch(frequency, duration=-1, pin=microbit.pin0, wait=True):
        assert isinstance(duration, int) and duration >= -1

        _thread_running[pin] = False
        if frequency <= 0:
            return
        if wait:
            _pitch(frequency, duration, pin)
        else:
            _play_bgm(_pitch, (frequency, duration, pin), pin)

    def stop(pin=microbit.pin0):
        _thread_running[pin] = False
        pin.write_digital(0)

    def reset():
        set_tempo()
        _octave = 4
        _duration = 4


if 'BGM':
    _bgm_thread = _Thread()
    _thread_running = dict((p, False) for p in pin_class.pins if p)

    def _play_bgm(func, args, pin):
        thr_id = _perf()
        _thread_running[pin] = thr_id
        _bgm_thread = _Thread(target=func, args=(*args, thr_id))
        _bgm_thread.start()


if 'builtin melody':
    DADADADUM = 'R4:2|G|G|G|Eb:8|R:2|F|F|F|D:8'.split('|')
    ENTERTAINER = 'D4:1|D#|E|C5:2|E4:1|C5:2|E4:1|C5:3|C:1|D|D#|E|C|D|E:2|B4:1|D5:2|C:4'.split(
        '|')
    PRELUDE = 'C4:1|E|G|C5|E|G4|C5|E|C4|E|G|C5|E|G4|C5|E|C4|D|G|D5|F|G4|D5|F|C4|D|G|D5|F|G4|D5|F|B3|D4|G|D5|F|G4|D5|F|B3|D4|G|D5|F|G4|D5|F|C4|E|G|C5|E|G4|C5|E|C4|E|G|C5|E|G4|C5|E'.split(
        '|')
    ODE = 'E4|E|F|G|G|F|E|D|C|C|D|E|E:6|D:2|D:8|E:4|E|F|G|G|F|E|D|C|C|D|E|D:6|C:2|C:8'.split(
        '|')
    NYAN = 'F#5:2|G#|C#:1|D#:2|B4:1|D5:1|C#|B4:2|B|C#5|D|D:1|C#|B4:1|C#5:1|D#|F#|G#|D#|F#|C#|D|B4|C#5|B4|D#5:2|F#|G#:1|D#|F#|C#|D#|B4|D5|D#|D|C#|B4|C#5|D:2|B4:1|C#5|D#|F#|C#|D|C#|B4|C#5:2|B4|C#5|B4|F#:1|G#|B:2|F#:1|G#|B|C#5|D#|B4|E5|D#|E|F#|B4:2|B|F#:1|G#|B|F#|E5|D#|C#|B4|F#|D#|E|F#|B:2|F#:1|G#|B:2|F#:1|G#|B|B|C#5|D#|B4|F#|G#|F#|B:2|B:1|A#|B|F#|G#|B|E5|D#|E|F#|B4:2|C#5'.split(
        '|')
    RINGTONE = 'C4:1|D|E:2|G|D:1|E|F:2|A|E:1|F|G:2|B|C5:4'.split('|')
    FUNK = 'C2:2|C|D#|C:1|F:2|C:1|F:2|F#|G|C|C|G|C:1|F#:2|C:1|F#:2|F|D#'.split(
        '|')
    BLUES = 'C2:2|E|G|A|A#|A|G|E|C2:2|E|G|A|A#|A|G|E|F|A|C3|D|D#|D|C|A2|C2:2|E|G|A|A#|A|G|E|G|B|D3|F|F2|A|C3|D#|C2:2|E|G|E|G|F|E|D'.split(
        '|')
    BIRTHDAY = 'C4:3|C:1|D:4|C:4|F|E:8|C:3|C:1|D:4|C:4|G|F:8|C:3|C:1|C5:4|A4|F|E|D|A#:3|A#:1|A:4|F|G|F:8'.split(
        '|')
    WEDDING = 'C4:4|F:3|F:1|F:8|C:4|G:3|E:1|F:8|C:4|F:3|A:1|C5:4|A4:3|F:1|F:4|E:3|F:1|G:8'.split(
        '|')
    FUNERAL = 'C3:4|C:3|C:1|C:4|D#:3|D:1|D:3|C:1|C:3|B2:1|C3:4'.split('|')
    PUNCHLINE = 'C4:3|G3:1|F#|G|G#:3|G|R|B|C4'.split('|')
    PYTHON = 'D5:1|B4|R|B|B|A#|B|G5|R|D|D|R|B4|C5|R|C|C|R|D|E:5|C:1|A4|R|A|A|G#|A|F#5|R|E|E|R|C|B4|R|B|B|R|C5|D:5|D:1|B4|R|B|B|A#|B|B5|R|G|G|R|D|C#|R|A|A|R|A|A:5|G:1|F#:2|A:1|A|G#|A|E:2|A:1|A|G#|A|D|R|C#|D|R|C#|D:2|R:3'.split(
        '|')
    BADDY = 'C3:3|R|D:2|D#|R|C|R|F#:8'.split('|')
    CHASE = 'A4:1|B|C5|B4|A:2|R|A:1|B|C5|B4|A:2|R|A:2|E5|D#|E|F|E|D#|E|B4:1|C5|D|C|B4:2|R|B:1|C5|D|C|B4:2|R|B:2|E5|D#|E|F|E|D#|E'.split(
        '|')
    BA_DING = 'B5:1|E6:3'.split('|')
    WAWAWAWAA = 'E3:3|R:1|D#:3|R:1|D:4|R:1|C#:8'.split('|')
    JUMP_UP = 'C5:1|D|E|F|G'.split('|')
    JUMP_DOWN = 'G5:1|F|E|D|C'.split('|')
    POWER_UP = 'G4:1|C5|E|G:2|E:1|G:3'.split('|')
    POWER_DOWN = 'G5:1|D#|C|G4:2|B:1|C5:3'.split('|')
