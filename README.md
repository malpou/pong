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
5. Run `uvicorn main:app --reload`