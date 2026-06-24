"""
Gerador de objetos de processos PJe da Justiça Eleitoral.

Produz dados sintéticos (1º e 2º Grau) compatíveis com o schema
dos loaders existentes (load_1g / load_2g), sem dependências externas
além de pandas.

Número CNJ gerado seguindo a estrutura:
    NNNNNNN-DD.AAAA.8.06.OOOO
    - 8  → Justiça Eleitoral
    - 06 → TRE-CE

Classificação de tipo de processo e peças processuais:
    - ORIGINÁRIO → petição inicial
    - RECURSO    → sentença + recurso/razões + contrarrazões
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import List, Optional

import pandas as pd

# ---------------------------------------------------------------------------
# Constantes da Justiça Eleitoral do Ceará
# ---------------------------------------------------------------------------

_SEGMENTO_ELEITORAL = 8
_TRIBUNAL_CE = 6  # TRE-CE

# Zonas eleitorais do Ceará (representativas)
_ZONAS_CE: list[tuple[int, str]] = [
    (1,  "FORTALEZA"),   (2,  "FORTALEZA"),    (3,  "FORTALEZA"),
    (4,  "FORTALEZA"),   (5,  "FORTALEZA"),    (6,  "FORTALEZA"),
    (7,  "FORTALEZA"),   (8,  "FORTALEZA"),    (9,  "FORTALEZA"),
    (10, "FORTALEZA"),   (11, "FORTALEZA"),    (12, "CAUCAIA"),
    (13, "MARACANAÚ"),   (14, "JUAZEIRO DO NORTE"), (15, "CRATO"),
    (16, "SOBRAL"),      (17, "QUIXADÁ"),      (18, "IGUATU"),
    (19, "LIMOEIRO DO NORTE"), (20, "ITAPIPOCA"), (21, "ARACATI"),
    (22, "RUSSAS"),      (23, "TIANGUÁ"),      (24, "CAMOCIM"),
    (25, "BREJO SANTO"), (26, "MOMBAÇA"),      (27, "BATURITÉ"),
    (28, "PACATUBA"),    (29, "HORIZONTE"),    (30, "EUSÉBIO"),
    (31, "BARBALHA"),    (32, "CANINDÉ"),      (33, "CASCAVEL"),
    (34, "CRATEÚS"),     (35, "MISSÃO VELHA"), (36, "TAUÁ"),
    (37, "PACAJUS"),     (38, "BEBERIBE"),     (39, "MORADA NOVA"),
    (40, "SENADOR POMPEU"),
]

# Classes processuais — 1º Grau (zonas eleitorais)
CLASSES_1G: list[str] = [
    "AÇÃO DE INVESTIGAÇÃO JUDICIAL ELEITORAL",
    "REGISTRO DE CANDIDATURA",
    "AÇÃO DE IMPUGNAÇÃO DE REGISTRO DE CANDIDATURA",
    "REPRESENTAÇÃO ELEITORAL",
    "NOTÍCIA DE INELEGIBILIDADE",
    "ALISTAMENTO ELEITORAL",
    "TRANSFERÊNCIA DE DOMICÍLIO ELEITORAL",
    "REVISÃO DO ELEITORADO",
    "RECURSO CONTRA EXPEDIÇÃO DE DIPLOMA",
    "MEDIDA CAUTELAR ELEITORAL",
    "RECLAMAÇÃO ELEITORAL",
    "MANDADO DE SEGURANÇA",
    "HABEAS CORPUS",
    "HABEAS DATA",
    "AÇÃO RESCISÓRIA ELEITORAL",
    "NULIDADE DE VOTAÇÃO",
    "RECURSO INOMINADO",
    "EMBARGOS DE DECLARAÇÃO",
]

# Pesos para simular distribuição realista no 1G
_PESOS_1G: list[float] = [
    8, 20, 5, 12, 3, 10, 8, 5, 4, 3, 4, 3, 1, 1, 1, 1, 6, 5,
]

# Classes processuais — 2º Grau (TRE-CE plenário / turmas)
CLASSES_2G: list[str] = [
    "RECURSO ORDINÁRIO",
    "REGISTRO DE CANDIDATURA",
    "AÇÃO DE INVESTIGAÇÃO JUDICIAL ELEITORAL",
    "AÇÃO DE IMPUGNAÇÃO DE MANDATO ELETIVO",
    "RECURSO CONTRA EXPEDIÇÃO DE DIPLOMA",
    "AGRAVO REGIMENTAL",
    "MANDADO DE SEGURANÇA",
    "HABEAS CORPUS",
    "AÇÃO RESCISÓRIA ELEITORAL",
    "CONSULTA",
    "PRESTAÇÃO DE CONTAS",
    "RECURSO INOMINADO",
    "RECURSO ESPECIAL ELEITORAL",
    "EMBARGOS DE DECLARAÇÃO",
    "MEDIDA CAUTELAR ELEITORAL",
    "RECLAMAÇÃO ELEITORAL",
    "NOTÍCIA DE INELEGIBILIDADE",
]

_PESOS_2G: list[float] = [
    20, 15, 10, 6, 5, 10, 8, 2, 2, 3, 5, 7, 3, 8, 3, 5, 3,
]

# Órgãos julgadores — 2º Grau
ORGAOS_2G: list[str] = [
    "PLENÁRIO",
    "PRIMEIRA TURMA",
    "SEGUNDA TURMA",
    "PRESIDENTE DO TRE-CE",
    "VICE-PRESIDENTE DO TRE-CE",
    "RELATOR Nº 1",
    "RELATOR Nº 2",
    "RELATOR Nº 3",
    "RELATOR Nº 4",
    "RELATOR Nº 5",
    "RELATOR Nº 6",
    "RELATOR Nº 7",
]

_PESOS_ORGAOS_2G: list[float] = [
    15, 20, 18, 5, 3, 7, 7, 7, 6, 5, 5, 4,
]

# Tipos de decisão
_TIPOS_DECISAO: list[str] = [
    "DECISÃO COLEGIADA",
    "DECISÃO MONOCRÁTICA",
    "",
]

_PESOS_DECISAO: list[float] = [30, 45, 25]

# Tarefas PJe (mapeadas às unidades em data_loader.py)
_TAREFAS_CPROC: list[str] = [
    "Manter Processo Arquivado",
    "Manter Processos Expedidos",
    "Manter Processos Devolvidos a Origem",
    "Manter Processos Suspensos ou Sobrestados",
    "Processos remetidos ao TSE",
    "Processos remetidos à zona",
    "Aguardando apreciação de outra instância",
    "Aguardando apreciação pela instância superior",
    "Processo com prazo em curso",
    "Verificar Pendências",
    "Analisar determinação",
    "Analisar petição avulsa de autuação",
    "Analisar Processos",
    "Elaborar Documentos",
    "Preparar comunicação",
]

_TAREFAS_ASSESSORIA: list[str] = [
    "Minutar Relatório, Voto e Ementa",
    "Conferir Relatório, Voto e Ementa",
    "Revisar Relatório, Voto e Ementa",
    "Assinar acórdão ou resolução",
    "Assinar Documentos",
    "Lançar movimentos de Julgamento Colegiado",
    "Realizar triagem ordinários",
    "Realizar triagem urgentes",
    "Aguarda Julgamento - incluído em pauta virtual",
    "Aguarda Julgamento - incluído em pauta",
    "Aguarda Sessão de Julgamento Virtual",
    "Aguarda Sessão de Julgamento",
    "Incluído em pauta",
    "Elaborar voto vista",
    "Analisar Petição Avulsa",
]

_TAREFAS_OUTRAS: list[str] = [
    "Analisar Processo - ASEPA",
    "Analisar Processo - Corregedoria",
]


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def _calcular_digito_verificador(nr_seq: int, ano: int, tt: int, oooo: int) -> str:
    """
    Calcula os dois dígitos verificadores do número CNJ (Resolução CNJ n° 65/2008).

    Formula: DD = 97 - (int(NNNNNNN_00_AAAA_J_TT_OOOO) % 97)
    onde J = 8 (Justiça Eleitoral).
    """
    base = f"{nr_seq:07d}00{ano:04d}{_SEGMENTO_ELEITORAL:01d}{tt:02d}{oooo:04d}"
    remainder = int(base) % 97
    dd = 97 - remainder
    return f"{dd:02d}"


def _numero_cnj(nr_seq: int, ano: int, oooo: int, tt: int = _TRIBUNAL_CE) -> str:
    """Formata um número CNJ completo no padrão NNNNNNN-DD.AAAA.J.TT.OOOO."""
    dd = _calcular_digito_verificador(nr_seq, ano, tt, oooo)
    return f"{nr_seq:07d}-{dd}.{ano:04d}.{_SEGMENTO_ELEITORAL}.{tt:02d}.{oooo:04d}"


def _data_aleatoria(ano: int, mes: Optional[int] = None) -> datetime:
    """Gera uma data aleatória dentro do ano (e mês, se fornecido)."""
    m = mes if mes else random.randint(1, 12)
    dia_max = (date(ano, m % 12 + 1, 1) - timedelta(days=1)).day if m < 12 else 31
    dia = random.randint(1, dia_max)
    hora = random.randint(7, 18)
    minuto = random.randint(0, 59)
    return datetime(ano, m, dia, hora, minuto, 0)


def _escolher_ponderado(opcoes: list, pesos: list):
    return random.choices(opcoes, weights=pesos, k=1)[0]


# ---------------------------------------------------------------------------
# Classificação de tipo de processo e peças processuais
# ---------------------------------------------------------------------------

class TipoProcesso(str, Enum):
    """Distingue processos originários de recursos eleitorais."""
    ORIGINARIO = "Originário"
    RECURSO = "Recurso"


# Prefixos que identificam inequivocamente um recurso
_PREFIXOS_RECURSO: tuple[str, ...] = ("RECURSO", "AGRAVO", "EMBARGOS")


def classificar_tipo_processo(classe: str) -> TipoProcesso:
    """
    Classifica uma classe processual como originário ou recurso.

    Regra: qualquer classe que comece com 'RECURSO', 'AGRAVO' ou 'EMBARGOS'
    é tratada como recurso; as demais são processos originários.
    """
    normalizada = classe.strip().upper()
    if any(normalizada.startswith(p) for p in _PREFIXOS_RECURSO):
        return TipoProcesso.RECURSO
    return TipoProcesso.ORIGINARIO


@dataclass
class DocumentoProcessual:
    """
    Representa uma peça processual associada a um processo PJe.

    Atributos
    ----------
    tipo        : identificador interno da peça
                  ("PETICAO_INICIAL" | "SENTENCA" | "RECURSO" | "CONTRARRAZOES")
    nome        : rótulo exibido na interface
    conteudo    : texto extraído do arquivo (None enquanto não carregado)
    nome_arquivo: nome original do arquivo enviado pelo usuário
    """

    tipo: str
    nome: str
    conteudo: Optional[str] = None
    nome_arquivo: Optional[str] = None

    @property
    def carregado(self) -> bool:
        return self.conteudo is not None


def pecas_requeridas(tipo: TipoProcesso) -> List[DocumentoProcessual]:
    """
    Retorna a lista de peças que devem ser lidas para cada tipo de processo.

    - Originário → petição inicial
    - Recurso    → sentença, recurso/razões, contrarrazões
    """
    if tipo == TipoProcesso.ORIGINARIO:
        return [
            DocumentoProcessual(tipo="PETICAO_INICIAL", nome="Petição Inicial"),
        ]
    return [
        DocumentoProcessual(tipo="SENTENCA",       nome="Sentença"),
        DocumentoProcessual(tipo="RECURSO",        nome="Recurso / Razões"),
        DocumentoProcessual(tipo="CONTRARRAZOES",  nome="Contrarrazões"),
    ]


# ---------------------------------------------------------------------------
# Dataclasses de processo
# ---------------------------------------------------------------------------

@dataclass
class ProcessoEleitoral1G:
    """Representa um processo PJe do 1º Grau da Justiça Eleitoral."""

    nr_processo: str
    classe: str
    orgao: str
    zona: int
    municipio: str
    ano: int
    mes: int
    DT_AUTUACAO: datetime
    tipo_processo: TipoProcesso = field(init=False)
    documentos: List[DocumentoProcessual] = field(init=False)

    def __post_init__(self) -> None:
        self.tipo_processo = classificar_tipo_processo(self.classe)
        self.documentos = pecas_requeridas(self.tipo_processo)

    def to_dict(self) -> dict:
        return {
            "nr_processo": self.nr_processo,
            "classe": self.classe,
            "orgao": self.orgao,
            "ano": self.ano,
            "mes": self.mes,
            "DT_AUTUACAO": self.DT_AUTUACAO,
        }


@dataclass
class ProcessoEleitoral2G:
    """Representa um processo PJe do 2º Grau da Justiça Eleitoral (TRE-CE)."""

    nr_processo: str
    classe: str
    orgao: str
    ano: int
    mes: int
    tipo_decisao: str
    tarefas: str
    dt_transito: str
    dt_distribuicao: datetime
    situacao: str
    decisao: str
    unidade: str
    tipo_processo: TipoProcesso = field(init=False)
    documentos: List[DocumentoProcessual] = field(init=False)

    def __post_init__(self) -> None:
        self.tipo_processo = classificar_tipo_processo(self.classe)
        self.documentos = pecas_requeridas(self.tipo_processo)

    def to_dict(self) -> dict:
        return {
            "nr_processo": self.nr_processo,
            "classe": self.classe,
            "orgao": self.orgao,
            "ano": self.ano,
            "mes": self.mes,
            "tipo_decisao": self.tipo_decisao,
            "tarefas": self.tarefas,
            "dt_transito": self.dt_transito,
            "dt_distribuicao": self.dt_distribuicao,
            "situacao": self.situacao,
            "decisao": self.decisao,
            "unidade": self.unidade,
        }


# ---------------------------------------------------------------------------
# Gerador principal
# ---------------------------------------------------------------------------

class GeradorProcessosPJe:
    """
    Gerador de objetos de processos PJe para a Justiça Eleitoral (TRE-CE).

    Uso básico:
        gerador = GeradorProcessosPJe(seed=42)
        df_1g = gerador.gerar_dataframe_1g(n=500, anos=[2022, 2023, 2024])
        df_2g = gerador.gerar_dataframe_2g(n=300, anos=[2022, 2023, 2024])
    """

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self._contador_1g: dict[tuple[int, int], int] = {}
        self._contador_2g: dict[tuple[int, int], int] = {}

    # ------------------------------------------------------------------
    # Geração de processos individuais
    # ------------------------------------------------------------------

    def gerar_processo_1g(
        self,
        ano: Optional[int] = None,
        mes: Optional[int] = None,
        classe: Optional[str] = None,
        zona: Optional[int] = None,
    ) -> ProcessoEleitoral1G:
        """Gera um único objeto ProcessoEleitoral1G."""
        ano = ano or random.randint(2020, 2024)
        mes = mes or random.randint(1, 12)

        zona_num, municipio = (
            _ZONAS_CE[zona - 1] if zona else random.choice(_ZONAS_CE)
        )
        classe = classe or _escolher_ponderado(CLASSES_1G, _PESOS_1G)

        chave = (ano, zona_num)
        self._contador_1g[chave] = self._contador_1g.get(chave, 0) + 1
        nr_seq = self._contador_1g[chave]

        return ProcessoEleitoral1G(
            nr_processo=_numero_cnj(nr_seq, ano, oooo=zona_num),
            classe=classe,
            orgao=f"ZONA ELEITORAL Nº {zona_num:03d} - {municipio}",
            zona=zona_num,
            municipio=municipio,
            ano=ano,
            mes=mes,
            DT_AUTUACAO=_data_aleatoria(ano, mes),
        )

    def gerar_processo_2g(
        self,
        ano: Optional[int] = None,
        mes: Optional[int] = None,
        classe: Optional[str] = None,
        orgao: Optional[str] = None,
    ) -> ProcessoEleitoral2G:
        """Gera um único objeto ProcessoEleitoral2G."""
        ano = ano or random.randint(2020, 2024)
        mes = mes or random.randint(1, 12)

        classe = classe or _escolher_ponderado(CLASSES_2G, _PESOS_2G)
        orgao = orgao or _escolher_ponderado(ORGAOS_2G, _PESOS_ORGAOS_2G)
        tipo_decisao = _escolher_ponderado(_TIPOS_DECISAO, _PESOS_DECISAO)

        # Tarefa e unidade
        sorteio_tarefa = random.random()
        if sorteio_tarefa < 0.40:
            tarefa = random.choice(_TAREFAS_CPROC)
        elif sorteio_tarefa < 0.75:
            tarefa = random.choice(_TAREFAS_ASSESSORIA)
        elif sorteio_tarefa < 0.82:
            tarefa = random.choice(_TAREFAS_OUTRAS)
        else:
            tarefa = ""

        # Situação derivada da tarefa
        situacao = _inferir_situacao(tarefa)
        decisao = _inferir_decisao(tipo_decisao)
        unidade = _inferir_unidade(tarefa)

        # Data de trânsito (apenas processos arquivados)
        dt_dist = _data_aleatoria(ano, mes)
        dt_transito = ""
        if situacao == "Arquivado" and random.random() > 0.3:
            dias = random.randint(30, 730)
            dt_transito_dt = dt_dist + timedelta(days=dias)
            if dt_transito_dt.year <= ano + 2:
                dt_transito = dt_transito_dt.strftime("%d/%m/%Y %H:%M:%S")

        chave = (ano, 0)
        self._contador_2g[chave] = self._contador_2g.get(chave, 0) + 1
        nr_seq = self._contador_2g[chave]

        return ProcessoEleitoral2G(
            nr_processo=_numero_cnj(nr_seq, ano, oooo=0),
            classe=classe,
            orgao=orgao,
            ano=ano,
            mes=mes,
            tipo_decisao=tipo_decisao,
            tarefas=tarefa,
            dt_transito=dt_transito,
            dt_distribuicao=dt_dist,
            situacao=situacao,
            decisao=decisao,
            unidade=unidade,
        )

    # ------------------------------------------------------------------
    # Geração em lote → DataFrame
    # ------------------------------------------------------------------

    def gerar_lista_1g(
        self,
        n: int = 100,
        anos: Optional[List[int]] = None,
    ) -> List[ProcessoEleitoral1G]:
        """Retorna uma lista de n ProcessoEleitoral1G."""
        anos = anos or list(range(2020, 2025))
        return [self.gerar_processo_1g(ano=random.choice(anos)) for _ in range(n)]

    def gerar_lista_2g(
        self,
        n: int = 100,
        anos: Optional[List[int]] = None,
    ) -> List[ProcessoEleitoral2G]:
        """Retorna uma lista de n ProcessoEleitoral2G."""
        anos = anos or list(range(2020, 2025))
        return [self.gerar_processo_2g(ano=random.choice(anos)) for _ in range(n)]

    def gerar_dataframe_1g(
        self,
        n: int = 100,
        anos: Optional[List[int]] = None,
    ) -> pd.DataFrame:
        """
        Gera um DataFrame do 1º Grau com o mesmo schema de load_1g():
        nr_processo, classe, orgao, ano, mes, DT_AUTUACAO
        """
        registros = [p.to_dict() for p in self.gerar_lista_1g(n=n, anos=anos)]
        df = pd.DataFrame(registros)
        df["DT_AUTUACAO"] = pd.to_datetime(df["DT_AUTUACAO"])
        df["ano"] = df["ano"].astype("Int64")
        df["mes"] = df["mes"].astype("Int64")
        return df[["nr_processo", "classe", "orgao", "ano", "mes", "DT_AUTUACAO"]]

    def gerar_dataframe_2g(
        self,
        n: int = 100,
        anos: Optional[List[int]] = None,
    ) -> pd.DataFrame:
        """
        Gera um DataFrame do 2º Grau com o mesmo schema de load_2g():
        nr_processo, classe, orgao, ano, mes, tipo_decisao,
        tarefas, dt_transito, dt_distribuicao, situacao, decisao, unidade
        """
        registros = [p.to_dict() for p in self.gerar_lista_2g(n=n, anos=anos)]
        df = pd.DataFrame(registros)
        df["dt_distribuicao"] = pd.to_datetime(df["dt_distribuicao"])
        df["ano"] = df["ano"].astype("Int64")
        df["mes"] = df["mes"].astype("Int64")
        return df[[
            "nr_processo", "classe", "orgao", "ano", "mes",
            "tipo_decisao", "tarefas", "dt_transito", "dt_distribuicao",
            "situacao", "decisao", "unidade",
        ]]


# ---------------------------------------------------------------------------
# Funções auxiliares de classificação (espelham data_loader.py)
# ---------------------------------------------------------------------------

def _inferir_situacao(tarefa: str) -> str:
    if not tarefa:
        return "Em tramitação"
    if "Arquivado" in tarefa or "arquivado" in tarefa:
        return "Arquivado"
    if any(k in tarefa for k in ("Expedido", "Devolvido", "remetido", "Origem")):
        return "Expedido/Devolvido"
    if "Aguardando" in tarefa or "Aguarda" in tarefa:
        return "Aguardando"
    return "Em tramitação"


def _inferir_decisao(tipo_decisao: str) -> str:
    if tipo_decisao == "DECISÃO COLEGIADA":
        return "Decisão Colegiada"
    if tipo_decisao == "DECISÃO MONOCRÁTICA":
        return "Decisão Monocrática"
    return "Sem decisão"


def _inferir_unidade(tarefa: str) -> str:
    if not tarefa:
        return "SEM TAREFA"
    _MAPA = {
        "Minutar Relatório": "ASSESSORIA",
        "Conferir Relatório": "ASSESSORIA",
        "Revisar Relatório": "ASSESSORIA",
        "Assinar": "ASSESSORIA",
        "Lançar movimento": "ASSESSORIA",
        "Realizar triagem": "ASSESSORIA",
        "Aguarda Julgamento": "ASSESSORIA",
        "Aguarda Sessão": "ASSESSORIA",
        "Incluído em pauta": "ASSESSORIA",
        "Elaborar voto": "ASSESSORIA",
        "Analisar Petição": "ASSESSORIA",
        "Petições": "ASSESSORIA",
        "Manter Processo": "CPROC",
        "Manter Processos": "CPROC",
        "Processos remetidos": "CPROC",
        "Aguardando apreciação": "CPROC",
        "Processo com prazo": "CPROC",
        "Verificar": "CPROC",
        "Analisar determinação": "CPROC",
        "Analisar petição avulsa": "CPROC",
        "Analisar Processos": "CPROC",
        "Elaborar Documentos": "CPROC",
        "Preparar comunicação": "CPROC",
        "Analisar Processo - ASEPA": "OUTRAS",
        "Analisar Processo - Corregedoria": "OUTRAS",
    }
    for chave, unidade in _MAPA.items():
        if chave in tarefa:
            return unidade
    return "SEM CLASSIFICAÇÃO"


# ---------------------------------------------------------------------------
# Exportações públicas
# ---------------------------------------------------------------------------

__all__ = [
    "TipoProcesso",
    "DocumentoProcessual",
    "classificar_tipo_processo",
    "pecas_requeridas",
    "ProcessoEleitoral1G",
    "ProcessoEleitoral2G",
    "GeradorProcessosPJe",
    "CLASSES_1G",
    "CLASSES_2G",
    "ORGAOS_2G",
]
