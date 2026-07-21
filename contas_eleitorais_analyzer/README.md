# Analisador de Contas Eleitorais

Ferramenta independente para triagem automatizada de prestações de contas
eleitorais (receitas e despesas de candidatos/comitês financeiros) à luz das
regras da **Resolução TSE nº 23.607/2019**, que dispõe sobre a arrecadação e
aplicação de recursos e a prestação de contas de campanhas eleitorais.

Não substitui o julgamento formal das contas pela Justiça Eleitoral — o
objetivo é gerar um relatório de pendências/alertas para apoiar o trabalho de
um analista humano.

## ⚠️ Aviso sobre a base normativa

As regras em `src/regras.py` foram escritas a partir do conhecimento geral do
conteúdo da Resolução TSE 23.607/2019. Não foi possível, no ambiente em que
este projeto foi criado, acessar ao vivo o texto compilado em tse.jus.br para
conferir a numeração exata dos artigos e os valores/parâmetros vigentes na
versão mais atual (a resolução ganha anexos e ajustes a cada eleição, com
tetos de gastos específicos por cargo/UF). **Antes de usar isto para
qualquer decisão real, confira cada regra contra o texto compilado vigente**
e ajuste os parâmetros marcados como `PARAMETRIZÁVEL` no topo de
`src/regras.py`.

## Como funciona

1. **Entrada**: uma `PrestacaoContas` — candidato/comitê + lista de receitas
   + lista de despesas (ver `src/modelos.py`).
2. **Motor de regras** (`src/regras.py`): cada regra do TSE vira uma função
   que recebe a prestação de contas e devolve uma lista de `Achado`
   (severidade `INFO`/`ALERTA`/`IRREGULARIDADE`/`GRAVE`, referência
   normativa, descrição).
3. **Análise** (`src/analisador.py`): roda todas as regras e monta um
   `Relatorio` com os achados e um parecer sugerido.
4. **Relatório** (`src/relatorio.py`): renderiza o resultado em Markdown.

## Fontes de dados de entrada

- **JSON estruturado** (já funciona): `src/ingestao/json_loader.py` lê o
  formato descrito em `dados_exemplo/exemplo_prestacao.json`.
- **Documentos do PJe** (ponto de extensão): coloque os PDFs do processo de
  prestação de contas em `docs_pje/`. `src/ingestao/pdf_loader.py` já extrai
  o texto bruto de cada PDF (`extrair_texto_de_pdfs`); falta implementar o
  mapeamento desse texto para os campos da `PrestacaoContas`
  (`construir_prestacao_de_pdfs`), o que depende do layout real dos
  documentos — o docstring dessa função tem o passo a passo.

## Uso

```bash
pip install -r requirements.txt

# Analisar o exemplo incluído
python main.py analisar dados_exemplo/exemplo_prestacao.json

# Salvar o relatório em arquivo
python main.py analisar dados_exemplo/exemplo_prestacao.json --saida relatorio.md

# Rodar os testes
pytest
```

## Estrutura

```
contas_eleitorais_analyzer/
├── main.py                     # CLI
├── src/
│   ├── modelos.py              # Doador, Receita, Despesa, CandidatoOuComite, PrestacaoContas
│   ├── achados.py              # Achado, Severidade
│   ├── regras.py               # regras da Res.-TSE 23.607/2019
│   ├── analisador.py           # roda as regras e monta o Relatorio
│   ├── relatorio.py            # renderização em Markdown
│   └── ingestao/
│       ├── json_loader.py      # carrega PrestacaoContas de JSON
│       └── pdf_loader.py       # extrai texto dos PDFs do PJe (ponto de extensão)
├── dados_exemplo/
│   └── exemplo_prestacao.json  # exemplo com várias irregularidades propositais
├── docs_pje/                   # coloque aqui os PDFs do processo do PJe
└── tests/
    └── test_regras.py
```

## Adicionando uma nova regra

1. Escreva uma função em `src/regras.py` no padrão
   `def regra_x(pc: PrestacaoContas) -> list[Achado]`.
2. Registre-a na lista `REGRAS_REGISTRADAS`, no fim do arquivo.
3. Adicione um teste em `tests/test_regras.py`.
