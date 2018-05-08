# microTk
[BBC micro:bit](https://microbit.org/) simulator ([MicroPython](http://python.microbit.org) interpreter) with tkinter canvas

## Completed:

* microbit root  
_running_time, sleep  
button_a, button_b (simulated with mouse buttons)  
temperature (simulated with mouse wheel & middle button)
pin0-19_

* microbit.Image  
_everything_

* microbit.display  
_same as above_

* microbit.accelerometer  
_everything...I guess  
value part and gesture part are saparate,   
controlled by different window_

* microbit.compass  
_without calibration minigame  
might do it later
magnetic field controlled by sub-window_

* sub control panel  
   * P: pin
   * B: beeper
   * R: rotation (for accelerometer)
   * G: gesture (for accelerometer)
   * C: magnetic field direction (for compass)

## TODO:
_maybe not_

***

## Epsilon 1.2
### Change log
* merges version code

### Bug fixes
* fixed a logical bug in __music__ and __display__, which causes unusual performance when providing empty lists into background thread.
* music module now receives notes with lower-letter names
* removes unnecessary import of sys in __\_screen__
* fixed a bug treating rest note improperly in __music__

***

## Delta 1.0
### Change log:
* disables printing events when pressing keyboard

### Bug fixes
* missed hook for several sub-windows added

***

## Gamma 1.0
### Change log:
* __compass__ module
* some optimization about spatial control sub-window
* unusual version code
    * _I guess there's not much time_

***

## Beta 1.0
Test it out!
### Change log:
* gesture part of accelerometer  
_yes it's done_

### Bug fixes:
* removes the ValueError bug when __music.pitch__ gets a frequency 0

***

## Alpha 0.2.0
Call me __THREAD MASTER__ :(
### Change log:
* sub-window system separated from __\_screen.py__
* music system  
    * playing and pitching
    * support of switching between pins
    * pressing B calls the beeper controller window
* accelerometer system (numeric value part)
    * getting acceleration value on XYZ axis
    * pressing R calls a  window to control spatial rotation with mouse

### Bug fixes:
* fixed background display system  
    now restarting background thread won't cause exceptions
* fixed improper import path redirect
* fixed some misunderstanding about Image operation functions, and a following bug causing display.scroll to loop infinitely

***

## Alpha 0.1.0
### Change log: 
* environment path redirect for music/audio import
* GUI
    * button status now showed by GUI button
    * mouse hover to check LED status at leftbottom of screen
* support for pins
    * read, write, etc.
    * pressing P toggles pin information window
* some code refactor

***

## Alpha 0.0.5
### __Now I have a REAL micro:bit!__
### Change log:
* full operational __display__ module
* disables float LED lightness and image input  
_yes because __real__ ones don't_
* minor alterations, bug fixes and 
* more abundant README.md  \yay/

***

## Alpha 0.0.4
### Change log:
* separate main widget into a standalone thread
* simple __\_\_doc____ for codes
* information bar (temporarily) at bottom

***

## Alpha 0.0.3

### Change log:
* code structure refactor

* display
    * auto cut long image into list
    * re-support float LED lightness

* image
    * defination of __\_\_sub____ operator

***

## Alpha 0.0.2

### Change log:
* display
    * new appearance of LED screen

* Image
    * Image.fill
    * Image.invert
    * Image.blit
    * Image.crop
    * Image + Image; Image * value
    * constant images

* tons of bugs fixed

***

## Alpha 0.0.1

### Completed:
* basic Image operations
* basic display module
* __button_a__ & __button_b__ input implement with mouse click
