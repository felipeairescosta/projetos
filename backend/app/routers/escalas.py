from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase import Client

from .. import crud, schemas
from ..deps import get_current_user, get_supabase

router = APIRouter(prefix="/escalas", tags=["Escalas"], dependencies=[Depends(get_current_user)])

TABLE = "escalas"
SELECT_COM_RELACOES = (
    "*, colaborador:colaboradores(id,nome_completo), zona_eleitoral:zonas_eleitorais(id,numero_zona,nome)"
)


@router.get("")
def listar_escalas(
    client: Client = Depends(get_supabase),
    data_inicio: date | None = None,
    data_fim: date | None = None,
    zona_eleitoral_id: UUID | None = None,
    colaborador_id: UUID | None = None,
):
    query = client.table(TABLE).select(SELECT_COM_RELACOES).order("data")
    if data_inicio is not None:
        query = query.gte("data", data_inicio.isoformat())
    if data_fim is not None:
        query = query.lte("data", data_fim.isoformat())
    if zona_eleitoral_id is not None:
        query = query.eq("zona_eleitoral_id", str(zona_eleitoral_id))
    if colaborador_id is not None:
        query = query.eq("colaborador_id", str(colaborador_id))
    return query.execute().data


@router.post("", response_model=schemas.Escala, status_code=201)
def criar_escala(payload: schemas.EscalaCreate, client: Client = Depends(get_supabase)):
    data = payload.model_dump(mode="json")
    return crud.create_row(client, TABLE, data)


@router.patch("/{escala_id}", response_model=schemas.Escala)
def atualizar_escala(escala_id: UUID, payload: schemas.EscalaUpdate, client: Client = Depends(get_supabase)):
    data = payload.model_dump(mode="json", exclude_unset=True)
    return crud.update_row(client, TABLE, str(escala_id), data)


@router.delete("/{escala_id}", status_code=204)
def remover_escala(escala_id: UUID, client: Client = Depends(get_supabase)):
    crud.delete_row(client, TABLE, str(escala_id))
