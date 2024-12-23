import asyncio
import struct
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from networking.binary_protocol import decode_command, CommandType
from networking.room_manager import RoomManager, RoomState
from logger import logger

async def game_loop():
    while True:
        try:
            for room in list(room_manager.rooms.values()):
                if room.players:
                    try:
                        room.game_state.update()
                        await room.broadcast_state()
                    except RuntimeError:
                        continue
        except Exception as e:
            logger.error(f"Error in game loop: {e}")
        await asyncio.sleep(1 / 60)  # 60 FPS


@asynccontextmanager
async def lifespan(_: FastAPI):
    game_loop_task = asyncio.create_task(game_loop())
    yield
    game_loop_task.cancel()
    try:
        await game_loop_task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)
room_manager = RoomManager()


@app.websocket("/game/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
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