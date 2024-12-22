from dataclasses import dataclass


@dataclass
class Paddle:
    y_position: float = 0.5  # Position as percentage of screen height (0-1)
    height: float = 0.2  # Height as percentage of screen height
    speed: float = 0.02  # Movement speed per frame

    def move_up(self) -> None:
        self.y_position = min(1.0 - self.height, self.y_position + self.speed)

    def move_down(self) -> None:
        self.y_position = max(0.0, self.y_position - self.speed)