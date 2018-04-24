from microbit import *
from random import randint
import music

def SNAKE():
    # ============ GAME DATA ============
    class SNAKE_data:
        def __init__(SNAKE):
            SNAKE.head = [0, 0]
            SNAKE.GOTO = [[1, 0, -1, 0], [0, 1, 0, -1]]
            SNAKE.GAME_RUNNING = True
            SNAKE.CURR_DIRECTION = 0
            SNAKE.SCORE = 1
            SNAKE.body = [[0, 0]]
            SNAKE.pt = [0, 0]
            while SNAKE.pt == SNAKE.head:
                SNAKE.pt = [randint(0, 4), randint(0, 4)]

    # ============ FUNCTIONS ============
    # update display
    def update_frame(frame):
        bitmap = Image(5, 5)
        for i in range(len(SNAKE.body)):
            bodypart = SNAKE.body[i]
            lightness = int(7 - (4 * (i + 1) / len(SNAKE.body)))
            bitmap.set_pixel(bodypart[0], bodypart[1], lightness)
        bitmap.set_pixel(SNAKE.head[0], SNAKE.head[1], 8)
        if frame:
            bitmap.set_pixel(SNAKE.pt[0], SNAKE.pt[1], 9 - 2 * abs(5 - frame))
        display.show(bitmap)
        sleep(50)

    # update game
    def game_logic():
        # handle & clear control
        left, right = button_a.get_presses() > 0, button_b.get_presses() > 0
        if left and not right:
            SNAKE.CURR_DIRECTION = (SNAKE.CURR_DIRECTION + 3) % 4
        elif right and not left:
            SNAKE.CURR_DIRECTION = (SNAKE.CURR_DIRECTION + 1) % 4

        # extend body
        SNAKE.body.insert(0, [SNAKE.head[0], SNAKE.head[1]])
        if len(SNAKE.body) > SNAKE.SCORE:
            SNAKE.body.pop()

        # move head
        SNAKE.head[0] = (
            SNAKE.head[0] + SNAKE.GOTO[0][SNAKE.CURR_DIRECTION] + 5) % 5
        SNAKE.head[1] = (
            SNAKE.head[1] + SNAKE.GOTO[1][SNAKE.CURR_DIRECTION] + 5) % 5

        # check collision
        for bodypart in SNAKE.body:
            if SNAKE.head == bodypart:
                SNAKE.GAME_RUNNING = False
                return

        # eat & regenerate point
        if SNAKE.pt == SNAKE.head:
            SNAKE.SCORE += 1
            music.play(['G5:1','C6:1'],wait=False)
            # end gmae
            if SNAKE.SCORE == 25:
                SNAKE.GAME_RUNNING = None
                return

            # generate new point
            occupied = [[False] * 5 for i in range(5)]
            occupied[SNAKE.head[0]][SNAKE.head[1]] = True
            for bodypart in SNAKE.body:
                occupied[bodypart[0]][bodypart[1]] = True
            tmp = []
            for x in range(5):
                for y in range(5):
                    if not occupied[x][y]:
                        tmp.append([x, y])
            SNAKE.pt = tmp[randint(0, len(tmp) - 1)]

    # end game
    def gameover_screen():
        music.play(music.POWER_DOWN,wait=False)
        update_frame(0)
        for i in range(2):
            display.set_pixel(SNAKE.head[0], SNAKE.head[1], 0)
            sleep(100)
            display.set_pixel(SNAKE.head[0], SNAKE.head[1], 9)
            sleep(100)
        display.set_pixel(SNAKE.pt[0], SNAKE.pt[1], 0)
        while SNAKE.body:
            display.set_pixel(SNAKE.body[0][0], SNAKE.body[0][1], 0)
            SNAKE.body.pop(0)
            sleep(100)
        display.scroll('SCORE:%d' % SNAKE.SCORE)

    def clear_screen():
        music.play(music.NYAN,wait=False)
        update_frame(0)
        while not (button_a.get_presses() or button_b.get_presses()):
            SNAKE.body.insert(0, SNAKE.head)
            SNAKE.head = SNAKE.body.pop()
            update_frame(0)
        display.scroll('GAMECLEAR')

    # ============ MAIN LOGIC ============
    # init
    SNAKE = SNAKE_data()

    # main process
    frame = 0
    button_a.get_presses()
    button_b.get_presses()
    while SNAKE.GAME_RUNNING:
        update_frame(frame)
        frame += 1
        if frame >= 10:
            frame -= 10
            game_logic()
    if SNAKE.GAME_RUNNING is None:
        clear_screen()
    else:
        gameover_screen()

display.scroll('SNAKE', 75)
while 1:
    SNAKE()