class GameBoard:

    def __init__(self, x_max, y_max):
        self.x_max = x_max
        self.y_max = y_max
        self.board_corners = [(0,0),
                              (x_max,0),
                              (0,y_max),
                              (x_max,y_max)]
        
    def is_in_boudaries(self, x, y):
        tol=self.x_max/1000

        if (
            (x > self.x_max - tol) or 
            (x < 0 + tol) or
            (y > self.y_max - tol) or
            (y < 0 + tol)
        ):
            return False
        return True
    
    
class Ball():

    def __init__(self, x_max, y_max, speed):
        self.x = x_max / 2
        self.y = y_max / 2
        self.vx = speed
        self.vy = 0

class Bat():

    def __init__(self, x_bat, y_bat, length):
        self.x = x_bat
        self.y = y_bat
        self.length = length


    


