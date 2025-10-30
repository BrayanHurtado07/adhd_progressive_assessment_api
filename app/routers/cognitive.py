from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

# POST /cognitive  y /cognitive/
@router.post("")
@router.post("/", include_in_schema=False)
async def create(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_cognitive_profiles", "M01", body)

# GET /cognitive  y /cognitive/
@router.get("")
@router.get("/", include_in_schema=False)
async def list(student_id: str | None = None, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_cognitive_profiles", "S01", {"student_id": student_id})
