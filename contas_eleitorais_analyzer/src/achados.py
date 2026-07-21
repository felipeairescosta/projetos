"""Estrutura dos achados (findings) gerados pela análise das contas."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severidade(str, Enum):
    INFO = "INFO"
    ALERTA = "ALERTA"
    IRREGULARIDADE = "IRREGULARIDADE"
    GRAVE = "GRAVE"  # risco de desaprovação das contas / art. 30-A Lei 9.504


@dataclass
class Achado:
    severidade: Severidade
    regra: str  # identificador curto da regra, ex.: "RES23607_ART20_LIMITE_PF"
    referencia_normativa: str  # citação legível, ex.: "Res.-TSE 23.607/2019, art. 20"
    titulo: str
    descricao: str
    item_relacionado_id: str | None = None
