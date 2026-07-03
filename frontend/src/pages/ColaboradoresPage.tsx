import { useEffect, useState, type FormEvent } from 'react'
import { api } from '../lib/api'
import {
  STATUS_LABELS,
  VINCULO_LABELS,
  type Cargo,
  type Colaborador,
  type ColaboradorStatus,
  type Vinculo,
  type ZonaEleitoral,
} from '../types'

const emptyForm = {
  nome_completo: '',
  cpf: '',
  matricula: '',
  email: '',
  telefone: '',
  cargo_id: '',
  zona_eleitoral_id: '',
  vinculo: 'efetivo' as Vinculo,
  status: 'ativo' as ColaboradorStatus,
  data_nascimento: '',
  data_admissao: '',
}

export function ColaboradoresPage() {
  const [colaboradores, setColaboradores] = useState<Colaborador[]>([])
  const [zonas, setZonas] = useState<ZonaEleitoral[]>([])
  const [cargos, setCargos] = useState<Cargo[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState<string | null>(null)
  const [filtroStatus, setFiltroStatus] = useState<string>('')
  const [busca, setBusca] = useState('')

  async function load() {
    setLoading(true)
    const [c, z, cg] = await Promise.all([
      api.get<Colaborador[]>('/colaboradores', {
        params: filtroStatus ? { status: filtroStatus } : {},
      }),
      api.get<ZonaEleitoral[]>('/zonas'),
      api.get<Cargo[]>('/cargos'),
    ])
    setColaboradores(c.data)
    setZonas(z.data)
    setCargos(cg.data)
    setLoading(false)
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtroStatus])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await api.post('/colaboradores', {
        nome_completo: form.nome_completo,
        cpf: form.cpf.replace(/\D/g, ''),
        matricula: form.matricula || null,
        email: form.email || null,
        telefone: form.telefone || null,
        cargo_id: form.cargo_id || null,
        zona_eleitoral_id: form.zona_eleitoral_id || null,
        vinculo: form.vinculo,
        status: form.status,
        data_nascimento: form.data_nascimento || null,
        data_admissao: form.data_admissao || null,
      })
      setForm(emptyForm)
      setShowForm(false)
      await load()
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Erro ao salvar colaborador.')
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Remover este colaborador?')) return
    await api.delete(`/colaboradores/${id}`)
    await load()
  }

  const filtrados = colaboradores.filter((c) =>
    c.nome_completo.toLowerCase().includes(busca.toLowerCase()),
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900">Colaboradores</h2>
          <p className="text-sm text-slate-500">
            Cadastro dos colaboradores lotados nos cartórios eleitorais do TRE-CE
          </p>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="rounded-md bg-blue-900 px-4 py-2 text-sm font-medium text-white hover:bg-blue-800"
        >
          {showForm ? 'Cancelar' : '+ Novo Colaborador'}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="grid grid-cols-1 gap-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm md:grid-cols-3"
        >
          <Field label="Nome completo" required>
            <input
              required
              value={form.nome_completo}
              onChange={(e) => setForm({ ...form, nome_completo: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="CPF" required>
            <input
              required
              value={form.cpf}
              onChange={(e) => setForm({ ...form, cpf: e.target.value })}
              className="input"
              placeholder="000.000.000-00"
            />
          </Field>
          <Field label="Matrícula">
            <input
              value={form.matricula}
              onChange={(e) => setForm({ ...form, matricula: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="E-mail">
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="Telefone">
            <input
              value={form.telefone}
              onChange={(e) => setForm({ ...form, telefone: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="Cargo">
            <select
              value={form.cargo_id}
              onChange={(e) => setForm({ ...form, cargo_id: e.target.value })}
              className="input"
            >
              <option value="">Selecione...</option>
              {cargos.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.nome}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Zona Eleitoral (lotação)">
            <select
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
          <Field label="Vínculo">
            <select
              value={form.vinculo}
              onChange={(e) => setForm({ ...form, vinculo: e.target.value as Vinculo })}
              className="input"
            >
              {Object.entries(VINCULO_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Status">
            <select
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value as ColaboradorStatus })}
              className="input"
            >
              {Object.entries(STATUS_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Data de nascimento">
            <input
              type="date"
              value={form.data_nascimento}
              onChange={(e) => setForm({ ...form, data_nascimento: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="Data de admissão">
            <input
              type="date"
              value={form.data_admissao}
              onChange={(e) => setForm({ ...form, data_admissao: e.target.value })}
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

      <div className="flex flex-wrap gap-3">
        <input
          placeholder="Buscar por nome..."
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          className="input max-w-xs"
        />
        <select
          value={filtroStatus}
          onChange={(e) => setFiltroStatus(e.target.value)}
          className="input max-w-xs"
        >
          <option value="">Todos os status</option>
          {Object.entries(STATUS_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>

      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <Th>Nome</Th>
              <Th>Cargo</Th>
              <Th>Zona / Cartório</Th>
              <Th>Vínculo</Th>
              <Th>Status</Th>
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
            ) : filtrados.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-slate-400">
                  Nenhum colaborador encontrado.
                </td>
              </tr>
            ) : (
              filtrados.map((c) => (
                <tr key={c.id}>
                  <td className="px-4 py-3 font-medium">{c.nome_completo}</td>
                  <td className="px-4 py-3 text-slate-600">{c.cargo?.nome ?? '—'}</td>
                  <td className="px-4 py-3 text-slate-600">
                    {c.zona_eleitoral ? `${c.zona_eleitoral.numero_zona}ª - ${c.zona_eleitoral.nome}` : '—'}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{VINCULO_LABELS[c.vinculo]}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={c.status} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDelete(c.id)}
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

function StatusBadge({ status }: { status: ColaboradorStatus }) {
  const colors: Record<ColaboradorStatus, string> = {
    ativo: 'bg-emerald-100 text-emerald-800',
    inativo: 'bg-slate-100 text-slate-600',
    afastado: 'bg-amber-100 text-amber-800',
  }
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[status]}`}>
      {STATUS_LABELS[status]}
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
