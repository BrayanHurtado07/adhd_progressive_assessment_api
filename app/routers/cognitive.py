# cognitive.py
from fastapi import APIRouter, Depends, HTTPException, status
from ..deps import db_pool
from ..utils import (
    call_fn_many, call_fn_one,
    fetch_last_snap_scores_by_student,
    fetch_last_form_id_by_student,
    fn_compute_snap_scores,
)

router = APIRouter()

def _infer_tdah(inatt: int, hyper: int) -> str:
    if inatt - hyper >= 2:
        return "inatento"
    if hyper - inatt >= 2:
        return "hiperactivo"
    return "combinado"

@router.post("")
@router.post("/", include_in_schema=False)
async def create(body: dict, pool=Depends(db_pool)):
    student_id = (body.get("student_id") or "").strip()
    if not student_id:
        raise HTTPException(status_code=400, detail="student_id es requerido")

    source = (body.get("source") or "").lower()

    if source == "reglas" and (not body.get("tdah") or not body.get("severity")):
        scores = await fetch_last_snap_scores_by_student(pool, student_id)
        if not scores:
            last_form_id = await fetch_last_form_id_by_student(pool, student_id)
            if not last_form_id:
                raise HTTPException(status_code=400, detail="No hay SNAP para derivar el perfil. Realiza primero un SNAP-IV.")
            await fn_compute_snap_scores(pool, last_form_id)
            scores = await fetch_last_snap_scores_by_student(pool, student_id)
            if not scores:
                raise HTTPException(status_code=500, detail="No se pudo computar SNAP scores para derivar el perfil.")

        inatt = int(scores.get("inattentive_score") or 0)
        hyper = int(scores.get("hyperimpulsive_score") or 0)
        odd   = int(scores.get("odd_score") or 0)
        total = int(scores.get("total_score") or 0)
        computed_at = scores.get("computed_at")
        # 👇 convertir datetime a string ISO si viene como datetime
        if computed_at is not None and hasattr(computed_at, "isoformat"):
            computed_at = computed_at.isoformat()

        body.setdefault("tdah", _infer_tdah(inatt, hyper))
        body.setdefault("severity", scores.get("severity") or "no_aplica")
        body.setdefault("model_version", "rules-v1")
        body.setdefault("features", {
            "inattentive_score": inatt,
            "hyperimpulsive_score": hyper,
            "odd_score": odd,
            "total_score": total,
            "computed_at": computed_at,
        })

    return await call_fn_one(pool, "fn_manage_cognitive_profiles", "M01", body)

@router.get("")
@router.get("/", include_in_schema=False)
async def list(student_id: str | None = None, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_cognitive_profiles", "S01", {"student_id": student_id})
