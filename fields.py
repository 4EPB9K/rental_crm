"""
Универсальное описание сущностей и проверка данных формы.

Каждая сущность (транспорт, клиенты, ...) описывается объектом Entity
со списком полей Field. По этому описанию строятся таблица списка,
форма, проверка данных и SQL-запросы. Код под конкретную сущность писать не нужно.
"""
import re
from dataclasses import dataclass, field as dc_field
from typing import Callable


@dataclass
class Field:
    name: str                       # имя колонки в БД и поля в форме
    label: str                      # подпись для пользователя
    kind: str = "text"              # text | number | select
    required: bool = True
    default: object = ""            # значение в пустой форме
    choices: dict | None = None     # для select: {ключ: подпись}
    min: int | None = None          # для number
    max: int | None = None
    max_length: int | None = None   # для text
    pattern: str | None = None      # регулярное выражение для text
    pattern_error: str = "Неверный формат."
    uppercase: bool = False         # привести к верхнему регистру
    unique: bool = False            # значение не должно повторяться
    hint: str = ""                  # подсказка под полем
    badge: bool = False             # показать в списке цветной плашкой


@dataclass
class Entity:
    name: str                       # имя таблицы в БД и часть адреса: /vehicles/
    title: str                      # заголовок списка: «Парк транспорта»
    add_title: str                  # заголовок формы добавления
    edit_title: str                 # заголовок формы редактирования
    empty_text: str                 # текст для пустого списка
    fields: list[Field]
    order_by: str = "id"            # сортировка списка
    # Дополнительные правила конкретной сущности: функция(values, errors)
    extra_check: Callable | None = dc_field(default=None)

    def column_names(self):
        return [f.name for f in self.fields]

    def empty_values(self):
        return {f.name: f.default for f in self.fields}


def display(f, value):
    """Как показать значение поля в списке."""
    if value is None or value == "":
        return "—"
    if f.kind == "select":
        return f.choices.get(value, value)
    return value


def _range_text(f):
    if f.min is not None and f.max is not None:
        return f" от {f.min} до {f.max}"
    if f.min is not None:
        return f" не меньше {f.min}"
    return ""


def validate(entity, form, repo, current_id=None):
    """
    Проверяет данные формы по описанию полей сущности.
    Возвращает (values, errors): значения и словарь {поле: текст ошибки}.
    """
    values, errors = {}, {}

    for f in entity.fields:
        raw = form.get(f.name, "").strip()
        if f.uppercase:
            raw = raw.upper()

        # Пустое значение
        if raw == "":
            values[f.name] = None
            if f.required:
                errors[f.name] = "Выберите значение." if f.kind == "select" else "Обязательное поле."
            continue

        values[f.name] = raw

        if f.kind == "number":
            try:
                number = int(raw)
            except ValueError:
                errors[f.name] = "Введите целое число" + _range_text(f) + "."
                continue
            if (f.min is not None and number < f.min) or (f.max is not None and number > f.max):
                errors[f.name] = "Введите целое число" + _range_text(f) + "."
                continue
            values[f.name] = number

        elif f.kind == "select":
            if raw not in f.choices:
                errors[f.name] = "Выберите значение из списка."
                continue

        else:  # text
            if f.max_length and len(raw) > f.max_length:
                errors[f.name] = f"Не больше {f.max_length} символов."
                continue
            if f.pattern and not re.match(f.pattern, raw):
                errors[f.name] = f.pattern_error
                continue

        # Уникальность проверяем в базе; свою же запись при редактировании не считаем
        if f.unique:
            same = repo.find_by(f.name, values[f.name])
            if same and same["id"] != current_id:
                errors[f.name] = f"Запись с таким значением поля «{f.label}» уже есть."

    # Особые правила конкретной сущности
    if entity.extra_check:
        entity.extra_check(values, errors)

    return values, errors
