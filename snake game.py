from microbit import *
from random import randint


def SNAKE():
    # ============ FUNCTIONS ============
    # update display
    def update_frame(frame):
        bitmap = Image()
        bitmap.set_pixel(*SNAKE.head, 6)
        for bodypart in SNAKE.body:
            bitmap.set_pixel(*bodypart, 3)
        if frame // 5 == 0:
            bitmap.set_pixel(*SNAKE.pt, 9)
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
        for i in range(2):
            display.set_pixel(*SNAKE.head,0)
            sleep(100)
            display.set_pixel(*SNAKE.head,9)
            sleep(100)
        display.set_pixel(*SNAKE.pt, 0)
        while SNAKE.body:
            display.set_pixel(*SNAKE.body[0], 0)
            SNAKE.body.pop(0)
            sleep(100)
        display.scroll('SCORE:%d' % SNAKE.SCORE)

    # ============ MAIN LOGIC ============
    # init
    SNAKE.head = [0, 0]
    SNAKE.GOTO = [[1, 0, -1, 0], [0, 1, 0, -1]]
    SNAKE.GAME_RUNNING = True
    SNAKE.CURR_DIRECTION = 0
    SNAKE.SCORE = 1
    SNAKE.body = [[0, 0]]
    SNAKE.pt = [0, 0]
    while SNAKE.pt == SNAKE.head:
        SNAKE.pt = [randint(0, 4), randint(0, 4)]

    # main process
    frame = 0
    while SNAKE.GAME_RUNNING:
        update_frame(frame)
        frame += 1
        if frame >= 10:
            frame -= 10
            game_logic()
    gameover_screen()


display.scroll('SNAKE', 75)
while 1:
    SNAKE()