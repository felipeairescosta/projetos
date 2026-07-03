from uuid import UUID

from fastapi import APIRouter, Depends
from supabase import Client

from .. import crud, schemas
from ..deps import get_current_user, get_supabase

router = APIRouter(prefix="/cargos", tags=["Cargos"], dependencies=[Depends(get_current_user)])

TABLE = "cargos"


@router.get("", response_model=list[schemas.Cargo])
def listar_cargos(client: Client = Depends(get_supabase)):
    return crud.list_rows(client, TABLE, order_by="nome")


@router.post("", response_model=schemas.Cargo, status_code=201)
def criar_cargo(payload: schemas.CargoCreate, client: Client = Depends(get_supabase)):
    return crud.create_row(client, TABLE, payload.model_dump(mode="json"))


@router.delete("/{cargo_id}", status_code=204)
def remover_cargo(cargo_id: UUID, client: Client = Depends(get_supabase)):
    crud.delete_row(client, TABLE, str(cargo_id))
