# app/routers/sessions.py
from fastapi import APIRouter, Depends, HTTPException, status
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

def _require_keys(body: dict, keys: list[str]):
    missing = [k for k in keys if not body.get(k)]
    if missing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Faltan campos: {', '.join(missing)}")

@router.post("/start")
@router.post("/start/", include_in_schema=False)
async def start(body: dict, pool=Depends(db_pool)):
    # esperado: student_id, activity_code, difficulty
    _require_keys(body, ["student_id", "activity_code", "difficulty"])

    res = await call_fn_one(pool, "fn_manage_activity_sessions", "START", body)
    if not res or not res.get("id"):
        raise HTTPException(status_code=500, detail="No se pudo iniciar la sesión.")

    # 🔑 Alias para compatibilidad con el front
    payload = dict(res)
    payload["session_id"] = res["id"]
    return payload

@router.post("/finish")
@router.post("/finish/", include_in_schema=False)
async def finish(body: dict, pool=Depends(db_pool)):
    _require_keys(body, ["session_id", "duration_sec", "score", "stars", "completed"])
    return await call_fn_one(pool, "fn_manage_activity_sessions", "FINISH", body)

@router.get("")
@router.get("/", include_in_schema=False)
async def list_sessions(student_id: str | None = None, limit: int = 100, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_activity_sessions", "S01",
                              {"student_id": student_id, "limit": limit})