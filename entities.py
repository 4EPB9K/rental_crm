"""
Описания сущностей CRM.
Чтобы добавить новую сущность: описать её здесь, добавить таблицу в schema.sql
и вписать в список ENTITIES. Шаблоны и маршруты писать не нужно.
"""
from fields import Entity, Field

# ---------------- Транспорт ----------------
VEHICLE_TYPES = {
    "bike": "Велосипед",
    "ebike": "Электровелосипед",
    "kickscooter": "Самокат",
    "escooter": "Электросамокат",
}
ELECTRIC_TYPES = {"ebike", "escooter"}

STATUSES = {
    "available": "Свободен",
    "rented": "В аренде",
    "service": "На обслуживании",
    "retired": "Списан",
}


def check_vehicle(values, errors):
    """Заряд обязателен только для электротранспорта, у остальных его нет."""
    if values.get("type") in ELECTRIC_TYPES:
        if values.get("battery") is None and "battery" not in errors:
            errors["battery"] = "Для электротранспорта укажите заряд."
    else:
        values["battery"] = None
        errors.pop("battery", None)


VEHICLES = Entity(
    name="vehicles",
    title="Парк транспорта",
    add_title="Новый транспорт",
    edit_title="Редактирование транспорта",
    empty_text="В парке пока нет транспорта.",
    order_by="inventory_no",
    extra_check=check_vehicle,
    fields=[
        Field("inventory_no", "Инвентарный номер", max_length=20, uppercase=True, unique=True,
              pattern=r"^[A-Z0-9-]{3,20}$",
              pattern_error="Латинские буквы, цифры и дефис, от 3 до 20 символов.",
              hint="Например: ES-0012"),
        Field("type", "Тип", kind="select", choices=VEHICLE_TYPES, default="escooter"),
        Field("model", "Модель", max_length=100),
        Field("status", "Статус", kind="select", choices=STATUSES, default="available", badge=True),
        Field("price_per_hour", "Тариф, ₽/ч", kind="number", min=1),
        Field("battery", "Заряд, %", kind="number", min=0, max=100, required=False,
              hint="Только для электротранспорта"),
        Field("station", "Точка проката", max_length=200),
    ],
)

# ---------------- Клиенты ----------------
CLIENTS = Entity(
    name="clients",
    title="Клиенты",
    add_title="Новый клиент",
    edit_title="Редактирование клиента",
    empty_text="Клиентов пока нет.",
    order_by="full_name",
    fields=[
        Field("full_name", "ФИО", max_length=150),
        Field("phone", "Телефон", unique=True, max_length=20,
              pattern=r"^\+?[0-9 ()-]{10,20}$",
              pattern_error="Цифры, пробелы, скобки и дефис, от 10 символов.",
              hint="Например: +7 900 123-45-67"),
        Field("email", "Email", required=False, max_length=100,
              pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", pattern_error="Неверный email."),
        Field("license_no", "Водительское удостоверение", required=False, max_length=20),
    ],
)

STATIONS = Entity(
    name="stations",
    title="Точки проката",
    add_title="Новая точка",
    edit_title="Редактирование точки",
    empty_text="Точек проката пока нет.",
    order_by="name",
    fields=[
        Field("name", "Название", max_length=100, unique=True),
        Field("address", "Адрес", max_length=200),
        Field("capacity", "Мест для транспорта", kind="number", min=1, max=500),
    ],
)


# Все сущности приложения: по этому списку регистрируются маршруты и меню
ENTITIES = [VEHICLES, CLIENTS, STATIONS]
