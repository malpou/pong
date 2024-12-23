import numpy as np

from dataclasses import dataclass
from dataclasses import field
from domain.ball import Ball
from domain.paddle import Paddle
from logger import logger

@dataclass
class GameState:
    POINTS_TO_WIN = 5  # Configurable win condition
    LEFT_PADDLE_X = 0.05  # X position for left paddle collision
    RIGHT_PADDLE_X = 0.95  # X position for right paddle collision
    GAME_WIDTH = 1.0  # Normalized game width
    GAME_HEIGHT = 1.0  # Normalized game height

    left_paddle: Paddle = field(default_factory=lambda: Paddle(GameState.LEFT_PADDLE_X))
    right_paddle: Paddle = field(default_factory=lambda: Paddle(GameState.RIGHT_PADDLE_X))
    ball: Ball = field(default_factory=Ball)
    left_score: int = 0
    right_score: int = 0
    winner: str | None = None
    room_id: str | None = None

    def update(self) -> None:
        if self.winner:  # Don't update if game is over
            return

        self.ball.update_position()

        # Check for scoring
        if self.ball.x <= 0:
            self.right_score += 1
            logger.info(f"Room {self.room_id}: Current score - Left: {self.left_score}, Right: {self.right_score} - RIGHT SCORED!")
            self.ball.reset()
            self._check_winner()
        elif self.ball.x >= self.GAME_WIDTH:
            self.left_score += 1
            logger.info(f"Room {self.room_id}: Current score - Left: {self.left_score}, Right: {self.right_score} - LEFT SCORED!")
            self.ball.reset()
            self._check_winner()

        # Basic paddle collision
        if (self.left_paddle.is_on_paddle(self.ball)):
            self.ball.x = self.left_paddle.x_position
            self.ball.angle += 3 * np.pi / 4

        if (self.right_paddle.is_on_paddle(self.ball)):
            self.ball.x = self.right_paddle.x_position
            self.ball.angle += 3 * np.pi / 4


    
    def _check_winner(self) -> None:
        if self.left_score >= self.POINTS_TO_WIN:
            self.winner = "left"
            logger.info(f"Room {self.room_id}: Game won by LEFT player with score {self.left_score}-{self.right_score}")
        elif self.right_score >= self.POINTS_TO_WIN:
            self.winner = "right"
            logger.info(f"Room {self.room_id}: Game won by RIGHT player with score {self.left_score}-{self.right_score}")