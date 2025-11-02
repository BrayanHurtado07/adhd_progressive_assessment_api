# utils.py
from typing import Any, Dict, List, Optional
import asyncpg
import json
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal

def record_to_dict(r: asyncpg.Record) -> Dict[str, Any]:
    return dict(r) if r is not None else {}

def _json_default(o):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if isinstance(o, UUID):
        return str(o)
    if isinstance(o, Decimal):
        # si prefieres string, usa str(o)
        return float(o)
    # último recurso: str
    return str(o)

def _safe_json_dumps(payload: dict | None) -> str | None:
    if payload is None:
        return None
    return json.dumps(payload, default=_json_default)

async def call_fn_many(pool: asyncpg.Pool, fn: str, accion: str, payload: dict) -> List[dict]:
    sql = f"SELECT * FROM adhd.{fn}($1::text, $2::jsonb)"
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, accion, _safe_json_dumps(payload))
    return [record_to_dict(r) for r in rows]

async def call_fn_one(pool: asyncpg.Pool, fn: str, accion: str, payload: dict) -> Optional[dict]:
    res = await call_fn_many(pool, fn, accion, payload)
    return res[0] if res else None

# ---- existentes ----
async def fn_compute_snap_scores(pool: asyncpg.Pool, form_id: str) -> dict | None:
    sql = "SELECT * FROM adhd.fn_compute_snap_scores($1::uuid)"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, form_id)
    return record_to_dict(row)

async def fn_report_student_period(pool: asyncpg.Pool, student_id: str, start: date, end: date, generated_by: str) -> dict | None:
    sql = "SELECT * FROM adhd.fn_report_student_period($1::uuid,$2::date,$3::date,$4::uuid)"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, student_id, start, end, generated_by)
    return record_to_dict(row)

# ---- ARREGLADO: lee de snap_scores (no snap_form_scores) ----
async def fetch_last_snap_scores_by_student(pool: asyncpg.Pool, student_id: str) -> dict | None:
    sql = """
    SELECT s.form_id,
           s.inattentive_score, s.hyperimpulsive_score, s.odd_score,
           s.total_score, s.severity, s.computed_at
    FROM adhd.snap_scores s
    JOIN adhd.snap_forms f ON f.id = s.form_id
    WHERE f.student_id = $1::uuid
    ORDER BY s.computed_at DESC
    LIMIT 1
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, student_id)
    return record_to_dict(row)

async def fetch_last_form_id_by_student(pool: asyncpg.Pool, student_id: str) -> str | None:
    sql = """
    SELECT id
    FROM adhd.snap_forms
    WHERE student_id = $1::uuid
    ORDER BY created_at DESC
    LIMIT 1
    """
    async with pool.acquire() as conn:
        val = await conn.fetchval(sql, student_id)
    return str(val) if val else None
