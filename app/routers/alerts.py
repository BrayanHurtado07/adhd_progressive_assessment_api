from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

# POST /alerts  y /alerts/
@router.post("")
@router.post("/", include_in_schema=False)
async def create(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_alerts", "M01", body)

# POST /alerts/{id}/ack  y con slash
@router.post("/{id}/ack")
@router.post("/{id}/ack/", include_in_schema=False)
async def acknowledge(id: str, user_id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_alerts", "ACK", {"id": id, "user_id": user_id})

# GET /alerts  y /alerts/
@router.get("")
@router.get("/", include_in_schema=False)
async def list(student_id: str | None = None, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_alerts", "S01", {"student_id": student_id})
