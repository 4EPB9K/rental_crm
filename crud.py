"""
Универсальные маршруты CRUD.

make_crud(entity, repo) создаёт набор маршрутов (Blueprint) для любой сущности:
  GET  /<имя>/                  — список
  GET  /<имя>/new               — форма добавления
  POST /<имя>/                  — сохранение новой записи
  GET  /<имя>/<id>/edit         — форма редактирования
  POST /<имя>/<id>              — проверка изменений, страница подтверждения
  POST /<имя>/<id>/confirm      — подтверждение или возврат к редактированию
  POST /<имя>/<id>/delete       — удаление
  POST /<имя>/draft/delete      — удаление черновика из сессии
"""
import json

from flask import Blueprint, abort, redirect, render_template, request, url_for

import viewstate
from drafts import delete_draft, get_draft, save_draft
from fields import display, validate


def make_crud(entity, repo):
    bp = Blueprint(entity.name, __name__, url_prefix=f"/{entity.name}")

    def show_form(values, errors, item_id=None, from_draft=False, state=None):
        if item_id is None:
            heading, action = entity.add_title, url_for(".create")
        else:
            heading, action = entity.edit_title, url_for(".update", item_id=item_id)
        return render_template("form.html", entity=entity, v=values, errors=errors,
                               heading=heading, action=action,
                               is_new=item_id is None, from_draft=from_draft,
                               viewstate=viewstate.dump(state) if state else None)

    # ---------- READ ----------
    @bp.get("/")
    def index():
        return render_template("list.html", entity=entity, rows=repo.list(),
                               has_draft=get_draft(entity.name) is not None)

    # ---------- CREATE ----------
    @bp.get("/new")
    def new():
        draft = get_draft(entity.name)
        if draft:
            return show_form(draft, {}, from_draft=True)   # поднимаем черновик из сессии
        return show_form(entity.empty_values(), {})

    @bp.post("/")
    def create():
        # Нажата кнопка «Сохранить черновик»: кладём форму в сессию без проверки
        if request.form.get("action") == "draft":
            values = {f.name: request.form.get(f.name, "") for f in entity.fields}
            save_draft(entity.name, values)
            return redirect(url_for(".index"))

        values, errors = validate(entity, request.form, repo)
        if errors:
            return show_form(values, errors)
        repo.add(values)
        delete_draft(entity.name)               # запись в базе — черновик больше не нужен
        return redirect(url_for(".index"))      # Post/Redirect/Get

    # ---------- UPDATE (с ViewState) ----------
    def without_id(row):
        return {f.name: row[f.name] for f in entity.fields}

    def changes(original, new):
        """Список изменённых полей: (подпись, было, стало)."""
        return [(f.label, display(f, original[f.name]), display(f, new[f.name]))
                for f in entity.fields if original[f.name] != new[f.name]]

    @bp.get("/<int:item_id>/edit")
    def edit(item_id):
        row = repo.get(item_id)
        if row is None:
            abort(404)
        # Исходную версию записи кладём в ViewState страницы
        state = {"id": item_id, "original": without_id(row)}
        return show_form(row, {}, item_id, state=state)

    @bp.post("/<int:item_id>")
    def update(item_id):
        state = viewstate.load(request.form)          # разбираем ViewState из скрытого поля
        if state["id"] != item_id:
            abort(400)

        values, errors = validate(entity, request.form, repo, current_id=item_id)
        if errors:
            return show_form(values, errors, item_id, state=state)

        diff = changes(state["original"], values)
        if not diff:
            return redirect(url_for(".index"))         # ничего не поменяли — сохранять нечего

        # В базу пока не пишем. Теперь во ViewState едут обе версии: исходная и новая
        state["new"] = values
        return render_template("confirm.html", entity=entity, item_id=item_id,
                               diff=diff, viewstate=viewstate.dump(state),
                               state_json=json.dumps(state, ensure_ascii=False, indent=2))

    @bp.post("/<int:item_id>/confirm")
    def confirm(item_id):
        state = viewstate.load(request.form)
        if state["id"] != item_id or "new" not in state:
            abort(400)

        # «Вернуться к редактированию»: поднимаем данные из ViewState и продолжаем
        if request.form.get("action") == "back":
            back_state = {"id": item_id, "original": state["original"]}
            return show_form(state["new"], {}, item_id, state=back_state)

        # «Подтвердить»: новая версия уже проверена на прошлом шаге,
        # а подпись гарантирует, что её не изменили на клиенте
        if repo.get(item_id) is None:
            abort(404)
        repo.update(item_id, state["new"])
        return redirect(url_for(".index"))

    # ---------- DELETE ----------
    @bp.post("/<int:item_id>/delete")
    def delete(item_id):
        repo.delete(item_id)
        return redirect(url_for(".index"))

    # ---------- ЧЕРНОВИК ----------
    @bp.post("/draft/delete")
    def draft_delete():
        delete_draft(entity.name)
        return redirect(url_for(".index"))

    return bp
