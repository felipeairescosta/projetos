# Analisador de Contas Eleitorais

Ferramenta independente para triagem automatizada de prestações de contas
eleitorais (receitas e despesas de candidatos/comitês financeiros) à luz das
regras da **Resolução TSE nº 23.607/2019**, que dispõe sobre a arrecadação e
aplicação de recursos e a prestação de contas de campanhas eleitorais.

Não substitui o julgamento formal das contas pela Justiça Eleitoral — o
objetivo é gerar um relatório de pendências/alertas para apoiar o trabalho de
um analista humano.

## ⚠️ Aviso sobre a base normativa

As regras em `src/regras.py` foram codificadas a partir do **texto compilado
oficial** da Resolução TSE nº 23.607/2019 (com as alterações das Resoluções
23.665/2021, 23.709/2022, 23.731/2024 e 23.752/2026), cada uma citando o
artigo correspondente. Ainda assim, alguns pontos exigem conferência manual
a cada eleição:

- o **teto de gastos de campanha** (art. 4º) é fixado por portaria do TSE a
  cada eleição — não há valor fixo na resolução; deve ser informado em
  `CandidatoOuComite.teto_gastos_campanha`;
- valores em reais citados na resolução (R$ 1.064,10 — art. 21, §1º;
  R$ 4.000,00 — art. 7º, §6º, I; R$ 40.000,00 — art. 27, §3º; R$ 20.000,00 —
  art. 62) são atualizados monetariamente a cada eleição; os valores em
  `src/regras.py` são os do texto compilado na data em que este módulo foi
  escrito;
- não são modeladas a exceção do art. 27, §3º (doações estimáveis em bens ou
  serviços próprios até R$ 40.000,00, fora do limite de 10% do rendimento)
  nem a soma de recursos próprios de vice/suplente ao do titular para o
  limite de autofinanciamento (art. 27, §1º-A).

Sempre que a resolução for atualizada por nova Res.-TSE, revise as regras e
os parâmetros no topo de `src/regras.py`.

## Como funciona

1. **Entrada**: uma `PrestacaoContas` — candidato/comitê + lista de receitas
   + lista de despesas (ver `src/modelos.py`).
2. **Motor de regras** (`src/regras.py`): cada regra do TSE vira uma função
   que recebe a prestação de contas e devolve uma lista de `Achado`
   (severidade `INFO`/`ALERTA`/`IRREGULARIDADE`/`GRAVE`, referência
   normativa, descrição).
3. **Análise** (`src/analisador.py`): roda todas as regras e separa os
   achados em três grupos, conforme o fluxo dos arts. 66, 69, 72 e 74 da
   resolução (ver seção abaixo).
4. **Relatório** (`src/relatorio.py`): renderiza o resultado em Markdown —
   ou um relatório de diligências, ou o parecer conclusivo, nunca os dois.

## Diligência antes do parecer conclusivo (arts. 66, 69, 72 e 74)

O parecer conclusivo (aprovação / aprovação com ressalvas / desaprovação /
não prestação) **só deve ser elaborado depois que todo achado passou por
diligência/oportunidade de manifestação da prestadora ou do prestador de
contas**. Isso é modelado assim:

- Cada achado gerado pelas regras tem uma chave (`achados.chave_diligencia`,
  formada por regra + item relacionado).
- `PrestacaoContas.diligencias_respondidas` é um dicionário opcional que
  mapeia essa chave para `StatusDiligencia.SANADA` (a prestadora/o prestador
  esclareceu ou corrigiu o ponto) ou `StatusDiligencia.NAO_SANADA` (houve
  manifestação, mas o ponto persiste).
- Ao analisar, todo achado cuja chave **não** aparece nesse dicionário vai
  para `Relatorio.achados_pendentes_diligencia` — enquanto essa lista não
  estiver vazia, `Relatorio.pronto_para_parecer_conclusivo` é `False` e
  `Relatorio.parecer_sugerido` é `None`. Nesse caso, o relatório gerado
  recomenda a **intimação da prestadora/do prestador de contas** para se
  manifestar (arts. 66, 69 e 72), em vez de um parecer.
- Só quando não há mais nenhum achado pendente é que o parecer conclusivo é
  calculado, com base nos achados marcados como `NAO_SANADA`
  (`Relatorio.achados_confirmados`) — os `SANADA` ficam registrados em
  `Relatorio.achados_sanados`, mas não pesam no parecer.

Ou seja: a primeira análise de um caso novo (sem `diligencias_respondidas`)
sempre resulta em relatório de diligências, se houver qualquer achado. Depois
que a diligência for cumprida no processo real, informe o resultado em
`diligencias_respondidas` e rode a análise de novo para obter o parecer.

## Regras implementadas

| Regra | Artigo | Severidade |
|---|---|---|
| Fonte vedada (PJ, origem estrangeira, PF permissionária de serviço público) | art. 31 | GRAVE |
| Origem não identificada | art. 32 | GRAVE |
| Doação de PF acima de 10% do rendimento do ano anterior | art. 27, caput | IRREGULARIDADE |
| Autofinanciamento acima de 10% do teto de gastos | art. 27, §1º | IRREGULARIDADE |
| Recibo eleitoral ausente (fora das dispensas do art. 7º) | art. 7º | IRREGULARIDADE |
| Doação ≥ R$ 1.064,10 sem meio bancário rastreável | art. 21, §1º | IRREGULARIDADE |
| Receita arrecadada em espécie | art. 21, caput | IRREGULARIDADE |
| Gasto pago por forma não autorizada (fora cheque cruzado/transferência/débito/Pix) | art. 38 | IRREGULARIDADE |
| Despesa sem documento fiscal idôneo | art. 60 | IRREGULARIDADE |
| Teto de gastos de campanha excedido | arts. 4º-6º | GRAVE |
| Prazo de apresentação das contas excedido / contas não apresentadas | art. 49; art. 74, IV | IRREGULARIDADE / GRAVE |
| CNPJ específico ausente | art. 3º, I, b; art. 8º | ALERTA |
| Conta bancária específica ausente | art. 3º, I, c; art. 8º | ALERTA |

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
