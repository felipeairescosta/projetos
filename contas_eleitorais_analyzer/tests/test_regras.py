import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.achados import Severidade, StatusDiligencia, chave_diligencia
from src.analisador import analisar
from src.ingestao.json_loader import carregar_prestacao_de_json

EXEMPLO = Path(__file__).parent.parent / "dados_exemplo" / "exemplo_prestacao.json"


def _analisar_exemplo():
    prestacao = carregar_prestacao_de_json(EXEMPLO)
    return analisar(prestacao)


# ---------------------------------------------------------------------------
# Primeira análise: nada passou por diligência ainda -> tudo fica pendente e
# o parecer conclusivo NÃO deve ser elaborado (Res. 23.607/2019, arts. 66, 69,
# 72 e 74).
# ---------------------------------------------------------------------------


def test_sem_diligencia_previa_nada_fica_pronto_para_parecer():
    relatorio = _analisar_exemplo()
    assert relatorio.pronto_para_parecer_conclusivo is False
    assert relatorio.parecer_sugerido is None
    assert relatorio.achados_confirmados == []
    assert relatorio.achados_pendentes_diligencia  # há achados aguardando diligência


def test_detecta_doacao_pessoa_juridica_como_pendente_de_diligencia():
    relatorio = _analisar_exemplo()
    achados = [a for a in relatorio.achados_pendentes_diligencia if a.regra == "RES23607_ORIGEM_VEDADA"]
    assert len(achados) == 1
    assert achados[0].item_relacionado_id == "REC-003"


def test_detecta_origem_nao_identificada_como_pendente_de_diligencia():
    relatorio = _analisar_exemplo()
    achados = [
        a for a in relatorio.achados_pendentes_diligencia if a.regra == "RES23607_ORIGEM_NAO_IDENTIFICADA"
    ]
    assert len(achados) == 1
    assert achados[0].item_relacionado_id == "REC-004"


def test_detecta_autofinanciamento_acima_do_limite():
    # Res.-TSE 23.607/2019, art. 27, §1º: recursos próprios limitados a 10% do
    # teto de gastos, não ao teto integral.
    relatorio = _analisar_exemplo()
    regras = {a.regra for a in relatorio.achados_pendentes_diligencia}
    assert "RES23607_AUTOFINANCIAMENTO_ACIMA_LIMITE" in regras


def test_detecta_limite_pessoa_fisica_excedido():
    relatorio = _analisar_exemplo()
    achados = [a for a in relatorio.achados_pendentes_diligencia if a.regra == "RES23607_LIMITE_PF_EXCEDIDO"]
    assert len(achados) == 1
    assert achados[0].item_relacionado_id == "REC-002"


def test_detecta_recibo_eleitoral_ausente():
    relatorio = _analisar_exemplo()
    achados = [
        a for a in relatorio.achados_pendentes_diligencia if a.regra == "RES23607_RECIBO_ELEITORAL_AUSENTE"
    ]
    assert len(achados) == 1
    assert achados[0].item_relacionado_id == "REC-003"


def test_detecta_receita_em_especie():
    relatorio = _analisar_exemplo()
    regras = {a.regra for a in relatorio.achados_pendentes_diligencia}
    assert "RES23607_RECEITA_EM_ESPECIE" in regras


def test_detecta_despesa_sem_documento_fiscal():
    relatorio = _analisar_exemplo()
    achados = [a for a in relatorio.achados_pendentes_diligencia if a.regra == "RES23607_DESPESA_SEM_DOCUMENTO"]
    assert len(achados) == 1
    assert achados[0].item_relacionado_id == "DESP-002"


def test_detecta_cnpj_e_conta_bancaria_ausentes():
    relatorio = _analisar_exemplo()
    regras = {a.regra for a in relatorio.achados_pendentes_diligencia}
    assert "RES23607_CNPJ_ESPECIFICO_AUSENTE" in regras
    assert "RES23607_CONTA_BANCARIA_ESPECIFICA_AUSENTE" in regras


# ---------------------------------------------------------------------------
# Segunda análise: depois que a diligência foi cumprida (todos os achados
# tiveram oportunidade de manifestação) é que o parecer conclusivo pode ser
# elaborado.
# ---------------------------------------------------------------------------


def test_apos_diligencia_cumprida_parecer_e_desaprovacao_por_achado_grave_nao_sanado():
    prestacao = carregar_prestacao_de_json(EXEMPLO)
    relatorio_inicial = analisar(prestacao)

    # Simula que a diligência foi cumprida para todos os pontos e nenhum foi sanado.
    prestacao.diligencias_respondidas = {
        chave_diligencia(a): StatusDiligencia.NAO_SANADA for a in relatorio_inicial.achados_pendentes_diligencia
    }

    relatorio_final = analisar(prestacao)
    assert relatorio_final.pronto_para_parecer_conclusivo is True
    achados_graves = relatorio_final.achados_confirmados_por_severidade(Severidade.GRAVE)
    assert achados_graves  # doação de PJ e origem não identificada (GRAVE)
    assert relatorio_final.parecer_sugerido == "DESAPROVAÇÃO (sugerido)"


def test_apos_diligencia_cumprida_achados_sanados_nao_contam_para_o_parecer():
    prestacao = carregar_prestacao_de_json(EXEMPLO)
    relatorio_inicial = analisar(prestacao)

    # Todos os achados foram esclarecidos/corrigidos em diligência.
    prestacao.diligencias_respondidas = {
        chave_diligencia(a): StatusDiligencia.SANADA for a in relatorio_inicial.achados_pendentes_diligencia
    }

    relatorio_final = analisar(prestacao)
    assert relatorio_final.pronto_para_parecer_conclusivo is True
    assert relatorio_final.achados_confirmados == []
    assert len(relatorio_final.achados_sanados) == len(relatorio_inicial.achados_pendentes_diligencia)
    assert relatorio_final.parecer_sugerido == "APROVAÇÃO (sugerido) — nenhuma pendência confirmada"


def test_prestacao_sem_pendencias_gera_parecer_aprovacao():
    from datetime import date
    from decimal import Decimal

    from src.modelos import (
        CandidatoOuComite,
        Cargo,
        Doador,
        FormaArrecadacao,
        PrestacaoContas,
        Receita,
        TipoDoador,
    )

    candidato = CandidatoOuComite(
        nome="Ciclana Exemplo",
        numero_ou_identificacao="999",
        cargo=Cargo.VEREADOR,
        uf="CE",
        municipio="Fortaleza",
        cnpj_especifico="00.000.000/0001-00",
        possui_conta_bancaria_especifica=True,
        teto_gastos_campanha=Decimal("50000.00"),
    )
    prestacao = PrestacaoContas(
        candidato_ou_comite=candidato,
        data_eleicao=date(2024, 10, 6),
        data_apresentacao=date(2024, 10, 20),
        receitas=[
            Receita(
                id="REC-001",
                data=date(2024, 8, 1),
                valor=Decimal("1000.00"),
                doador=Doador(
                    nome="Doador Regular",
                    cpf_cnpj="000.000.000-00",
                    tipo=TipoDoador.PESSOA_FISICA,
                    rendimento_bruto_ano_anterior=Decimal("60000.00"),
                ),
                forma_arrecadacao=FormaArrecadacao.TRANSFERENCIA_ELETRONICA,
                tem_recibo_eleitoral=True,
            )
        ],
        despesas=[],
    )
    relatorio = analisar(prestacao)
    assert relatorio.achados_pendentes_diligencia == []
    assert relatorio.pronto_para_parecer_conclusivo is True
    assert relatorio.parecer_sugerido.startswith("APROVAÇÃO")
