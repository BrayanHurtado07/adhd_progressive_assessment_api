from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

@router.post("")
async def create(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_users", "M01", body)

@router.get("")
async def list(institution_id: str | None = None, role: str | None = None, q: str | None = None, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_users", "S01", {"institution_id": institution_id, "role": role, "q": q})

@router.get("/{id}")
async def get_one(id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_users", "R01", {"id": id})

@router.put("/{id}")
async def update(id: str, body: dict, pool=Depends(db_pool)):
    body = {"id": id, **body}
    return await call_fn_one(pool, "fn_manage_users", "M02", body)

@router.delete("/{id}")
async def delete(id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_users", "D01", {"id": id})
