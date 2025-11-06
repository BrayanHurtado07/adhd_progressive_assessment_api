# app/routers/alerts.py
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends

from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

# ------------ Helpers internos ------------

def _normalize_severity(raw: str | None) -> str:
    """
    Normaliza severidad a enum adhd.severity_t:
    -> 'severo' | 'moderado' | 'leve' | 'no_aplica'
    Acepta high/medium/info/leve/moderado/severo/etc.
    """
    if not raw:
        return "no_aplica"

    r = raw.lower().strip()

    # Alta / crítica
    if r in {"high", "alta", "crítica", "critica", "severo", "severe", "crit"}:
        return "severo"

    # Media / moderada
    if r in {"medium", "media", "moderado", "moderate"}:
        return "moderado"

    # Baja / info
    if r in {"low", "leve", "info", "informativa"}:
        return "leve"

    # Fallback
    return "no_aplica"


def _normalize_body_severity(body: dict) -> dict:
    sev = body.get("severity")
    body = dict(body)  # copia defensiva
    body["severity"] = _normalize_severity(sev)
    return body


# POST /alerts (crear/actualizar)
@router.post("")
@router.post("/", include_in_schema=False)
async def create(body: dict, pool=Depends(db_pool)):
    """
    Crea una alerta. Espera al menos:
    { student_id, kind, severity, title, description, [source], [metadata] }

    La severidad puede llegar como:
    - "high" / "medium" / "info"
    - "severo" / "moderado" / "leve" / "no_aplica"
    y se normaliza a enum adhd.severity_t antes de llamar a la función SQL.
    """
    body = _normalize_body_severity(body)
    return await call_fn_one(pool, "fn_manage_alerts", "M01", body)


# POST /alerts/{id}/ack
@router.post("/{id}/ack")
@router.post("/{id}/ack/", include_in_schema=False)
async def acknowledge(id: str, user_id: str, pool=Depends(db_pool)):
    return await call_fn_one(
        pool,
        "fn_manage_alerts",
        "ACK",
        {"id": id, "user_id": user_id},
    )


# GET /alerts (listar)
@router.get("")
@router.get("/", include_in_schema=False)
async def list(
    student_id: str | None = None,
    only_open: bool = False,
    pool=Depends(db_pool),
):
    """
    Devuelve alertas. Si tu SQL soporta 'only_open', lo usa; si no, lo ignora.
    """
    return await call_fn_many(
        pool,
        "fn_manage_alerts",
        "S01",
        {
            "student_id": student_id,
            "only_open": only_open,
        },
    )


# Recomputar alertas tras una sesión
@router.post("/recompute/session/{session_id}")
async def recompute_for_session(session_id: str, pool=Depends(db_pool)):
    return await call_fn_many(
        pool,
        "fn_generate_alerts_after_session",
        session_id,
    )


# Escanear inactividad (default 5 días)
@router.post("/scan/inactivity")
async def scan_inactivity(days: int = 5, pool=Depends(db_pool)):
    return await call_fn_many(
        pool,
        "fn_generate_inactivity_alerts",
        {"p_days": days},
    )


# -------- DEMO/SEED: crea 4 alertas de ejemplo para un estudiante ----------
@router.post("/seed-demo")
async def seed_demo(student_id: str, pool=Depends(db_pool)):
    """
    Inserta 4 alertas de prueba (source='demo') para el student_id dado.
    Útil para probar UI sin datos reales. Bórralas luego desde tu SQL si quieres.

    IMPORTANTE: aquí usamos severidad ya NORMALIZADA al enum severity_t.
    """
    now = datetime.now(timezone.utc)
    iso = lambda d: d.isoformat()

    samples = [
        {
            "student_id": student_id,
            "kind": "inactividad",
            "severity": "moderado",  # antes "medium"
            "title": "Sin actividad en 6 días",
            "description": "No se han registrado sesiones en casi una semana.",
            "source": "demo",
            "metadata": {"days": 6},
            "created_at": iso(now - timedelta(hours=2)),
        },
        {
            "student_id": student_id,
            "kind": "bajo_rendimiento",
            "severity": "severo",  # antes "high"
            "title": "Bajo rendimiento en Memory",
            "description": "El puntaje estuvo por debajo del umbral esperado en la última sesión.",
            "source": "demo",
            "metadata": {"activity": "memory", "score": 42, "threshold": 60},
            "created_at": iso(now - timedelta(hours=3)),
        },
        {
            "student_id": student_id,
            "kind": "regresion",
            "severity": "moderado",  # antes "medium"
            "title": "Regresión de desempeño semanal",
            "description": "Caída del 18% vs. promedio de la semana pasada.",
            "source": "demo",
            "metadata": {"window": "7d", "drop_pct": 18},
            "created_at": iso(now - timedelta(days=1)),
        },
        {
            "student_id": student_id,
            "kind": "bajo_rendimiento",
            "severity": "leve",  # antes "info"
            "title": "Recomendación: Quick Count",
            "description": "Intenta una sesión corta de 'Quick Count' (2–3 min) para mantener la racha.",
            "source": "demo",
            "metadata": {"activity": "quick_count"},
            "created_at": iso(now - timedelta(days=2)),
        },
    ]

    out = []
    for body in samples:
        # Por si algún día alguien mete "high/medium/info" aquí, la normalizamos igual
        body = _normalize_body_severity(body)
        out.append(await call_fn_one(pool, "fn_manage_alerts", "M01", body))
    return out