from dataclasses import dataclass
import math


@dataclass
class Ball:
    x: float = 0.5  # Position as percentage of screen width
    y: float = 0.5  # Position as percentage of screen height
    dx: float = 0.01  # X velocity
    dy: float = 0.01  # Y velocity
    radius: float = 0.02  # Radius as percentage of screen width

    def update_position(self) -> None:
        self.x += self.dx
        self.y += self.dy

        # Bounce off top and bottom
        if self.y <= 0 or self.y >= 1:
            self.dy *= -1

    def reset(self) -> None:
        self.x = 0.5
        self.y = 0.5
        # Random starting direction
        angle = math.pi * (0.25 + 0.5 * (hash(str(self)) % 2))
        self.dx = 0.01 * math.cos(angle)
        self.dy = 0.01 * math.sin(angle)