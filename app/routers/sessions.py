from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

# POST /sessions/start  y /sessions/start/
@router.post("/start")
@router.post("/start/", include_in_schema=False)
async def start(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_activity_sessions", "START", body)

# POST /sessions/finish  y /sessions/finish/
@router.post("/finish")
@router.post("/finish/", include_in_schema=False)
async def finish(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_activity_sessions", "FINISH", body)

# GET /sessions  y /sessions/
@router.get("")
@router.get("/", include_in_schema=False)
async def list_sessions(student_id: str | None = None, limit: int = 100, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_activity_sessions", "S01", {"student_id": student_id, "limit": limit})
