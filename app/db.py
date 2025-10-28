# app/db.py
import os
import ssl
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_pool: asyncpg.Pool | None = None

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        # SSL para Azure PostgreSQL
        ssl_ctx = ssl.create_default_context()
        _pool = await asyncpg.create_pool(
            DATABASE_URL, min_size=1, max_size=10, ssl=ssl_ctx
        )
    return _pool

async def close_pool():
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
