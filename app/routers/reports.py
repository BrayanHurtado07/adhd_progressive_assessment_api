# app/routers/reports.py
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, UUID4, model_validator
from ..deps import db_pool
from ..utils import fn_report_student_period, call_fn_many
from datetime import date, datetime, timedelta
import zoneinfo

router = APIRouter()
LIMA = zoneinfo.ZoneInfo("America/Lima")

class ReportGeneratePayload(BaseModel):
    student_id: UUID4
    period_start: date
    period_end: date
    generated_by: UUID4

    # ✅ Pydantic v2: validación cruzada de campos
    @model_validator(mode="after")
    def check_dates(self):
        if self.period_end < self.period_start:
            raise ValueError("period_end no puede ser menor que period_start")
        # (opcional) límite de rango
        # if (self.period_end - self.period_start).days > 366:
        #     raise ValueError("El rango no debe exceder 366 días")
        return self

@router.post("/generate")
@router.post("/generate/", include_in_schema=False)
async def generate(payload: ReportGeneratePayload, pool=Depends(db_pool)):
    # Ya vienen tipados como UUID y date
    return await fn_report_student_period(
        pool,
        str(payload.student_id),
        payload.period_start,
        payload.period_end,
        str(payload.generated_by),
    )

@router.post("/generate/quick")
async def generate_quick(
    student_id: UUID4,
    generated_by: UUID4,
    period: str = Query("weekly", pattern="^(daily|weekly|monthly)$"),
    pool=Depends(db_pool)
):
    now = datetime.now(LIMA).date()
    if period == "daily":
        start, end = now, now
    elif period == "weekly":
        start, end = now - timedelta(days=6), now
    else:  # monthly
        start = now.replace(day=1)
        next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        end = next_month - timedelta(days=1)

    if end < start:
        raise HTTPException(status_code=422, detail="Rango de fechas inválido")

    return await fn_report_student_period(pool, str(student_id), start, end, str(generated_by))

@router.get("")
async def list_reports(student_id: UUID4, pool=Depends(db_pool)):
    q = """
    SELECT * FROM adhd.reports
     WHERE student_id = $1
     ORDER BY period_start DESC, created_at DESC
    """
    return await call_fn_many(pool, None, None, None, raw_sql=q, params=[str(student_id)])

@router.get("/{report_id}")
async def get_report(report_id: UUID4, pool=Depends(db_pool)):
    q = "SELECT * FROM adhd.reports WHERE id = $1"
    rows = await call_fn_many(pool, None, None, None, raw_sql=q, params=[str(report_id)])
    return rows[0] if rows else {}