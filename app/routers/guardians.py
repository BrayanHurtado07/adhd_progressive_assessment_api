from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

@router.post("")
async def create(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_guardians", "M01", body)

@router.get("")
async def list(institution_id: str | None = None, q: str | None = None, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_guardians", "S01", {"institution_id": institution_id, "q": q})

@router.post("/link")
async def link(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_guardian_student", "M01", body)

@router.delete("/link")
async def unlink(guardian_id: str, student_id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_guardian_student", "D01", {"guardian_id": guardian_id, "student_id": student_id})
