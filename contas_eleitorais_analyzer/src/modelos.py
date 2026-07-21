"""
Modelos de dados para a prestação de contas eleitorais.

Representa a estrutura mínima necessária para aplicar as regras da
Resolução TSE nº 23.607/2019 (arrecadação e aplicação de recursos e
prestação de contas de campanhas eleitorais) sobre um conjunto de
receitas e despesas de um candidato ou comitê financeiro.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum


class TipoDoador(str, Enum):
    PESSOA_FISICA = "PESSOA_FISICA"
    PESSOA_JURIDICA = "PESSOA_JURIDICA"
    PARTIDO = "PARTIDO"
    FUNDO_PARTIDARIO = "FUNDO_PARTIDARIO"
    FUNDO_ELEITORAL = "FUNDO_ELEITORAL"  # FEFC
    RECURSOS_PROPRIOS = "RECURSOS_PROPRIOS"
    OUTRO_CANDIDATO = "OUTRO_CANDIDATO"
    ENTE_PUBLICO = "ENTE_PUBLICO"
    ENTIDADE_ESTRANGEIRA = "ENTIDADE_ESTRANGEIRA"
    ENTIDADE_CLASSE_SINDICATO = "ENTIDADE_CLASSE_SINDICATO"
    ENTIDADE_BENEFICENTE_RELIGIOSA = "ENTIDADE_BENEFICENTE_RELIGIOSA"
    ORIGEM_NAO_IDENTIFICADA = "ORIGEM_NAO_IDENTIFICADA"


class FormaArrecadacao(str, Enum):
    TRANSFERENCIA_ELETRONICA = "TRANSFERENCIA_ELETRONICA"
    CHEQUE_NOMINAL = "CHEQUE_NOMINAL"
    CARTAO_CREDITO = "CARTAO_CREDITO"
    FINANCIAMENTO_COLETIVO = "FINANCIAMENTO_COLETIVO"
    ESPECIE = "ESPECIE"
    BENS_SERVICOS_ESTIMAVEIS = "BENS_SERVICOS_ESTIMAVEIS"


class Cargo(str, Enum):
    PREFEITO = "PREFEITO"
    VICE_PREFEITO = "VICE_PREFEITO"
    VEREADOR = "VEREADOR"
    GOVERNADOR = "GOVERNADOR"
    VICE_GOVERNADOR = "VICE_GOVERNADOR"
    SENADOR = "SENADOR"
    DEPUTADO_FEDERAL = "DEPUTADO_FEDERAL"
    DEPUTADO_ESTADUAL = "DEPUTADO_ESTADUAL"
    PRESIDENTE = "PRESIDENTE"
    VICE_PRESIDENTE = "VICE_PRESIDENTE"


@dataclass
class Doador:
    nome: str
    cpf_cnpj: str
    tipo: TipoDoador
    rendimento_bruto_ano_anterior: Decimal | None = None  # exigido só para PF


@dataclass
class Receita:
    id: str
    data: date
    valor: Decimal
    doador: Doador
    forma_arrecadacao: FormaArrecadacao
    tem_recibo_eleitoral: bool = True
    descricao: str = ""


@dataclass
class Despesa:
    id: str
    data: date
    valor: Decimal
    fornecedor_nome: str
    fornecedor_cpf_cnpj: str
    categoria: str
    tem_documento_fiscal: bool = True
    forma_pagamento: FormaArrecadacao = FormaArrecadacao.TRANSFERENCIA_ELETRONICA
    descricao: str = ""


@dataclass
class CandidatoOuComite:
    nome: str
    numero_ou_identificacao: str
    cargo: Cargo
    uf: str
    municipio: str
    cnpj_especifico: str | None = None
    possui_conta_bancaria_especifica: bool = False
    teto_gastos_campanha: Decimal | None = None  # limite fixado p/ o cargo/UF


@dataclass
class PrestacaoContas:
    candidato_ou_comite: CandidatoOuComite
    data_eleicao: date
    data_apresentacao: date | None
    receitas: list[Receita] = field(default_factory=list)
    despesas: list[Despesa] = field(default_factory=list)

    @property
    def total_receitas(self) -> Decimal:
        return sum((r.valor for r in self.receitas), Decimal("0"))

    @property
    def total_despesas(self) -> Decimal:
        return sum((d.valor for d in self.despesas), Decimal("0"))
