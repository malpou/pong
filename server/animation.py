import numpy as np
import matplotlib.pyplot as plt
import time 

from matplotlib.animation import FuncAnimation

from domain.game import GameState


def show_animation(game: GameState, dt):
    fig, ax = plt.subplots()

    # Boundaries of the game board
    ax.set_xlim(0, game.GAME_WIDTH)
    ax.set_ylim(0, game.GAME_HEIGHT)

    # Scatter plot for the game elements
    ball_scatter, = ax.plot([], [], 'bo', markersize=10)
    paddle_left_scatter, = ax.plot(
        [game.left_paddle.x_position, game.left_paddle.x_position],
        [game.left_paddle.y_position + game.left_paddle.height/2, game.left_paddle.y_position - game.left_paddle.height/2], 
        'r-', 
        linewidth=10)
    paddle_right_scatter, = ax.plot(
        [game.right_paddle.x_position, game.right_paddle.x_position],
        [game.right_paddle.y_position + game.right_paddle.height/2, game.right_paddle.y_position - game.right_paddle.height/2], 
        'r-', 
        linewidth=10)

    # Initialize the plot
    def init():
        ball_scatter.set_data([game.ball.x], [game.ball.y])
        return ball_scatter,

    # Update function for the animation
    def update(frame):
        # Generate random coordinates for the ball within the rectangle
        game.update()
        
        # Update the ball position
        ball_scatter.set_data([game.ball.x], [game.ball.y])
        return ball_scatter,

    # Create an animation that updates every second (1000ms)
    ani = FuncAnimation(fig, update, frames=100, init_func=init, blit=True, interval=dt)

    # Show the plot
    plt.show()

#other inputs
dt = 1/60 # frames / second

game = GameState()

# show the animation
show_animation(game, dt)




