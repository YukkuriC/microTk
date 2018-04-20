from microbit import *
from random import randrange

display.show(Image.ALL_CLOCKS,wait=False,loop=True)
while 1:
    for i in range(randrange(1,10)):
        display.set_pixel(randrange(5),randrange(5),randrange(10))
    sleep(randrange(100,1000))
