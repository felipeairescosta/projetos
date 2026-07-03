import { useEffect, useState, type FormEvent } from 'react'
import { api } from '../lib/api'
import {
  ESCALA_TIPO_LABELS,
  TURNO_LABELS,
  type Colaborador,
  type Escala,
  type EscalaTipo,
  type Turno,
  type ZonaEleitoral,
} from '../types'

const emptyForm = {
  colaborador_id: '',
  zona_eleitoral_id: '',
  data: '',
  turno: 'integral' as Turno,
  tipo: 'atendimento' as EscalaTipo,
  observacoes: '',
}

export function EscalasPage() {
  const [escalas, setEscalas] = useState<Escala[]>([])
  const [colaboradores, setColaboradores] = useState<Colaborador[]>([])
  const [zonas, setZonas] = useState<ZonaEleitoral[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState<string | null>(null)

  async function load() {
    setLoading(true)
    const [e, c, z] = await Promise.all([
      api.get<Escala[]>('/escalas'),
      api.get<Colaborador[]>('/colaboradores'),
      api.get<ZonaEleitoral[]>('/zonas'),
    ])
    setEscalas(e.data)
    setColaboradores(c.data)
    setZonas(z.data)
    setLoading(false)
  }

  useEffect(() => {
    load()
  }, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await api.post('/escalas', {
        colaborador_id: form.colaborador_id,
        zona_eleitoral_id: form.zona_eleitoral_id,
        data: form.data,
        turno: form.turno,
        tipo: form.tipo,
        observacoes: form.observacoes || null,
      })
      setForm(emptyForm)
      setShowForm(false)
      await load()
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Erro ao salvar escala.')
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Remover esta escala?')) return
    await api.delete(`/escalas/${id}`)
    await load()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900">Escalas</h2>
          <p className="text-sm text-slate-500">
            Escalas de atendimento e plantões nos cartórios/zonas eleitorais
          </p>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="rounded-md bg-blue-900 px-4 py-2 text-sm font-medium text-white hover:bg-blue-800"
        >
          {showForm ? 'Cancelar' : '+ Nova Escala'}
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
          <Field label="Zona Eleitoral" required>
            <select
              required
              value={form.zona_eleitoral_id}
              onChange={(e) => setForm({ ...form, zona_eleitoral_id: e.target.value })}
              className="input"
            >
              <option value="">Selecione...</option>
              {zonas.map((z) => (
                <option key={z.id} value={z.id}>
                  {z.numero_zona}ª Zona - {z.nome}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Data" required>
            <input
              type="date"
              required
              value={form.data}
              onChange={(e) => setForm({ ...form, data: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="Turno">
            <select
              value={form.turno}
              onChange={(e) => setForm({ ...form, turno: e.target.value as Turno })}
              className="input"
            >
              {Object.entries(TURNO_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Tipo">
            <select
              value={form.tipo}
              onChange={(e) => setForm({ ...form, tipo: e.target.value as EscalaTipo })}
              className="input"
            >
              {Object.entries(ESCALA_TIPO_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
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
              <Th>Data</Th>
              <Th>Colaborador</Th>
              <Th>Zona</Th>
              <Th>Turno</Th>
              <Th>Tipo</Th>
              <Th></Th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-slate-400">
                  Carregando...
                </td>
              </tr>
            ) : escalas.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-slate-400">
                  Nenhuma escala cadastrada.
                </td>
              </tr>
            ) : (
              escalas.map((e) => (
                <tr key={e.id}>
                  <td className="px-4 py-3 font-medium">
                    {new Date(e.data + 'T00:00:00').toLocaleDateString('pt-BR')}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{e.colaborador?.nome_completo ?? '—'}</td>
                  <td className="px-4 py-3 text-slate-600">
                    {e.zona_eleitoral ? `${e.zona_eleitoral.numero_zona}ª - ${e.zona_eleitoral.nome}` : '—'}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{TURNO_LABELS[e.turno]}</td>
                  <td className="px-4 py-3 text-slate-600">{ESCALA_TIPO_LABELS[e.tipo]}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDelete(e.id)}
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
