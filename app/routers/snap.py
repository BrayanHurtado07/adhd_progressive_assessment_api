from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one, fn_compute_snap_scores

router = APIRouter()

# POST /snap/forms  y /snap/forms/
@router.post("/forms")
@router.post("/forms/", include_in_schema=False)
async def create_form(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_snap_forms", "M01", body)

# GET /snap/forms  y /snap/forms/
@router.get("/forms")
@router.get("/forms/", include_in_schema=False)
async def list_forms(student_id: str | None = None, limit: int = 100, offset: int = 0, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_snap_forms", "S01", {"student_id": student_id, "limit": limit, "offset": offset})

# GET /snap/forms/{form_id}  y /snap/forms/{form_id}/
@router.get("/forms/{form_id}")
@router.get("/forms/{form_id}/", include_in_schema=False)
async def get_form(form_id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_snap_forms", "R01", {"id": form_id})

# POST /snap/forms/{form_id}/answers  y con slash
@router.post("/forms/{form_id}/answers")
@router.post("/forms/{form_id}/answers/", include_in_schema=False)
async def upsert_answers(form_id: str, body: dict, pool=Depends(db_pool)):
    payload = {"form_id": form_id, "answers": body.get("answers", [])}
    return await call_fn_one(pool, "fn_manage_snap_answers", "M01", payload)

# POST /snap/forms/{form_id}/scores/compute  y con slash
@router.post("/forms/{form_id}/scores/compute")
@router.post("/forms/{form_id}/scores/compute/", include_in_schema=False)
async def compute_scores(form_id: str, pool=Depends(db_pool)):
    return await fn_compute_snap_scores(pool, form_id)
