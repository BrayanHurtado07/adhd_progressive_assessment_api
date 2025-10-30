import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt  # PyJWT

from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()
bearer = HTTPBearer(auto_error=False)

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALG    = os.getenv("JWT_ALG", "HS256")
JWT_EXP_MIN= int(os.getenv("JWT_EXP_MIN", "10080"))  # 7 días

def _create_access_token(sub: str) -> str:
    exp = datetime.utcnow() + timedelta(minutes=JWT_EXP_MIN)
    payload = {"sub": sub, "exp": exp}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def _verify_password(plain: str, stored: str | None) -> bool:
    if not stored:
        return False
    if stored == plain:
        return True
    try:
        if stored.startswith("$2"):
            from passlib.hash import bcrypt
            return bcrypt.verify(plain, stored)
    except Exception:
        pass
    return False

async def _get_user_by_username(pool, username: str) -> dict | None:
    rows = await call_fn_many(pool, "fn_manage_users", "S01", {"q": username})
    for r in rows or []:
        if r.get("username") == username:
            return r
    return None

class LoginBody(BaseModel):
    username: str
    password: str

# POST /auth/token  y /auth/token/
@router.post("/token")
@router.post("/token/", include_in_schema=False)
async def login_token(form: OAuth2PasswordRequestForm = Depends(), pool=Depends(db_pool)):
    user = await _get_user_by_username(pool, form.username)
    if not user or not user.get("is_active", True) or not _verify_password(form.password, user.get("password_hash")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Credenciales inválidas")
    token = _create_access_token(str(user["id"]))
    return {"access_token": token, "token_type": "bearer"}

# POST /auth/login  y /auth/login/
@router.post("/login")
@router.post("/login/", include_in_schema=False)
async def login_json(body: LoginBody, pool=Depends(db_pool)):
    user = await _get_user_by_username(pool, body.username)
    if not user or not user.get("is_active", True) or not _verify_password(body.password, user.get("password_hash")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Credenciales inválidas")
    token = _create_access_token(str(user["id"]))
    return {"access_token": token, "token_type": "bearer"}

# GET /auth/me  y /auth/me/
@router.get("/me")
@router.get("/me/", include_in_schema=False)
async def me(credentials: HTTPAuthorizationCredentials = Depends(bearer), pool=Depends(db_pool)):
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="No autenticado")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        uid = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = await call_fn_one(pool, "fn_manage_users", "R01", {"id": uid})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"id": user["id"], "username": user["username"], "role": user["role"]}
