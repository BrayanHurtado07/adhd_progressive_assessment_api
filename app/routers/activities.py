from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

@router.post("")
async def create_activity(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_activities", "M01", body)

@router.put("/{id}")
async def update_activity(id: str, body: dict, pool=Depends(db_pool)):
    body = {"id": id, **body}
    return await call_fn_one(pool, "fn_manage_activities", "M02", body)

@router.get("")
async def list_activities(q: str | None = None, only_active: bool = True, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_activities", "S01", {"q": q, "only_active": only_active})

# assignments
@router.post("/assign")
async def assign(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_activity_assignments", "M01", body)

@router.get("/assign")
async def list_assignments(student_id: str | None = None, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_activity_assignments", "S01", {"student_id": student_id})
