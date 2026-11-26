# SweetLove

Учебный интернет-магазин сладостей и напитков: FastAPI + PostgreSQL (SQLAlchemy) + HTML/CSS/JS.

## Структура

```
sweetlove/
├── backend/
│   ├── db.py            # модели, создание БД, наполнение товарами
│   └── main.py          # FastAPI: API и страницы
├── fronted/
│   ├── index.html       # главная (BabyFox)
│   ├── zapivon.html     # «Запивон» (IceTea)
│   ├── korzina.html, oformlenie.html, register.html, login.html
│   ├── script.js, style.css
│   └── foto_baby_fox/, foto_ice_tea/
├── req.txt
└── .env                 # DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
```

## Запуск

```
pip install -r req.txt
cd backend
python db.py     # создать БД, таблицы, товары
python main.py   # сервер на http://127.0.0.1:8000
```

## Функционал

- Каталог из БД: «Главная» и «Запивон»
- Сортировка «дешевле / дороже»
- Фильтры по видам: Батончики, Вафли, Вафельные трубочки, Шоколад, Конфеты и драже / Чёрный чай, Зелёный чай, Wellbeing collection
- Корзина (localStorage) со счётчиком в шапке, оформление с промокодом
- Регистрация и вход, имя пользователя в шапке

## API

- `GET /api/products?section=main|zapivon`
- `POST /api/register`, `POST /api/login`

## БД

Таблицы `categories`, `products`, `users`. Товары лежат в словаре `PRODUCTS` в `db.py`, после правки нужно снова запустить `python db.py`

