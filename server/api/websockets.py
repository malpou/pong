import struct
from fastapi import WebSocket, WebSocketDisconnect
from logger import logger
from networking.binary_protocol import decode_command, CommandType
from networking.game_room_manager import Game
import asyncio

CONNECTION_TIMEOUT = 60  # Connection timeout in seconds
VALID_COMMANDS = {0x01, 0x02}  # Only paddle up/down commands are valid

async def handle_game_connection(websocket: WebSocket, room_id: str, room_manager):
    """Handle WebSocket connection for a game room."""
    room = await room_manager.create_room(room_id)  # Add await here
    player_role = None

    try:
        async with asyncio.timeout(CONNECTION_TIMEOUT):
            player_role = await room.connect(websocket)

        if not player_role:
            await websocket.close(code=1000, reason="Room is full")
            return

        # Check game state using room.game_state instead of room.state
        while True:
            try:
                async with asyncio.timeout(CONNECTION_TIMEOUT):
                    message = await websocket.receive()

                if message["type"] == "websocket.disconnect":
                    break

                if room.game_state.state != Game.State.PLAYING:
                    continue

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
                        except Exception as e:
                            logger.error(f"Unexpected error processing command: {e}")
                            continue
            except asyncio.TimeoutError:
                logger.warning("Connection timed out")
                break

    except asyncio.TimeoutError:
        logger.warning(f"Connection timeout for room {room_id}")
        await websocket.close(code=1000, reason="Connection timeout")
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for room {room_id}")
    except Exception as e:
        logger.error(f"Error in websocket connection: {e}")
        await websocket.close(code=1011, reason="Internal server error")
    finally:
        if player_role:  # Only disconnect if the player was successfully connected
            room.disconnect(websocket)
        if not room.players:
            room_manager.remove_room(room_id)