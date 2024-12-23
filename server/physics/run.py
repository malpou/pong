from animation import show_animation
from game_elements import *

# input lengths of the game elements 
x_max = 1
y_max = 1
ball_speed = x_max / 3 # units per second
ball_angle = 0
length_paddle = 0.2

#other inputs
dt = 1/60 # frames / second
tol = x_max / 1000

# create an instance of the game elements
game_board = GameBoard(x_max, y_max, tol)
ball = Ball(x_max, y_max, ball_speed, ball_angle)
paddle_left = Paddle(0, y_max/2, length_paddle, tol)
paddle_right = Paddle(1, y_max/2, length_paddle, tol)

# show the animation
show_animation(game_board, ball, paddle_left, paddle_right, dt)




