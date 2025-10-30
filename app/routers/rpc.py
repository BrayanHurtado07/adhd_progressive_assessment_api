from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import call_fn_many

router = APIRouter()

# POST /rpc/{fn}/{accion}  y con slash final
@router.post("/{fn}/{accion}")
@router.post("/{fn}/{accion}/", include_in_schema=False)
async def rpc(fn: str, accion: str, payload: dict, pool=Depends(db_pool)):
    rows = await call_fn_many(pool, fn, accion, payload)
    return {"rows": rows, "count": len(rows)}
