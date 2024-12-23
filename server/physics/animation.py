import numpy as np
import matplotlib.pyplot as plt
import time 

from matplotlib.animation import FuncAnimation

def move_ball(game_board, ball, paddle_left, paddle_right, dt):
    x, y = calc_pos(ball, dt)    

    # inside of the board
    if game_board.is_in_boudaries(x, y):
        return x, y, ball.angle
    
    # bounces on the paddles
    elif (
        paddle_left.is_on_paddle(x, y) or 
        paddle_right.is_on_paddle(x, y)
        ):
        ball.angle += 3 * np.pi / 4
        x, y = calc_pos(ball, dt)
        return x, y, ball.angle
    
    # bounces on a horizontal wall
    elif (game_board.is_on_horizontal_wall(x,y)):
        print(f"Collision with horizontal wall. Angle before flip: {ball.angle}")
        ball.angle = -ball.angle
        print(f"Angle after flip: {ball.angle}")
        x, y = calc_pos(ball, dt)
        return x, y, ball.angle
    
    # the ball is not caught by the opponent
    else:
        if ball.x > 0.5:
            winner = "left"
        else:
            winner = "right"

        ball.reset_ball_pos(winner)
        time.sleep(1.5)
        return ball.x, ball.y, ball.angle

def calc_pos(ball, dt):
    v_x = ball.speed * np.cos(ball.angle)
    v_y = ball.speed * np.sin(ball.angle)

    x = ball.x + v_x * dt
    y = ball.y + v_y * dt

    return x, y

def show_animation(game_board, ball, paddle_left, paddle_right, dt):
    fig, ax = plt.subplots()

    # Boundaries of the game board
    ax.set_xlim(0, game_board.x_max)
    ax.set_ylim(0, game_board.y_max)

    # Scatter plot for the game elements
    ball_scatter, = ax.plot([], [], 'bo', markersize=10)
    paddle_left_scatter, = ax.plot(
        [paddle_left.x, paddle_left.x],
        [paddle_left.y + paddle_left.length/2, paddle_left.y - paddle_left.length/2], 
        'r-', 
        linewidth=10)
    paddle_right_scatter, = ax.plot(
        [paddle_right.x, paddle_right.x],
        [paddle_right.y + paddle_right.length/2, paddle_right.y - paddle_right.length/2], 
        'r-', 
        linewidth=10)

    # Initialize the plot
    def init():
        ball_scatter.set_data([ball.x], [ball.y])
        return ball_scatter,

    # Update function for the animation
    def update(frame):
        # Generate random coordinates for the ball within the rectangle
        ball.x, ball.y, ball.angle = move_ball(game_board, ball, paddle_left, paddle_right, dt)
        
        # Update the ball position
        ball_scatter.set_data([ball.x], [ball.y])
        return ball_scatter,

    # Create an animation that updates every second (1000ms)
    ani = FuncAnimation(fig, update, frames=100, init_func=init, blit=True, interval=dt)

    # Show the plot
    plt.show()