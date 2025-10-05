# app/routers/ml.py
import os, joblib, asyncpg
from fastapi import APIRouter, Depends, HTTPException
from ..deps import db_pool

MODEL_PATH = os.getenv("MODEL_PATH", "./artifacts/rf_snap.joblib")
model = None

router = APIRouter()

async def _load_model():
    global model
    if model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"MODEL_PATH not found: {MODEL_PATH}")
        model = joblib.load(MODEL_PATH)
    return model

@router.post("/predict/{student_id}")
async def predict(student_id: str, pool=Depends(db_pool)):
    m = await _load_model()
    # trae features de la vista
    sql = "SELECT * FROM adhd.vw_student_features WHERE student_id = $1::uuid"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, student_id)
    if not row:
        raise HTTPException(404, "No features for student")
    # a dict -> dataframe con columnas en el orden del training
    import pandas as pd
    X = pd.DataFrame([dict(row)])
    # elimina columnas no usadas
    X = X.drop(columns=["student_id"])
    pred = m.predict(X)[0]
    proba = float(m.predict_proba(X)[0].max())

    # registra en ml_inferences
    await conn.execute("""
      INSERT INTO adhd.ml_inferences(id, model_id, student_id, input_ref, prediction, severity, confidence)
      VALUES (gen_random_uuid(), (SELECT id FROM adhd.ml_models ORDER BY created_at DESC LIMIT 1),
              $1::uuid, NULL, $2::tdah_type, 'no_aplica', $3::numeric)
    """, student_id, pred, proba)

    return {"student_id": student_id, "prediction": pred, "confidence": proba}
