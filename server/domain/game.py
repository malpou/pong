from dataclasses import dataclass
from dataclasses import field
from domain.paddle import Paddle
from domain.ball import Ball


@dataclass
class GameState:
    left_paddle: Paddle = field(default_factory=Paddle)
    right_paddle: Paddle = field(default_factory=Paddle)
    ball: Ball = field(default_factory=Ball)
    left_score: int = 0
    right_score: int = 0

    def update(self) -> None:
        self.ball.update_position()

        # Check for scoring
        if self.ball.x <= 0:
            self.right_score += 1
            self.ball.reset()
        elif self.ball.x >= 1:
            self.left_score += 1
            self.ball.reset()

        # Basic paddle collision
        if (self.ball.x <= 0.1 and
                self.left_paddle.y_position <= self.ball.y <=
                self.left_paddle.y_position + self.left_paddle.height):
            self.ball.dx *= -1

        if (self.ball.x >= 0.9 and
                self.right_paddle.y_position <= self.ball.y <=
                self.right_paddle.y_position + self.right_paddle.height):
            self.ball.dx *= -1