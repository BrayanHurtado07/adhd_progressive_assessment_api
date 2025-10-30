from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import fn_report_student_period

router = APIRouter()

# POST /reports/generate  y con slash
@router.post("/generate")
@router.post("/generate/", include_in_schema=False)
async def generate(body: dict, pool=Depends(db_pool)):
    return await fn_report_student_period(
        pool,
        body["student_id"], body["period_start"], body["period_end"], body["generated_by"]
    )
