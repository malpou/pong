import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from api.endpoints import endpoints
from api.websockets import handle_game_connection
from core.game_loop import GameLoop
from networking.room_manager import RoomManager

room_manager = RoomManager()
game_loop = GameLoop(room_manager)


@asynccontextmanager
async def lifespan(_: FastAPI):
    game_loop_task = asyncio.create_task(game_loop.run())
    yield
    await game_loop.shutdown()
    game_loop_task.cancel()
    try:
        await game_loop_task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)
app.include_router(endpoints)


@app.websocket("/game/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await handle_game_connection(websocket, room_id, room_manager)
