"""Orquestra a execução de todas as regras sobre uma prestação de contas.

Fluxo, conforme Res. 23.607/2019 (arts. 66, 69, 72 e 74):

1. As regras são executadas e geram achados.
2. Achados sobre os quais a prestadora/o prestador de contas ainda não teve
   oportunidade de se manifestar (não constam em
   `PrestacaoContas.diligencias_respondidas`) ficam em
   `achados_pendentes_diligencia` — enquanto houver algum, o caso NÃO está
   pronto para parecer conclusivo; a providência cabível é a diligência com
   intimação da prestadora/do prestador (arts. 66, 69 e 72).
3. Só quando não houver nenhum achado pendente de diligência
   (`pronto_para_parecer_conclusivo`) é que o parecer conclusivo (art. 74)
   deve ser elaborado, com base nos achados confirmados (diligência
   cumprida e o ponto não foi sanado).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .achados import Achado, Severidade, StatusDiligencia, chave_diligencia
from .modelos import PrestacaoContas
from .regras import REGRAS_REGISTRADAS

PARECER_SUGERIDO_POR_SEVERIDADE = {
    Severidade.GRAVE: "DESAPROVAÇÃO (sugerido)",
    Severidade.IRREGULARIDADE: "APROVAÇÃO COM RESSALVAS (sugerido)",
    Severidade.ALERTA: "APROVAÇÃO COM RESSALVAS (sugerido)",
    Severidade.INFO: "APROVAÇÃO (sugerido)",
}


@dataclass
class Relatorio:
    prestacao: PrestacaoContas
    achados_confirmados: list[Achado] = field(default_factory=list)
    achados_pendentes_diligencia: list[Achado] = field(default_factory=list)
    achados_sanados: list[Achado] = field(default_factory=list)

    @property
    def pronto_para_parecer_conclusivo(self) -> bool:
        """Só é True quando não há achado pendente de diligência (art. 74)."""
        return len(self.achados_pendentes_diligencia) == 0

    @property
    def parecer_sugerido(self) -> str | None:
        """Parecer sugerido com base na severidade mais grave entre os
        achados confirmados.

        Retorna `None` enquanto houver achado pendente de diligência —
        nesse caso o parecer conclusivo NÃO deve ser elaborado; a etapa
        cabível é a diligência com intimação (arts. 66, 69 e 72).

        Isto é apenas um indicativo para triagem do analista humano — o
        julgamento formal das contas é sempre um ato do órgão competente da
        Justiça Eleitoral, considerando o conjunto das circunstâncias.
        """
        if not self.pronto_para_parecer_conclusivo:
            return None
        if not self.achados_confirmados:
            return "APROVAÇÃO (sugerido) — nenhuma pendência confirmada"
        severidade_mais_grave = max(
            self.achados_confirmados,
            key=lambda a: list(Severidade).index(a.severidade),
        ).severidade
        return PARECER_SUGERIDO_POR_SEVERIDADE[severidade_mais_grave]

    def achados_confirmados_por_severidade(self, severidade: Severidade) -> list[Achado]:
        return [a for a in self.achados_confirmados if a.severidade == severidade]


def analisar(prestacao: PrestacaoContas) -> Relatorio:
    """Executa todas as regras registradas e separa os achados conforme já
    tenham (ou não) passado por diligência/manifestação."""
    pendentes: list[Achado] = []
    confirmados: list[Achado] = []
    sanados: list[Achado] = []

    for regra in REGRAS_REGISTRADAS:
        for achado in regra(prestacao):
            status = prestacao.diligencias_respondidas.get(chave_diligencia(achado))
            if status is None:
                pendentes.append(achado)
            elif status == StatusDiligencia.SANADA:
                sanados.append(achado)
            else:
                confirmados.append(achado)

    return Relatorio(
        prestacao=prestacao,
        achados_confirmados=confirmados,
        achados_pendentes_diligencia=pendentes,
        achados_sanados=sanados,
    )
