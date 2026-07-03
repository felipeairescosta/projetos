export type Vinculo =
  | 'efetivo'
  | 'requisitado'
  | 'comissionado'
  | 'terceirizado'
  | 'estagiario'
  | 'cedido'

export type ColaboradorStatus = 'ativo' | 'inativo' | 'afastado'

export type Turno = 'manha' | 'tarde' | 'integral' | 'noite'

export type EscalaTipo = 'atendimento' | 'plantao_eleitoral' | 'plantao_especial' | 'teletrabalho'

export type AfastamentoTipo =
  | 'ferias'
  | 'licenca_medica'
  | 'licenca_maternidade'
  | 'licenca_paternidade'
  | 'licenca_premio'
  | 'licenca_capacitacao'
  | 'outros'

export type AfastamentoStatus = 'agendado' | 'em_andamento' | 'concluido' | 'cancelado'

export interface ZonaEleitoral {
  id: string
  numero_zona: number
  nome: string
  municipio: string
  endereco?: string | null
  telefone?: string | null
  email?: string | null
}

export interface Cargo {
  id: string
  nome: string
  descricao?: string | null
}

export interface Colaborador {
  id: string
  nome_completo: string
  cpf: string
  matricula?: string | null
  email?: string | null
  telefone?: string | null
  cargo_id?: string | null
  zona_eleitoral_id?: string | null
  vinculo: Vinculo
  status: ColaboradorStatus
  data_nascimento?: string | null
  data_admissao?: string | null
  data_desligamento?: string | null
  observacoes?: string | null
  cargo?: Cargo | null
  zona_eleitoral?: ZonaEleitoral | null
}

export interface Escala {
  id: string
  colaborador_id: string
  zona_eleitoral_id: string
  data: string
  turno: Turno
  tipo: EscalaTipo
  observacoes?: string | null
  colaborador?: { id: string; nome_completo: string } | null
  zona_eleitoral?: { id: string; numero_zona: number; nome: string } | null
}

export interface Afastamento {
  id: string
  colaborador_id: string
  tipo: AfastamentoTipo
  data_inicio: string
  data_fim: string
  status: AfastamentoStatus
  observacoes?: string | null
  colaborador?: { id: string; nome_completo: string } | null
}

export const VINCULO_LABELS: Record<Vinculo, string> = {
  efetivo: 'Efetivo',
  requisitado: 'Requisitado',
  comissionado: 'Comissionado',
  terceirizado: 'Terceirizado',
  estagiario: 'Estagiário',
  cedido: 'Cedido',
}

export const STATUS_LABELS: Record<ColaboradorStatus, string> = {
  ativo: 'Ativo',
  inativo: 'Inativo',
  afastado: 'Afastado',
}

export const TURNO_LABELS: Record<Turno, string> = {
  manha: 'Manhã',
  tarde: 'Tarde',
  integral: 'Integral',
  noite: 'Noite',
}

export const ESCALA_TIPO_LABELS: Record<EscalaTipo, string> = {
  atendimento: 'Atendimento',
  plantao_eleitoral: 'Plantão Eleitoral',
  plantao_especial: 'Plantão Especial',
  teletrabalho: 'Teletrabalho',
}

export const AFASTAMENTO_TIPO_LABELS: Record<AfastamentoTipo, string> = {
  ferias: 'Férias',
  licenca_medica: 'Licença Médica',
  licenca_maternidade: 'Licença Maternidade',
  licenca_paternidade: 'Licença Paternidade',
  licenca_premio: 'Licença Prêmio',
  licenca_capacitacao: 'Licença Capacitação',
  outros: 'Outros',
}

export const AFASTAMENTO_STATUS_LABELS: Record<AfastamentoStatus, string> = {
  agendado: 'Agendado',
  em_andamento: 'Em andamento',
  concluido: 'Concluído',
  cancelado: 'Cancelado',
}
