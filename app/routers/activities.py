from fastapi import APIRouter, Depends
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

# POST /activities  y /activities/
@router.post("")
@router.post("/", include_in_schema=False)
async def create_activity(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_activities", "M01", body)

# PUT /activities/{id}  y /activities/{id}/
@router.put("/{id}")
@router.put("/{id}/", include_in_schema=False)
async def update_activity(id: str, body: dict, pool=Depends(db_pool)):
    body = {"id": id, **body}
    return await call_fn_one(pool, "fn_manage_activities", "M02", body)

# GET /activities  y /activities/
@router.get("")
@router.get("/", include_in_schema=False)
async def list_activities(q: str | None = None, only_active: bool = True, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_activities", "S01", {"q": q, "only_active": only_active})

# POST /activities/assign  y /activities/assign/
@router.post("/assign")
@router.post("/assign/", include_in_schema=False)
async def assign(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_activity_assignments", "M01", body)

# GET /activities/assign  y /activities/assign/
@router.get("/assign")
@router.get("/assign/", include_in_schema=False)
async def list_assignments(student_id: str | None = None, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_activity_assignments", "S01", {"student_id": student_id})
