"""
«Четверть» — CRM для сервиса проката велосипедов и самокатов.

Приложение собирается из описаний сущностей (entities.py):
для каждой сущности создаётся хранилище и набор CRUD-маршрутов.
"""
import os
from pathlib import Path

from flask import Flask, redirect, url_for

from crud import make_crud
from entities import ENTITIES
from fields import display
from storage import Repository, create_schema

# Адрес базы: postgresql://пользователь:пароль@сервер:порт/имя_базы
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:401906@localhost:5432/rental"
)

app = Flask(__name__)
# Ключ для подписи cookie с номером сессии (без него сессии не работают)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
create_schema(DATABASE_URL, Path(__file__).parent / "schema.sql")

# Для каждой сущности: хранилище + маршруты
for entity in ENTITIES:
    repo = Repository(DATABASE_URL, entity)
    app.register_blueprint(make_crud(entity, repo))

# Доступно во всех шаблонах: список сущностей (для меню) и функция показа значения
app.jinja_env.globals["entities"] = ENTITIES
app.jinja_env.globals["display"] = display


@app.get("/")
def home():
    return redirect(url_for("vehicles.index"))


if __name__ == "__main__":
    app.run(debug=True)
