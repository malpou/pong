from struct import pack, unpack
from enum import IntEnum


class CommandType(IntEnum):
    PADDLE_UP = 1
    PADDLE_DOWN = 2


def decode_command(data: bytes) -> CommandType:
    """Decode binary data into a command."""
    command_value = unpack('!B', data)[0]
    return CommandType(command_value)


def encode_game_state(ball_x: float, ball_y: float,
                      left_paddle_y: float, right_paddle_y: float,
                      left_score: int, right_score: int) -> bytes:
    """Encode game state into binary format.
    Format:
    - 4 bytes each for float values (ball_x, ball_y, left_paddle_y, right_paddle_y)
    - 1 byte each for scores
    Total: 18 bytes
    """
    return pack('!ffffBB',
                ball_x, ball_y,
                left_paddle_y, right_paddle_y,
                left_score, right_score)
