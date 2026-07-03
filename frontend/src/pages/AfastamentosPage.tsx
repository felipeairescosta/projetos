import { useEffect, useState, type FormEvent } from 'react'
import { api } from '../lib/api'
import {
  AFASTAMENTO_STATUS_LABELS,
  AFASTAMENTO_TIPO_LABELS,
  type Afastamento,
  type AfastamentoStatus,
  type AfastamentoTipo,
  type Colaborador,
} from '../types'

const emptyForm = {
  colaborador_id: '',
  tipo: 'ferias' as AfastamentoTipo,
  data_inicio: '',
  data_fim: '',
  status: 'agendado' as AfastamentoStatus,
  observacoes: '',
}

export function AfastamentosPage() {
  const [afastamentos, setAfastamentos] = useState<Afastamento[]>([])
  const [colaboradores, setColaboradores] = useState<Colaborador[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState<string | null>(null)

  async function load() {
    setLoading(true)
    const [a, c] = await Promise.all([
      api.get<Afastamento[]>('/afastamentos'),
      api.get<Colaborador[]>('/colaboradores'),
    ])
    setAfastamentos(a.data)
    setColaboradores(c.data)
    setLoading(false)
  }

  useEffect(() => {
    load()
  }, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await api.post('/afastamentos', {
        colaborador_id: form.colaborador_id,
        tipo: form.tipo,
        data_inicio: form.data_inicio,
        data_fim: form.data_fim,
        status: form.status,
        observacoes: form.observacoes || null,
      })
      setForm(emptyForm)
      setShowForm(false)
      await load()
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Erro ao salvar afastamento.')
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Remover este afastamento?')) return
    await api.delete(`/afastamentos/${id}`)
    await load()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900">Afastamentos</h2>
          <p className="text-sm text-slate-500">Férias, licenças e demais afastamentos dos colaboradores</p>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="rounded-md bg-blue-900 px-4 py-2 text-sm font-medium text-white hover:bg-blue-800"
        >
          {showForm ? 'Cancelar' : '+ Novo Afastamento'}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="grid grid-cols-1 gap-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm md:grid-cols-3"
        >
          <Field label="Colaborador" required>
            <select
              required
              value={form.colaborador_id}
              onChange={(e) => setForm({ ...form, colaborador_id: e.target.value })}
              className="input"
            >
              <option value="">Selecione...</option>
              {colaboradores.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.nome_completo}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Tipo">
            <select
              value={form.tipo}
              onChange={(e) => setForm({ ...form, tipo: e.target.value as AfastamentoTipo })}
              className="input"
            >
              {Object.entries(AFASTAMENTO_TIPO_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Status">
            <select
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value as AfastamentoStatus })}
              className="input"
            >
              {Object.entries(AFASTAMENTO_STATUS_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Data início" required>
            <input
              type="date"
              required
              value={form.data_inicio}
              onChange={(e) => setForm({ ...form, data_inicio: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="Data fim" required>
            <input
              type="date"
              required
              value={form.data_fim}
              onChange={(e) => setForm({ ...form, data_fim: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="Observações">
            <input
              value={form.observacoes}
              onChange={(e) => setForm({ ...form, observacoes: e.target.value })}
              className="input"
            />
          </Field>
          {error && <p className="col-span-full text-sm text-red-600">{error}</p>}
          <div className="col-span-full">
            <button
              type="submit"
              className="rounded-md bg-blue-900 px-4 py-2 text-sm font-medium text-white hover:bg-blue-800"
            >
              Salvar
            </button>
          </div>
        </form>
      )}

      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <Th>Colaborador</Th>
              <Th>Tipo</Th>
              <Th>Período</Th>
              <Th>Status</Th>
              <Th></Th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-400">
                  Carregando...
                </td>
              </tr>
            ) : afastamentos.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-400">
                  Nenhum afastamento registrado.
                </td>
              </tr>
            ) : (
              afastamentos.map((a) => (
                <tr key={a.id}>
                  <td className="px-4 py-3 font-medium">{a.colaborador?.nome_completo ?? '—'}</td>
                  <td className="px-4 py-3 text-slate-600">{AFASTAMENTO_TIPO_LABELS[a.tipo]}</td>
                  <td className="px-4 py-3 text-slate-600">
                    {formatDate(a.data_inicio)} – {formatDate(a.data_fim)}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={a.status} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDelete(a.id)}
                      className="text-xs font-medium text-red-600 hover:underline"
                    >
                      Remover
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function formatDate(d: string) {
  return new Date(d + 'T00:00:00').toLocaleDateString('pt-BR')
}

function StatusBadge({ status }: { status: AfastamentoStatus }) {
  const colors: Record<AfastamentoStatus, string> = {
    agendado: 'bg-blue-100 text-blue-800',
    em_andamento: 'bg-amber-100 text-amber-800',
    concluido: 'bg-emerald-100 text-emerald-800',
    cancelado: 'bg-slate-100 text-slate-500',
  }
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[status]}`}>
      {AFASTAMENTO_STATUS_LABELS[status]}
    </span>
  )
}

function Field({
  label,
  required,
  children,
}: {
  label: string
  required?: boolean
  children: React.ReactNode
}) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block font-medium text-slate-700">
        {label} {required && <span className="text-red-500">*</span>}
      </span>
      {children}
    </label>
  )
}

function Th({ children }: { children?: React.ReactNode }) {
  return (
    <th className="px-4 py-2.5 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
      {children}
    </th>
  )
}
