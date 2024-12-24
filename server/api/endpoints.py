import uuid
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.config import get_db
from database.models import GameModel
from domain.ball import Ball
from domain.paddle import Paddle
from networking.game_room_manager import Game
endpoints = APIRouter()

class GameInfo(BaseModel):
    id: uuid.UUID
    state: Game.State
    player_count: int
    left_score: int
    right_score: int
    winner: str | None

    class Config:
        from_attributes = True

@endpoints.post("/games")
async def create_game(_: Request, db: Session = Depends(get_db)):
   """Create a new game and return its ID."""
   game = GameModel() # Use GameModel instead of Game domain class
   db.add(game)
   try:
       db.commit()
       db.refresh(game)
   except Exception as _:
       db.rollback()
       raise HTTPException(status_code=500, detail="Failed to create game")

   return GameInfo(
       id=game.id,
       state=Game.State(game.state), # Convert DB enum to domain enum
       player_count=len(game.players),
       left_score=game.left_score,
       right_score=game.right_score,
       winner=game.winner
   )


@endpoints.post("/games")
async def create_game(_: Request, db: Session = Depends(get_db)):
    """Create a new game and return its ID."""
    game = GameModel()
    db.add(game)
    try:
        db.commit()
        db.refresh(game)
    except Exception as _:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create game")

    return GameInfo(
        id=game.id,
        state=Game.State(game.state),
        player_count=len(game.players) if game.players is not None else 0,
        left_score=game.left_score,
        right_score=game.right_score,
        winner=game.winner
    )


@endpoints.get("/specs")
def get_game_specs(_: Request) -> Dict:
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
                "left": Game.LEFT_PADDLE_X,
                "right": Game.RIGHT_PADDLE_X
            }
        },
        "game": {
            "points_to_win": Game.POINTS_TO_WIN,
            "bounds": {
                "width": Game.GAME_WIDTH,
                "height": Game.GAME_HEIGHT
            }
        }
    }

@endpoints.get("/health")
def health_check(_: Request) -> Dict:
    """Health check endpoint to verify the server is running."""
    return {
        "status": "healthy",
        "service": "pong-server"
    }