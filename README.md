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

## TODO:
2. compass

3. audio, etc.

4. more GUI

5. setting menu at start-up

5. inner [uFlash](https://uflash.readthedocs.io/en/latest/_modules/uflash.html) support

***

## Alpha 0.2.0
Call me __THREAD MASTER__ :(
### Change log:
* sub-window system separated from '_screen.py'
* music system  
    * playing and pitching
    * support of switching between pins
    * pressing B calls the beeper controller window
* accelerometer system (numeric value part)
    * getting acceleration value on XYZ axis
    * pressing R calls a  window to control spatial rotation with mouse

### Bug fixes
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
* full operational 'display' module
* disables float LED lightness and image input  
_yes because __real__ ones don't_
* minor alterations, bug fixes and 
* more abundant README.md  \yay/

***

## Alpha 0.0.4
### Change log:
* separate main widget into a standalone thread
* simple '\_\_doc__' for codes
* information bar (temporarily) at bottom

***

## Alpha 0.0.3

### Change log:
* code structure refactor

* display
    * auto cut long image into list
    * re-support float LED lightness

* image
    * defination of \_\_sub__ operator

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
* button_a & button_b input implement with mouse click