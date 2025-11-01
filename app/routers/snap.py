# snap.py
from fastapi import APIRouter, Depends, HTTPException, status
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one, fn_compute_snap_scores

router = APIRouter()

@router.post("/forms")
@router.post("/forms/", include_in_schema=False)
async def create_form(body: dict, pool=Depends(db_pool)):
    try:
        # Si no llegó institution_id, lo inferimos desde el student:
        if not body.get("institution_id") and body.get("student_id"):
            async with pool.acquire() as conn:
                inst = await conn.fetchval(
                    "SELECT institution_id FROM adhd.students WHERE id = $1::uuid",
                    body["student_id"],
                )
            if inst:
                body["institution_id"] = str(inst)

        if not body.get("institution_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="snap/forms: institution_id es requerido (no se pudo inferir del estudiante).",
            )

        return await call_fn_one(pool, "fn_manage_snap_forms", "M01", body)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"fn_manage_snap_forms/M01: {str(e)}")

@router.get("/forms")
@router.get("/forms/", include_in_schema=False)
async def list_forms(student_id: str | None = None, limit: int = 100, offset: int = 0, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_snap_forms", "S01", {"student_id": student_id, "limit": limit, "offset": offset})

@router.get("/forms/{form_id}")
@router.get("/forms/{form_id}/", include_in_schema=False)
async def get_form(form_id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_snap_forms", "R01", {"id": form_id})

@router.post("/forms/{form_id}/answers")
@router.post("/forms/{form_id}/answers/", include_in_schema=False)
async def upsert_answers(form_id: str, body: dict, pool=Depends(db_pool)):
    # Normaliza por si llegaran 1..4 desde apps antiguas
    answers = body.get("answers", [])
    for a in answers:
        v = a.get("value")
        if isinstance(v, int):
            a["value"] = max(0, min(3, v))  # clamp a 0..3
    payload = {"form_id": form_id, "answers": answers}
    return await call_fn_one(pool, "fn_manage_snap_answers", "M01", payload)

@router.post("/forms/{form_id}/scores/compute")
@router.post("/forms/{form_id}/scores/compute/", include_in_schema=False)
async def compute_scores(form_id: str, pool=Depends(db_pool)):
    return await fn_compute_snap_scores(pool, form_id)
