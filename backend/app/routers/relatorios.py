from collections import Counter
from datetime import date

from fastapi import APIRouter, Depends
from supabase import Client

from ..deps import get_current_user, get_supabase

router = APIRouter(prefix="/relatorios", tags=["Relatórios"], dependencies=[Depends(get_current_user)])


@router.get("/resumo")
def resumo_geral(client: Client = Depends(get_supabase)):
    hoje = date.today().isoformat()

    colaboradores = client.table("colaboradores").select("id,status").execute().data
    zonas = client.table("zonas_eleitorais").select("id").execute().data
    afastamentos_hoje = (
        client.table("afastamentos")
        .select("id")
        .lte("data_inicio", hoje)
        .gte("data_fim", hoje)
        .neq("status", "cancelado")
        .execute()
        .data
    )
    escalas_hoje = client.table("escalas").select("id").eq("data", hoje).execute().data

    status_counter = Counter(c["status"] for c in colaboradores)

    return {
        "total_colaboradores": len(colaboradores),
        "colaboradores_ativos": status_counter.get("ativo", 0),
        "colaboradores_inativos": status_counter.get("inativo", 0),
        "colaboradores_afastados": status_counter.get("afastado", 0),
        "total_zonas_eleitorais": len(zonas),
        "afastamentos_em_andamento_hoje": len(afastamentos_hoje),
        "escalas_hoje": len(escalas_hoje),
    }


@router.get("/quadro-por-zona")
def quadro_por_zona(client: Client = Depends(get_supabase)):
    colaboradores = (
        client.table("colaboradores")
        .select("status, zona_eleitoral:zonas_eleitorais(id,numero_zona,nome,municipio)")
        .execute()
        .data
    )
    agregados: dict[str, dict] = {}
    for c in colaboradores:
        zona = c.get("zona_eleitoral")
        chave = zona["id"] if zona else "sem_zona"
        nome = f"Zona {zona['numero_zona']} - {zona['nome']}" if zona else "Sem lotação definida"
        if chave not in agregados:
            agregados[chave] = {"zona": nome, "total": 0, "ativos": 0}
        agregados[chave]["total"] += 1
        if c["status"] == "ativo":
            agregados[chave]["ativos"] += 1
    return sorted(agregados.values(), key=lambda x: x["zona"])


@router.get("/quadro-por-cargo")
def quadro_por_cargo(client: Client = Depends(get_supabase)):
    colaboradores = (
        client.table("colaboradores").select("status, cargo:cargos(id,nome)").execute().data
    )
    agregados: dict[str, dict] = {}
    for c in colaboradores:
        cargo = c.get("cargo")
        chave = cargo["id"] if cargo else "sem_cargo"
        nome = cargo["nome"] if cargo else "Sem cargo definido"
        if chave not in agregados:
            agregados[chave] = {"cargo": nome, "total": 0, "ativos": 0}
        agregados[chave]["total"] += 1
        if c["status"] == "ativo":
            agregados[chave]["ativos"] += 1
    return sorted(agregados.values(), key=lambda x: -x["total"])


@router.get("/quadro-por-vinculo")
def quadro_por_vinculo(client: Client = Depends(get_supabase)):
    colaboradores = client.table("colaboradores").select("vinculo").execute().data
    contagem = Counter(c["vinculo"] for c in colaboradores)
    return [{"vinculo": vinculo, "total": total} for vinculo, total in contagem.items()]


@router.get("/afastamentos-por-tipo")
def afastamentos_por_tipo(client: Client = Depends(get_supabase)):
    afastamentos = client.table("afastamentos").select("tipo").execute().data
    contagem = Counter(a["tipo"] for a in afastamentos)
    return [{"tipo": tipo, "total": total} for tipo, total in contagem.items()]
