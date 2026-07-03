/**
 * Camada de acesso a dados com duas implementações:
 * - "http": chama o backend FastAPI (VITE_API_URL configurado)
 * - "direct": chama o Supabase diretamente do navegador (RLS protege escrita)
 *
 * Escolhida automaticamente: se VITE_API_URL estiver vazio, usa "direct".
 * Isso permite publicar o frontend como site estático (ex: GitHub Pages)
 * sem depender de um backend hospedado.
 */
import { api } from './api'
import { supabase } from './supabaseClient'
import type {
  Afastamento,
  AfastamentoStatus,
  Cargo,
  Colaborador,
  ColaboradorStatus,
  Escala,
  ZonaEleitoral,
} from '../types'

const USE_DIRECT = !(import.meta.env.VITE_API_URL as string | undefined)?.trim()

function unwrap<T>(result: { data: T | null; error: { message: string } | null }): T {
  if (result.error) throw new Error(result.error.message)
  return result.data as T
}

export function extractErrorMessage(err: unknown, fallback: string): string {
  const anyErr = err as any
  return anyErr?.response?.data?.detail ?? anyErr?.message ?? fallback
}

// ---------- Zonas ----------
export async function listZonas(): Promise<ZonaEleitoral[]> {
  if (USE_DIRECT) {
    const res = await supabase.from('zonas_eleitorais').select('*').order('numero_zona')
    return unwrap(res)
  }
  return (await api.get<ZonaEleitoral[]>('/zonas')).data
}

export async function createZona(payload: Record<string, unknown>): Promise<ZonaEleitoral> {
  if (USE_DIRECT) {
    const res = await supabase.from('zonas_eleitorais').insert(payload).select().single()
    return unwrap(res)
  }
  return (await api.post<ZonaEleitoral>('/zonas', payload)).data
}

export async function deleteZona(id: string): Promise<void> {
  if (USE_DIRECT) {
    const { error } = await supabase.from('zonas_eleitorais').delete().eq('id', id)
    if (error) throw new Error(error.message)
    return
  }
  await api.delete(`/zonas/${id}`)
}

// ---------- Cargos ----------
export async function listCargos(): Promise<Cargo[]> {
  if (USE_DIRECT) {
    const res = await supabase.from('cargos').select('*').order('nome')
    return unwrap(res)
  }
  return (await api.get<Cargo[]>('/cargos')).data
}

// ---------- Colaboradores ----------
const COLABORADOR_SELECT =
  '*, cargo:cargos(id,nome), zona_eleitoral:zonas_eleitorais(id,numero_zona,nome,municipio)'

export async function listColaboradores(filters?: { status?: ColaboradorStatus }): Promise<Colaborador[]> {
  if (USE_DIRECT) {
    let query = supabase.from('colaboradores').select(COLABORADOR_SELECT).order('nome_completo')
    if (filters?.status) query = query.eq('status', filters.status)
    const res = await query
    return unwrap(res)
  }
  return (await api.get<Colaborador[]>('/colaboradores', { params: filters })).data
}

export async function createColaborador(payload: Record<string, unknown>): Promise<Colaborador> {
  if (USE_DIRECT) {
    const res = await supabase.from('colaboradores').insert(payload).select(COLABORADOR_SELECT).single()
    return unwrap(res)
  }
  return (await api.post<Colaborador>('/colaboradores', payload)).data
}

export async function deleteColaborador(id: string): Promise<void> {
  if (USE_DIRECT) {
    const { error } = await supabase.from('colaboradores').delete().eq('id', id)
    if (error) throw new Error(error.message)
    return
  }
  await api.delete(`/colaboradores/${id}`)
}

// ---------- Escalas ----------
const ESCALA_SELECT =
  '*, colaborador:colaboradores(id,nome_completo), zona_eleitoral:zonas_eleitorais(id,numero_zona,nome)'

export async function listEscalas(): Promise<Escala[]> {
  if (USE_DIRECT) {
    const res = await supabase.from('escalas').select(ESCALA_SELECT).order('data')
    return unwrap(res)
  }
  return (await api.get<Escala[]>('/escalas')).data
}

export async function createEscala(payload: Record<string, unknown>): Promise<Escala> {
  if (USE_DIRECT) {
    const res = await supabase.from('escalas').insert(payload).select(ESCALA_SELECT).single()
    return unwrap(res)
  }
  return (await api.post<Escala>('/escalas', payload)).data
}

export async function deleteEscala(id: string): Promise<void> {
  if (USE_DIRECT) {
    const { error } = await supabase.from('escalas').delete().eq('id', id)
    if (error) throw new Error(error.message)
    return
  }
  await api.delete(`/escalas/${id}`)
}

// ---------- Afastamentos ----------
const AFASTAMENTO_SELECT = '*, colaborador:colaboradores(id,nome_completo,zona_eleitoral_id)'

export async function listAfastamentos(filters?: { status?: AfastamentoStatus }): Promise<Afastamento[]> {
  if (USE_DIRECT) {
    let query = supabase.from('afastamentos').select(AFASTAMENTO_SELECT).order('data_inicio', {
      ascending: false,
    })
    if (filters?.status) query = query.eq('status', filters.status)
    const res = await query
    return unwrap(res)
  }
  return (await api.get<Afastamento[]>('/afastamentos', { params: filters })).data
}

export async function createAfastamento(payload: Record<string, unknown>): Promise<Afastamento> {
  if (USE_DIRECT) {
    const res = await supabase.from('afastamentos').insert(payload).select(AFASTAMENTO_SELECT).single()
    return unwrap(res)
  }
  return (await api.post<Afastamento>('/afastamentos', payload)).data
}

export async function deleteAfastamento(id: string): Promise<void> {
  if (USE_DIRECT) {
    const { error } = await supabase.from('afastamentos').delete().eq('id', id)
    if (error) throw new Error(error.message)
    return
  }
  await api.delete(`/afastamentos/${id}`)
}

// ---------- Relatórios ----------
export interface Resumo {
  total_colaboradores: number
  colaboradores_ativos: number
  colaboradores_inativos: number
  colaboradores_afastados: number
  total_zonas_eleitorais: number
  afastamentos_em_andamento_hoje: number
  escalas_hoje: number
}

export async function getResumo(): Promise<Resumo> {
  if (!USE_DIRECT) return (await api.get<Resumo>('/relatorios/resumo')).data

  const hoje = new Date().toISOString().slice(0, 10)
  const colaboradores = unwrap(
    await supabase.from('colaboradores').select('id,status'),
  ) as { id: string; status: string }[]
  const zonas = unwrap(await supabase.from('zonas_eleitorais').select('id')) as { id: string }[]
  const afastamentosHoje = unwrap(
    await supabase
      .from('afastamentos')
      .select('id')
      .lte('data_inicio', hoje)
      .gte('data_fim', hoje)
      .neq('status', 'cancelado'),
  ) as { id: string }[]
  const escalasHoje = unwrap(
    await supabase.from('escalas').select('id').eq('data', hoje),
  ) as { id: string }[]

  const contagem = (status: string) => colaboradores.filter((c) => c.status === status).length

  return {
    total_colaboradores: colaboradores.length,
    colaboradores_ativos: contagem('ativo'),
    colaboradores_inativos: contagem('inativo'),
    colaboradores_afastados: contagem('afastado'),
    total_zonas_eleitorais: zonas.length,
    afastamentos_em_andamento_hoje: afastamentosHoje.length,
    escalas_hoje: escalasHoje.length,
  }
}

export interface QuadroZona {
  zona: string
  total: number
  ativos: number
}

export async function getQuadroPorZona(): Promise<QuadroZona[]> {
  if (!USE_DIRECT) return (await api.get<QuadroZona[]>('/relatorios/quadro-por-zona')).data

  const colaboradores = unwrap(
    await supabase
      .from('colaboradores')
      .select('status, zona_eleitoral:zonas_eleitorais(id,numero_zona,nome)'),
  ) as any[]

  const agregados = new Map<string, QuadroZona>()
  for (const c of colaboradores) {
    const zona = c.zona_eleitoral
    const chave = zona ? zona.id : 'sem_zona'
    const nome = zona ? `Zona ${zona.numero_zona} - ${zona.nome}` : 'Sem lotação definida'
    if (!agregados.has(chave)) agregados.set(chave, { zona: nome, total: 0, ativos: 0 })
    const item = agregados.get(chave)!
    item.total += 1
    if (c.status === 'ativo') item.ativos += 1
  }
  return [...agregados.values()].sort((a, b) => a.zona.localeCompare(b.zona))
}

export interface QuadroCargo {
  cargo: string
  total: number
  ativos: number
}

export async function getQuadroPorCargo(): Promise<QuadroCargo[]> {
  if (!USE_DIRECT) return (await api.get<QuadroCargo[]>('/relatorios/quadro-por-cargo')).data

  const colaboradores = unwrap(
    await supabase.from('colaboradores').select('status, cargo:cargos(id,nome)'),
  ) as any[]

  const agregados = new Map<string, QuadroCargo>()
  for (const c of colaboradores) {
    const cargo = c.cargo
    const chave = cargo ? cargo.id : 'sem_cargo'
    const nome = cargo ? cargo.nome : 'Sem cargo definido'
    if (!agregados.has(chave)) agregados.set(chave, { cargo: nome, total: 0, ativos: 0 })
    const item = agregados.get(chave)!
    item.total += 1
    if (c.status === 'ativo') item.ativos += 1
  }
  return [...agregados.values()].sort((a, b) => b.total - a.total)
}

export interface QuadroVinculo {
  vinculo: string
  total: number
}

export async function getQuadroPorVinculo(): Promise<QuadroVinculo[]> {
  if (!USE_DIRECT) return (await api.get<QuadroVinculo[]>('/relatorios/quadro-por-vinculo')).data

  const colaboradores = unwrap(await supabase.from('colaboradores').select('vinculo')) as {
    vinculo: string
  }[]
  const contagem = new Map<string, number>()
  for (const c of colaboradores) contagem.set(c.vinculo, (contagem.get(c.vinculo) ?? 0) + 1)
  return [...contagem.entries()].map(([vinculo, total]) => ({ vinculo, total }))
}

export interface AfastamentoPorTipo {
  tipo: string
  total: number
}

export async function getAfastamentosPorTipo(): Promise<AfastamentoPorTipo[]> {
  if (!USE_DIRECT) return (await api.get<AfastamentoPorTipo[]>('/relatorios/afastamentos-por-tipo')).data

  const afastamentos = unwrap(await supabase.from('afastamentos').select('tipo')) as { tipo: string }[]
  const contagem = new Map<string, number>()
  for (const a of afastamentos) contagem.set(a.tipo, (contagem.get(a.tipo) ?? 0) + 1)
  return [...contagem.entries()].map(([tipo, total]) => ({ tipo, total }))
}
