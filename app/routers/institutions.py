from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

# POST /institutions  y /institutions/
@router.post("")
@router.post("/", include_in_schema=False)
async def create(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_institutions", "M01", body)

# GET /institutions  y /institutions/
@router.get("")
@router.get("/", include_in_schema=False)
async def list(inst_id: str | None = None, q: str | None = None, pool=Depends(db_pool)):
    payload = {"id": inst_id, "q": q}
    return await call_fn_many(pool, "fn_manage_institutions", "S01", payload)

# GET /institutions/{id}  y /institutions/{id}/
@router.get("/{id}")
@router.get("/{id}/", include_in_schema=False)
async def get_one(id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_institutions", "R01", {"id": id})

# PUT /institutions/{id}  y /institutions/{id}/
@router.put("/{id}")
@router.put("/{id}/", include_in_schema=False)
async def update(id: str, body: dict, pool=Depends(db_pool)):
    body = {"id": id, **body}
    return await call_fn_one(pool, "fn_manage_institutions", "M02", body)

# DELETE /institutions/{id}  y /institutions/{id}/
@router.delete("/{id}")
@router.delete("/{id}/", include_in_schema=False)
async def delete(id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_institutions", "D01", {"id": id})
