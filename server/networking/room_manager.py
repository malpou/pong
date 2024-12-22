from typing import Dict, Optional, Set
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from domain.game import GameState
from networking.binary_protocol import encode_game_state


class GameRoom:
    def __init__(self):
        self.game_state = GameState()
        self.players: Set[WebSocket] = set()
        self.player_roles: Dict[WebSocket, str] = {}  # 'left' or 'right'

    async def connect(self, websocket: WebSocket) -> Optional[str]:
        if len(self.players) >= 2:
            return None

        await websocket.accept()
        self.players.add(websocket)
        role = 'left' if len(self.players) == 1 else 'right'
        self.player_roles[websocket] = role
        return role

    def disconnect(self, websocket: WebSocket) -> None:
        self.players.remove(websocket)
        del self.player_roles[websocket]

    async def broadcast_state(self) -> None:
        if not self.players:
            return

        state_bytes = encode_game_state(
            self.game_state.ball.x,
            self.game_state.ball.y,
            self.game_state.left_paddle.y_position,
            self.game_state.right_paddle.y_position,
            self.game_state.left_score,
            self.game_state.right_score
        )

        for player in self.players:
            try:
                await player.send_bytes(state_bytes)
            except WebSocketDisconnect:
                pass

class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, GameRoom] = {}

    def create_room(self, room_id: str) -> GameRoom:
        if room_id not in self.rooms:
            self.rooms[room_id] = GameRoom()
        return self.rooms[room_id]

    def get_room(self, room_id: str) -> Optional[GameRoom]:
        return self.rooms.get(room_id)

    def remove_room(self, room_id: str) -> None:
        if room_id in self.rooms:
            del self.rooms[room_id]