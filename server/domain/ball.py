from dataclasses import dataclass

@dataclass
class Ball:
    x: float = 0.5  # Position as percentage of screen width
    y: float = 0.5  # Position as percentage of screen height
    dx: float = 0.025  # X velocity
    dy: float = 0.025  # Y velocity
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
        # Alternate starting direction left/right
        self.dx = -self.dx
        self.dy = self.dy