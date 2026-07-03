# Backend — Gestão de Colaboradores (Cartórios Eleitorais TRE-CE)

API em FastAPI que expõe operações de CRUD e relatórios sobre o banco Postgres
hospedado no Supabase (projeto `cartorios-eleitorais-tre-ce`).

## Rodando localmente

```bash
cd backend
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # já vem com URL/anon key do projeto Supabase
uvicorn app.main:app --reload --port 8000
```

A documentação interativa fica em `http://localhost:8000/docs`.

## Autenticação

Cada requisição precisa do header `Authorization: Bearer <jwt>`, onde o JWT é
o access token retornado pelo login no Supabase Auth (feito pelo frontend).
O backend usa esse token para autenticar as chamadas ao Postgres via
PostgREST, então as políticas de Row Level Security (RLS) do banco são
aplicadas de acordo com o usuário logado — o backend nunca usa a
`service_role key`.

- Leitura: qualquer usuário autenticado.
- Escrita (criar/editar/remover): apenas usuários com perfil `admin` ou
  `gestor` na tabela `perfis`.

## Estrutura

```
app/
  main.py        # app FastAPI + CORS + routers
  config.py      # variáveis de ambiente
  deps.py        # cliente Supabase autenticado por requisição
  crud.py        # helpers genéricos de CRUD sobre PostgREST
  schemas.py     # modelos Pydantic
  routers/
    zonas.py           # zonas eleitorais / cartórios
    cargos.py           # cargos
    colaboradores.py    # colaboradores
    escalas.py           # escalas de atendimento/plantão
    afastamentos.py      # férias, licenças
    relatorios.py         # agregações para o dashboard
```
