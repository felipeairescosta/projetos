"""
Motor de regras — Resolução TSE nº 23.607/2019 (texto compilado).

As regras abaixo foram codificadas a partir do texto compilado da Resolução
TSE nº 23.607/2019 fornecido pelo usuário (versão com as alterações das
Resoluções 23.665/2021, 23.709/2022, 23.731/2024 e 23.752/2026).

⚠️ Pontos que ainda exigem confirmação manual por eleição:
- O teto de gastos de campanha (art. 4º) é fixado por portaria do TSE a cada
  eleição — não há um valor fixo na resolução. Deve ser informado em
  `CandidatoOuComite.teto_gastos_campanha`.
- Valores em reais citados na resolução (R$ 1.064,10 — art. 21, §1º / art. 43;
  R$ 4.000,00 — art. 7º, §6º, I; R$ 40.000,00 — art. 27, §3º; R$ 20.000,00 —
  art. 62) são atualizados monetariamente a cada eleição (INPC/IBGE ou outro
  índice). Os valores usados aqui são os do texto compilado na data em que
  este módulo foi escrito e devem ser conferidos contra a portaria vigente da
  eleição em análise.
- Este motor não modela integralmente a exceção do art. 27, §3º (doações
  estimáveis em bens/serviços próprios até R$ 40.000,00, fora do limite de
  10% do rendimento) nem a soma de recursos próprios de vice/suplente ao do
  titular (art. 27, §1º-A). Casos que dependam dessas exceções devem ser
  revisados manualmente.

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
# Parâmetros — conferir valores/prazos vigentes por portaria de cada eleição
# ---------------------------------------------------------------------------
LIMITE_DOACAO_PF_PERC_RENDIMENTO = Decimal("0.10")  # art. 27, caput
LIMITE_RECURSOS_PROPRIOS_PERC_TETO_GASTOS = Decimal("0.10")  # art. 27, §1º
VALOR_MINIMO_EXIGE_MEIO_BANCARIO_RASTREAVEL = Decimal("1064.10")  # art. 21, §1º

PRAZO_APRESENTACAO_CONTAS_DIAS_1_TURNO = 30  # art. 49, caput
PRAZO_APRESENTACAO_CONTAS_DIAS_2_TURNO = 20  # art. 49, §1º

# Formas de pagamento aceitas para gastos eleitorais (art. 38, caput)
FORMAS_PAGAMENTO_GASTOS_PERMITIDAS = {
    FormaArrecadacao.CHEQUE_NOMINAL,
    FormaArrecadacao.TRANSFERENCIA_ELETRONICA,
    FormaArrecadacao.CARTAO_DEBITO,
    FormaArrecadacao.PIX,
}

# Fontes de recursos vedadas (art. 31, caput)
ORIGENS_SEMPRE_VEDADAS = {
    TipoDoador.PESSOA_JURIDICA,
    TipoDoador.ORIGEM_ESTRANGEIRA,
    TipoDoador.PESSOA_FISICA_PERMISSIONARIA_SERVICO_PUBLICO,
}


def regra_origem_vedada(pc: PrestacaoContas) -> list[Achado]:
    """É vedado receber, direta ou indiretamente, doação em dinheiro ou
    estimável em dinheiro de: pessoa jurídica, origem estrangeira ou pessoa
    física permissionária de serviço público (Res. 23.607/2019, art. 31)."""
    achados = []
    for r in pc.receitas:
        if r.doador.tipo in ORIGENS_SEMPRE_VEDADAS:
            achados.append(
                Achado(
                    severidade=Severidade.GRAVE,
                    regra="RES23607_ORIGEM_VEDADA",
                    referencia_normativa="Res.-TSE 23.607/2019, art. 31",
                    titulo="Recurso de fonte vedada",
                    descricao=(
                        f"Receita {r.id} no valor de R$ {r.valor}, doador '{r.doador.nome}' "
                        f"({r.doador.cpf_cnpj}), tem origem classificada como "
                        f"'{r.doador.tipo.value}', que é fonte vedada de recursos de campanha "
                        "(art. 31). O recurso deve ser devolvido à doadora/ao doador ou, na "
                        "impossibilidade, recolhido ao Tesouro Nacional via GRU (art. 31, §§3º e 4º)."
                    ),
                    item_relacionado_id=r.id,
                )
            )
    return achados


def regra_origem_nao_identificada(pc: PrestacaoContas) -> list[Achado]:
    """Recursos de origem não identificada não podem ser utilizados e devem
    ser recolhidos ao Tesouro Nacional (Res. 23.607/2019, art. 32)."""
    achados = []
    for r in pc.receitas:
        if r.doador.tipo == TipoDoador.ORIGEM_NAO_IDENTIFICADA:
            achados.append(
                Achado(
                    severidade=Severidade.GRAVE,
                    regra="RES23607_ORIGEM_NAO_IDENTIFICADA",
                    referencia_normativa="Res.-TSE 23.607/2019, art. 32",
                    titulo="Recurso de origem não identificada",
                    descricao=(
                        f"Receita {r.id} (R$ {r.valor}) está classificada como de origem não "
                        "identificada. Deve ser recolhida ao Tesouro Nacional por GRU (art. 32, caput)."
                    ),
                    item_relacionado_id=r.id,
                )
            )
    return achados


def regra_limite_doacao_pessoa_fisica(pc: PrestacaoContas) -> list[Achado]:
    """Doações de pessoa física são limitadas a 10% dos rendimentos brutos
    auferidos pela doadora ou pelo doador no ano-calendário anterior à
    eleição (Res. 23.607/2019, art. 27, caput)."""
    achados = []
    for r in pc.receitas:
        if r.doador.tipo != TipoDoador.PESSOA_FISICA:
            continue
        if r.doador.rendimento_bruto_ano_anterior is None:
            achados.append(
                Achado(
                    severidade=Severidade.ALERTA,
                    regra="RES23607_LIMITE_PF_SEM_DADO",
                    referencia_normativa="Res.-TSE 23.607/2019, art. 27, caput",
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
                    referencia_normativa="Res.-TSE 23.607/2019, art. 27, caput e §4º",
                    titulo="Doação de pessoa física acima do limite legal",
                    descricao=(
                        f"Receita {r.id}: doação de R$ {r.valor} do doador '{r.doador.nome}' "
                        f"ultrapassa o limite de 10% do rendimento bruto informado "
                        f"(limite calculado: R$ {limite}). Sujeita a multa de até 100% do "
                        "valor excedente (art. 27, §4º)."
                    ),
                    item_relacionado_id=r.id,
                )
            )
    return achados


def regra_limite_autofinanciamento(pc: PrestacaoContas) -> list[Achado]:
    """Recursos próprios do candidato (autofinanciamento) são limitados a 10%
    do teto de gastos fixado para o cargo em que concorre (Res. 23.607/2019,
    art. 27, §1º) — não ao teto integral."""
    achados = []
    teto = pc.candidato_ou_comite.teto_gastos_campanha
    if teto is None:
        return achados
    limite = teto * LIMITE_RECURSOS_PROPRIOS_PERC_TETO_GASTOS
    total_proprios = sum(
        (r.valor for r in pc.receitas if r.doador.tipo == TipoDoador.RECURSOS_PROPRIOS),
        Decimal("0"),
    )
    if total_proprios > limite:
        achados.append(
            Achado(
                severidade=Severidade.IRREGULARIDADE,
                regra="RES23607_AUTOFINANCIAMENTO_ACIMA_LIMITE",
                referencia_normativa="Res.-TSE 23.607/2019, art. 27, §1º",
                titulo="Autofinanciamento acima do limite de 10% do teto de gastos",
                descricao=(
                    f"Total de recursos próprios (R$ {total_proprios}) ultrapassa o limite de "
                    f"10% do teto de gastos de campanha fixado para o cargo "
                    f"(teto: R$ {teto}; limite de recursos próprios: R$ {limite})."
                ),
            )
        )
    return achados


def regra_recibo_eleitoral_ausente(pc: PrestacaoContas) -> list[Achado]:
    """Toda arrecadação estimável em dinheiro deve ter recibo eleitoral,
    ressalvadas as dispensas do art. 7º, §§6º e 6º-A (cessão de bens móveis
    até R$ 4.000,00; doações do FEFC/Fundo Partidário via transferência
    bancária do partido; doações via Pix) — Res. 23.607/2019, art. 7º."""
    achados = []
    for r in pc.receitas:
        dispensado = (
            r.doador.tipo in (TipoDoador.FUNDO_ELEITORAL, TipoDoador.FUNDO_PARTIDARIO)
            and r.forma_arrecadacao == FormaArrecadacao.TRANSFERENCIA_ELETRONICA
        ) or r.forma_arrecadacao == FormaArrecadacao.PIX
        if not r.tem_recibo_eleitoral and not dispensado:
            achados.append(
                Achado(
                    severidade=Severidade.IRREGULARIDADE,
                    regra="RES23607_RECIBO_ELEITORAL_AUSENTE",
                    referencia_normativa="Res.-TSE 23.607/2019, art. 7º",
                    titulo="Receita sem recibo eleitoral",
                    descricao=(
                        f"Receita {r.id} (R$ {r.valor}) não possui recibo eleitoral vinculado "
                        "e não se enquadra nas dispensas do art. 7º, §§6º/6º-A."
                    ),
                    item_relacionado_id=r.id,
                )
            )
        elif not r.tem_recibo_eleitoral and r.forma_arrecadacao == FormaArrecadacao.PIX:
            achados.append(
                Achado(
                    severidade=Severidade.ALERTA,
                    regra="RES23607_PIX_SEM_RELATORIO_CPF",
                    referencia_normativa="Res.-TSE 23.607/2019, art. 7º, §6º-B",
                    titulo="Doação via Pix dispensada de recibo — conferir relatório de CPF",
                    descricao=(
                        f"Receita {r.id} (R$ {r.valor}) foi recebida via Pix, dispensada de "
                        "recibo eleitoral, mas a dispensa não afasta a obrigação de manter "
                        "relatório com CPF e valor de cada doação recebida por esse meio "
                        "(art. 7º, §6º-B). Confirmar se esse relatório existe."
                    ),
                    item_relacionado_id=r.id,
                )
            )
    return achados


def regra_receita_alto_valor_sem_meio_bancario_rastreavel(pc: PrestacaoContas) -> list[Achado]:
    """Doações financeiras de pessoa física ou recursos próprios de valor >=
    R$ 1.064,10 só podem ser feitas por transferência eletrônica entre contas
    bancárias ou cheque cruzado e nominal (Res. 23.607/2019, art. 21, §1º)."""
    achados = []
    for r in pc.receitas:
        if r.doador.tipo not in (TipoDoador.PESSOA_FISICA, TipoDoador.RECURSOS_PROPRIOS):
            continue
        if r.valor < VALOR_MINIMO_EXIGE_MEIO_BANCARIO_RASTREAVEL:
            continue
        if r.forma_arrecadacao not in (FormaArrecadacao.TRANSFERENCIA_ELETRONICA, FormaArrecadacao.CHEQUE_NOMINAL):
            achados.append(
                Achado(
                    severidade=Severidade.IRREGULARIDADE,
                    regra="RES23607_DOACAO_ALTO_VALOR_SEM_MEIO_BANCARIO",
                    referencia_normativa="Res.-TSE 23.607/2019, art. 21, §1º",
                    titulo="Doação de alto valor sem meio bancário rastreável",
                    descricao=(
                        f"Receita {r.id} (R$ {r.valor}, doador '{r.doador.nome}') é igual ou "
                        f"superior a R$ {VALOR_MINIMO_EXIGE_MEIO_BANCARIO_RASTREAVEL} e foi "
                        f"registrada com forma de arrecadação '{r.forma_arrecadacao.value}', mas "
                        "só pode ser feita por transferência eletrônica entre contas bancárias "
                        "ou cheque cruzado e nominal."
                    ),
                    item_relacionado_id=r.id,
                )
            )
    return achados


def regra_receita_em_especie(pc: PrestacaoContas) -> list[Achado]:
    """As doações de pessoa física e de recursos próprios só podem ser
    realizadas por transação bancária identificada, doação/cessão de bens ou
    serviços estimáveis, financiamento coletivo ou Pix (Res. 23.607/2019,
    art. 21) — não há previsão legal de arrecadação financeira em espécie."""
    achados = []
    for r in pc.receitas:
        if r.forma_arrecadacao == FormaArrecadacao.ESPECIE:
            achados.append(
                Achado(
                    severidade=Severidade.IRREGULARIDADE,
                    regra="RES23607_RECEITA_EM_ESPECIE",
                    referencia_normativa="Res.-TSE 23.607/2019, art. 21, caput",
                    titulo="Receita arrecadada em espécie",
                    descricao=(
                        f"Receita {r.id} (R$ {r.valor}, doador '{r.doador.nome}') foi "
                        "registrada como arrecadação em espécie, forma não prevista entre "
                        "os meios lícitos de arrecadação do art. 21."
                    ),
                    item_relacionado_id=r.id,
                )
            )
    return achados


def regra_despesa_forma_pagamento_vedada(pc: PrestacaoContas) -> list[Achado]:
    """Gastos eleitorais só podem ser pagos por cheque nominal cruzado,
    transferência bancária, débito em conta, cartão de débito ou Pix; é
    vedado o pagamento em moeda virtual ou cartão pré-pago de empresa
    intermediadora (Res. 23.607/2019, art. 38). Pagamentos de pequeno vulto
    via Fundo de Caixa (art. 39/40) são uma exceção não modelada aqui."""
    achados = []
    for d in pc.despesas:
        if d.forma_pagamento not in FORMAS_PAGAMENTO_GASTOS_PERMITIDAS:
            achados.append(
                Achado(
                    severidade=Severidade.IRREGULARIDADE,
                    regra="RES23607_DESPESA_FORMA_PAGAMENTO_VEDADA",
                    referencia_normativa="Res.-TSE 23.607/2019, art. 38",
                    titulo="Gasto eleitoral pago por forma não autorizada",
                    descricao=(
                        f"Despesa {d.id} (R$ {d.valor}, fornecedor '{d.fornecedor_nome}') foi "
                        f"paga via '{d.forma_pagamento.value}', forma não prevista no art. 38, "
                        "caput, salvo se enquadrada na exceção de pequeno vulto (Fundo de "
                        "Caixa, arts. 39-40), que deve ser confirmada manualmente."
                    ),
                    item_relacionado_id=d.id,
                )
            )
    return achados


def regra_despesa_sem_documento_fiscal(pc: PrestacaoContas) -> list[Achado]:
    """A comprovação dos gastos eleitorais deve ser feita por documento
    fiscal idôneo (Res. 23.607/2019, art. 60)."""
    achados = []
    for d in pc.despesas:
        if not d.tem_documento_fiscal:
            achados.append(
                Achado(
                    severidade=Severidade.IRREGULARIDADE,
                    regra="RES23607_DESPESA_SEM_DOCUMENTO",
                    referencia_normativa="Res.-TSE 23.607/2019, art. 60",
                    titulo="Despesa sem documento fiscal / comprovante idôneo",
                    descricao=(
                        f"Despesa {d.id} (R$ {d.valor}, fornecedor '{d.fornecedor_nome}') "
                        "não possui documento fiscal idôneo vinculado."
                    ),
                    item_relacionado_id=d.id,
                )
            )
    return achados


def regra_limite_gastos_campanha(pc: PrestacaoContas) -> list[Achado]:
    """O total de despesas não pode ultrapassar o teto de gastos fixado por
    portaria do TSE para o cargo/UF na eleição (Res. 23.607/2019, arts. 4º a
    6º). O excesso sujeita a(o) responsável a multa de 100% do valor
    excedente, sem prejuízo de eventual abuso de poder econômico (art. 6º)."""
    achados = []
    teto = pc.candidato_ou_comite.teto_gastos_campanha
    if teto is None:
        return achados
    if pc.total_despesas > teto:
        excesso = pc.total_despesas - teto
        achados.append(
            Achado(
                severidade=Severidade.GRAVE,
                regra="RES23607_TETO_GASTOS_EXCEDIDO",
                referencia_normativa="Res.-TSE 23.607/2019, arts. 4º a 6º",
                titulo="Teto de gastos de campanha excedido",
                descricao=(
                    f"Total de despesas (R$ {pc.total_despesas}) ultrapassa o teto de "
                    f"gastos fixado para o cargo/UF (R$ {teto}) em R$ {excesso}, sujeito a "
                    "multa de 100% do excesso (art. 6º)."
                ),
            )
        )
    return achados


def regra_cnpj_especifico_ausente(pc: PrestacaoContas) -> list[Achado]:
    """Candidatos/partidos devem obter CNPJ específico como pré-requisito
    para arrecadar recursos (Res. 23.607/2019, art. 3º, I, b; art. 8º)."""
    if not pc.candidato_ou_comite.cnpj_especifico:
        return [
            Achado(
                severidade=Severidade.ALERTA,
                regra="RES23607_CNPJ_ESPECIFICO_AUSENTE",
                referencia_normativa="Res.-TSE 23.607/2019, art. 3º, I, b",
                titulo="CNPJ específico de campanha não informado",
                descricao=(
                    f"'{pc.candidato_ou_comite.nome}' não possui CNPJ específico de "
                    "campanha registrado. Confirmar se a candidatura está dispensada "
                    "dessa exigência (art. 8º, §4º)."
                ),
            )
        ]
    return []


def regra_conta_bancaria_especifica_ausente(pc: PrestacaoContas) -> list[Achado]:
    """É obrigatória a abertura de conta bancária específica para
    movimentação de recursos de campanha (Res. 23.607/2019, art. 3º, I, c;
    art. 8º), ressalvadas as hipóteses de dispensa do art. 8º, §4º."""
    if not pc.candidato_ou_comite.possui_conta_bancaria_especifica:
        return [
            Achado(
                severidade=Severidade.ALERTA,
                regra="RES23607_CONTA_BANCARIA_ESPECIFICA_AUSENTE",
                referencia_normativa="Res.-TSE 23.607/2019, art. 3º, I, c; art. 8º",
                titulo="Conta bancária específica de campanha não confirmada",
                descricao=(
                    f"'{pc.candidato_ou_comite.nome}' não confirma o uso de conta "
                    "bancária específica para movimentação dos recursos de campanha. "
                    "Confirmar se a candidatura está dispensada dessa exigência (art. 8º, §4º)."
                ),
            )
        ]
    return []


def regra_prazo_apresentacao_contas(pc: PrestacaoContas) -> list[Achado]:
    """As contas finais devem ser apresentadas até o 30º dia posterior à
    eleição (1º turno) ou até o 20º dia posterior ao 2º turno, quando houver
    (Res. 23.607/2019, art. 49, caput e §1º). A não apresentação leva ao
    julgamento das contas como não prestadas (art. 74, IV)."""
    achados = []
    if pc.data_apresentacao is None:
        achados.append(
            Achado(
                severidade=Severidade.GRAVE,
                regra="RES23607_CONTAS_NAO_APRESENTADAS",
                referencia_normativa="Res.-TSE 23.607/2019, art. 74, IV",
                titulo="Contas não apresentadas",
                descricao=f"'{pc.candidato_ou_comite.nome}' ainda não apresentou a prestação de contas.",
            )
        )
        return achados

    dias_prazo = (
        PRAZO_APRESENTACAO_CONTAS_DIAS_2_TURNO
        if pc.houve_segundo_turno
        else PRAZO_APRESENTACAO_CONTAS_DIAS_1_TURNO
    )
    prazo_limite = pc.data_eleicao + timedelta(days=dias_prazo)
    if pc.data_apresentacao > prazo_limite:
        achados.append(
            Achado(
                severidade=Severidade.IRREGULARIDADE,
                regra="RES23607_PRAZO_APRESENTACAO_EXCEDIDO",
                referencia_normativa="Res.-TSE 23.607/2019, art. 49, caput e §1º",
                titulo="Contas apresentadas fora do prazo",
                descricao=(
                    f"Contas apresentadas em {pc.data_apresentacao.isoformat()}, após o prazo "
                    f"limite de {prazo_limite.isoformat()} ({dias_prazo} dias da eleição)."
                ),
            )
        )
    return achados


REGRAS_REGISTRADAS = [
    regra_origem_vedada,
    regra_origem_nao_identificada,
    regra_limite_doacao_pessoa_fisica,
    regra_limite_autofinanciamento,
    regra_recibo_eleitoral_ausente,
    regra_receita_alto_valor_sem_meio_bancario_rastreavel,
    regra_receita_em_especie,
    regra_despesa_forma_pagamento_vedada,
    regra_despesa_sem_documento_fiscal,
    regra_limite_gastos_campanha,
    regra_cnpj_especifico_ausente,
    regra_conta_bancaria_especifica_ausente,
    regra_prazo_apresentacao_contas,
]
