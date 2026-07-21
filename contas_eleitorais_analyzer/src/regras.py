"""
Motor de regras — Resolução TSE nº 23.607/2019.

⚠️ AVISO IMPORTANTE
--------------------
Estas regras foram codificadas a partir do conhecimento geral do conteúdo da
Resolução TSE nº 23.607/2019 (arrecadação e aplicação de recursos e prestação
de contas de campanhas eleitorais). Não foi possível, neste ambiente, acessar
ao vivo o texto compilado publicado em tse.jus.br (bloqueio de rede) para
conferir a numeração exata dos artigos e valores vigentes na versão mais
atual (a resolução é republicada/atualizada a cada eleição, com anexos que
fixam tetos de gastos e outros parâmetros específicos do pleito).

Antes de usar este analisador para qualquer decisão real, um analista humano
deve confirmar cada `referencia_normativa` abaixo contra o texto compilado
vigente e ajustar os parâmetros marcados como PARAMETRIZÁVEL (limites,
prazos, valores) conforme o ato normativo da eleição em análise.

Cada função de regra recebe uma `PrestacaoContas` e devolve uma lista de
`Achado`. Para adicionar uma nova regra: escreva a função e registre-a em
`REGRAS_REGISTRADAS`, no fim deste arquivo.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from .achados import Achado, Severidade
from .modelos import FormaArrecadacao, PrestacaoContas, TipoDoador

# ---------------------------------------------------------------------------
# Parâmetros PARAMETRIZÁVEL — confirmar/ajustar por eleição
# ---------------------------------------------------------------------------
LIMITE_DOACAO_PF_PERC_RENDIMENTO = Decimal("0.10")  # 10% do rendimento bruto do ano anterior
PRAZO_APRESENTACAO_CONTAS_DIAS = 30  # até o 30º dia após a eleição

ORIGENS_SEMPRE_VEDADAS = {
    TipoDoador.ENTE_PUBLICO,
    TipoDoador.ENTIDADE_ESTRANGEIRA,
    TipoDoador.ENTIDADE_CLASSE_SINDICATO,
    TipoDoador.ENTIDADE_BENEFICENTE_RELIGIOSA,
    TipoDoador.ORIGEM_NAO_IDENTIFICADA,
}


def regra_doacao_pessoa_juridica(pc: PrestacaoContas) -> list[Achado]:
    """Doação de pessoa jurídica é vedada em campanhas eleitorais (Lei 9.504/97,
    art. 24, na redação vigente após a ADI 4.650/STF, reproduzida na resolução)."""
    achados = []
    for r in pc.receitas:
        if r.doador.tipo == TipoDoador.PESSOA_JURIDICA:
            achados.append(
                Achado(
                    severidade=Severidade.GRAVE,
                    regra="RES23607_DOACAO_PJ_VEDADA",
                    referencia_normativa="Lei 9.504/97, art. 24 (vedação a doações de PJ); Res.-TSE 23.607/2019",
                    titulo="Doação de pessoa jurídica",
                    descricao=(
                        f"Receita {r.id} no valor de R$ {r.valor} tem como doador "
                        f"'{r.doador.nome}' ({r.doador.cpf_cnpj}), classificado como pessoa "
                        "jurídica. Doações de PJ a campanhas são vedadas."
                    ),
                    item_relacionado_id=r.id,
                )
            )
    return achados


def regra_limite_doacao_pessoa_fisica(pc: PrestacaoContas) -> list[Achado]:
    """Doação de pessoa física não pode ultrapassar 10% dos rendimentos brutos
    auferidos pelo doador no ano anterior à eleição."""
    achados = []
    for r in pc.receitas:
        if r.doador.tipo != TipoDoador.PESSOA_FISICA:
            continue
        if r.doador.rendimento_bruto_ano_anterior is None:
            achados.append(
                Achado(
                    severidade=Severidade.ALERTA,
                    regra="RES23607_LIMITE_PF_SEM_DADO",
                    referencia_normativa="Res.-TSE 23.607/2019 (limite de doação de pessoa física)",
                    titulo="Rendimento do doador PF não informado",
                    descricao=(
                        f"Receita {r.id} (doador '{r.doador.nome}') não informa o "
                        "rendimento bruto do ano anterior; não é possível verificar "
                        "automaticamente o limite de 10%."
                    ),
                    item_relacionado_id=r.id,
                )
            )
            continue
        limite = r.doador.rendimento_bruto_ano_anterior * LIMITE_DOACAO_PF_PERC_RENDIMENTO
        if r.valor > limite:
            achados.append(
                Achado(
                    severidade=Severidade.IRREGULARIDADE,
                    regra="RES23607_LIMITE_PF_EXCEDIDO",
                    referencia_normativa="Res.-TSE 23.607/2019 (limite de doação de pessoa física a 10% do rendimento)",
                    titulo="Doação de pessoa física acima do limite legal",
                    descricao=(
                        f"Receita {r.id}: doação de R$ {r.valor} do doador '{r.doador.nome}' "
                        f"ultrapassa o limite de 10% do rendimento bruto informado "
                        f"(limite calculado: R$ {limite})."
                    ),
                    item_relacionado_id=r.id,
                )
            )
    return achados


def regra_origem_vedada(pc: PrestacaoContas) -> list[Achado]:
    """Recursos de origem não identificada ou de fontes vedadas (entes públicos,
    entidades estrangeiras, sindicatos/entidades de classe, entidades
    beneficentes/religiosas)."""
    achados = []
    for r in pc.receitas:
        if r.doador.tipo in ORIGENS_SEMPRE_VEDADAS:
            achados.append(
                Achado(
                    severidade=Severidade.GRAVE,
                    regra="RES23607_ORIGEM_VEDADA",
                    referencia_normativa="Res.-TSE 23.607/2019 (fontes de recursos vedadas)",
                    titulo="Recurso de origem vedada",
                    descricao=(
                        f"Receita {r.id} no valor de R$ {r.valor} tem origem classificada "
                        f"como '{r.doador.tipo.value}', que é fonte vedada de recursos de "
                        "campanha."
                    ),
                    item_relacionado_id=r.id,
                )
            )
    return achados


def regra_recibo_eleitoral_ausente(pc: PrestacaoContas) -> list[Achado]:
    """Toda receita deve estar amparada por recibo eleitoral (RECE) emitido pelo
    sistema de prestação de contas."""
    achados = []
    for r in pc.receitas:
        if not r.tem_recibo_eleitoral:
            achados.append(
                Achado(
                    severidade=Severidade.IRREGULARIDADE,
                    regra="RES23607_RECIBO_ELEITORAL_AUSENTE",
                    referencia_normativa="Res.-TSE 23.607/2019 (emissão obrigatória de recibo eleitoral)",
                    titulo="Receita sem recibo eleitoral",
                    descricao=f"Receita {r.id} (R$ {r.valor}) não possui recibo eleitoral vinculado.",
                    item_relacionado_id=r.id,
                )
            )
    return achados


def regra_receita_em_especie(pc: PrestacaoContas) -> list[Achado]:
    """Arrecadação em espécie é vedada/fortemente restrita; recursos devem ser
    movimentados por meios que permitam identificar doador e rastrear o valor."""
    achados = []
    for r in pc.receitas:
        if r.forma_arrecadacao == FormaArrecadacao.ESPECIE:
            achados.append(
                Achado(
                    severidade=Severidade.IRREGULARIDADE,
                    regra="RES23607_RECEITA_EM_ESPECIE",
                    referencia_normativa="Res.-TSE 23.607/2019 (vedação/restrição a arrecadação em espécie)",
                    titulo="Receita arrecadada em espécie",
                    descricao=(
                        f"Receita {r.id} (R$ {r.valor}, doador '{r.doador.nome}') foi "
                        "registrada como arrecadação em espécie. Confirmar se há "
                        "hipótese legal aplicável ao caso concreto."
                    ),
                    item_relacionado_id=r.id,
                )
            )
    return achados


def regra_despesa_sem_documento_fiscal(pc: PrestacaoContas) -> list[Achado]:
    """Toda despesa deve estar amparada por documento fiscal idôneo."""
    achados = []
    for d in pc.despesas:
        if not d.tem_documento_fiscal:
            achados.append(
                Achado(
                    severidade=Severidade.IRREGULARIDADE,
                    regra="RES23607_DESPESA_SEM_DOCUMENTO",
                    referencia_normativa="Res.-TSE 23.607/2019 (comprovação documental idônea das despesas)",
                    titulo="Despesa sem documento fiscal / comprovante idôneo",
                    descricao=(
                        f"Despesa {d.id} (R$ {d.valor}, fornecedor '{d.fornecedor_nome}') "
                        "não possui documento fiscal idôneo vinculado."
                    ),
                    item_relacionado_id=d.id,
                )
            )
    return achados


def regra_limite_autofinanciamento(pc: PrestacaoContas) -> list[Achado]:
    """Recursos próprios do candidato (autofinanciamento) não podem ultrapassar
    o limite de gastos fixado para o cargo/UF na eleição."""
    achados = []
    teto = pc.candidato_ou_comite.teto_gastos_campanha
    if teto is None:
        return achados
    total_proprios = sum(
        (r.valor for r in pc.receitas if r.doador.tipo == TipoDoador.RECURSOS_PROPRIOS),
        Decimal("0"),
    )
    if total_proprios > teto:
        achados.append(
            Achado(
                severidade=Severidade.IRREGULARIDADE,
                regra="RES23607_AUTOFINANCIAMENTO_ACIMA_TETO",
                referencia_normativa="Res.-TSE 23.607/2019 (limite de recursos próprios do candidato)",
                titulo="Autofinanciamento acima do teto de gastos",
                descricao=(
                    f"Total de recursos próprios (R$ {total_proprios}) ultrapassa o teto "
                    f"de gastos de campanha fixado (R$ {teto})."
                ),
            )
        )
    return achados


def regra_limite_gastos_campanha(pc: PrestacaoContas) -> list[Achado]:
    """Total de despesas não pode ultrapassar o teto de gastos fixado para a
    eleição/cargo."""
    achados = []
    teto = pc.candidato_ou_comite.teto_gastos_campanha
    if teto is None:
        return achados
    if pc.total_despesas > teto:
        achados.append(
            Achado(
                severidade=Severidade.GRAVE,
                regra="RES23607_TETO_GASTOS_EXCEDIDO",
                referencia_normativa="Res.-TSE 23.607/2019 (limite de gastos de campanha)",
                titulo="Teto de gastos de campanha excedido",
                descricao=(
                    f"Total de despesas (R$ {pc.total_despesas}) ultrapassa o teto de "
                    f"gastos fixado para o cargo/UF (R$ {teto})."
                ),
            )
        )
    return achados


def regra_cnpj_especifico_ausente(pc: PrestacaoContas) -> list[Achado]:
    """Candidatos/comitês devem obter CNPJ específico para movimentação
    financeira de campanha."""
    if not pc.candidato_ou_comite.cnpj_especifico:
        return [
            Achado(
                severidade=Severidade.ALERTA,
                regra="RES23607_CNPJ_ESPECIFICO_AUSENTE",
                referencia_normativa="Res.-TSE 23.607/2019 (obrigatoriedade de CNPJ específico)",
                titulo="CNPJ específico de campanha não informado",
                descricao=(
                    f"'{pc.candidato_ou_comite.nome}' não possui CNPJ específico de "
                    "campanha registrado. Confirmar se a candidatura está dispensada "
                    "dessa exigência."
                ),
            )
        ]
    return []


def regra_conta_bancaria_especifica_ausente(pc: PrestacaoContas) -> list[Achado]:
    """Movimentação de recursos deve ocorrer por conta bancária específica de
    campanha."""
    if not pc.candidato_ou_comite.possui_conta_bancaria_especifica:
        return [
            Achado(
                severidade=Severidade.ALERTA,
                regra="RES23607_CONTA_BANCARIA_ESPECIFICA_AUSENTE",
                referencia_normativa="Res.-TSE 23.607/2019 (obrigatoriedade de conta bancária específica)",
                titulo="Conta bancária específica de campanha não confirmada",
                descricao=(
                    f"'{pc.candidato_ou_comite.nome}' não confirma o uso de conta "
                    "bancária específica para movimentação dos recursos de campanha."
                ),
            )
        ]
    return []


def regra_prazo_apresentacao_contas(pc: PrestacaoContas) -> list[Achado]:
    """Contas devem ser apresentadas até o prazo legal contado da data da eleição."""
    achados = []
    if pc.data_apresentacao is None:
        achados.append(
            Achado(
                severidade=Severidade.GRAVE,
                regra="RES23607_CONTAS_NAO_APRESENTADAS",
                referencia_normativa="Res.-TSE 23.607/2019 (prazo de apresentação da prestação de contas)",
                titulo="Contas não apresentadas",
                descricao=f"'{pc.candidato_ou_comite.nome}' ainda não apresentou a prestação de contas.",
            )
        )
        return achados

    prazo_limite = pc.data_eleicao + timedelta(days=PRAZO_APRESENTACAO_CONTAS_DIAS)
    if pc.data_apresentacao > prazo_limite:
        achados.append(
            Achado(
                severidade=Severidade.IRREGULARIDADE,
                regra="RES23607_PRAZO_APRESENTACAO_EXCEDIDO",
                referencia_normativa="Res.-TSE 23.607/2019 (prazo de apresentação da prestação de contas)",
                titulo="Contas apresentadas fora do prazo",
                descricao=(
                    f"Contas apresentadas em {pc.data_apresentacao.isoformat()}, após o prazo "
                    f"limite de {prazo_limite.isoformat()} "
                    f"({PRAZO_APRESENTACAO_CONTAS_DIAS} dias da eleição)."
                ),
            )
        )
    return achados


REGRAS_REGISTRADAS = [
    regra_doacao_pessoa_juridica,
    regra_limite_doacao_pessoa_fisica,
    regra_origem_vedada,
    regra_recibo_eleitoral_ausente,
    regra_receita_em_especie,
    regra_despesa_sem_documento_fiscal,
    regra_limite_autofinanciamento,
    regra_limite_gastos_campanha,
    regra_cnpj_especifico_ausente,
    regra_conta_bancaria_especifica_ausente,
    regra_prazo_apresentacao_contas,
]
