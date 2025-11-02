# app/db.py
import os
import ssl
import asyncpg
import certifi
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# Opcional: para desarrollo local puedes poner DATABASE_SSL=disable
DATABASE_SSL = os.getenv("DATABASE_SSL", "require").lower()

_pool: asyncpg.Pool | None = None

def _build_ssl_context() -> ssl.SSLContext | None:
    if DATABASE_SSL in ("disable", "off", "false", "none"):
        return None
    # SSL con cadena de confianza (soluciona CERTIFICATE_VERIFY_FAILED)
    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED
    return ctx

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        ssl_ctx = _build_ssl_context()
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1,
            max_size=10,
            ssl=ssl_ctx,
        )
    return _pool

async def close_pool():
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None