from typing import Any, Dict, List, Optional
import asyncpg
import json
from fastapi import HTTPException

def record_to_dict(r: asyncpg.Record) -> Dict[str, Any]:
    return dict(r) if r is not None else {}

async def call_fn_many(pool: asyncpg.Pool, fn: str, accion: str, payload: dict) -> List[dict]:
    """
    Llama a funciones: adhd.<fn>(accion TEXT, payload JSONB)
    Si PG arroja error, transformamos a 400 con detalle legible.
    """
    sql = f"SELECT * FROM adhd.{fn}($1::text, $2::jsonb)"
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                sql,
                accion,
                json.dumps(payload) if payload is not None else None
            )
        return [record_to_dict(r) for r in rows]
    except asyncpg.PostgresError as e:
        detail = getattr(e, "detail", None) or getattr(e, "message", str(e))
        raise HTTPException(status_code=400, detail=f"{fn}/{accion}: {detail}")

async def call_fn_one(pool: asyncpg.Pool, fn: str, accion: str, payload: dict) -> Optional[dict]:
    res = await call_fn_many(pool, fn, accion, payload)
    return res[0] if res else None

# -------- específicas --------

async def fn_compute_snap_scores(pool: asyncpg.Pool, form_id: str) -> dict | None:
    sql = "SELECT * FROM adhd.fn_compute_snap_scores($1::uuid)"
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(sql, form_id)
        return record_to_dict(row)
    except asyncpg.PostgresError as e:
        detail = getattr(e, "detail", None) or getattr(e, "message", str(e))
        raise HTTPException(status_code=400, detail=f"fn_compute_snap_scores: {detail}")

async def fn_report_student_period(pool: asyncpg.Pool, student_id: str, start: str, end: str, generated_by: str) -> dict | None:
    sql = "SELECT * FROM adhd.fn_report_student_period($1::uuid,$2::date,$3::date,$4::uuid)"
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(sql, student_id, start, end, generated_by)
        return record_to_dict(row)
    except asyncpg.PostgresError as e:
        detail = getattr(e, "detail", None) or getattr(e, "message", str(e))
        raise HTTPException(status_code=400, detail=f"fn_report_student_period: {detail}")
