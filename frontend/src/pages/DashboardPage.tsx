import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api } from '../lib/api'
import { StatCard } from '../components/StatCard'
import { AFASTAMENTO_TIPO_LABELS, VINCULO_LABELS, type AfastamentoTipo, type Vinculo } from '../types'

interface Resumo {
  total_colaboradores: number
  colaboradores_ativos: number
  colaboradores_inativos: number
  colaboradores_afastados: number
  total_zonas_eleitorais: number
  afastamentos_em_andamento_hoje: number
  escalas_hoje: number
}

interface QuadroZona {
  zona: string
  total: number
  ativos: number
}

interface QuadroCargo {
  cargo: string
  total: number
  ativos: number
}

interface QuadroVinculo {
  vinculo: Vinculo
  total: number
}

interface AfastamentoPorTipo {
  tipo: AfastamentoTipo
  total: number
}

const PALETTE = ['#1e3a8a', '#3b82f6', '#6366f1', '#06b6d4', '#f59e0b', '#10b981', '#ef4444']

export function DashboardPage() {
  const [resumo, setResumo] = useState<Resumo | null>(null)
  const [porZona, setPorZona] = useState<QuadroZona[]>([])
  const [porCargo, setPorCargo] = useState<QuadroCargo[]>([])
  const [porVinculo, setPorVinculo] = useState<QuadroVinculo[]>([])
  const [afastamentosPorTipo, setAfastamentosPorTipo] = useState<AfastamentoPorTipo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const [r1, r2, r3, r4, r5] = await Promise.all([
          api.get<Resumo>('/relatorios/resumo'),
          api.get<QuadroZona[]>('/relatorios/quadro-por-zona'),
          api.get<QuadroCargo[]>('/relatorios/quadro-por-cargo'),
          api.get<QuadroVinculo[]>('/relatorios/quadro-por-vinculo'),
          api.get<AfastamentoPorTipo[]>('/relatorios/afastamentos-por-tipo'),
        ])
        setResumo(r1.data)
        setPorZona(r2.data)
        setPorCargo(r3.data)
        setPorVinculo(r4.data)
        setAfastamentosPorTipo(r5.data)
      } catch {
        setError('Não foi possível carregar os dados do dashboard.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <p className="text-slate-500">Carregando dashboard...</p>
  if (error) return <p className="text-red-600">{error}</p>

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900">Dashboard</h2>
        <p className="text-sm text-slate-500">
          Visão geral do quadro de colaboradores dos cartórios eleitorais do TRE-CE
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Colaboradores ativos" value={resumo?.colaboradores_ativos ?? 0} />
        <StatCard label="Afastados" value={resumo?.colaboradores_afastados ?? 0} />
        <StatCard label="Zonas eleitorais cadastradas" value={resumo?.total_zonas_eleitorais ?? 0} />
        <StatCard
          label="Afastamentos em andamento hoje"
          value={resumo?.afastamentos_em_andamento_hoje ?? 0}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-slate-700">
            Colaboradores por Zona Eleitoral
          </h3>
          {porZona.length === 0 ? (
            <EmptyState text="Nenhuma zona eleitoral cadastrada ainda." />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={porZona} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" allowDecimals={false} />
                <YAxis type="category" dataKey="zona" width={160} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="total" name="Total" fill={PALETTE[0]} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-slate-700">Colaboradores por Cargo</h3>
          {porCargo.length === 0 ? (
            <EmptyState text="Nenhum colaborador cadastrado ainda." />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={porCargo} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" allowDecimals={false} />
                <YAxis type="category" dataKey="cargo" width={160} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="total" name="Total" fill={PALETTE[1]} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-slate-700">Colaboradores por Vínculo</h3>
          {porVinculo.length === 0 ? (
            <EmptyState text="Nenhum colaborador cadastrado ainda." />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={porVinculo}
                  dataKey="total"
                  nameKey="vinculo"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  label={(entry: any) => VINCULO_LABELS[entry.vinculo as Vinculo]}
                >
                  {porVinculo.map((entry, i) => (
                    <Cell key={entry.vinculo} fill={PALETTE[i % PALETTE.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, _name, item) => [value, VINCULO_LABELS[item.payload.vinculo as Vinculo]]} />
                <Legend formatter={(value) => VINCULO_LABELS[value as Vinculo] ?? value} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="mb-4 text-sm font-semibold text-slate-700">Afastamentos por Tipo</h3>
          {afastamentosPorTipo.length === 0 ? (
            <EmptyState text="Nenhum afastamento registrado ainda." />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={afastamentosPorTipo}
                  dataKey="total"
                  nameKey="tipo"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  label={(entry: any) => AFASTAMENTO_TIPO_LABELS[entry.tipo as AfastamentoTipo]}
                >
                  {afastamentosPorTipo.map((entry, i) => (
                    <Cell key={entry.tipo} fill={PALETTE[i % PALETTE.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value, _name, item) => [
                    value,
                    AFASTAMENTO_TIPO_LABELS[item.payload.tipo as AfastamentoTipo],
                  ]}
                />
                <Legend formatter={(value) => AFASTAMENTO_TIPO_LABELS[value as AfastamentoTipo] ?? value} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  )
}

function EmptyState({ text }: { text: string }) {
  return <p className="flex h-[300px] items-center justify-center text-sm text-slate-400">{text}</p>
}
