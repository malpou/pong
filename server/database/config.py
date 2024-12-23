from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://pong:pong@localhost:5432/pong")
MAX_CONNECTIONS = int(os.getenv("MAX_DB_CONNECTIONS", "90"))
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=30,  # 30 seconds timeout for getting a connection
    pool_pre_ping=True  # Enable connection health checks
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Track active connections
active_game_connections = 0

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def acquire_game_connection() -> bool:
    """Try to acquire a connection for a new game."""
    global active_game_connections
    if active_game_connections >= MAX_CONNECTIONS:
        return False
    active_game_connections += 1
    return True

def release_game_connection():
    """Release a game connection."""
    global active_game_connections
    if active_game_connections > 0:
        active_game_connections -= 1

@event.listens_for(engine, 'checkout')
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Validate connection on checkout."""
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        raise Exception("Database connection failed health check")
    finally:
        cursor.close() 