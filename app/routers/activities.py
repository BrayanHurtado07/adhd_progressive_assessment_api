# app/routers/activities.py
from fastapi import APIRouter, Depends, HTTPException, status
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one, record_to_dict
from asyncpg.exceptions import UndefinedColumnError  # <-- importa esto

router = APIRouter()

@router.post("")
@router.post("/", include_in_schema=False)
async def create_activity(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_activities", "M01", body)

@router.put("/{id}")
@router.put("/{id}/", include_in_schema=False)
async def update_activity(id: str, body: dict, pool=Depends(db_pool)):
    body = {"id": id, **body}
    return await call_fn_one(pool, "fn_manage_activities", "M02", body)

@router.get("")
@router.get("/", include_in_schema=False)
async def list_activities(q: str | None = None, only_active: bool = True, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_activities", "S01", {"q": q, "only_active": only_active})

@router.post("/assign")
@router.post("/assign/", include_in_schema=False)
async def assign(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_activity_assignments", "M01", body)

@router.get("/assign")
@router.get("/assign/", include_in_schema=False)
async def list_assignments(student_id: str | None = None, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_activity_assignments", "S01", {"student_id": student_id})


def _severity_to_difficulty(severity: str | None) -> str:
    s = (severity or "").lower()
    if s == "severo": return "hard"
    if s == "moderado": return "medium"
    if s == "leve": return "easy"
    return "easy"

def _mix_for_tdah(tdah: str | None) -> list[str]:
    t = (tdah or "").lower()
    if t == "inatento":
        return ["color_sequence", "memory", "quick_count"]
    if t in ("hiperimpulsivo", "hiper_impulsivo", "hiperimpulsivo/impulsivo"):
        return ["quick_count", "memory", "sort_objects"]
    # combinado / desconocido
    return ["color_sequence", "memory", "sort_objects", "quick_count", "puzzle"]


@router.get("/recommend")
@router.get("/recommend/", include_in_schema=False)
async def recommend(student_id: str, limit: int = 5, pool=Depends(db_pool)):
    # 1) Perfil cognitivo
    async with pool.acquire() as conn:
        prof = await conn.fetchrow("""
            SELECT tdah, severity, features
            FROM adhd.cognitive_profiles
            WHERE student_id = $1::uuid
            ORDER BY generated_at DESC
            LIMIT 1
        """, student_id)

    if not prof:
        mix = _mix_for_tdah(None)[:limit]
        return {"difficulty": "easy", "items": [{"code": c, "title": c.replace("_"," ").title()} for c in mix]}

    prof = record_to_dict(prof)
    diff = _severity_to_difficulty(prof.get("severity"))
    mix  = _mix_for_tdah(prof.get("tdah"))

    # 2) Catálogo de actividades con Fallback si faltan columnas (tag, icon, est_minutes, is_active)
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch("""
                SELECT
                  code,
                  COALESCE(title, initcap(replace(code,'_',' '))) AS title,
                  COALESCE(tag, 'General')                       AS tag,
                  COALESCE(est_minutes, 3)                        AS est_minutes,
                  COALESCE(icon, '🎯')                             AS icon
                FROM adhd.activities
                WHERE code = ANY($1::text[])
                  AND (is_active IS TRUE OR is_active IS NULL)
                LIMIT $2
            """, mix, limit)
        except UndefinedColumnError:
            # Fallback minimalista: no dependas de columnas que quizá no existen
            rows = await conn.fetch("""
                SELECT
                  code,
                  COALESCE(title, initcap(replace(code,'_',' '))) AS title
                FROM adhd.activities
                WHERE code = ANY($1::text[])
                LIMIT $2
            """, mix, limit)

    items = [record_to_dict(r) for r in rows] if rows else []
    if not items:
        items = [{"code": c, "title": c.replace("_"," ").title()} for c in mix[:limit]]

    # Normaliza keys esperadas por el front
    norm = []
    for it in items[:limit]:
        norm.append({
            "code": it.get("code"),
            "title": it.get("title") or it.get("code", "").replace("_", " ").title(),
            "tag": it.get("tag", "General"),
            "est_minutes": it.get("est_minutes", 3),
            "icon": it.get("icon", "🎯"),
        })

    return {"difficulty": diff, "items": norm}