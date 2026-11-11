"""
Черновики в сессии.

Данные хранятся в памяти сервера, в словаре DRAFTS.
У пользователя в cookie лежит только номер его сессии (sid),
по которому сервер находит его черновики.

При перезапуске сервера словарь очищается — это данные в памяти, а не в базе.
"""
from uuid import uuid4

from flask import session

# {номер_сессии: {имя_сущности: данные_формы}}
DRAFTS = {}


def _session_id():
    """Номер сессии текущего пользователя; при первом обращении создаётся."""
    if "sid" not in session:
        session["sid"] = uuid4().hex
    return session["sid"]


def save_draft(entity_name, values):
    """Положить черновик в сессию."""
    DRAFTS.setdefault(_session_id(), {})[entity_name] = values


def get_draft(entity_name):
    """Достать черновик из сессии (или None, если его нет)."""
    return DRAFTS.get(_session_id(), {}).get(entity_name)


def delete_draft(entity_name):
    """Удалить черновик из сессии."""
    DRAFTS.get(_session_id(), {}).pop(entity_name, None)
