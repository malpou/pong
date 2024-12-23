from enum import Enum
from typing import Dict, Optional, Set
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from domain.game import GameState
from logger import logger
from networking.binary_protocol import encode_game_state, encode_game_status


class RoomState(Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class GameRoom:
    def __init__(self):
        self.game_state = GameState()
        self.players: Set[WebSocket] = set()
        self.player_roles: Dict[WebSocket, str] = {}
        self.state = RoomState.WAITING
        self.room_id: Optional[str] = None

    async def connect(self, websocket: WebSocket) -> Optional[str]:
        if len(self.players) >= 2:
            logger.warning(f"Room {self.room_id}: Connection rejected - room is full")
            return None

        await websocket.accept()
        self.players.add(websocket)
        role = 'left' if len(self.players) == 1 else 'right'
        self.player_roles[websocket] = role
        logger.info(f"Room {self.room_id}: Player connected as {role} ({len(self.players)}/2 players)")

        # If we now have 2 players, start the game
        if len(self.players) == 2:
            self.state = RoomState.PLAYING
            self.game_state = GameState()
            logger.info(f"Room {self.room_id}: Game starting with 2 players")
            await self.broadcast_game_status("game_starting")
        else:
            logger.info(f"Room {self.room_id}: Waiting for more players")
            await self.broadcast_game_status("waiting_for_players")

        return role

    async def broadcast_game_status(self, status: str) -> None:
        logger.debug(f"Room {self.room_id}: Broadcasting status - {status}")
        status_bytes = encode_game_status(status)
        disconnected_players = set()

        for player in self.players:
            try:
                await player.send_bytes(status_bytes)
            except WebSocketDisconnect:
                disconnected_players.add(player)
                logger.warning(f"Room {self.room_id}: Player disconnected during status broadcast")

        # Handle any disconnections
        for player in disconnected_players:
            self.disconnect(player)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.players:
            role = self.player_roles[websocket]
            self.players.remove(websocket)
            del self.player_roles[websocket]
            logger.info(f"Room {self.room_id}: {role} player disconnected ({len(self.players)}/2 players)")

            # If we now have less than 2 players, pause the game
            if len(self.players) < 2 and self.state == RoomState.PLAYING:
                self.state = RoomState.PAUSED
                logger.info(f"Room {self.room_id}: Game paused due to player disconnect")

    async def update(self) -> None:
        if self.state != RoomState.PLAYING:
            return

        previous_score = (self.game_state.left_score, self.game_state.right_score)
        self.game_state.update()

        # Log score changes
        if (self.game_state.left_score, self.game_state.right_score) != previous_score:
            logger.info(
                f"Room {self.room_id}: Score update - Left: {self.game_state.left_score}, Right: {self.game_state.right_score}")

        # Check if game is over
        if self.game_state.winner:
            self.state = RoomState.GAME_OVER
            logger.info(f"Room {self.room_id}: Game over - {self.game_state.winner} player wins!")
            await self.broadcast_game_status(f"game_over_{self.game_state.winner}")

        await self.broadcast_state()

    async def broadcast_state(self) -> None:
        if not self.players:
            return

        state_bytes = encode_game_state(
            self.game_state.ball.x,
            self.game_state.ball.y,
            self.game_state.left_paddle.y_position,
            self.game_state.right_paddle.y_position,
            self.game_state.left_score,
            self.game_state.right_score,
            self.game_state.winner
        )

        disconnected_players = set()
        for player in list(self.players):
            try:
                await player.send_bytes(state_bytes)
            except (WebSocketDisconnect, RuntimeError) as e:
                logger.error(f"Error broadcasting state to player: {e}")
                disconnected_players.add(player)

        # Handle any disconnections
        for player in disconnected_players:
            self.disconnect(player)


class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, GameRoom] = {}

    def create_room(self, room_id: str) -> GameRoom:
        if room_id not in self.rooms:
            logger.info(f"Creating new room: {room_id}")
            room = GameRoom()
            room.room_id = room_id
            self.rooms[room_id] = room
        return self.rooms[room_id]

    def get_room(self, room_id: str) -> Optional[GameRoom]:
        return self.rooms.get(room_id)

    def remove_room(self, room_id: str) -> None:
        if room_id in self.rooms:
            logger.info(f"Removing room: {room_id}")
            del self.rooms[room_id]