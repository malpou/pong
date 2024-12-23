import asyncio
from logger import logger


class GameLoop:
    def __init__(self, room_manager):
        self.room_manager = room_manager
        self.shutdown_event = asyncio.Event()

    async def run(self):
        """Run the game loop until shutdown event is set."""
        while not self.shutdown_event.is_set():
            try:
                for room in list(self.room_manager.rooms.values()):
                    if room.players:
                        try:
                            room.game_state.update()
                            if not self.shutdown_event.is_set():
                                await room.broadcast_state()
                        except RuntimeError:
                            continue
            except Exception as e:
                logger.error(f"Error in game loop: {e}")
            await asyncio.sleep(1 / 60)  # 60 FPS

    async def shutdown(self):
        """Gracefully shutdown the game loop."""
        logger.info("Application shutting down...")
        self.shutdown_event.set()

        for room_id in list(self.room_manager.rooms.keys()):
            room = self.room_manager.rooms[room_id]
            for player in list(room.players):
                try:
                    await player.close(code=1000, reason="Server shutting down")
                except Exception as e:
                    logger.error(f"Error closing WebSocket connection in room {room_id}: {e}")
            self.room_manager.remove_room(room_id)
