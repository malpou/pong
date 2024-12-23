from typing import Dict
from fastapi import APIRouter
from domain.ball import Ball
from domain.game import GameState
from domain.paddle import Paddle

endpoints = APIRouter()


@endpoints.get("/specs")
def get_game_specs() -> Dict:
    """Get the game specifications needed to set up the playing field."""
    ball = Ball()
    paddle = Paddle()

    return {
        "ball": {
            "radius": ball.radius,
            "initial": {
                "x": ball.x,
                "y": ball.y,
            }
        },
        "paddle": {
            "height": paddle.height,
            "initial": {
                "y": paddle.y_position
            },
            "collision_bounds": {
                "left": GameState.LEFT_PADDLE_X,
                "right": GameState.RIGHT_PADDLE_X
            }
        },
        "game": {
            "points_to_win": GameState.POINTS_TO_WIN,
            "bounds": {
                "width": GameState.GAME_WIDTH,
                "height": GameState.GAME_HEIGHT
            }
        }
    }

@endpoints.get("/health")
def health_check() -> Dict:
    """Health check endpoint to verify the server is running."""
    return {
        "status": "healthy",
        "service": "pong-server"
    }