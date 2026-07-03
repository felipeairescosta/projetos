from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class VinculoTipo(str, Enum):
    efetivo = "efetivo"
    requisitado = "requisitado"
    comissionado = "comissionado"
    terceirizado = "terceirizado"
    estagiario = "estagiario"
    cedido = "cedido"


class ColaboradorStatus(str, Enum):
    ativo = "ativo"
    inativo = "inativo"
    afastado = "afastado"


class TurnoTipo(str, Enum):
    manha = "manha"
    tarde = "tarde"
    integral = "integral"
    noite = "noite"


class EscalaTipo(str, Enum):
    atendimento = "atendimento"
    plantao_eleitoral = "plantao_eleitoral"
    plantao_especial = "plantao_especial"
    teletrabalho = "teletrabalho"


class AfastamentoTipo(str, Enum):
    ferias = "ferias"
    licenca_medica = "licenca_medica"
    licenca_maternidade = "licenca_maternidade"
    licenca_paternidade = "licenca_paternidade"
    licenca_premio = "licenca_premio"
    licenca_capacitacao = "licenca_capacitacao"
    outros = "outros"


class AfastamentoStatus(str, Enum):
    agendado = "agendado"
    em_andamento = "em_andamento"
    concluido = "concluido"
    cancelado = "cancelado"


# ---------- Zonas eleitorais ----------
class ZonaEleitoralBase(BaseModel):
    numero_zona: int
    nome: str
    municipio: str
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None


class ZonaEleitoralCreate(ZonaEleitoralBase):
    pass


class ZonaEleitoralUpdate(BaseModel):
    numero_zona: Optional[int] = None
    nome: Optional[str] = None
    municipio: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None


class ZonaEleitoral(ZonaEleitoralBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


# ---------- Cargos ----------
class CargoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None


class CargoCreate(CargoBase):
    pass


class Cargo(CargoBase):
    id: UUID
    created_at: datetime


# ---------- Colaboradores ----------
class ColaboradorBase(BaseModel):
    nome_completo: str
    cpf: str = Field(min_length=11, max_length=14)
    matricula: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    cargo_id: Optional[UUID] = None
    zona_eleitoral_id: Optional[UUID] = None
    vinculo: VinculoTipo = VinculoTipo.efetivo
    status: ColaboradorStatus = ColaboradorStatus.ativo
    data_nascimento: Optional[date] = None
    data_admissao: Optional[date] = None
    data_desligamento: Optional[date] = None
    observacoes: Optional[str] = None


class ColaboradorCreate(ColaboradorBase):
    pass


class ColaboradorUpdate(BaseModel):
    nome_completo: Optional[str] = None
    cpf: Optional[str] = None
    matricula: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    cargo_id: Optional[UUID] = None
    zona_eleitoral_id: Optional[UUID] = None
    vinculo: Optional[VinculoTipo] = None
    status: Optional[ColaboradorStatus] = None
    data_nascimento: Optional[date] = None
    data_admissao: Optional[date] = None
    data_desligamento: Optional[date] = None
    observacoes: Optional[str] = None


class Colaborador(ColaboradorBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


# ---------- Escalas ----------
class EscalaBase(BaseModel):
    colaborador_id: UUID
    zona_eleitoral_id: UUID
    data: date
    turno: TurnoTipo = TurnoTipo.integral
    tipo: EscalaTipo = EscalaTipo.atendimento
    observacoes: Optional[str] = None


class EscalaCreate(EscalaBase):
    pass


class EscalaUpdate(BaseModel):
    colaborador_id: Optional[UUID] = None
    zona_eleitoral_id: Optional[UUID] = None
    data: Optional[date] = None
    turno: Optional[TurnoTipo] = None
    tipo: Optional[EscalaTipo] = None
    observacoes: Optional[str] = None


class Escala(EscalaBase):
    id: UUID
    created_at: datetime


# ---------- Afastamentos ----------
class AfastamentoBase(BaseModel):
    colaborador_id: UUID
    tipo: AfastamentoTipo
    data_inicio: date
    data_fim: date
    status: AfastamentoStatus = AfastamentoStatus.agendado
    observacoes: Optional[str] = None


class AfastamentoCreate(AfastamentoBase):
    pass


class AfastamentoUpdate(BaseModel):
    colaborador_id: Optional[UUID] = None
    tipo: Optional[AfastamentoTipo] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    status: Optional[AfastamentoStatus] = None
    observacoes: Optional[str] = None


class Afastamento(AfastamentoBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
