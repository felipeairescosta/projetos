from uuid import UUID

from fastapi import APIRouter, Depends, Query
from supabase import Client

from .. import crud, schemas
from ..deps import get_current_user, get_supabase

router = APIRouter(prefix="/colaboradores", tags=["Colaboradores"], dependencies=[Depends(get_current_user)])

TABLE = "colaboradores"
SELECT_COM_RELACOES = "*, cargo:cargos(id,nome), zona_eleitoral:zonas_eleitorais(id,numero_zona,nome,municipio)"


@router.get("")
def listar_colaboradores(
    client: Client = Depends(get_supabase),
    status: schemas.ColaboradorStatus | None = None,
    zona_eleitoral_id: UUID | None = None,
    cargo_id: UUID | None = None,
):
    query = client.table(TABLE).select(SELECT_COM_RELACOES).order("nome_completo")
    if status is not None:
        query = query.eq("status", status.value)
    if zona_eleitoral_id is not None:
        query = query.eq("zona_eleitoral_id", str(zona_eleitoral_id))
    if cargo_id is not None:
        query = query.eq("cargo_id", str(cargo_id))
    return query.execute().data


@router.post("", response_model=schemas.Colaborador, status_code=201)
def criar_colaborador(payload: schemas.ColaboradorCreate, client: Client = Depends(get_supabase)):
    data = payload.model_dump(mode="json")
    return crud.create_row(client, TABLE, data)


@router.get("/{colaborador_id}")
def obter_colaborador(colaborador_id: UUID, client: Client = Depends(get_supabase)):
    return crud.get_row(client, TABLE, str(colaborador_id), select=SELECT_COM_RELACOES)


@router.patch("/{colaborador_id}", response_model=schemas.Colaborador)
def atualizar_colaborador(
    colaborador_id: UUID, payload: schemas.ColaboradorUpdate, client: Client = Depends(get_supabase)
):
    data = payload.model_dump(mode="json", exclude_unset=True)
    return crud.update_row(client, TABLE, str(colaborador_id), data)


@router.delete("/{colaborador_id}", status_code=204)
def remover_colaborador(colaborador_id: UUID, client: Client = Depends(get_supabase)):
    crud.delete_row(client, TABLE, str(colaborador_id))
