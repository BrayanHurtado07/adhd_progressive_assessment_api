from typing import Any, Dict, List, Optional
import asyncpg
import json


def record_to_dict(r: asyncpg.Record) -> Dict[str, Any]:
    return dict(r) if r is not None else {}

async def call_fn_many(pool: asyncpg.Pool, fn: str, accion: str, payload: dict) -> List[dict]:
    sql = f"SELECT * FROM adhd.{fn}($1::text, $2::jsonb)"
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, accion, json.dumps(payload) if payload is not None else None)
    return [record_to_dict(r) for r in rows]

async def call_fn_one(pool: asyncpg.Pool, fn: str, accion: str, payload: dict) -> Optional[dict]:
    res = await call_fn_many(pool, fn, accion, payload)
    return res[0] if res else None

# Específicas (no llevan 'accion,payload'):
async def fn_compute_snap_scores(pool: asyncpg.Pool, form_id: str) -> dict | None:
    sql = "SELECT * FROM adhd.fn_compute_snap_scores($1::uuid)"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, form_id)
    return record_to_dict(row)

async def fn_report_student_period(pool: asyncpg.Pool, student_id: str, start: str, end: str, generated_by: str) -> dict | None:
    sql = "SELECT * FROM adhd.fn_report_student_period($1::uuid,$2::date,$3::date,$4::uuid)"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, student_id, start, end, generated_by)
    return record_to_dict(row)
