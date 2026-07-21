"""Estrutura dos achados (findings) gerados pela análise das contas."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severidade(str, Enum):
    INFO = "INFO"
    ALERTA = "ALERTA"
    IRREGULARIDADE = "IRREGULARIDADE"
    GRAVE = "GRAVE"  # risco de desaprovação das contas / art. 30-A Lei 9.504


class StatusDiligencia(str, Enum):
    """Resultado do ciclo de diligência/manifestação (Res. 23.607/2019, arts.
    66, 69 e 72) já realizado sobre um achado específico."""

    SANADA = "SANADA"  # a prestadora/o prestador esclareceu ou corrigiu o ponto
    NAO_SANADA = "NAO_SANADA"  # houve oportunidade de manifestação, mas o ponto persiste


@dataclass
class Achado:
    severidade: Severidade
    regra: str  # identificador curto da regra, ex.: "RES23607_ART20_LIMITE_PF"
    referencia_normativa: str  # citação legível, ex.: "Res.-TSE 23.607/2019, art. 20"
    titulo: str
    descricao: str
    item_relacionado_id: str | None = None


def chave_diligencia(achado: Achado) -> str:
    """Chave usada para casar um achado com uma entrada de
    `PrestacaoContas.diligencias_respondidas` (regra + item específico, quando
    houver, já que a mesma regra pode ser disparada por vários lançamentos)."""
    return f"{achado.regra}:{achado.item_relacionado_id or ''}"
