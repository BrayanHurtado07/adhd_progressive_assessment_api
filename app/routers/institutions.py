from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

@router.post("")
async def create(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_institutions", "M01", body)

@router.get("")
async def list(inst_id: str | None = None, q: str | None = None, pool=Depends(db_pool)):
    payload = {"id": inst_id, "q": q}
    return await call_fn_many(pool, "fn_manage_institutions", "S01", payload)

@router.get("/{id}")
async def get_one(id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_institutions", "R01", {"id": id})

@router.put("/{id}")
async def update(id: str, body: dict, pool=Depends(db_pool)):
    body = {"id": id, **body}
    return await call_fn_one(pool, "fn_manage_institutions", "M02", body)

@router.delete("/{id}")
async def delete(id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_institutions", "D01", {"id": id})
