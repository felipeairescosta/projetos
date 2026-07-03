from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase import Client

from .. import crud, schemas
from ..deps import get_current_user, get_supabase

router = APIRouter(prefix="/afastamentos", tags=["Afastamentos"], dependencies=[Depends(get_current_user)])

TABLE = "afastamentos"
SELECT_COM_RELACOES = "*, colaborador:colaboradores(id,nome_completo,zona_eleitoral_id)"


@router.get("")
def listar_afastamentos(
    client: Client = Depends(get_supabase),
    status: schemas.AfastamentoStatus | None = None,
    colaborador_id: UUID | None = None,
    ativos_em: date | None = None,
):
    query = client.table(TABLE).select(SELECT_COM_RELACOES).order("data_inicio", desc=True)
    if status is not None:
        query = query.eq("status", status.value)
    if colaborador_id is not None:
        query = query.eq("colaborador_id", str(colaborador_id))
    if ativos_em is not None:
        query = query.lte("data_inicio", ativos_em.isoformat()).gte("data_fim", ativos_em.isoformat())
    return query.execute().data


@router.post("", response_model=schemas.Afastamento, status_code=201)
def criar_afastamento(payload: schemas.AfastamentoCreate, client: Client = Depends(get_supabase)):
    data = payload.model_dump(mode="json")
    return crud.create_row(client, TABLE, data)


@router.patch("/{afastamento_id}", response_model=schemas.Afastamento)
def atualizar_afastamento(
    afastamento_id: UUID, payload: schemas.AfastamentoUpdate, client: Client = Depends(get_supabase)
):
    data = payload.model_dump(mode="json", exclude_unset=True)
    return crud.update_row(client, TABLE, str(afastamento_id), data)


@router.delete("/{afastamento_id}", status_code=204)
def remover_afastamento(afastamento_id: UUID, client: Client = Depends(get_supabase)):
    crud.delete_row(client, TABLE, str(afastamento_id))
