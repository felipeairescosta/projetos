"""Carrega uma PrestacaoContas a partir de um JSON estruturado.

Este é o formato "canônico" de entrada do analisador — tanto os dados de
exemplo (`dados_exemplo/`) quanto qualquer extração feita a partir dos
documentos do PJe (ver `pdf_loader.py`) devem, no fim, produzir um dicionário
neste formato antes de virar uma `PrestacaoContas`.

Ver `dados_exemplo/exemplo_prestacao.json` para um exemplo completo.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from ..modelos import (
    CandidatoOuComite,
    Cargo,
    Despesa,
    Doador,
    FormaArrecadacao,
    PrestacaoContas,
    Receita,
    TipoDoador,
)


def _parse_data(valor: str | None) -> date | None:
    if not valor:
        return None
    return date.fromisoformat(valor)


def _parse_doador(dados: dict[str, Any]) -> Doador:
    rendimento = dados.get("rendimento_bruto_ano_anterior")
    return Doador(
        nome=dados["nome"],
        cpf_cnpj=dados["cpf_cnpj"],
        tipo=TipoDoador(dados["tipo"]),
        rendimento_bruto_ano_anterior=Decimal(str(rendimento)) if rendimento is not None else None,
    )


def _parse_receita(dados: dict[str, Any]) -> Receita:
    return Receita(
        id=dados["id"],
        data=_parse_data(dados["data"]),
        valor=Decimal(str(dados["valor"])),
        doador=_parse_doador(dados["doador"]),
        forma_arrecadacao=FormaArrecadacao(dados["forma_arrecadacao"]),
        tem_recibo_eleitoral=dados.get("tem_recibo_eleitoral", True),
        descricao=dados.get("descricao", ""),
    )


def _parse_despesa(dados: dict[str, Any]) -> Despesa:
    return Despesa(
        id=dados["id"],
        data=_parse_data(dados["data"]),
        valor=Decimal(str(dados["valor"])),
        fornecedor_nome=dados["fornecedor_nome"],
        fornecedor_cpf_cnpj=dados["fornecedor_cpf_cnpj"],
        categoria=dados["categoria"],
        tem_documento_fiscal=dados.get("tem_documento_fiscal", True),
        forma_pagamento=FormaArrecadacao(dados.get("forma_pagamento", "TRANSFERENCIA_ELETRONICA")),
        descricao=dados.get("descricao", ""),
    )


def carregar_prestacao_de_dict(dados: dict[str, Any]) -> PrestacaoContas:
    cand_dados = dados["candidato_ou_comite"]
    teto = cand_dados.get("teto_gastos_campanha")
    candidato = CandidatoOuComite(
        nome=cand_dados["nome"],
        numero_ou_identificacao=cand_dados["numero_ou_identificacao"],
        cargo=Cargo(cand_dados["cargo"]),
        uf=cand_dados["uf"],
        municipio=cand_dados["municipio"],
        cnpj_especifico=cand_dados.get("cnpj_especifico"),
        possui_conta_bancaria_especifica=cand_dados.get("possui_conta_bancaria_especifica", False),
        teto_gastos_campanha=Decimal(str(teto)) if teto is not None else None,
    )
    return PrestacaoContas(
        candidato_ou_comite=candidato,
        data_eleicao=_parse_data(dados["data_eleicao"]),
        data_apresentacao=_parse_data(dados.get("data_apresentacao")),
        receitas=[_parse_receita(r) for r in dados.get("receitas", [])],
        despesas=[_parse_despesa(d) for d in dados.get("despesas", [])],
        houve_segundo_turno=dados.get("houve_segundo_turno", False),
    )


def carregar_prestacao_de_json(caminho: str | Path) -> PrestacaoContas:
    caminho = Path(caminho)
    with caminho.open(encoding="utf-8") as f:
        dados = json.load(f)
    return carregar_prestacao_de_dict(dados)
