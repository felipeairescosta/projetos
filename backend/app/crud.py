from typing import Any

from fastapi import HTTPException, status
from postgrest.exceptions import APIError
from supabase import Client


def _handle_error(exc: APIError) -> None:
    detail = exc.message or "Erro ao acessar o banco de dados."
    code = status.HTTP_400_BAD_REQUEST
    if exc.code == "23505":
        detail = "Já existe um registro com esses dados (violação de unicidade)."
    elif exc.code == "PGRST116":
        code = status.HTTP_404_NOT_FOUND
        detail = "Registro não encontrado."
    raise HTTPException(status_code=code, detail=detail) from exc


def list_rows(
    client: Client,
    table: str,
    select: str = "*",
    order_by: str | None = None,
    filters: dict[str, Any] | None = None,
) -> list[dict]:
    try:
        query = client.table(table).select(select)
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        if order_by:
            query = query.order(order_by)
        return query.execute().data
    except APIError as exc:
        _handle_error(exc)


def get_row(client: Client, table: str, row_id: str, select: str = "*") -> dict:
    try:
        result = client.table(table).select(select).eq("id", row_id).single().execute()
        return result.data
    except APIError as exc:
        _handle_error(exc)


def create_row(client: Client, table: str, payload: dict) -> dict:
    try:
        result = client.table(table).insert(payload).execute()
        return result.data[0]
    except APIError as exc:
        _handle_error(exc)


def update_row(client: Client, table: str, row_id: str, payload: dict) -> dict:
    payload = {k: v for k, v in payload.items() if v is not None}
    try:
        result = client.table(table).update(payload).eq("id", row_id).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado.")
        return result.data[0]
    except APIError as exc:
        _handle_error(exc)


def delete_row(client: Client, table: str, row_id: str) -> None:
    try:
        result = client.table(table).delete().eq("id", row_id).execute()
        if not result.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado.")
    except APIError as exc:
        _handle_error(exc)
