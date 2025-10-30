from fastapi import APIRouter, Depends, HTTPException
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

@router.post("")
@router.post("/", include_in_schema=False)
async def create(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_users", "M01", body)

@router.get("")
@router.get("/", include_in_schema=False)
async def list(institution_id: str | None = None, role: str | None = None, q: str | None = None, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_users", "S01", {"institution_id": institution_id, "role": role, "q": q})

@router.get("/{id}")
@router.get("/{id}/", include_in_schema=False)
async def get_one(id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_users", "R01", {"id": id})

@router.put("/{id}")
@router.put("/{id}/", include_in_schema=False)
async def update(id: str, body: dict, pool=Depends(db_pool)):
    body = {"id": id, **body}
    return await call_fn_one(pool, "fn_manage_users", "M02", body)

@router.delete("/{id}")
@router.delete("/{id}/", include_in_schema=False)
async def delete(id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_users", "D01", {"id": id})

# 👇 NUEVO: perfil agregado básico
@router.get("/profile/{id}")
@router.get("/profile/{id}/", include_in_schema=False)
async def profile(id: str, pool=Depends(db_pool)):
    user = await call_fn_one(pool, "fn_manage_users", "R01", {"id": id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # TODO: cuando tengas la relación user -> guardian -> students, aquí rellenas students
    return {
        "id": user["id"],
        "username": user.get("username"),
        "email": user.get("email"),
        "full_name": user.get("full_name"),
        "role": user.get("role"),
        "created_at": user.get("created_at"),
        "students": []
    }
