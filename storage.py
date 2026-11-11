"""
Универсальное хранилище (паттерн «Репозиторий») для PostgreSQL.

Один класс работает с любой сущностью: имя таблицы и колонки
берутся из описания Entity, SQL-запросы собираются из них.
"""
import psycopg
from psycopg.rows import dict_row


def create_schema(database_url, schema_path):
    """Создаёт таблицы по файлу schema.sql, если их ещё нет."""
    with psycopg.connect(database_url) as conn:
        conn.execute(schema_path.read_text(encoding="utf-8"))


class Repository:
    def __init__(self, database_url, entity):
        self.database_url = database_url
        self.table = entity.name
        self.columns = entity.column_names()
        self.order_by = entity.order_by

    def _connect(self):
        # dict_row: строки приходят словарями {"model": "...", ...}
        return psycopg.connect(self.database_url, row_factory=dict_row)

    # Имена таблиц и колонок берутся из нашего описания сущностей, а не от
    # пользователя, поэтому их можно вставлять в текст запроса.
    # Значения из формы передаются только через %s / %(name)s — это защита от SQL-инъекций.

    def list(self):
        columns = ", ".join(["id"] + self.columns)
        with self._connect() as conn:
            return conn.execute(
                f"SELECT {columns} FROM {self.table} ORDER BY {self.order_by}"
            ).fetchall()

    def get(self, item_id):
        columns = ", ".join(["id"] + self.columns)
        with self._connect() as conn:
            return conn.execute(
                f"SELECT {columns} FROM {self.table} WHERE id = %s", (item_id,)
            ).fetchone()

    def find_by(self, column, value):
        with self._connect() as conn:
            return conn.execute(
                f"SELECT id FROM {self.table} WHERE {column} = %s", (value,)
            ).fetchone()

    def add(self, values):
        columns = ", ".join(self.columns)                              # model, status, ...
        placeholders = ", ".join(f"%({c})s" for c in self.columns)     # %(model)s, %(status)s, ...
        with self._connect() as conn:
            conn.execute(
                f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})", values
            )

    def update(self, item_id, values):
        assignments = ", ".join(f"{c} = %({c})s" for c in self.columns)  # model = %(model)s, ...
        with self._connect() as conn:
            conn.execute(
                f"UPDATE {self.table} SET {assignments} WHERE id = %(id)s",
                {**values, "id": item_id},
            )

    def delete(self, item_id):
        with self._connect() as conn:
            conn.execute(f"DELETE FROM {self.table} WHERE id = %s", (item_id,))
