from fastapi import APIRouter, Depends, HTTPException
from ..deps import db_pool
from ..utils import call_fn_many, call_fn_one

router = APIRouter()

@router.post("")
@router.post("/", include_in_schema=False)
async def create(body: dict, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_users", "M01", body)

@router.get("")
@router.get("/", include_in_schema=False)
async def list(institution_id: str | None = None, role: str | None = None, q: str | None = None, pool=Depends(db_pool)):
    return await call_fn_many(pool, "fn_manage_users", "S01", {"institution_id": institution_id, "role": role, "q": q})

@router.get("/{id}")
@router.get("/{id}/", include_in_schema=False)
async def get_one(id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_users", "R01", {"id": id})

@router.put("/{id}")
@router.put("/{id}/", include_in_schema=False)
async def update(id: str, body: dict, pool=Depends(db_pool)):
    body = {"id": id, **body}
    return await call_fn_one(pool, "fn_manage_users", "M02", body)

@router.delete("/{id}")
@router.delete("/{id}/", include_in_schema=False)
async def delete(id: str, pool=Depends(db_pool)):
    return await call_fn_one(pool, "fn_manage_users", "D01", {"id": id})

# PERFIL COMPLETO: user + students asociados
@router.get("/profile/{id}")
@router.get("/profile/{id}/", include_in_schema=False)
async def profile(id: str, pool=Depends(db_pool)):
    # 1) Traemos al usuario
    user = await call_fn_one(pool, "fn_manage_users", "R01", {"id": id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    email = user.get("email")
    students: list[dict] = []

    print(f"[PROFILE] user_id={id} email={email}")

    if email:
        # 2) Buscamos guardian por email (sin filtrar por institución para simplificar)
        guardians = await call_fn_many(
            pool,
            "fn_manage_guardians",
            "S01",
            {
                "institution_id": None,  # <- importante: no filtramos por institución
                "q": email,              # S01 busca por full_name / email / phone
            },
        )
        print(f"[PROFILE] guardians encontrados: {len(guardians)}")

        if guardians:
            guardian = guardians[0]
            guardian_id = str(guardian["id"])

            # 3) Vínculos guardian_student de ese guardian
            links = await call_fn_many(
                pool,
                "fn_manage_guardian_student",
                "S01",
                {"guardian_id": guardian_id},
            )
            print(f"[PROFILE] links encontrados: {len(links)}")

            # 4) Por cada vínculo, traemos al estudiante
            for link in links:
                student_id = str(link["student_id"])
                stu = await call_fn_one(
                    pool,
                    "fn_manage_students",
                    "R01",
                    {"id": student_id},
                )
                if stu:
                    students.append(
                        {
                            "id": stu["id"],
                            "full_name": stu["full_name"],
                            "birthdate": stu["birthdate"],
                            "gender": stu["gender"],
                            "doc_type": stu["doc_type"],
                            "doc_number": stu["doc_number"],
                        }
                    )

    print(f"[PROFILE] students devueltos: {len(students)}")

    return {
        "id": user["id"],
        "username": user.get("username"),
        "email": user.get("email"),
        "full_name": user.get("full_name"),
        "role": user.get("role"),
        "created_at": user.get("created_at"),
        "students": students,
    }