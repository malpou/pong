from animation import show_animation
from game_elements import *

# input lengths of the game elements 
x_max = 1
y_max = 1
ball_speed = 0.1 # units per seconds
length_bat = 0.2

# create an instance of the game elements
game_board = GameBoard(x_max, y_max)
ball = Ball(x_max, y_max, ball_speed)
bat_1 = Bat(0, y_max/2, length=length_bat)
bat_2 = Bat(1, y_max/2, length=length_bat)

# show the animation
show_animation(game_board, ball, bat_1, bat_2)




