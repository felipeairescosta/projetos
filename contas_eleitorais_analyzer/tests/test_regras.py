import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.achados import Severidade
from src.analisador import analisar
from src.ingestao.json_loader import carregar_prestacao_de_json

EXEMPLO = Path(__file__).parent.parent / "dados_exemplo" / "exemplo_prestacao.json"


def _analisar_exemplo():
    prestacao = carregar_prestacao_de_json(EXEMPLO)
    return analisar(prestacao)


def test_detecta_doacao_pessoa_juridica():
    relatorio = _analisar_exemplo()
    achados = [a for a in relatorio.achados if a.regra == "RES23607_ORIGEM_VEDADA"]
    assert len(achados) == 1
    assert achados[0].item_relacionado_id == "REC-003"


def test_detecta_origem_nao_identificada():
    relatorio = _analisar_exemplo()
    achados = [a for a in relatorio.achados if a.regra == "RES23607_ORIGEM_NAO_IDENTIFICADA"]
    assert len(achados) == 1
    assert achados[0].item_relacionado_id == "REC-004"


def test_detecta_autofinanciamento_acima_do_limite():
    # Res.-TSE 23.607/2019, art. 27, §1º: recursos próprios limitados a 10% do
    # teto de gastos, não ao teto integral.
    relatorio = _analisar_exemplo()
    achados = [a for a in relatorio.achados if a.regra == "RES23607_AUTOFINANCIAMENTO_ACIMA_LIMITE"]
    assert len(achados) == 1


def test_detecta_limite_pessoa_fisica_excedido():
    relatorio = _analisar_exemplo()
    achados_limite = [a for a in relatorio.achados if a.regra == "RES23607_LIMITE_PF_EXCEDIDO"]
    assert len(achados_limite) == 1
    assert achados_limite[0].item_relacionado_id == "REC-002"


def test_detecta_recibo_eleitoral_ausente():
    relatorio = _analisar_exemplo()
    achados = [a for a in relatorio.achados if a.regra == "RES23607_RECIBO_ELEITORAL_AUSENTE"]
    assert len(achados) == 1
    assert achados[0].item_relacionado_id == "REC-003"


def test_detecta_receita_em_especie():
    relatorio = _analisar_exemplo()
    regras_disparadas = {a.regra for a in relatorio.achados}
    assert "RES23607_RECEITA_EM_ESPECIE" in regras_disparadas


def test_detecta_despesa_sem_documento_fiscal():
    relatorio = _analisar_exemplo()
    achados = [a for a in relatorio.achados if a.regra == "RES23607_DESPESA_SEM_DOCUMENTO"]
    assert len(achados) == 1
    assert achados[0].item_relacionado_id == "DESP-002"


def test_detecta_cnpj_e_conta_bancaria_ausentes():
    relatorio = _analisar_exemplo()
    regras_disparadas = {a.regra for a in relatorio.achados}
    assert "RES23607_CNPJ_ESPECIFICO_AUSENTE" in regras_disparadas
    assert "RES23607_CONTA_BANCARIA_ESPECIFICA_AUSENTE" in regras_disparadas


def test_parecer_sugerido_e_desaprovacao_por_haver_achado_grave():
    relatorio = _analisar_exemplo()
    achados_graves = relatorio.achados_por_severidade(Severidade.GRAVE)
    assert achados_graves  # o exemplo contém doação de PJ e origem vedada (GRAVE)
    assert relatorio.parecer_sugerido == "DESAPROVAÇÃO (sugerido)"


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
    assert relatorio.achados == []
    assert relatorio.parecer_sugerido.startswith("APROVAÇÃO")
