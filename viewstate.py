"""

Данные страницы сериализуются в строку и кладутся в скрытое поле формы
__VIEWSTATE. Поле уезжает на клиент вместе со страницей и возвращается
на сервер при отправке формы, где строка разбирается обратно в объект.
Сервер между запросами ничего не хранит: ни в памяти, ни в сессии, ни в базе.

Строка = JSON -> base64 + подпись секретным ключом приложения.
Подпись нужна, потому что скрытое поле видно в коде страницы и его можно
изменить. Без подписи пользователь мог бы подсунуть любые данные.
В ASP.NET это называется ViewState MAC.
"""
from flask import abort, current_app
from itsdangerous import BadSignature, URLSafeSerializer

FIELD_NAME = "__VIEWSTATE"


def _serializer():
    # salt отделяет подписи ViewState от подписей cookie сессии
    return URLSafeSerializer(current_app.secret_key, salt="viewstate")


def dump(data):
    """Объект -> строка для скрытого поля (сериализация)."""
    return _serializer().dumps(data)


def load(form):
    """Строка из скрытого поля -> объект (десериализация).
    Если поле подменили, подпись не сойдётся и запрос будет отклонён."""
    try:
        return _serializer().loads(form.get(FIELD_NAME, ""))
    except BadSignature:
        abort(400, description="ViewState повреждён или подменён.")
