from microbit import *
from random import randint
import music


def game():
    # data
    ball_pool = [[False, 0, 0, 0, 0] for i in range(5)]
    brick_field = [[1] * 5 for i in range(2)]
    for i in range(3):
        brick_field.append([0] * 5)

    class DT:
        padx = 2.5
        bricks_count = 10
        new_brick_counter = 0
        active_balls = 0
        score = 0
        lives = 3

    # screen
    screen = Image(5, 5)

    # calculate ball speed
    get_ball_speed = lambda: min(0.3 + DT.score * 0.01, 0.6)

    # insert a ball
    def add_ball(x, y, vx, vy):
        music.play(['G5:1', 'C6:1'], wait=False)
        for ball in ball_pool:
            if not ball[0]:
                ball[0] = True
                ball[1] = x
                ball[2] = y
                ball[3] = vx
                ball[4] = vy
                DT.active_balls += 1
                return

    # update ball bouncing
    def update_ball_bounce(ball):
        # bounce at border
        if ball[1] < 0.5:
            ball[1] = 1 - ball[1]
            if ball[3] < 0:
                ball[3] *= -1
        if ball[1] >= 4.5:
            ball[1] = 9 - ball[1]
            if ball[3] > 0:
                ball[3] *= -1
        if ball[2] < 0.5:
            ball[2] = 1 - ball[2]
            if ball[4] < 0:
                ball[4] *= -1

    def update_ball_fall(ball):
        # bounce at pad
        if ball[2] >= 4 and ball[4] > 0 and abs(ball[1] - DT.padx) < 1:
            ball[3] = (ball[1] - DT.padx) * 0.5
            ball[4] *= -1
            scale = (ball[3]**2 + ball[4]**2)**0.5 / get_ball_speed()
            ball[3] /= scale
            ball[4] /= scale

        # deactive when falling
        if ball[2] >= 5:
            music.play('A3:2', wait=False)
            ball[0] = False
            DT.active_balls -= 1

    # hit brick
    def interact_brick(ball):
        x = int(ball[1])
        y = int(ball[2])
        if brick_field[y][x]:
            # break current brick
            if brick_field[y][x] == 1:
                music.play('C6:1', wait=False)
                DT.score += 1
            else:
                add_ball(x + 0.5, y + 0.5, 0, 0.4)
            brick_field[y][x] = 0
            DT.bricks_count -= 1

            # bounce ball
            if abs(ball[1] - x - 0.5) > abs(ball[2] - y - 0.5):
                ball[3] *= -1
            else:
                ball[4] *= -1

    # generate new brick field
    def new_brick_line():
        res = []
        for i in range(5):
            chance = randint(1, 100)
            if chance < 5:
                res.append(0)
            else:
                DT.bricks_count += 1
                if chance > 90:
                    res.append(-1)
                else:
                    res.append(1)
        return res

    # game logic
    def logic():
        # control pad with accelerometer
        DT.padx = min(4.5, max(0.5, accelerometer.get_x() / 200 + 2.5))

        # update bricks
        if DT.new_brick_counter > 50 + 10 * DT.bricks_count:
            brick_field.pop()
            brick_field.insert(0, new_brick_line())
            DT.new_brick_counter = 0

        # update balls
        if DT.active_balls > 0:
            DT.new_brick_counter += 1
            for ball in ball_pool:
                if not ball[0]:
                    continue
                # dx=vdt
                ball[1] += ball[3]
                ball[2] += ball[4]

                # update bounce
                update_ball_bounce(ball)
                update_ball_fall(ball)

                # hit brick
                if ball[0]:
                    interact_brick(ball)

        # shoot a new ball
        elif button_a.was_pressed() or button_b.was_pressed():
            DT.lives -= 1
            add_ball(DT.padx, 4.5, 0, -0.5)

    # draw a frame
    def update_frame():
        # draw pad
        for i in range(5):
            for j in range(5):
                screen.set_pixel(i, j, 0)
        for i in range(5):
            screen.set_pixel(i, 4, int(max(1 - abs(DT.padx - i - 0.5), 0) * 5))

        # draw ball
        for ball in ball_pool:
            if ball[0]:
                screen.set_pixel(int(ball[1]), int(ball[2]), 9)

        # draw bricks
        for x in range(5):
            for y in range(5):
                if brick_field[y][x] == 1:
                    screen.set_pixel(x, y, 4)
                elif brick_field[y][x] == -1:
                    screen.set_pixel(x, y, randint(3, 9))

        display.show(screen)
        sleep(50)

    # main loop
    while DT.active_balls + DT.lives > 0:
        logic()
        update_frame()
    sleep(100)
    music.play(music.POWER_DOWN)
    display.scroll('SCORE:%d' % DT.score, 100)


if __name__ == '__main__': game()