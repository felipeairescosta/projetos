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

## Publicando como site estático (sem backend)

O frontend tem dois modos de acesso a dados (`src/lib/dataClient.ts`):

- **Com backend**: se `VITE_API_URL` estiver definido, todas as chamadas vão
  para a API FastAPI (`../backend`).
- **Direto ao Supabase**: se `VITE_API_URL` estiver vazio/ausente, o
  frontend usa `@supabase/supabase-js` diretamente no navegador. A
  autorização continua sendo aplicada pelas políticas de RLS do banco, então
  é seguro publicar assim.

Isso permite publicar o frontend como site estático (Vercel, Netlify, GitHub
Pages) sem precisar hospedar o backend em lugar nenhum:

1. No painel da Vercel/Netlify, importe o repositório e aponte o **Root
   Directory** para `frontend`.
2. Build command: `npm run build` · Output directory: `dist`.
3. Configure as variáveis de ambiente `VITE_SUPABASE_URL` e
   `VITE_SUPABASE_ANON_KEY` (valores em `.env.example`) — e **não** defina
   `VITE_API_URL`.
4. Deploy. `vercel.json` e `public/_redirects` já cuidam do fallback de
   rotas do React Router (SPA) tanto na Vercel quanto na Netlify.
