from fastapi import Depends
from .db import get_pool

# Dependencia para inyectar el pool en rutas
async def db_pool(pool=Depends(get_pool)):
    return pool
