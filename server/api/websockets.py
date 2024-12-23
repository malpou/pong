import struct
from fastapi import WebSocket, WebSocketDisconnect
from logger import logger
from networking.binary_protocol import decode_command, CommandType
from networking.room_manager import RoomState


async def handle_game_connection(websocket: WebSocket, room_id: str, room_manager):
    """Handle WebSocket connection for a game room."""
    room = room_manager.create_room(room_id)
    player_role = await room.connect(websocket)

    if not player_role:
        await websocket.close(code=1000, reason="Room is full")
        return

    try:
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                break

            if room.state != RoomState.PLAYING:
                continue  # Ignore gameplay messages if not in PLAYING state

            if message["type"] == "websocket.receive":
                if "bytes" in message and message["bytes"]:
                    try:
                        data = message["bytes"]
                        command = decode_command(data)

                        if command == CommandType.PADDLE_UP:
                            if player_role == "left":
                                room.game_state.left_paddle.move_up()
                            else:
                                room.game_state.right_paddle.move_up()
                        elif command == CommandType.PADDLE_DOWN:
                            if player_role == "left":
                                room.game_state.left_paddle.move_down()
                            else:
                                room.game_state.right_paddle.move_down()

                    except struct.error as e:
                        logger.error(f"Error decoding command: {e}")
                        continue

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for room {room_id}")
    except Exception as e:
        logger.error(f"Error in websocket connection: {e}")
    finally:
        room.disconnect(websocket)
        if not room.players:
            room_manager.remove_room(room_id)
