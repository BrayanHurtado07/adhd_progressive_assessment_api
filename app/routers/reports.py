from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import fn_report_student_period

router = APIRouter()

@router.post("/generate")
async def generate(body: dict, pool=Depends(db_pool)):
    # body: {student_id, period_start (YYYY-MM-DD), period_end, generated_by}
    return await fn_report_student_period(
        pool,
        body["student_id"], body["period_start"], body["period_end"], body["generated_by"]
    )
