import os
from datetime import datetime
from decimal import Decimal

from dotenv import load_dotenv

from sqlalchemy import ForeignKey, Numeric, String, create_engine, select
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

load_dotenv()

DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "1903")),
    database=os.getenv("DB_NAME", "sweetlove"),
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    section: Mapped[str] = mapped_column(String(50), default="main", server_default="main")

    products: Mapped[list["Product"]] = relationship(back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))  
    image: Mapped[str] = mapped_column(String(255), unique=True) 
    volume: Mapped[str | None] = mapped_column(String(20))  
    is_active: Mapped[bool] = mapped_column(default=True)        
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    category: Mapped["Category"] = relationship(back_populates="products")

    def __repr__(self):
        return f"<Product {self.name} — {self.price} руб.>"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))  # пароль в открытом виде не хранится
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    def __repr__(self):
        return f"<User {self.name} {self.email}>"


PRODUCTS = {
    "Батончики": [
        ("BabyFox с молочной начинкой", 55, "foto_baby_fox/baton_milk.png"),
        ("BabyFox с ореховой начинкой", 62, "foto_baby_fox/baton_orehi.png"),
        ("BabyFox с солёной карамелью", 70, "foto_baby_fox/baton_caramel.png"),
        ("BabyFox со вкусом Дубайский шоколад", 80, "foto_baby_fox/baton_dubai.png"),
    ],
    "Вафли": [
        ("BabyFox Creamy White", 30, "foto_baby_fox/vafli_white.png"),
        ("BabyFox Creamy Dark", 30, "foto_baby_fox/vafli_dark.png"),
        ("BabyFox Creamy Chocolate", 42, "foto_baby_fox/vafli_choco.png"),
    ],
    "Вафельные трубочки": [
        ("BabyFox Wafer Rolls с молочной начинкой", 20, "foto_baby_fox/vafli_roll_milk.png"),
        ("BabyFox Wafer Rolls с ореховой начинкой и какао", 20, "foto_baby_fox/vafli_roll_orehi.png"),
        ("BabyFox Wafer Rolls с солёной карамелью", 20, "foto_baby_fox/vafli_roll_caramel.png"),
    ],
    "Шоколад": [
        ("BabyFox Шоколад с молочной начинкой", 130, "foto_baby_fox/plitka_milk.png"),
        ("BabyFox Шоколад с ореховой начинкой", 130, "foto_baby_fox/plitka_orehi.png"),
        ("BabyFox Шоколад с арахисом и солёной карамелью", 140, "foto_baby_fox/plitka_arahis_caramel.png"),
        ("BabyFox Шоколад с арахисом", 140, "foto_baby_fox/plitka_arahis.png"),
    ],
    "Конфеты и драже": [
        ("BabyFox Galaxy sphere", 160, "foto_baby_fox/konfeti_galaxy.png"),
        ("BabyFox Mini с молочной начинкой", 120, "foto_baby_fox/konfeti_mini.png"),
        ("BabyFox Pralines Style", 120, "foto_baby_fox/konfeti_praline.png"),
        ("BabyFox Драже двухслойный шоколад в цветной глазури", 65, "foto_baby_fox/konfeti_glazur.png"),
    ],
    "Чёрный чай": [
        ("IceTea чёрный чай персик", 80, "foto_ice_tea/black_persik.png", "0.5 л"),
        ("IceTea чёрный чай лимон", 80, "foto_ice_tea/black_limon.png", "0.5 л"),
        ("IceTea чёрный чай лесные ягоды", 80, "foto_ice_tea/black_yagodi.png", "0.5 л"),
    ],
    "Зелёный чай": [
        ("IceTea зелёный чай малина", 80, "foto_ice_tea/green_malina.png", "0.5 л"),
        ("IceTea зелёный чай клубника и алоэ вера", 80, "foto_ice_tea/green_aloe.png", "0.5 л"),
        ("IceTea зелёный чай цитрусовые фрукты", 80, "foto_ice_tea/green_citrus.png", "0.5 л"),
    ],
    "Wellbeing collection": [
        ("IceTea wellbeing collection апельсин и бергамот", 90, "foto_ice_tea/WC_apelsin.png", "0.5 л"),
        ("IceTea wellbeing collection персик и жасмин", 80, "foto_ice_tea/WC_zhasmin.png", "0.5 л"),
        ("IceTea wellbeing collection ZERO улун", 80, "foto_ice_tea/WC_ulun.png", "0.5 л"),
    ],
}

SECTIONS = {
    "Чёрный чай": "zapivon",
    "Зелёный чай": "zapivon",
    "Wellbeing collection": "zapivon",
}

def ensure_database():
    db_name = DATABASE_URL.database
    admin_engine = create_engine(DATABASE_URL.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.exec_driver_sql(
            "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
        ).scalar()
        if not exists:
            conn.exec_driver_sql(f'CREATE DATABASE "{db_name}"')
            print(f"База данных '{db_name}' создана")
    admin_engine.dispose()


def init_db():
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.exec_driver_sql("ALTER TABLE products ADD COLUMN IF NOT EXISTS volume VARCHAR(20)")
        conn.exec_driver_sql("ALTER TABLE categories ADD COLUMN IF NOT EXISTS section VARCHAR(50) NOT NULL DEFAULT 'main'")
    print("Таблицы созданы:", ", ".join(Base.metadata.tables))


def fill_products():
    with SessionLocal() as session:
        existing = {p.image: p for p in session.scalars(select(Product))}
        added = moved = 0
        for cat_name, items in PRODUCTS.items():
            section = SECTIONS.get(cat_name, "main")
            category = session.scalar(select(Category).where(Category.name == cat_name))
            if category is None:
                category = Category(name=cat_name, section=section)
                session.add(category)
            else:
                category.section = section
            for name, price, image, *rest in items:
                product = existing.get(image)
                if product is None:
                    category.products.append(
                        Product(name=name, price=price, image=image, volume=rest[0] if rest else None)
                    )
                    added += 1
                elif product.category is not category:
                    product.category = category  # товар уже был, но лежал в другой категории
                    moved += 1
        session.flush()
        for c in session.scalars(select(Category)):
            if c.name not in PRODUCTS and not c.products:
                session.delete(c)
        session.commit()
        print(f"Добавлено новых товаров: {added}, перенесено в другую категорию: {moved}")


if __name__ == "__main__":
    ensure_database()
    init_db()
    fill_products()
