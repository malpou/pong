import asyncio
import random
import struct
import time
from dataclasses import dataclass
from typing import Optional
import websockets


@dataclass
class GameState:
    ball_x: float
    ball_y: float
    paddle_left: float
    paddle_right: float
    score_left: int
    score_right: int
    winner: Optional[int]


class PongClient:
    def __init__(self, room_id: str, player: str):
        self.room_id = room_id
        self.player = player
        self.ws = None
        self.game_state = None
        self.running = True

    async def connect(self):
        uri = f"ws://localhost:8000/game/{self.room_id}"
        try:
            self.ws = await websockets.connect(uri)
            print(f"Connected to room {self.room_id} as {self.player}")
        except websockets.exceptions.InvalidURI as e:
            print(f"Invalid URI error: {e}")
            raise
        except websockets.exceptions.InvalidStatus as e:
            print(f"Server rejected connection: {e}")
            raise
        except Exception as e:
            print(f"Failed to connect to room {self.room_id}: {str(e)}")
            raise

    @staticmethod
    def parse_game_state(data: bytes) -> GameState:
        # Parse binary game state message
        ball_x, ball_y, paddle_left, paddle_right = struct.unpack('>ffff', data[1:17])
        score_left, score_right, winner = struct.unpack('BBB', data[17:20])

        return GameState(
            ball_x=ball_x,
            ball_y=ball_y,
            paddle_left=paddle_left,
            paddle_right=paddle_right,
            score_left=score_left,
            score_right=score_right,
            winner=winner if winner != 0 else None
        )

    @staticmethod
    def parse_game_status(data: bytes) -> str:
        length = data[1]
        return data[2:2 + length].decode('utf-8')

    async def send_paddle_command(self):
        # Randomly move paddle up or down
        command = bytes([random.choice([0x01, 0x02])])
        if self.ws:
            await self.ws.send(command)

    async def game_loop(self):
        try:
            while self.running:
                if self.ws:
                    data = await self.ws.recv()
                    message_type = data[0]

                    if message_type == 0x01:  # Game State
                        self.game_state = self.parse_game_state(data)

                        # Send paddle movements based on ball position
                        if self.player == "left":
                            if self.game_state.ball_y > self.game_state.paddle_left:
                                await self.ws.send(bytes([0x01]))  # Move UP
                            elif self.game_state.ball_y < self.game_state.paddle_left:
                                await self.ws.send(bytes([0x02]))  # Move DOWN
                        else:  # right player
                            if self.game_state.ball_y > self.game_state.paddle_right:
                                await self.ws.send(bytes([0x01]))  # Move UP
                            elif self.game_state.ball_y < self.game_state.paddle_right:
                                await self.ws.send(bytes([0x02]))  # Move DOWN

                        # Check for game over
                        if self.game_state.winner is not None:
                            print(
                                f"Game over in room {self.room_id}! Winner: {'Left' if self.game_state.winner == 1 else 'Right'}")
                            self.running = False

                    elif message_type == 0x02:  # Game Status
                        status = self.parse_game_status(data)
                        print(f"Room {self.room_id} status: {status}")

                        if status.startswith("game_over"):
                            self.running = False

                await asyncio.sleep(0.016)  # ~60fps

        except websockets.exceptions.ConnectionClosed:
            print(f"Connection closed for room {self.room_id}, {self.player}")
        except Exception as e:
            print(f"Error in room {self.room_id}, {self.player}: {str(e)}")
        finally:
            if self.ws:
                await self.ws.close()


async def run_game(room_id: str):
    # Create two clients for each room
    client1 = PongClient(room_id, "left")
    client2 = PongClient(room_id, "right")

    # Connect both clients
    await client1.connect()
    await client2.connect()

    # Run both game loops concurrently
    await asyncio.gather(
        client1.game_loop(),
        client2.game_loop()
    )


async def main():
    start_time = time.time()

    # Create 10 concurrent games
    games = [run_game(str(i)) for i in range(1, 11)]

    # Run all games concurrently
    await asyncio.gather(*games)

    end_time = time.time()
    print(f"\nAll games completed in {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    print("Starting Pong server load test with 10 simultaneous games...")
    asyncio.run(main())