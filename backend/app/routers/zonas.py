from uuid import UUID

from fastapi import APIRouter, Depends
from supabase import Client

from .. import crud, schemas
from ..deps import get_current_user, get_supabase

router = APIRouter(prefix="/zonas", tags=["Zonas Eleitorais"], dependencies=[Depends(get_current_user)])

TABLE = "zonas_eleitorais"


@router.get("", response_model=list[schemas.ZonaEleitoral])
def listar_zonas(client: Client = Depends(get_supabase)):
    return crud.list_rows(client, TABLE, order_by="numero_zona")


@router.post("", response_model=schemas.ZonaEleitoral, status_code=201)
def criar_zona(payload: schemas.ZonaEleitoralCreate, client: Client = Depends(get_supabase)):
    data = payload.model_dump(mode="json")
    return crud.create_row(client, TABLE, data)


@router.get("/{zona_id}", response_model=schemas.ZonaEleitoral)
def obter_zona(zona_id: UUID, client: Client = Depends(get_supabase)):
    return crud.get_row(client, TABLE, str(zona_id))


@router.patch("/{zona_id}", response_model=schemas.ZonaEleitoral)
def atualizar_zona(zona_id: UUID, payload: schemas.ZonaEleitoralUpdate, client: Client = Depends(get_supabase)):
    data = payload.model_dump(mode="json", exclude_unset=True)
    return crud.update_row(client, TABLE, str(zona_id), data)


@router.delete("/{zona_id}", status_code=204)
def remover_zona(zona_id: UUID, client: Client = Depends(get_supabase)):
    crud.delete_row(client, TABLE, str(zona_id))
