import { useEffect, useState, type FormEvent } from 'react'
import { api } from '../lib/api'
import type { ZonaEleitoral } from '../types'

const emptyForm = { numero_zona: '', nome: '', municipio: '', endereco: '', telefone: '', email: '' }

export function ZonasPage() {
  const [zonas, setZonas] = useState<ZonaEleitoral[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState<string | null>(null)

  async function load() {
    setLoading(true)
    const { data } = await api.get<ZonaEleitoral[]>('/zonas')
    setZonas(data)
    setLoading(false)
  }

  useEffect(() => {
    load()
  }, [])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await api.post('/zonas', {
        numero_zona: Number(form.numero_zona),
        nome: form.nome,
        municipio: form.municipio,
        endereco: form.endereco || null,
        telefone: form.telefone || null,
        email: form.email || null,
      })
      setForm(emptyForm)
      setShowForm(false)
      await load()
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Erro ao salvar zona eleitoral.')
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('Remover esta zona eleitoral?')) return
    await api.delete(`/zonas/${id}`)
    await load()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900">Zonas Eleitorais</h2>
          <p className="text-sm text-slate-500">
            Cadastro dos cartórios/zonas eleitorais do TRE-CE. Insira os dados oficiais de cada zona.
          </p>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="rounded-md bg-blue-900 px-4 py-2 text-sm font-medium text-white hover:bg-blue-800"
        >
          {showForm ? 'Cancelar' : '+ Nova Zona'}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="grid grid-cols-1 gap-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm md:grid-cols-3"
        >
          <Field label="Número da zona" required>
            <input
              type="number"
              required
              value={form.numero_zona}
              onChange={(e) => setForm({ ...form, numero_zona: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="Nome" required>
            <input
              required
              value={form.nome}
              onChange={(e) => setForm({ ...form, nome: e.target.value })}
              className="input"
              placeholder="Ex: Cartório da 1ª Zona Eleitoral"
            />
          </Field>
          <Field label="Município" required>
            <input
              required
              value={form.municipio}
              onChange={(e) => setForm({ ...form, municipio: e.target.value })}
              className="input"
            />
          </Field>
          <Field label="Endereço">
            <input
              value={form.endereco}
              onChange={(e) => setForm({ ...form, endereco: e.target.value })}
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
          <Field label="E-mail">
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
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
              <Th>Zona</Th>
              <Th>Nome</Th>
              <Th>Município</Th>
              <Th>Contato</Th>
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
            ) : zonas.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-400">
                  Nenhuma zona eleitoral cadastrada.
                </td>
              </tr>
            ) : (
              zonas.map((z) => (
                <tr key={z.id}>
                  <td className="px-4 py-3 font-medium">{z.numero_zona}ª</td>
                  <td className="px-4 py-3">{z.nome}</td>
                  <td className="px-4 py-3">{z.municipio}</td>
                  <td className="px-4 py-3 text-slate-500">{z.telefone || z.email || '—'}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDelete(z.id)}
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
