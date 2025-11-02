# app/routers/alerts.py
from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one
from datetime import datetime, timedelta, timezone

router = APIRouter()

# POST /alerts (crear/actualizar)
@router.post("")
@router.post("/", include_in_schema=False)
async def create(body: dict, pool=Depends(db_pool)):
    """
    Crea una alerta. Espera al menos:
    { student_id, kind, severity, title, description, [source], [metadata] }
    """
    return await call_fn_one(pool, "fn_manage_alerts", "M01", body)

# POST /alerts/{id}/ack
@router.post("/{id}/ack")
@router.post("/{id}/ack/", include_in_schema=False)
async def acknowledge(id: str, user_id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_alerts", "ACK", {"id": id, "user_id": user_id})

# GET /alerts (listar)
@router.get("")
@router.get("/", include_in_schema=False)
async def list(student_id: str | None = None, only_open: bool = False, pool=Depends(db_pool)):
    """
    Devuelve alertas. Si your SQL soporta 'only_open', lo usa; si no, lo ignora.
    """
    return await call_fn_many(pool, "fn_manage_alerts", "S01", {
        "student_id": student_id,
        "only_open": only_open
    })

# Recomputar alertas tras una sesión
@router.post("/recompute/session/{session_id}")
async def recompute_for_session(session_id: str, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_generate_alerts_after_session", session_id)

# Escanear inactividad (default 5 días)
@router.post("/scan/inactivity")
async def scan_inactivity(days: int = 5, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_generate_inactivity_alerts", {"p_days": days})

# -------- DEMO/SEED: crea 4 alertas de ejemplo para un estudiante ----------
@router.post("/seed-demo")
async def seed_demo(student_id: str, pool=Depends(db_pool)):
    """
    Inserta 4 alertas de prueba (source='demo') para el student_id dado.
    Útil para probar UI sin datos reales. Bórralas luego desde tu SQL si quieres.
    """
    now = datetime.now(timezone.utc)
    samples = [
        {
            "student_id": student_id,
            "kind": "inactividad",
            "severity": "medium",
            "title": "Sin actividad en 6 días",
            "description": "No se han registrado sesiones en casi una semana.",
            "source": "demo",
            "metadata": {"days": 6},
            "created_at": (now - timedelta(hours=2)).isoformat(),
        },
        {
            "student_id": student_id,
            "kind": "bajo_rendimiento",
            "severity": "high",
            "title": "Bajo rendimiento en Memory",
            "description": "El puntaje estuvo por debajo del umbral esperado en la última sesión.",
            "source": "demo",
            "metadata": {"activity": "memory", "score": 42, "threshold": 60},
            "created_at": (now - timedelta(hours=3)).isoformat(),
        },
        {
            "student_id": student_id,
            "kind": "regresion",
            "severity": "medium",
            "title": "Regresión de desempeño semanal",
            "description": "Caída del 18% vs. promedio de la semana pasada.",
            "source": "demo",
            "metadata": {"window": "7d", "drop_pct": 18},
            "created_at": (now - timedelta(days=1)).isoformat(),
        },
        {
            "student_id": student_id,
            "kind": "bajo_rendimiento",
            "severity": "info",
            "title": "Recomendación: Quick Count",
            "description": "Intenta una sesión corta de 'Quick Count' (2–3 min) para mantener la racha.",
            "source": "demo",
            "metadata": {"activity": "quick_count"},
            "created_at": (now - timedelta(days=2)).isoformat(),
        },
    ]
    out = []
    for body in samples:
        out.append(await call_fn_one(pool, "fn_manage_alerts", "M01", body))
    return out