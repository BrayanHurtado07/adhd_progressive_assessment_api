from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

@router.post("/start")
async def start(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_activity_sessions", "START", body)

@router.post("/finish")
async def finish(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_activity_sessions", "FINISH", body)

@router.get("")
async def list_sessions(student_id: str | None = None, limit: int = 100, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_activity_sessions", "S01", {"student_id": student_id, "limit": limit})
