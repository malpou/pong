import numpy as np

class GameBoard:

    def __init__(self, x_max, y_max, tol):
        self.x_max = x_max
        self.y_max = y_max
        self.tol = tol
        self.board_corners = [(0,0),
                              (x_max,0),
                              (0,y_max),
                              (x_max,y_max)]
        
    def is_in_boudaries(self, x_obj, y_obj):

        if (
            (x_obj > self.x_max - self.tol) or 
            (x_obj < 0 + self.tol) or
            (y_obj > self.y_max - self.tol) or
            (y_obj < 0 + self.tol)
        ):
            return False
        return True
    
    def is_on_horizontal_wall(self, x_obj, y_obj):

        if (
            ((x_obj > self.tol) and (x_obj - self.x_max < self.tol)) and
            ((self.y_max - y_obj < self.tol) or (y_obj < self.tol))
        ):
            return True
        return False
    
    
class Ball:

    def __init__(self, x_max, y_max, speed, angle):
        self.x_max = x_max
        self.y_max = y_max
        self.x = x_max / 2
        self.y = y_max / 2
        self.speed = speed
        self.angle = angle

    def reset_ball_pos(self, winner):
        if winner == "left":     
            self.angle = np.pi
        else:
            self.angle = 0
        self.__init__(self.x_max, self.y_max, self.speed, self.angle)

class Paddle:

    def __init__(self, x_paddle, y_paddle, length, tol):
        self.x = x_paddle
        self.y = y_paddle
        self.length = length
        self.tol = tol
        self.y_max = y_paddle + length / 2
        self.y_min = y_paddle - length / 2

    def is_on_paddle(self, x_obj, y_obj):

        if (
            (x_obj - self.x < self.tol) and
            ((y_obj - self.y_max < self.tol) or
            (y_obj - self.y_min < self.tol))
        ):
            return True
        return False
    
    # def reset_paddle_pos():
        ## to do


    

