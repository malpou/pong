import asyncio
import struct
import sys
import time
import uuid
from dataclasses import dataclass
from typing import Optional, Dict
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
        self.completed = False

    async def connect(self):
        uri = f"ws://localhost:8000/game/{self.room_id}"
        try:
            self.ws = await websockets.connect(uri)
        except websockets.exceptions.WebSocketException as ws_err:
            print(f"WebSocket error connecting to room {self.room_id} as {self.player}: {str(ws_err)}")
            raise
        except Exception as conn_err:
            print(f"Unexpected error connecting to room {self.room_id} as {self.player}: {str(conn_err)}")
            raise

    @staticmethod
    def parse_game_state(data: bytes) -> GameState:
        try:
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
        except struct.error as struct_err:
            print(f"Error parsing game state: {struct_err}")
            raise
        except Exception as parse_err:
            print(f"Unexpected error parsing game state: {parse_err}")
            raise

    @staticmethod
    def parse_game_status(data: bytes) -> str:
        try:
            length = data[1]
            return data[2:2 + length].decode('utf-8')
        except (IndexError, UnicodeDecodeError) as decode_err:
            print(f"Error parsing game status: {decode_err}")
            raise

    async def game_loop(self) -> bool:
        try:
            while self.running:
                if not self.ws:
                    raise RuntimeError(f"WebSocket connection lost in room {self.room_id}")

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

                    if self.game_state.winner is not None:
                        print(f"Game over in room {self.room_id}! Winner: {'Left' if self.game_state.winner == 1 else 'Right'}")
                        self.completed = True
                        self.running = False

                elif message_type == 0x02:  # Game Status
                    status = self.parse_game_status(data)

                    status_str = str(status)
                    if "game_over" in status_str:
                        self.completed = True
                        self.running = False

                await asyncio.sleep(0.016)  # ~60fps

        except websockets.exceptions.ConnectionClosed as ws_err:
            print(f"Connection closed for room {self.room_id}, {self.player}: {ws_err}")
            return False
        except Exception as loop_err:
            print(f"Error in room {self.room_id}, {self.player}: {str(loop_err)}")
            raise
        finally:
            if self.ws:
                await self.ws.close()

        return self.completed


class TestResults:
    def __init__(self):
        self.completed_games = 0
        self.failed_games = 0
        self.timed_out_games = 0
        self.errors: Dict[str, str] = {}

    def add_result(self, room_id: str, success: bool, error: Optional[str] = None, timed_out: bool = False):
        if timed_out:
            self.timed_out_games += 1
            self.failed_games += 1
            if error:
                self.errors[room_id] = error
        elif success:
            self.completed_games += 1
        else:
            self.failed_games += 1
            if error:
                self.errors[room_id] = error


async def run_game(results: TestResults):
    room_id = str(uuid.uuid4())
    try:
        client1 = PongClient(room_id, "left")
        client2 = PongClient(room_id, "right")

        # Connect both clients
        await client1.connect()
        await client2.connect()

        # Run both game loops concurrently with a timeout
        try:
            client1_result, client2_result = await asyncio.wait_for(
                asyncio.gather(
                    client1.game_loop(),
                    client2.game_loop(),
                    return_exceptions=True
                ),
                timeout=120  # 2 minutes timeout
            )

            # Check for exceptions
            for result in [client1_result, client2_result]:
                if isinstance(result, Exception):
                    results.add_result(room_id, False, str(result))
                    return

            # Check if both clients completed successfully
            if client1_result and client2_result:
                results.add_result(room_id, True)
            else:
                results.add_result(room_id, False, "Game did not complete properly")

        except asyncio.TimeoutError:
            results.add_result(room_id, False, "Game timed out after 2 minutes", timed_out=True)
            print(f"Room {room_id} timed out after 2 minutes")

    except (websockets.exceptions.WebSocketException, asyncio.exceptions.TimeoutError) as conn_err:
        results.add_result(room_id, False, f"Connection error: {str(conn_err)}")
    except Exception as game_err:
        results.add_result(room_id, False, f"Unexpected error: {str(game_err)}")

async def main():
    print("Starting Pong server load test with 10 simultaneous games...")
    start_time = time.time()
    results = TestResults()

    # Create and run games
    games = [run_game(results) for i in range(1, 11)]
    
    # Wait for all games to complete
    await asyncio.gather(*games)
    
    # Print results
    end_time = time.time()
    print(f"\nTest Results:")
    print(f"Duration: {end_time - start_time:.2f} seconds")
    print(f"Completed Games: {results.completed_games}")
    print(f"Failed Games: {results.failed_games}")
    print(f"Timed Out Games: {results.timed_out_games}")

    # Exit with error if any games failed
    if results.failed_games > 0:
        print("\nTest failed: Not all games completed successfully")
        sys.exit(1)

    print("\nAll tests passed successfully!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as main_err:
        print(f"\nTest failed with error: {str(main_err)}")
        sys.exit(1)