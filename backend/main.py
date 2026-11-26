import hashlib
import hmac
import os
import re
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import contains_eager
from db import Category, Product, SessionLocal, User
import uvicorn

app = FastAPI(title="SweetLove")

FRONT_DIR = Path(__file__).resolve().parent.parent / "fronted"


def _price(value):

    return int(value) if value == int(value) else float(value)


@app.get("/api/products")
def get_products(section: str | None = None):
    with SessionLocal() as session:
        query = (
            select(Product)
            .join(Product.category)
            .options(contains_eager(Product.category))
            .where(Product.is_active.is_(True))
            .order_by(Category.id, Product.id)
        )
        if section:
            query = query.where(Category.section == section)

        products = session.scalars(query).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "price": _price(p.price),
                "volume": p.volume,
                "image": p.image,
                "category": p.category.name,
            }
            for p in products
        ]


@app.get("/zapivon")
def zapivon_page():
    return FileResponse(FRONT_DIR / "zapivon.html")

@app.get("/korzina")
def korzina_page():
    return FileResponse(FRONT_DIR / "korzina.html")

@app.get("/oformlenie")
def oformlenie_page():
    return FileResponse(FRONT_DIR / "oformlenie.html")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return salt.hex() + "$" + digest.hex()


def check_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split("$")
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return hmac.compare_digest(digest.hex(), hash_hex)


class RegisterData(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=255)
    password: str = Field(min_length=6, max_length=128)


@app.post("/api/register")
def register(data: RegisterData):
    name = data.name.strip()
    email = data.email.strip().lower()
    if not name:
        raise HTTPException(status_code=400, detail="Введите имя")
    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=400, detail="Введите корректную почту")

    with SessionLocal() as session:
        if session.scalar(select(User).where(User.email == email)):
            raise HTTPException(status_code=400, detail="Эта почта уже зарегистрирована")
        user = User(name=name, email=email, password_hash=hash_password(data.password))
        session.add(user)
        try:
            session.commit()
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Эта почта уже зарегистрирована")
        return {"name": user.name}


class LoginData(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(max_length=128)


@app.post("/api/login")
def login(data: LoginData):
    email = data.email.strip().lower()
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        if user is None or not check_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Неверная почта или пароль")
        return {"name": user.name}

@app.get("/register")
def register_page():
    return FileResponse(FRONT_DIR / "register.html")


@app.get("/login")
def login_page():
    return FileResponse(FRONT_DIR / "login.html")


app.mount("/", StaticFiles(directory=FRONT_DIR, html=True), name="site")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)