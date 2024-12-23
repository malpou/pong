# Ping Pong
Online multiplayer implementation of the classic Pong game, coded during Christmas 2024.

## Hosting
The app is hosted on Render.com and can be accessed on these domains:
- Client: ping.malpou.io
- Server: pong.malpou.io

## Local Development
Instructions for running the applications locally.

### Client
The client is built with React and TypeScript, bundled using Vite.

#### Prerequisites
- Node.js 20 or higher

#### Steps
1. Go to the `client` directory
2. Run `npm i`
3. Run `npm run dev`

### Server
The server is implemented in Python using FastAPI as the web framework and PostgreSQL as the database.

#### Prerequisites
- Python 3.13
- Poetry
- Docker

#### Steps
1. Go to the `server` directory
2. Run `poetry env use 3.13`
3. Run `poetry install`
4. Run `uvicorn main:app --reload`

## Network Protocol
The game uses a binary WebSocket protocol for efficient real-time communication between client and server.

### Connection Setup
1. Client connects to WebSocket endpoint: `ws://<server>/game/<room_id>?player_name=<name>`
   - `player_name` is optional and defaults to "Anonymous"
2. Server assigns player role ("left" or "right") upon successful connection
3. Connection is rejected if room is full (2 players already connected)
4. Game starts automatically when second player joins
5. Game pauses if a player disconnects and resumes when they reconnect

### Game States
- `WAITING`: Room has less than 2 players, waiting for more
- `PLAYING`: Active game with 2 players
- `PAUSED`: Game paused due to player disconnection
- `GAME_OVER`: Game ended with a winner (first to 5 points)

### Game Specifications
The server provides game specifications needed to set up the playing field through a REST endpoint.

#### Endpoint
`GET /specs`

#### Response Format
```json
{
  "ball": {
    "radius": 0.02,      // Ball radius as percentage of screen width
    "initial": {
      "x": 0.5,         // Initial X position (0-1)
      "y": 0.5          // Initial Y position (0-1)
    }
  },
  "paddle": {
    "height": 0.2,      // Paddle height as percentage of screen height
    "initial": {
      "y": 0.5         // Initial Y position (0-1)
    },
    "collision_bounds": {
      "left": 0.1,     // X position for left paddle collision
      "right": 0.9     // X position for right paddle collision
    }
  },
  "game": {
    "points_to_win": 5, // Points needed to win the game
    "bounds": {
      "width": 1.0,    // Game field width (normalized)
      "height": 1.0    // Game field height (normalized)
    }
  }
}
```

All dimensions are normalized (0-1) so clients can scale them to their actual screen dimensions. These specifications should be retrieved before connecting to the WebSocket to properly set up the game field.

The specifications provide:
- Ball dimensions and initial position
- Paddle dimensions, initial position, and collision boundaries
- Game field dimensions and win condition

### Binary Message Format

#### Client to Server Messages
##### Command Message
Size: 1 byte
```
[Message Type]
   1 byte
```

Message Types:
- `0x01`: Paddle Up Command
- `0x02`: Paddle Down Command

#### Server to Client Messages
Each server message begins with a message type indicator:
```
[Message Type]
   1 byte
```

Message Types:
- `0x01`: Game State Message
- `0x02`: Game Status Message

##### Game State Message
Size: 20 bytes total
```
[Message Type][Ball X][Ball Y][Left Paddle Y][Right Paddle Y][Left Score][Right Score][Winner]
   1 byte     4 bytes 4 bytes    4 bytes       4 bytes      1 byte      1 byte     1 byte
```

Field Types:
- Message Type: uint8 (1 byte)
- Ball X Position: float32, big-endian (4 bytes)
- Ball Y Position: float32, big-endian (4 bytes)
- Left Paddle Y Position: float32, big-endian (4 bytes)
- Right Paddle Y Position: float32, big-endian (4 bytes)
- Left Score: uint8 (1 byte)
- Right Score: uint8 (1 byte)
- Winner: uint8 (1 byte)
  - 0: No winner
  - 1: Left player won
  - 2: Right player won

##### Game Status Message
Variable size message containing JSON-encoded status data
```
[Message Type][Length][Status Data]
   1 byte     1 byte    variable
```

Field Types:
- Message Type: uint8 (1 byte)
- Length: uint8 (1 byte) - length of status data
- Status Data: UTF-8 encoded JSON string containing:
  ```json
  {
    "status": "<status_string>",
    "players": {
      "left": "<player_name>",
      "right": "<player_name>"
    }
  }
  ```

Status String Values:
- "waiting_for_players": Waiting for more players to join
- "game_starting": Both players present, game is starting
- "game_paused": Game paused due to player disconnect
- "game_over_left": Left player won
- "game_over_right": Right player won

### Example Client Implementation (TypeScript)
```typescript
interface GameState {
    ball: {
        x: number;
        y: number;
    };
    paddles: {
        left: number;
        right: number;
    };
    score: {
        left: number;
        right: number;
    };
    winner: 'left' | 'right' | null;
}

interface GameStatus {
    status: string;
    players: {
        left?: string;
        right?: string;
    };
}

class PongClient {
    private ws: WebSocket;

    constructor(server: string, roomId: string, playerName: string = "Anonymous") {
        this.ws = new WebSocket(`ws://${server}/game/${roomId}?player_name=${encodeURIComponent(playerName)}`);
        this.ws.binaryType = 'arraybuffer';
        this.setupHandlers();
    }

    private setupHandlers() {
        this.ws.onmessage = (event) => {
            const data = new DataView(event.data);
            const messageType = data.getUint8(0);

            switch (messageType) {
                case 0x01: // Game State
                    this.handleGameState(data);
                    break;
                case 0x02: // Game Status
                    this.handleGameStatus(data);
                    break;
            }
        };
    }

    private handleGameState(data: DataView) {
        const gameState = {
            ball: {
                x: data.getFloat32(1),
                y: data.getFloat32(5)
            },
            paddles: {
                left: data.getFloat32(9),
                right: data.getFloat32(13)
            },
            score: {
                left: data.getUint8(17),
                right: data.getUint8(18)
            },
            winner: (() => {
                const winnerCode = data.getUint8(19);
                switch (winnerCode) {
                    case 1: return 'left';
                    case 2: return 'right';
                    default: return null;
                }
            })()
        };
        this.updateGame(gameState);
    }

    private handleGameStatus(data: DataView) {
        const length = data.getUint8(1);
        const decoder = new TextDecoder();
        const statusJson = decoder.decode(new Uint8Array(data.buffer, 2, length));
        const status: GameStatus = JSON.parse(statusJson);
        this.updateGameStatus(status);
    }

    public sendPaddleUp() {
        const command = new Uint8Array([0x01]);
        this.ws.send(command);
    }

    public sendPaddleDown() {
        const command = new Uint8Array([0x02]);
        this.ws.send(command);
    }

    private updateGame(gameState: GameState) {
        // Update game rendering with new state
    }

    private updateGameStatus(status: GameStatus) {
        // Update UI based on game status and player names
    }
}
```

### Example Server Implementation (Python)
See the following modules for the server-side implementation:
- `binary_protocol.py`: Protocol encoding/decoding
- `room_manager.py`: Game room and player management
- `main.py`: WebSocket endpoint and game loop
