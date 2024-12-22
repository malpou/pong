import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def show_animation(game_board, ball, bat_1, bat_2):
    fig, ax = plt.subplots()

    # Boundaries of the game board
    ax.set_xlim(0, game_board.x_max)
    ax.set_ylim(0, game_board.y_max)

    # Scatter plot for the game elements
    ball_scatter, = ax.plot([], [], 'bo', markersize=10)
    bat_1_scatter, = ax.plot(
        [bat_1.x, bat_1.x],
        [bat_1.y + bat_1.length/2, bat_1.y - bat_1.length/2], 
        'r-', 
        linewidth=10)
    bat_2_scatter, = ax.plot(
        [bat_2.x, bat_2.x],
        [bat_2.y + bat_2.length/2, bat_2.y - bat_2.length/2], 
        'r-', 
        linewidth=10)

    # Initialize the plot
    def init():
        ball_scatter.set_data([ball.x], [ball.y])
        return ball_scatter,

    # Update function for the animation
    def update(frame):
        # Generate random coordinates for the ball within the rectangle
        ball.x += np.random.uniform(-game_board.x_max/10, game_board.x_max/10)
        ball.y += np.random.uniform(-game_board.y_max/10, game_board.y_max/10)
        
        # Update the ball position
        ball_scatter.set_data([ball.x], [ball.y])
        return ball_scatter,

    # Create an animation that updates every second (1000ms)
    ani = FuncAnimation(fig, update, frames=100, init_func=init, blit=True, interval=1000)

    # Show the plot
    plt.show()