# Pong
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
1. Client connects to WebSocket endpoint: `ws://<server>/ws/<room_id>`
2. Server assigns player role ("left" or "right") upon successful connection
3. Connection is rejected if room is full (2 players already connected)

### Binary Message Format

#### Client to Server: Commands
Size: 1 byte

```
[Command Type]
   1 byte
```

Command Types:
- `0x01`: Paddle Up
- `0x02`: Paddle Down

#### Server to Client: Game State
Size: 18 bytes

```
[Ball X][Ball Y][Left Paddle Y][Right Paddle Y][Left Score][Right Score]
 4 bytes 4 bytes    4 bytes      4 bytes        1 byte      1 byte
```

Data Types:
- Ball positions (X, Y): 32-bit float, network byte order (big-endian)
- Paddle positions (Y): 32-bit float, network byte order (big-endian)
- Scores: 8-bit unsigned integer

### Example Client Implementation (TypeScript)

```typescript
class PongClient {
    private ws: WebSocket;

    constructor(roomId: string) {
        this.ws = new WebSocket(`ws://localhost:8000/ws/${roomId}`);
        this.ws.binaryType = 'arraybuffer';
        this.setupHandlers();
    }

    private setupHandlers() {
        this.ws.onmessage = (event) => {
            const data = new DataView(event.data);
            const gameState = {
                ball: {
                    x: data.getFloat32(0),
                    y: data.getFloat32(4)
                },
                paddles: {
                    left: data.getFloat32(8),
                    right: data.getFloat32(12)
                },
                score: {
                    left: data.getUint8(16),
                    right: data.getUint8(17)
                }
            };
            this.updateGame(gameState);
        };
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
}
```

### Example Server Implementation (Python)

See the `binary_protocol.py` module for the server-side protocol implementation.