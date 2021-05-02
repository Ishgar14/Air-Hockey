from math import atan2 as angle, atan
from math import cos, sin, pi
from typing import *

import pygame
from pygame import Rect, color, display, draw, key

pygame.init()
WIDTH, HEIGHT = 800, 500

# Colours
WHITE = (255, 255, 255)
BLACK = (0,   0,   0)
RED = (255, 0,   0)
BLUE = (0,  0,  255)

# pygame essentials
screen = display.set_mode((WIDTH, HEIGHT))
display.set_caption("Air Hockey!")
font = pygame.font.SysFont(None, 30)

clock = pygame.time.Clock()
FPS = 60

# The left and right goals of game
GOALWIDTH = 10
GOALHEIGHT = HEIGHT // 5
GOAL = 5 # The number of goals needed to win the game

leftpost = Rect(0, HEIGHT // 2 - GOALHEIGHT // 2, GOALWIDTH, GOALHEIGHT)
rightpost = Rect(WIDTH - GOALWIDTH, HEIGHT // 2 -
                 GOALHEIGHT // 2, GOALWIDTH, GOALHEIGHT)

# Players of game
leftplayer = [WIDTH // 4, HEIGHT // 2]
rightplayer = [3 * WIDTH // 4, HEIGHT // 2]
PLAYERRADIUS = 20
MOVESPEED = 3
COLOURFRACTION = 0.3
LSCORE = RSCORE = 0
WINNER = None

# The ball
ball = [WIDTH // 2, HEIGHT // 2]
BALLVELL = [0, 0]
BALLRADIUS = HEIGHT // 35
BALLFRACTION = 0.3


# This function returns distance between two points
def distance(from_: Tuple[int], to: Tuple[int]) -> float:
    firstdiff = from_[0] - to[0]
    seconddiff = from_[1] - to[1]
    return (firstdiff ** 2 + seconddiff ** 2) ** 0.5

# this function draws the background of screen


def drawbackground() -> None:
    draw.line(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
    draw.circle(screen, WHITE, (WIDTH // 2, HEIGHT // 2), HEIGHT // 7, 1)

    # draw goal posts of both sides
    draw.rect(screen, (255, 115, 0), leftpost)
    draw.rect(screen, (0, 140, 155), rightpost)


# this function draws score on each player on top of screen
def drawscores() -> None:
    score = f"{LSCORE}"
    img = font.render(score, True, WHITE)
    screen.blit(img, (WIDTH // 3 - 3 * len(score), 0))

    score = f"{RSCORE}"
    img = font.render(score, True, WHITE)
    screen.blit(img, (2 * WIDTH // 3 - 3 * len(score), 0))


# this function draws the players of the game
def drawplayers() -> None:
    draw.circle(screen, (255, 140, 0), leftplayer, PLAYERRADIUS,
                int(PLAYERRADIUS * COLOURFRACTION))
    draw.circle(screen, WHITE, leftplayer, int(
        PLAYERRADIUS * (1 - COLOURFRACTION)))

    draw.circle(screen, (0, 140, 180), rightplayer,
                PLAYERRADIUS, int(PLAYERRADIUS * COLOURFRACTION))
    draw.circle(screen, WHITE, rightplayer, int(
        PLAYERRADIUS * (1 - COLOURFRACTION)))


def drawball() -> None:
    draw.circle(screen, BLACK, ball, BALLRADIUS,
                int(BALLRADIUS * BALLFRACTION))
    draw.circle(screen, WHITE, ball, int(BALLRADIUS * (1 - BALLFRACTION)))


# this function handles movement of given player
def move(object: List[int], x: int, y: int) -> List[int]:
    object[0] += x
    object[1] += y
    return object


def leftmove(key: int) -> None:
    global leftplayer

    if key == pygame.K_w:
        move(leftplayer, 0, -MOVESPEED)
    elif key == pygame.K_s:
        move(leftplayer, 0, MOVESPEED)

    if key == pygame.K_a:
        move(leftplayer, -MOVESPEED, 0)
    elif key == pygame.K_d:
        move(leftplayer, MOVESPEED, 0)


# this function detects collision of given player with border
def check(player: List[int]) -> None:
    global BALLVELL

    if player is leftplayer:
        if player[0] - PLAYERRADIUS < 0:
            player[0] = PLAYERRADIUS
        if player[1] - PLAYERRADIUS < 0:
            player[1] = PLAYERRADIUS

        if player[0] + PLAYERRADIUS > WIDTH // 2:
            player[0] = WIDTH // 2 - PLAYERRADIUS
        if player[1] + PLAYERRADIUS > HEIGHT:
            player[1] = HEIGHT - PLAYERRADIUS

    elif player is rightplayer:
        if player[0] - PLAYERRADIUS < WIDTH // 2:
            player[0] = WIDTH // 2 + PLAYERRADIUS
        if player[1] - PLAYERRADIUS < 0:
            player[1] = PLAYERRADIUS

        if player[0] + PLAYERRADIUS > WIDTH:
            player[0] = WIDTH - PLAYERRADIUS
        if player[1] + PLAYERRADIUS > HEIGHT:
            player[1] = HEIGHT - PLAYERRADIUS

    elif player is ball:
        if (ball[0] - BALLRADIUS < 0 or ball[0] + BALLRADIUS > WIDTH):
            BALLVELL[0] *= -1
        if (ball[1] - BALLRADIUS < 0 or ball[1] + BALLRADIUS > HEIGHT):
            BALLVELL[1] *= -1


# This function checks if player has hit ball
def hit_ball(player: List[int]) -> None:
    global BALLVELL

    if distance(player, ball) <= (PLAYERRADIUS + BALLRADIUS):
        direction = angle(ball[1] - player[1], ball[0] - player[0])
        BALLVELL = [MOVESPEED * cos(direction), MOVESPEED * sin(direction)]


# This function checks if ball hit either of goal posts
def goal(post: Rect) -> bool:
    # Find the closest point of circle lying in rectangle
    closestX = clamp(ball[0], post.x, post.x + post.width)
    closestY = clamp(ball[1], post.y, post.y + post.height)

    distanceX = ball[0] - closestX
    distanceY = ball[1] - closestY

    return (distanceX ** 2 + distanceY ** 2) < BALLRADIUS ** 2


# This function is used to set the value within given bounds
def clamp(val: int, minimum: int, maximum: int) -> int:
    if val < minimum:
        return minimum
    elif val > maximum:
        return maximum
    else:
        return val


# This function resets everything to its initial state
def reset(resetScore: bool = False) -> None:
    global ball, BALLVELL, leftplayer, rightplayer, LSCORE, RSCORE

    ball = [WIDTH // 2, HEIGHT // 2]
    BALLVELL = [0, 0]

    leftplayer = [WIDTH // 4, HEIGHT // 2]
    rightplayer = [3 * WIDTH // 4, HEIGHT // 2]

    if resetScore:
        LSCORE = RSCORE = 0


# this function is called every frame of game
def loop() -> None:
    global LSCORE, RSCORE, ball, BALLVELL, WINNER

    screen.fill((80, 190, 125))  # fill the screen with light green
    drawbackground()
    drawscores()
    drawplayers()
    drawball()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(1)

    keys = key.get_pressed()

    # If player presses R then restart the game
    if keys[pygame.K_r]:
        reset(True)

    # handle movement of left player
    move(leftplayer, (keys[pygame.K_d] - keys[pygame.K_a]) * MOVESPEED,
         (keys[pygame.K_s] - keys[pygame.K_w]) * MOVESPEED)

    # handle movement of right player
    move(rightplayer, (keys[pygame.K_l] - keys[pygame.K_j]) * MOVESPEED,
         (keys[pygame.K_k] - keys[pygame.K_i]) * MOVESPEED)

    # checking collision of player with walls
    check(leftplayer)
    check(rightplayer)
    check(ball)

    # checking collision of player with ball
    hit_ball(leftplayer)
    hit_ball(rightplayer)

    # check collision of ball with post
    if goal(leftpost):
        reset()
        RSCORE += 1

    if goal(rightpost):
        reset()
        LSCORE += 1
    
    if LSCORE == GOAL:
        WINNER = "Left PLayer"
    elif RSCORE == GOAL:
        WINNER = "Right Player"

    ball[0] += BALLVELL[0]
    ball[1] += BALLVELL[1]

    clock.tick(FPS)
    display.flip()

def showWinner() -> None:
    global WINNER

    screen.fill((90, 180, 180))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
        
    keys = key.get_pressed()

    # If player presses R then restart the game
    if keys[pygame.K_r]:
        reset(True)
        WINNER = None
        return

    win = f"The winner is {WINNER}!"
    img = font.render(win, True, WHITE)
    screen.blit(img, (WIDTH // 2 - 5 * len(win), HEIGHT // 2))

    restartmsg = "Press R to restart"
    img = font.render(restartmsg, True, WHITE)
    screen.blit(img, (0, 0))

    clock.tick(FPS)
    display.flip()
    

while True:
    if WINNER is None:
        loop()
    else:
        showWinner()