"""Orquestra a execução de todas as regras sobre uma prestação de contas."""

from __future__ import annotations

from dataclasses import dataclass

from .achados import Achado, Severidade
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
    achados: list[Achado]

    @property
    def parecer_sugerido(self) -> str:
        """Parecer sugerido com base na severidade mais grave encontrada.

        Isto é apenas um indicativo para triagem do analista humano — o
        julgamento formal das contas é sempre um ato do órgão competente da
        Justiça Eleitoral, considerando o conjunto das circunstâncias.
        """
        if not self.achados:
            return "APROVAÇÃO (sugerido) — nenhuma pendência identificada"
        severidade_mais_grave = max(
            self.achados,
            key=lambda a: list(Severidade).index(a.severidade),
        ).severidade
        return PARECER_SUGERIDO_POR_SEVERIDADE[severidade_mais_grave]

    def achados_por_severidade(self, severidade: Severidade) -> list[Achado]:
        return [a for a in self.achados if a.severidade == severidade]


def analisar(prestacao: PrestacaoContas) -> Relatorio:
    """Executa todas as regras registradas contra a prestação de contas informada."""
    achados: list[Achado] = []
    for regra in REGRAS_REGISTRADAS:
        achados.extend(regra(prestacao))
    return Relatorio(prestacao=prestacao, achados=achados)
