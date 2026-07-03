# Sistema de Gestão de Colaboradores — Cartórios Eleitorais TRE-CE

Sistema web para gestão dos colaboradores que trabalham nos cartórios
(zonas) eleitorais do TRE-CE: cadastro, lotação, escalas de atendimento/
plantão, afastamentos (férias e licenças) e dashboards gerenciais.

Este sistema é independente do Dashboard PJe já existente neste repositório
(`app.py`, `data_loader.py` na raiz) — vivem lado a lado, sem dependência
entre si.

## Arquitetura

- **`backend/`** — API em FastAPI (Python), autentica cada requisição com o
  JWT do usuário e delega ao Postgres via PostgREST/Supabase, respeitando
  Row Level Security.
- **`frontend/`** — SPA em React + TypeScript + Vite + Tailwind, consome a
  API e usa o Supabase Auth para login.
- **Banco de dados** — Supabase (Postgres), projeto `cartorios-eleitorais-tre-ce`
  (`https://ysrjkogujrkdtifiiqww.supabase.co`), organização `FELIPE-AIRES-COSTA`.

## Modelo de dados

| Tabela                | Descrição                                                  |
|------------------------|-------------------------------------------------------------|
| `zonas_eleitorais`     | Cartórios/zonas eleitorais (número, nome, município, contato) |
| `cargos`               | Cargos/funções (pré-cadastrados: Chefe de Cartório, Escrevente Eleitoral etc.) |
| `colaboradores`        | Dados pessoais, cargo, lotação, vínculo, status              |
| `lotacoes_historico`   | Histórico de transferências entre zonas                      |
| `escalas`               | Escalas de atendimento/plantão por colaborador, zona e data   |
| `afastamentos`          | Férias, licenças e outros afastamentos                        |
| `perfis`                | Perfil de acesso de cada usuário (`admin`, `gestor`, `colaborador`), vinculado ao Supabase Auth |

## Primeiro acesso

1. **Criar o primeiro usuário administrador**: no painel do Supabase
   (Authentication → Users → Add user), crie uma conta com e-mail/senha e
   marque "Auto Confirm User". Depois, insira o perfil correspondente:

   ```sql
   insert into perfis (id, nome_completo, role)
   values ('<uuid-do-usuario-criado>', 'Nome do Administrador', 'admin');
   ```

2. **Cadastrar as zonas eleitorais oficiais**: por precisão, o banco não vem
   com uma lista pré-populada de zonas eleitorais (números, endereços e
   contatos variam e devem refletir os dados oficiais do TRE-CE). Cadastre-as
   pela tela "Zonas Eleitorais" do sistema ou via SQL/CSV em lote.

3. Rode o backend e o frontend (ver READMEs em `backend/` e `frontend/`) e
   faça login com a conta criada no passo 1.

## Permissões

- Qualquer usuário autenticado pode **visualizar** dados.
- Apenas usuários com perfil `admin` ou `gestor` podem **criar, editar ou
  remover** registros (aplicado via política de Row Level Security no
  Postgres, não apenas na interface).

## Limitação conhecida desta sessão de desenvolvimento

O ambiente onde este sistema foi desenvolvido tem acesso de rede de saída
bloqueado para o domínio do projeto Supabase (`*.supabase.co`), por política
de egress do ambiente sandbox. Isso impediu testar o fluxo de login e as
chamadas à API ponta a ponta num navegador dentro desta sessão. Foi possível
verificar:

- Schema, RLS e seed aplicados com sucesso no Supabase (via MCP).
- Backend importa, sobe e responde `401` corretamente sem token.
- Frontend compila sem erros de tipo e a tela de login renderiza
  corretamente.

Recomenda-se rodar `backend` e `frontend` localmente (fora deste sandbox,
onde o acesso ao Supabase não é bloqueado) e validar o fluxo completo de
login e CRUD antes de considerar o sistema pronto para uso em produção.
