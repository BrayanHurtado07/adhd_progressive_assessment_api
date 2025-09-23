from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

@router.post("")
async def create(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_alerts", "M01", body)

@router.post("/{id}/ack")
async def acknowledge(id: str, user_id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_alerts", "ACK", {"id": id, "user_id": user_id})

@router.get("")
async def list(student_id: str | None = None, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_alerts", "S01", {"student_id": student_id})
