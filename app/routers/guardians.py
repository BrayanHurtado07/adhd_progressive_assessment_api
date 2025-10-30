import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

# POST /guardians  y /guardians/
@router.post("")
@router.post("/", include_in_schema=False)
async def create(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_guardians", "M01", body)

# GET /guardians  y /guardians/
@router.get("")
@router.get("/", include_in_schema=False)
async def list(institution_id: str | None = None, q: str | None = None, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_guardians", "S01", {"institution_id": institution_id, "q": q})

def _normalize_relation(raw: str | None) -> str:
    """
    Normaliza valores desde app ('Padre', 'Docente', 'Tutor') a lo que la BD espera.
    Ajusta aquí si tu enum/constraint usa otras etiquetas.
    """
    val = (raw or "").strip().lower()
    if val in ("padre", "madre", "apoderado", "encargado", "parent"):
        return "parent"
    if val in ("docente", "maestro", "profesor", "teacher"):
        return "teacher"
    if val in ("tutor",):
        return "tutor"
    # fallback seguro
    return "parent"

# POST /guardians/link  y /guardians/link/
@router.post("/link")
@router.post("/link/", include_in_schema=False)
async def link(body: dict, pool=Depends(db_pool)):
    """
    body: { guardian_id, student_id, relation }
    """
    payload = {
        **body,
        "relation": _normalize_relation(body.get("relation"))
    }
    try:
        return await call_fn_one(pool, "fn_manage_guardian_student", "M01", payload)
    except asyncpg.exceptions.UniqueViolationError:
        # ya existía el vínculo -> idempotente
        return {"status": "already_linked", **payload}
    except asyncpg.PostgresError as e:
        msg = getattr(e, "detail", None) or getattr(e, "message", str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# DELETE /guardians/link  y /guardians/link/
@router.delete("/link")
@router.delete("/link/", include_in_schema=False)
async def unlink(guardian_id: str, student_id: str, pool=Depends(db_pool)):
    return await call_fn_one(
        pool,
        "fn_manage_guardian_student",
        "D01",
        {"guardian_id": guardian_id, "student_id": student_id}
    )
