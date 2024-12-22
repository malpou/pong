class GameBoard:

    def __init__(self, x_max, y_max):
        self.x_max = x_max
        self.y_max = y_max
        self.board_corners = [(0,0),
                              (x_max,0),
                              (0,y_max),
                              (x_max,y_max)]
        
    def is_in_boudaries(self, x, y):
        if (
            (x > self.x_max) or 
            (x < 0) or
            (y > self.y_max) or
            (y < 0)
        ):
            return False
        return True
    
    
class Ball():

    def __init__(self, x_max, y_max):
        self.x_ball = x_max / 2
        self.y_ball = y_max / 2
        self.vector = (0,1)

class Bat():

    def __init__(self, x_bat, y_bat, length):
        self.x_bat = x_bat
        self.y_bat = y_bat
        self.length = length


    


