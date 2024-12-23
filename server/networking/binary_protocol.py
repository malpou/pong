from struct import pack, unpack
from enum import IntEnum
from typing import Optional

class CommandType(IntEnum):
    PADDLE_UP = 1
    PADDLE_DOWN = 2

class MessageType(IntEnum):
    GAME_STATE = 1
    GAME_STATUS = 2

def decode_command(data: bytes) -> CommandType:
    """Decode binary data into a command."""
    command_value = unpack('!B', data)[0]
    return CommandType(command_value)


def encode_game_status(status: str) -> bytes:
    """Encode game status messages.
    Status can be:
    - "waiting_for_players"
    - "game_starting"
    - "game_paused"
    - "game_over"
    """
    status_bytes = status.encode('utf-8')
    return pack(f'!BB{len(status_bytes)}s',
               MessageType.GAME_STATUS,
               len(status_bytes),
               status_bytes)


def encode_game_state(ball_x: float, ball_y: float,
                      left_paddle_y: float, right_paddle_y: float,
                      left_score: int, right_score: int,
                      winner: Optional[str] = None) -> bytes:
    """Encode game state into binary format."""
    # winner_code: 0 = no winner, 1 = left won, 2 = right won
    winner_code = 0
    if winner == "left":
        winner_code = 1
    elif winner == "right":
        winner_code = 2

    return pack('!BffffBBB',
                MessageType.GAME_STATE,
                ball_x, ball_y,
                left_paddle_y, right_paddle_y,
                left_score, right_score,
                winner_code)