# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .db import get_pool, close_pool
from .routers import (
    institutions, users, students, guardians, consents,
    snap, cognitive, activities, sessions, alerts, reports, ml, auth
)

load_dotenv()

app = FastAPI(title="ADHD Progressive Assessment API", version="1.0.0")
app.router.redirect_slashes = False

# CORS
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    pool = await get_pool()  # calienta el pool
    # ping rápido a la DB para log de “conectado”
    async with pool.acquire() as conn:
        val = await conn.fetchval("SELECT 1;")
    print(f"[STARTUP] Pool inicializado. Ping DB = {val} ✅")

@app.on_event("shutdown")
async def shutdown():
    await close_pool()
    print("[SHUTDOWN] Pool cerrado ✅")

# Health (para pruebas locales y desde el teléfono)
@app.get("/health", tags=["Health"])
async def health():
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1;")
        return {"status": "ok", "db": "up"}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}

# Routers
app.include_router(auth.router,         prefix="/auth",         tags=["Auth"])
app.include_router(institutions.router, prefix="/institutions", tags=["Institutions"])
app.include_router(users.router,        prefix="/users",        tags=["Users"])
app.include_router(students.router,     prefix="/students",     tags=["Students"])
app.include_router(guardians.router,    prefix="/guardians",    tags=["Guardians"])
app.include_router(consents.router,     prefix="/consents",     tags=["Consents"])
app.include_router(snap.router,         prefix="/snap",         tags=["SNAP-IV"])
app.include_router(cognitive.router,    prefix="/cognitive",    tags=["Cognitive Profiles"])
app.include_router(activities.router,   prefix="/activities",   tags=["Activities"])
app.include_router(sessions.router,     prefix="/sessions",     tags=["Sessions"])
app.include_router(alerts.router,       prefix="/alerts",       tags=["Alerts"])
app.include_router(reports.router,      prefix="/reports",      tags=["Reports"])
app.include_router(ml.router,           prefix="/ml",           tags=["ML"])