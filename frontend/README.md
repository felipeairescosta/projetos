# Frontend — Gestão de Colaboradores (Cartórios Eleitorais TRE-CE)

Aplicação React + TypeScript (Vite) para gestão de colaboradores, lotação,
escalas e afastamentos dos cartórios eleitorais do TRE-CE.

## Rodando localmente

```bash
cd frontend
npm install
cp .env.example .env     # já vem com URL/anon key do projeto Supabase
npm run dev
```

Acesse `http://localhost:5173`. É necessário que o backend (`../backend`)
esteja rodando em `http://localhost:8000` (ou ajuste `VITE_API_URL` no `.env`).

## Login

A autenticação é feita via Supabase Auth. Contas de usuário são criadas pelo
administrador diretamente no painel do Supabase (Authentication → Users) ou
via SQL, e o perfil (`admin`, `gestor` ou `colaborador`) é definido na tabela
`perfis`. Não há tela de auto-cadastro por padrão.

## Páginas

- **Dashboard** — indicadores gerais e gráficos (colaboradores por zona,
  cargo, vínculo, afastamentos por tipo).
- **Colaboradores** — cadastro, busca, filtro por status.
- **Zonas Eleitorais** — cadastro dos cartórios/zonas eleitorais.
- **Escalas** — escalas de atendimento e plantões.
- **Afastamentos** — férias, licenças e demais afastamentos.

## Stack

React 19 · TypeScript · Vite · Tailwind CSS v4 · React Router · Recharts ·
Axios · Supabase JS
