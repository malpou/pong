import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from networking.binary_protocol import decode_command, CommandType
from networking.room_manager import RoomManager


# Game loop task
async def game_loop():
    while True:
        for room in room_manager.rooms.values():
            room.game_state.update()
            await room.broadcast_state()
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


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    room = room_manager.create_room(room_id)
    player_role = await room.connect(websocket)

    if not player_role:
        await websocket.close(code=1000, reason="Room is full")
        return

    try:
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.receive":
                if "bytes" in message:
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

                    room.game_state.update()
                    await room.broadcast_state()
                elif "text" in message:
                    print(f"Received text message: {message['text']}")

    except WebSocketDisconnect:
        room.disconnect(websocket)
        if not room.players:
            room_manager.remove_room(room_id)