from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

@router.post("")
async def create(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_students", "M01", body)

@router.get("")
async def list(institution_id: str | None = None, q: str | None = None,
               limit: int = 100, offset: int = 0, pool=Depends(db_pool)):
    payload = {"institution_id": institution_id, "q": q, "limit": limit, "offset": offset}
    return await call_fn_many(pool, "fn_manage_students", "S01", payload)

@router.get("/{id}")
async def get_one(id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_students", "R01", {"id": id})

@router.put("/{id}")
async def update(id: str, body: dict, pool=Depends(db_pool)):
    body = {"id": id, **body}
    return await call_fn_one(pool, "fn_manage_students", "M02", body)

@router.delete("/{id}")
async def delete(id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_students", "D01", {"id": id})
