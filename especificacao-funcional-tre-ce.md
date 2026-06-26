# Especificação Funcional — Sistema de Gestão Processual de Segundo Grau
## Tribunal Regional Eleitoral do Ceará (TRE-CE)

**Versão:** 1.0  
**Data:** Junho de 2026  
**Classificação:** Documento Interno — Uso Restrito  

---

## Sumário

1. [Visão Geral do Sistema](#1-visão-geral-do-sistema)
2. [Módulos do Sistema](#2-módulos-do-sistema)
3. [Funcionalidades por Módulo](#3-funcionalidades-por-módulo)
4. [Fluxo Processual](#4-fluxo-processual)
5. [Perfis de Usuários e Permissões](#5-perfis-de-usuários-e-permissões)
6. [Requisitos de Segurança](#6-requisitos-de-segurança)
7. [Requisitos Não Funcionais](#7-requisitos-não-funcionais)
8. [Modelo Conceitual de Dados](#8-modelo-conceitual-de-dados)
9. [Integrações](#9-integrações)
10. [Sugestões Técnicas](#10-sugestões-técnicas)

---

## 1. Visão Geral do Sistema

### 1.1 Objetivo do Sistema

O **Sistema de Gestão Processual de Segundo Grau do TRE-CE (SGP-2G)** tem por objetivo apoiar a tramitação eletrônica, o controle administrativo e o acompanhamento dos processos judiciais em sede recursal no âmbito do Tribunal Regional Eleitoral do Ceará. O sistema visa garantir celeridade, transparência, rastreabilidade e segurança na condução dos processos de segundo grau, em conformidade com as diretrizes do Conselho Nacional de Justiça (CNJ) e do Tribunal Superior Eleitoral (TSE).

### 1.2 Escopo Funcional

O sistema abrange:

- Recebimento e distribuição de processos oriundos do primeiro grau (zonas eleitorais) e de outros tribunais
- Gestão da tramitação interna entre secretaria judiciária, gabinetes e plenário
- Controle de prazos processuais e administrativos
- Preparação, realização e registro de sessões de julgamento colegiadas
- Publicação de decisões e expedição de comunicações processuais
- Gestão documental eletrônica dos autos digitais
- Geração de relatórios gerenciais e indicadores de desempenho
- Consulta pública e acompanhamento processual por advogados e partes

**Fora do escopo:**
- Tramitação de processos de primeiro grau (zonas eleitorais)
- Gestão eleitoral (cadastro de eleitores, urnas, resultados)
- Sistemas financeiros e de recursos humanos do TRE-CE

### 1.3 Perfis de Usuários

| Perfil | Descrição |
|--------|-----------|
| Desembargador/Relator | Magistrado responsável pela relatoria do processo |
| Assessor Judiciário | Servidor de apoio ao gabinete do desembargador |
| Diretor de Secretaria | Servidor responsável pela direção da secretaria judiciária |
| Analista/Técnico Judiciário | Servidor responsável pela movimentação e controle processual |
| Administrador do Sistema | Responsável pela configuração e suporte técnico |
| Advogado | Usuário externo com acesso à consulta e peticionamento |
| Parte/Interessado | Usuário externo com acesso somente à consulta pública |
| Ministério Público Eleitoral | Órgão com acesso como parte e custos legis |
| Presidência do Tribunal | Magistrado com acesso ampliado para gestão e pauta |

---

## 2. Módulos do Sistema

### 2.1 Visão Geral dos Módulos

```
┌─────────────────────────────────────────────────────────────────┐
│                     SGP-2G / TRE-CE                             │
├──────────────┬───────────────┬──────────────────────────────────┤
│  Distribuição│   Gabinete    │     Secretaria Judiciária        │
│  Processual  │  (Relatoria)  │                                  │
├──────────────┼───────────────┼──────────────────────────────────┤
│  Sessões de  │  Publicações  │     Gestão Documental            │
│ Julgamento   │  e Intimações │                                  │
├──────────────┼───────────────┼──────────────────────────────────┤
│  Controle de │  Consultas e  │     Painel Gerencial (BI)        │
│   Prazos     │  Relatórios   │                                  │
└──────────────┴───────────────┴──────────────────────────────────┘
```

### 2.2 Lista de Módulos

| # | Módulo | Função Principal |
|---|--------|-----------------|
| M01 | Distribuição Processual | Recebimento e distribuição de processos entre relatores |
| M02 | Gabinete (Relatoria) | Instrução e elaboração de votos e decisões |
| M03 | Secretaria Judiciária | Movimentação, controle e despachos |
| M04 | Sessões de Julgamento | Pauta, realização e registro de sessões |
| M05 | Publicações e Intimações | Expedição e controle de comunicações processuais |
| M06 | Gestão Documental | Armazenamento e gestão dos autos digitais |
| M07 | Consultas e Relatórios | Pesquisa processual e emissão de relatórios |
| M08 | Controle de Prazos | Monitoramento e alertas de prazos |
| M09 | Painel Gerencial (BI) | Indicadores e dashboards de desempenho |

---

## 3. Funcionalidades por Módulo

### 3.1 M01 — Distribuição Processual

#### 3.1.1 Principais Funcionalidades

- **Recebimento de Processos:** Importação automática de processos provenientes do PJe (primeiro grau), TSE e outros órgãos via integração ou carga manual
- **Triagem Processual:** Classificação por classe processual, assunto e tipo de recurso (agravo regimental, recurso ordinário, recurso especial, mandado de segurança, habeas corpus, entre outros)
- **Distribuição Automática:** Algoritmo de distribuição equitativa considerando carga de trabalho, prevenção, impedimentos e suspeições
- **Distribuição Manual:** Possibilidade de distribuição manual com justificativa registrada, restrita ao Presidente e Diretor de Secretaria
- **Redistribuição:** Movimentação de processo entre relatores por motivo de impedimento, suspeição, afastamento ou decisão administrativa
- **Prevenção:** Verificação automática de prevenção com base em processos anteriores das mesmas partes ou do mesmo fato

#### 3.1.2 Fluxo de Uso

```
Recebimento via PJe/protocolo
        ↓
  Triagem e classificação
        ↓
Verificação de prevenção
        ↓
  ┌─── Prevento? ───┐
  │ Sim             │ Não
  ↓                 ↓
Relator           Distribuição
prevento         automática (sorteio
                 ponderado por carga)
        ↓
Notificação ao gabinete
        ↓
Inclusão na fila do gabinete
```

#### 3.1.3 Entradas e Saídas

| Entrada | Saída |
|---------|-------|
| Dados do processo (número, classe, partes, assunto) | Número de distribuição interno |
| Documentos iniciais (petição, acórdão recorrido) | Designação do relator |
| Dados das partes e representantes | Notificação ao gabinete do relator |
| Metadados de origem (PJe, protocolo) | Registro no histórico de movimentações |

#### 3.1.4 Regras de Negócio

- **RN-M01-01:** A distribuição automática deve ponderar o peso processual por classe (ex.: mandado de segurança = peso 3; agravo = peso 1)
- **RN-M01-02:** Processos urgentes (medidas cautelares, habeas corpus) devem ser distribuídos ao plantonista quando fora do horário de expediente
- **RN-M01-03:** O relator deve ser notificado por e-mail e alerta no sistema em até 30 minutos após a distribuição
- **RN-M01-04:** Toda redistribuição deve ser precedida de registro da causa e aprovação da presidência
- **RN-M01-05:** Processos com segredo de justiça devem ser sinalizados na distribuição, com restrição de acesso automática
- **RN-M01-06:** O sistema deve impedir distribuição a relator com impedimento ou suspeição declarados nas partes do processo

---

### 3.2 M02 — Gabinete (Relatoria)

#### 3.2.1 Principais Funcionalidades

- **Fila do Gabinete:** Listagem e priorização dos processos sob relatoria, com filtros por urgência, prazo e classe
- **Visualização dos Autos:** Acesso completo aos documentos digitais do processo, com navegação por peças e índice
- **Elaboração de Minutas:** Editor integrado para elaboração de votos, decisões monocráticas, despachos e certidões, com modelos pré-configurados
- **Controle de Vistas:** Registro e controle do envio de processos em vista a outros magistrados
- **Destaque para Pauta:** Inclusão de processos na pauta de julgamento com definição de tipo de julgamento
- **Pedido de Diligência:** Solicitação de diligências à secretaria (intimação, juntada, certidão)
- **Conclusão ao Relator:** Registro de recebimento dos autos em conclusão com data e hora
- **Histórico de Minutas:** Versionamento de documentos com histórico de alterações

#### 3.2.2 Fluxo de Uso — Decisão Monocrática

```
Recebimento em conclusão
        ↓
Visualização dos autos
        ↓
Elaboração de minuta (editor)
        ↓
Revisão do assessor
        ↓
Assinatura digital do desembargador
        ↓
Envio à secretaria para publicação
        ↓
Publicação no Diário da Justiça
```

#### 3.2.3 Fluxo de Uso — Voto para Sessão

```
Processo incluído na pauta
        ↓
Elaboração de voto (editor)
        ↓
Revisão do assessor
        ↓
Assinatura prévia do relator
        ↓
Encaminhamento para pauta da sessão
        ↓
Apresentação na sessão de julgamento
        ↓
Registro do resultado na sessão
        ↓
Lavratura do acórdão
```

#### 3.2.4 Regras de Negócio

- **RN-M02-01:** Apenas o relator ou assessores autorizados do respectivo gabinete podem elaborar minutas de processos sob sua relatoria
- **RN-M02-02:** Toda minuta deve obrigatoriamente ser assinada digitalmente pelo desembargador antes do encaminhamento
- **RN-M02-03:** O sistema deve manter versionamento com no mínimo 30 dias de histórico de minutas
- **RN-M02-04:** Processos com prazo vencendo em até 5 dias úteis devem ser destacados com alerta visual na fila
- **RN-M02-05:** Vista a outro magistrado deve ter prazo máximo configurável (padrão: 10 dias úteis), com alerta automático ao vencer

---

### 3.3 M03 — Secretaria Judiciária

#### 3.3.1 Principais Funcionalidades

- **Protocolo e Recebimento:** Registro de petições externas, recursos e demais documentos, com geração automática de recibo
- **Juntada de Documentos:** Juntada de peças aos autos, com classificação por tipo de documento
- **Despachos e Certidões:** Elaboração e assinatura de certidões, despachos e ofícios
- **Controle de Movimentação:** Registro e controle de toda a movimentação processual (carga, vista, remessa, arquivo)
- **Conclusão:** Envio dos processos em conclusão ao relator ou à presidência, com controle de data
- **Expedição de Ofícios:** Criação e envio de ofícios a órgãos externos, com confirmação de recebimento
- **Arquivo e Digitalização:** Controle de digitalização de documentos físicos e arquivamento de autos findos
- **Controle de Guias de Prazo:** Gerenciamento de guias de prazo para controle de respostas esperadas

#### 3.3.2 Fluxo de Uso — Recebimento de Petição Externa

```
Petição protocolada (via PJe ou balcão)
        ↓
Cadastro e geração de protocolo
        ↓
Verificação do processo relacionado
        ↓
Triagem pelo servidor
        ↓
  ┌──────────┬────────────┬─────────────┐
  ↓          ↓            ↓             ↓
Juntada  Despacho    Conclusão    Remessa ao
aos autos para relator  relator    1º grau
```

#### 3.3.3 Regras de Negócio

- **RN-M03-01:** O prazo para juntada de petições aos autos é de 24 horas após o protocolo, salvo urgência (imediato)
- **RN-M03-02:** Certidões devem ser geradas automaticamente por modelo e assinadas eletronicamente pelo diretor da secretaria
- **RN-M03-03:** Toda movimentação processual deve ser registrada no histórico com identificação do servidor responsável, data e hora
- **RN-M03-04:** Remessas ao primeiro grau ou a outros órgãos devem gerar comprovante eletrônico de envio
- **RN-M03-05:** O sistema deve bloquear movimentações em processos com segredo de justiça para servidores sem autorização específica

---

### 3.4 M04 — Sessões de Julgamento

#### 3.4.1 Principais Funcionalidades

- **Criação de Pauta:** Organização da pauta de julgamento com inclusão de processos, definição de ordem e tipo (julgamento, sustentação oral, pedido de vista)
- **Gestão da Sessão:** Abertura, condução e encerramento da sessão com registro em ata
- **Controle de Presença:** Registro de presença e votos dos magistrados, incluindo impedimentos e ausências
- **Sustentação Oral:** Gerenciamento de inscrições e tempos para sustentação oral por advogados
- **Registro de Votos:** Captura dos votos de cada magistrado (procedente, improcedente, parcialmente procedente) com divergências
- **Lavratura do Acórdão:** Geração automática da ementa e estrutura do acórdão com base nos votos registrados
- **Transmissão ao Vivo:** Integração com sistema de transmissão ao vivo para sessões públicas (link para canal oficial)
- **Atas e Publicação:** Geração da ata da sessão e encaminhamento para publicação no Diário da Justiça

#### 3.4.2 Fluxo de Uso — Sessão de Julgamento

```
Criação e publicação da pauta (prévia)
        ↓
Período de inscrição para sustentação oral
        ↓
Abertura da sessão (presidente)
        ↓
Para cada processo da pauta:
  ├─ Chamada do processo
  ├─ Sustentação oral (se inscrito)
  ├─ Apresentação do voto do relator
  ├─ Deliberação colegiada
  ├─ Registro dos votos individuais
  └─ Proclamação do resultado
        ↓
Encerramento da sessão
        ↓
Lavratura da ata
        ↓
Lavratura dos acórdãos
        ↓
Publicação no DJE
```

#### 3.4.3 Regras de Negócio

- **RN-M04-01:** A pauta deve ser publicada com antecedência mínima de 48 horas da sessão
- **RN-M04-02:** Inscrições para sustentação oral devem ser permitidas até 24 horas antes da sessão, com tempo padrão de 15 minutos
- **RN-M04-03:** O quórum mínimo para julgamento colegiado é de 3 (três) magistrados
- **RN-M04-04:** Votos devem ser registrados individualmente para cada magistrado, com possibilidade de divergência fundamentada
- **RN-M04-05:** A lavratura do acórdão deve ocorrer em até 10 dias após a sessão
- **RN-M04-06:** Processos julgados por unanimidade podem ter ementa gerada automaticamente; divergências exigem redação manual do vencido e do vencedor
- **RN-M04-07:** A ata da sessão deve ser assinada digitalmente pelo presidente e pelo secretário da sessão

---

### 3.5 M05 — Publicações e Intimações

#### 3.5.1 Principais Funcionalidades

- **Publicação no DJE:** Envio automatizado de decisões, acórdãos, despachos e editais ao Diário da Justiça Eletrônico do TRE-CE
- **Intimação Eletrônica:** Expedição de intimações via portal do PJe para advogados cadastrados
- **Intimação por Edital:** Geração de editais para partes não localizadas, com publicação no DJE
- **Controle de Ciência:** Registro da data de ciência da intimação (acesso ao portal ou publicação no DJE)
- **Comunicação a Órgãos:** Expedição de ofícios e comunicações a órgãos públicos (MP, Polícia, TSE, outros TREs)
- **Certidões de Publicação:** Emissão de certidões com data e veículo de publicação
- **Cadastro de Advogados:** Gerenciamento do cadastro de advogados e seus dados para intimação eletrônica

#### 3.5.2 Regras de Negócio

- **RN-M05-01:** O prazo processual conta-se a partir do dia útil seguinte à publicação no DJE ou ao acesso ao portal (o que ocorrer primeiro)
- **RN-M05-02:** Intimações a advogados habilitados no PJe devem ser feitas exclusivamente pela via eletrônica
- **RN-M05-03:** Todas as publicações devem ser enviadas com identificação do processo, classe, relator e dispositivo da decisão
- **RN-M05-04:** O sistema deve confirmar o recebimento da publicação no DJE e registrar a data de disponibilização
- **RN-M05-05:** Processos com segredo de justiça devem ter seus dados omitidos nas publicações, com uso de identificador genérico

---

### 3.6 M06 — Gestão Documental

#### 3.6.1 Principais Funcionalidades

- **Repositório de Autos Digitais:** Armazenamento centralizado dos documentos dos processos com controle de versão
- **Indexação e Busca:** Busca por conteúdo (OCR), tipo de documento, data, autor e número de processo
- **Classificação Documental:** Categorização dos documentos por tipo (petição, decisão, acórdão, certidão, ofício, procuração, etc.)
- **Controle de Acesso a Documentos:** Restrição de documentos sigilosos com log de acesso
- **Assinatura Digital:** Integração com ICP-Brasil para assinatura e validação de documentos
- **Digitalização:** Interface para recepção de documentos digitalizados e validação de qualidade
- **Exportação de Autos:** Geração de arquivo compactado (ZIP/PDF unificado) dos autos para impressão ou envio

#### 3.6.2 Regras de Negócio

- **RN-M06-01:** Todo documento inserido nos autos deve ter sua integridade garantida por hash SHA-256 registrado no banco de dados
- **RN-M06-02:** Documentos assinados digitalmente devem ter a validação da assinatura verificável pelo sistema
- **RN-M06-03:** Documentos classificados como sigilosos só podem ser acessados por perfis autorizados, com registro obrigatório de acesso
- **RN-M06-04:** O sistema deve aceitar documentos nos formatos: PDF, PDF/A, DOCX (conversão automática para PDF/A)
- **RN-M06-05:** O tamanho máximo por arquivo é de 30 MB; o sistema deve rejeitar arquivos acima desse limite com mensagem orientativa
- **RN-M06-06:** Documentos não podem ser excluídos definitivamente dos autos; operações de exclusão devem ser substituídas por cancelamento com registro

---

### 3.7 M07 — Consultas e Relatórios

#### 3.7.1 Principais Funcionalidades

- **Consulta Processual Pública:** Pesquisa por número de processo, nome da parte, CPF/CNPJ, advogado (OAB), assunto e classe processual
- **Consulta Avançada (Interna):** Filtros adicionais por relator, situação, data de distribuição, prazo vencido, e combinações
- **Relatórios de Acervo:** Listagem do acervo por relator, classe, situação e período
- **Relatórios de Produtividade:** Processos julgados por período, por magistrado e por classe
- **Relatórios de Prazo:** Processos com prazo vencido ou próximo ao vencimento
- **Relatórios de Sessão:** Ata, pautas, processos julgados e não julgados por sessão
- **Exportação de Dados:** Exportação em formatos CSV, XLSX e PDF
- **Relatórios CNJ (DataJud):** Geração automática de dados para envio ao CNJ conforme resolução

#### 3.7.2 Regras de Negócio

- **RN-M07-01:** A consulta pública não deve exibir dados pessoais de partes em processos com segredo de justiça
- **RN-M07-02:** Relatórios com dados pessoais devem ser protegidos e acessíveis apenas a perfis autorizados
- **RN-M07-03:** O DataJud deve ser alimentado diariamente com as movimentações do dia anterior

---

### 3.8 M08 — Controle de Prazos

#### 3.8.1 Principais Funcionalidades

- **Calendário Processual:** Calendário integrado com feriados nacionais, estaduais e suspensos por portaria do TRE-CE
- **Gestão de Prazos:** Cadastro, monitoramento e alertas de prazos processuais e administrativos
- **Prazo Automático:** Cálculo automático de prazos com base na data de publicação/intimação
- **Suspensão de Prazos:** Registro e controle de suspensões de prazo (recesso, portaria, decisão)
- **Alertas e Notificações:** Envio de alertas por e-mail e notificação no sistema para prazos próximos ao vencimento
- **Histórico de Prazos:** Registro completo dos prazos com datas de início, fim, suspensões e intercorrências

#### 3.8.2 Regras de Negócio

- **RN-M08-01:** Prazos processuais são contados em dias úteis, excluindo sábados, domingos e feriados cadastrados
- **RN-M08-02:** O sistema deve enviar alertas 5, 3 e 1 dia(s) útil(eis) antes do vencimento do prazo
- **RN-M08-03:** O recesso forense deve ser cadastrado anualmente e suas datas carregadas automaticamente no sistema
- **RN-M08-04:** Prazos vencidos devem ser sinalizados com destaque vermelho no painel do servidor responsável

---

### 3.9 M09 — Painel Gerencial (BI)

#### 3.9.1 Principais Funcionalidades

- **Dashboard Executivo:** Indicadores consolidados para presidência e direção do tribunal
- **Indicadores de Acervo:** Total de processos por relator, classe, situação e tempo médio de tramitação
- **Indicadores de Produção:** Processos distribuídos, julgados e arquivados por período
- **Indicadores de Prazo:** Percentual de processos com prazo respeitado e em atraso
- **Taxa de Congestionamento:** Cálculo da taxa de congestionamento conforme metodologia CNJ
- **Comparativo Histórico:** Gráficos de evolução dos indicadores ao longo do tempo
- **Filtros Dinâmicos:** Filtragem por período, relator, classe e tipo de processo
- **Exportação de Gráficos:** Exportação de dashboards em PDF e imagem

#### 3.9.2 Indicadores Prioritários

| Indicador | Descrição | Referência CNJ |
|-----------|-----------|----------------|
| IPC | Índice de Produtividade Comparada | Resolução CNJ 76/2009 |
| Taxa de Congestionamento | (acervo inicial + distribuídos - julgados) / (acervo inicial + distribuídos) | Meta CNJ |
| Tempo Médio de Tramitação | Dias da distribuição ao trânsito em julgado | Meta CNJ |
| Taxa de Atendimento à Demanda | Julgados / Distribuídos | Meta CNJ |
| Processos por Relator | Acervo distribuído por magistrado | Gestão interna |

---

## 4. Fluxo Processual

### 4.1 Fluxo Completo do Processo de Segundo Grau

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUXO PROCESSUAL DE SEGUNDO GRAU — TRE-CE                │
└─────────────────────────────────────────────────────────────────────────────┘

[INGRESSO]
    │
    ├─→ Recurso oriundo do 1º grau (remessa pelo PJe)
    ├─→ Ação originária (MS, HC, AIJE, AIME, RO)
    └─→ Recurso de outro tribunal (TSE → TRE)
    │
    ▼
[RECEBIMENTO E TRIAGEM — Secretaria Judiciária]
    │
    ├─ Conferência de pressupostos de admissibilidade formal
    ├─ Classificação da classe processual e assunto
    ├─ Identificação de urgência (cautelar, HC)
    └─ Registro no sistema com número interno
    │
    ▼
[DISTRIBUIÇÃO]
    │
    ├─ Verificação de prevenção
    ├─ Verificação de impedimento/suspeição
    └─ Distribuição automática (sorteio ponderado)
    │
    ▼
[CONCLUSÃO AO RELATOR — Gabinete]
    │
    ├─ Análise inicial do processo
    ├─ Determinações de diligências (se necessário)
    └─ Retorno para diligências ←──────────────────┐
    │                                              │
    ▼                                              │
[INSTRUÇÃO PROCESSUAL — Secretaria + Gabinete]    │
    │                                              │
    ├─ Citações e intimações das partes           │
    ├─ Prazo para manifestações/resposta          │
    ├─ Juntada de documentos e informações        │
    ├─ Oitiva do Ministério Público (se cabível)  │
    └─ Perícias e diligências ────────────────────┘
    │
    ▼
[ELABORAÇÃO DO VOTO/DECISÃO — Gabinete]
    │
    ├─ Decisão Monocrática?
    │    ├─ SIM → Elaboração e assinatura → Secretaria → Publicação → [FIM FASE]
    │    └─ NÃO → Preparação de voto para sessão ↓
    │
    ▼
[INCLUSÃO EM PAUTA — Presidência/Secretaria]
    │
    ├─ Definição da data da sessão
    ├─ Publicação da pauta (mínimo 48h antes)
    └─ Inscrições para sustentação oral
    │
    ▼
[SESSÃO DE JULGAMENTO]
    │
    ├─ Sustentação oral (se inscrito)
    ├─ Leitura e deliberação sobre o voto
    ├─ Registro dos votos individuais
    ├─ Pedido de vista? → Processo adiado ──────→ [Retorno em sessão futura]
    └─ Proclamação do resultado
    │
    ▼
[LAVRATURA DO ACÓRDÃO — Gabinete]
    │
    ├─ Redação do acórdão (relator ou vencedor)
    ├─ Assinatura digital dos magistrados
    └─ Encaminhamento para publicação
    │
    ▼
[PUBLICAÇÃO — Secretaria/DJE]
    │
    ├─ Publicação no Diário da Justiça Eletrônico
    ├─ Intimação das partes
    └─ Início da contagem do prazo recursal
    │
    ▼
[FASE PÓS-JULGAMENTO]
    │
    ├─ Recursos Cabíveis?
    │    ├─ Embargos de Declaração → Julgamento em sessão
    │    ├─ Recurso ao TSE → Admissibilidade e remessa
    │    └─ NÃO → Aguarda prazo recursal
    │
    ▼
[TRÂNSITO EM JULGADO]
    │
    ├─ Certidão de trânsito em julgado
    ├─ Cumprimento da decisão (se aplicável)
    └─ Arquivamento dos autos
```

### 4.2 Eventos Processuais Principais

| Código | Evento | Descrição |
|--------|--------|-----------|
| EVT-001 | Distribuição | Designação do relator ao processo |
| EVT-002 | Conclusão | Envio dos autos ao relator |
| EVT-003 | Intimação | Comunicação a parte ou advogado |
| EVT-004 | Juntada | Inclusão de documento nos autos |
| EVT-005 | Despacho | Determinação do relator/secretaria |
| EVT-006 | Inclusão em Pauta | Processo colocado em pauta de julgamento |
| EVT-007 | Julgamento | Resultado da deliberação em sessão |
| EVT-008 | Publicação | Disponibilização no DJE |
| EVT-009 | Pedido de Vista | Adiamento do julgamento por vista |
| EVT-010 | Trânsito em Julgado | Certificação do trânsito em julgado |
| EVT-011 | Remessa | Encaminhamento a outro órgão |
| EVT-012 | Arquivamento | Encerramento definitivo do processo |

---

## 5. Perfis de Usuários e Permissões

### 5.1 Matriz de Permissões por Módulo

| Permissão | Desemb. | Assessor | Dir. Secr. | Analista | Admin | Advogado | Público |
|-----------|---------|----------|------------|----------|-------|----------|---------|
| Visualizar processo (público) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Visualizar processo (sigiloso) | ✓* | ✓* | ✓ | ✓** | ✓ | ✗ | ✗ |
| Elaborar minuta/voto | ✓ | ✓* | ✗ | ✗ | ✗ | ✗ | ✗ |
| Assinar decisão | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Movimentar processo | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Distribuir processo | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Gerir pauta de sessão | ✓*** | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Registrar votos em sessão | ✓ | ✗ | ✓*** | ✗ | ✗ | ✗ | ✗ |
| Emitir certidão | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Peticionamento eletrônico | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Configurar sistema | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| Relatórios gerenciais | ✓ | ✗ | ✓ | ✓** | ✓ | ✗ | ✗ |

*Apenas nos processos de seu gabinete  
**Acesso parcial, sem dados sigilosos  
***Apenas a presidência  

### 5.2 Descrição dos Perfis

#### 5.2.1 Desembargador/Relator

**Responsabilidades:**
- Condução da instrução processual sob sua relatoria
- Elaboração e assinatura de votos, decisões e despachos
- Participação em sessões de julgamento
- Presidência de sessões (quando na presidência)

**Recursos Específicos:**
- Acesso à fila do gabinete com visão prioritária
- Editor de minutas com modelos especializados
- Assinatura digital integrada ao certificado ICP-Brasil
- Visualização de estatísticas do próprio gabinete

#### 5.2.2 Assessor Judiciário

**Responsabilidades:**
- Apoio técnico ao desembargador
- Elaboração de minutas sob supervisão do relator
- Pesquisa jurisprudencial e doutrinária
- Controle de prazos do gabinete

**Recursos Específicos:**
- Acesso restrito aos processos do gabinete ao qual está vinculado
- Editor de minutas com envio para revisão do desembargador
- Visualização de alertas de prazo do gabinete

#### 5.2.3 Diretor de Secretaria Judiciária

**Responsabilidades:**
- Supervisão de toda a movimentação processual
- Distribuição e redistribuição de processos
- Assinatura de certidões e documentos oficiais da secretaria
- Gerenciamento da equipe de servidores

**Recursos Específicos:**
- Acesso irrestrito à secretaria judiciária
- Painel de controle de movimentação de todos os processos
- Aprovação de redistribuições e expedição de certidões

#### 5.2.4 Analista/Técnico Judiciário

**Responsabilidades:**
- Juntada e tramitação de documentos
- Expedição de intimações e ofícios
- Controle de prazos e guias
- Elaboração de certidões e despachos de rotina

**Recursos Específicos:**
- Acesso à fila de trabalho da secretaria
- Ferramentas de movimentação processual
- Alertas de prazo e pendências

#### 5.2.5 Administrador do Sistema

**Responsabilidades:**
- Configuração e manutenção do sistema
- Gestão de usuários, perfis e permissões
- Monitoramento de logs e auditoria
- Gestão de integrações com sistemas externos

**Recursos Específicos:**
- Console de administração
- Visualização de logs de auditoria
- Gerenciamento de parâmetros do sistema
- Gestão de feriados e calendário

#### 5.2.6 Advogado (Usuário Externo)

**Responsabilidades:**
- Acompanhamento de processos em que esteja habilitado
- Peticionamento eletrônico
- Inscrição para sustentação oral
- Recebimento de intimações eletrônicas

**Recursos Específicos:**
- Portal do advogado com autenticação via Gov.br ou OAB Digital
- Acesso aos autos dos processos em que é procurador
- Módulo de peticionamento com upload de documentos

#### 5.2.7 Consulta Pública

**Acesso:**
- Consulta por número de processo, partes e classe
- Visualização de movimentações não sigilosas
- Download de decisões públicas
- Sem necessidade de autenticação

---

## 6. Requisitos de Segurança

### 6.1 Autenticação

| Requisito | Descrição |
|-----------|-----------|
| **SEC-01** | Autenticação obrigatória por Gov.br (ConectaGov) para acesso externo (advogados, partes) |
| **SEC-02** | Autenticação integrada com o Active Directory do TRE-CE para usuários internos |
| **SEC-03** | Autenticação multifator (MFA) obrigatória para desembargadores e diretores |
| **SEC-04** | MFA disponível (opcional→obrigatório por configuração) para demais servidores |
| **SEC-05** | Sessões inativas devem ser encerradas automaticamente após 30 minutos |
| **SEC-06** | Bloqueio automático de conta após 5 tentativas de login consecutivas inválidas |
| **SEC-07** | Suporte a login via certificado digital ICP-Brasil (e-CPF, e-CNPJ) para magistrados |

### 6.2 Controle de Acesso (RBAC)

| Requisito | Descrição |
|-----------|-----------|
| **SEC-08** | Controle de acesso baseado em papéis (RBAC) com granularidade por módulo e operação |
| **SEC-09** | Acesso a processos sigilosos controlado por lista explícita de autorizados |
| **SEC-10** | Separação de papéis (segregation of duties): nenhum perfil pode realizar sozinho distribuição e aprovação de redistribuição |
| **SEC-11** | Revisão periódica de permissões (ao menos semestral) |
| **SEC-12** | Revogação automática de acesso ao fim do vínculo funcional (integração com sistema de RH) |

### 6.3 Criptografia de Dados

| Requisito | Descrição |
|-----------|-----------|
| **SEC-13** | Todos os dados em trânsito protegidos por TLS 1.3 ou superior |
| **SEC-14** | Dados sensíveis em repouso criptografados com AES-256 |
| **SEC-15** | Chaves criptográficas armazenadas em HSM (Hardware Security Module) ou serviço equivalente |
| **SEC-16** | Assinaturas digitais conformes ICP-Brasil (certificados tipo A3 ou A4 para magistrados) |
| **SEC-17** | Hashes SHA-256 para verificação de integridade de documentos armazenados |

### 6.4 Registro de Logs e Auditoria

| Requisito | Descrição |
|-----------|-----------|
| **SEC-18** | Log de todas as ações realizadas no sistema: acesso, leitura, criação, alteração e exclusão |
| **SEC-19** | Logs imutáveis armazenados em repositório separado com controle de integridade |
| **SEC-20** | Retenção de logs por mínimo de 5 anos, conforme LGPD e normas de guarda de documentos públicos |
| **SEC-21** | Painel de auditoria para administradores com filtros por usuário, data, ação e processo |
| **SEC-22** | Alertas automáticos para acessos fora do padrão (horário incomum, volume elevado de consultas) |
| **SEC-23** | Logs de acesso a documentos sigilosos com identificação do usuário e justificativa registrada |

### 6.5 Proteção contra Vulnerabilidades

| Requisito | Descrição |
|-----------|-----------|
| **SEC-24** | Proteção contra injeção SQL via uso de ORM e queries parametrizadas |
| **SEC-25** | Proteção contra XSS com sanitização de entradas e Content Security Policy (CSP) |
| **SEC-26** | Proteção contra CSRF com tokens anti-CSRF em formulários |
| **SEC-27** | Rate limiting para endpoints de autenticação e peticionamento |
| **SEC-28** | Varredura automática de vulnerabilidades (SAST/DAST) integrada ao pipeline CI/CD |
| **SEC-29** | Pentest bianual por empresa especializada |

### 6.6 Conformidade com LGPD

| Requisito | Descrição |
|-----------|-----------|
| **SEC-30** | Tratamento de dados pessoais com base legal na Lei nº 13.709/2018 (LGPD), art. 7º, II e III (cumprimento de obrigação legal e exercício de função pública) |
| **SEC-31** | Mapeamento de dados pessoais tratados (ROPA — Record of Processing Activities) |
| **SEC-32** | Direitos dos titulares: acesso, correção e eliminação (quando aplicável) via canal específico do TRE-CE |
| **SEC-33** | Relatório de Impacto à Proteção de Dados (RIPD) elaborado antes da implantação |
| **SEC-34** | Anonimização de dados em relatórios e consultas públicas quando não necessária identificação |
| **SEC-35** | Notificação de incidentes à ANPD conforme prazos legais (72h) |
| **SEC-36** | Contratos com fornecedores terceirizados devem prever cláusulas de conformidade LGPD |

---

## 7. Requisitos Não Funcionais

### 7.1 Desempenho

| ID | Requisito | Métrica |
|----|-----------|---------|
| **RNF-01** | Tempo de resposta para consultas simples (por número de processo) | ≤ 2 segundos |
| **RNF-02** | Tempo de resposta para consultas complexas (filtros múltiplos, relatórios) | ≤ 10 segundos |
| **RNF-03** | Tempo de carregamento da lista de processos do gabinete | ≤ 3 segundos |
| **RNF-04** | Suporte a pelo menos 200 usuários simultâneos em operação normal | Teste de carga comprovado |
| **RNF-05** | Processamento de uploads de até 30 MB por arquivo | ≤ 30 segundos |

### 7.2 Escalabilidade

| ID | Requisito |
|----|-----------|
| **RNF-06** | Arquitetura preparada para escalonamento horizontal (mínimo 2 instâncias em load balancer) |
| **RNF-07** | Banco de dados com suporte a réplicas de leitura para consultas públicas |
| **RNF-08** | Armazenamento de documentos em serviço escalável (object storage) com capacidade expansível |
| **RNF-09** | Design para suportar crescimento de 30% ao ano no volume de processos sem degradação |

### 7.3 Disponibilidade

| ID | Requisito | Métrica |
|----|-----------|---------|
| **RNF-10** | Disponibilidade do sistema em horário de expediente | ≥ 99,5% (≤ 3,6h/mês de indisponibilidade) |
| **RNF-11** | Disponibilidade do portal externo (consulta e peticionamento) | ≥ 99,0% (24x7) |
| **RNF-12** | Janela de manutenção programada | Fora do horário de expediente, com aviso de 48h |
| **RNF-13** | RTO (Recovery Time Objective) para falhas críticas | ≤ 4 horas |
| **RNF-14** | RPO (Recovery Point Objective) — perda máxima de dados | ≤ 1 hora |
| **RNF-15** | Backup diário dos dados com retenção mínima de 90 dias | Comprovado por relatório |

### 7.4 Usabilidade

| ID | Requisito |
|----|-----------|
| **RNF-16** | Interface responsiva para uso em desktop, tablet e dispositivos móveis |
| **RNF-17** | Onboarding guiado para novos usuários (tour interativo ou vídeos tutoriais) |
| **RNF-18** | Manual do usuário e FAQ integrados ao sistema (help contextual) |
| **RNF-19** | Ações críticas (exclusão, redistribuição) devem exigir confirmação explícita do usuário |
| **RNF-20** | O sistema deve persistir filtros e preferências de visualização por usuário |

### 7.5 Interoperabilidade

| ID | Requisito |
|----|-----------|
| **RNF-21** | Integração bidirecional com PJe via APIs REST/SOAP conforme padrão CNJ |
| **RNF-22** | Exportação de dados no formato DataJud (CNJ) conforme Resolução CNJ 331/2020 |
| **RNF-23** | Integração com DJE do TRE-CE via API para publicações automatizadas |
| **RNF-24** | Suporte ao protocolo SAML 2.0 ou OpenID Connect para SSO |
| **RNF-25** | APIs documentadas em padrão OpenAPI 3.0 para integração com outros sistemas do TRE-CE |

### 7.6 Acessibilidade (eMAG)

| ID | Requisito |
|----|-----------|
| **RNF-26** | Conformidade com eMAG (Modelo de Acessibilidade em Governo Eletrônico), versão 3.1 |
| **RNF-27** | Compatibilidade com leitores de tela (NVDA, JAWS) para usuários com deficiência visual |
| **RNF-28** | Contraste mínimo de 4.5:1 para texto normal e 3:1 para texto grande (WCAG 2.1 AA) |
| **RNF-29** | Navegação completa por teclado sem dependência de mouse |
| **RNF-30** | Textos alternativos em todas as imagens e ícones funcionais |
| **RNF-31** | Formulários com labels associados e mensagens de erro descritivas |

---

## 8. Modelo Conceitual de Dados

### 8.1 Principais Entidades

#### 8.1.1 PROCESSO

```
PROCESSO {
    id_processo          UUID (PK)
    numero_processo      VARCHAR(25) UNIQUE  -- Formato CNJ: NNNNNNN-DD.AAAA.J.TT.OOOO
    numero_interno       VARCHAR(20)
    classe_processual    FK → CLASSE_PROCESSUAL
    assunto_principal    FK → ASSUNTO
    situacao             ENUM [DISTRIBUIDO, INSTRUCAO, CONCLUSO, EM_PAUTA, JULGADO,
                               TRANSITADO, ARQUIVADO, SUSPENSO]
    sigilo               BOOLEAN
    nivel_sigilo         ENUM [PUBLICO, SEGREDO_JUSTICA, SIGILOSO]
    relator_atual        FK → MAGISTRADO
    data_distribuicao    TIMESTAMP
    data_autuacao        TIMESTAMP
    data_conclusao       TIMESTAMP
    origem               ENUM [PRIMEIRO_GRAU, TSE, ORIGINARIO, OUTRO_TRE]
    id_processo_pje      VARCHAR(50)  -- Referência no PJe
    peso_processual      INTEGER      -- Para cálculo de carga do gabinete
    criado_em            TIMESTAMP
    atualizado_em        TIMESTAMP
}
```

#### 8.1.2 PARTE

```
PARTE {
    id_parte             UUID (PK)
    nome                 VARCHAR(255)
    tipo                 ENUM [PESSOA_FISICA, PESSOA_JURIDICA, ORGAO_PUBLICO]
    cpf_cnpj             VARCHAR(18) (CRIPTOGRAFADO)
    email                VARCHAR(255) (CRIPTOGRAFADO)
    telefone             VARCHAR(20) (CRIPTOGRAFADO)
    endereco             TEXT (CRIPTOGRAFADO)
    criado_em            TIMESTAMP
}
```

#### 8.1.3 POLO_PROCESSUAL

```
POLO_PROCESSUAL {
    id_polo              UUID (PK)
    id_processo          FK → PROCESSO
    id_parte             FK → PARTE
    polo                 ENUM [ATIVO, PASSIVO, TERCEIRO_INTERESSADO, AMICUS_CURIAE]
    id_representante     FK → ADVOGADO (nullable)
}
```

#### 8.1.4 MOVIMENTACAO

```
MOVIMENTACAO {
    id_movimentacao      UUID (PK)
    id_processo          FK → PROCESSO
    tipo_movimento       FK → TIPO_MOVIMENTO  -- Tabela CNJ de movimentos
    descricao            TEXT
    data_movimento       TIMESTAMP
    id_usuario           FK → USUARIO
    complemento          JSONB        -- Dados específicos do movimento
    publicado_dje        BOOLEAN
    data_publicacao      DATE
}
```

#### 8.1.5 DOCUMENTO

```
DOCUMENTO {
    id_documento         UUID (PK)
    id_processo          FK → PROCESSO
    tipo_documento       FK → TIPO_DOCUMENTO
    nome_arquivo         VARCHAR(500)
    path_storage         TEXT         -- Caminho no object storage
    hash_sha256          CHAR(64)     -- Integridade
    tamanho_bytes        BIGINT
    mime_type            VARCHAR(100)
    sigiloso             BOOLEAN
    assinado             BOOLEAN
    id_assinatura        VARCHAR(255) -- Referência à assinatura ICP-Brasil
    id_usuario           FK → USUARIO -- Quem juntou
    data_juntada         TIMESTAMP
    cancelado            BOOLEAN      -- Nunca deletar
    data_cancelamento    TIMESTAMP
}
```

#### 8.1.6 SESSAO

```
SESSAO {
    id_sessao            UUID (PK)
    tipo_sessao          ENUM [ORDINARIA, EXTRAORDINARIA, ADMINISTRATIVA]
    data_hora_inicio     TIMESTAMP
    data_hora_fim        TIMESTAMP
    situacao             ENUM [AGENDADA, EM_ANDAMENTO, ENCERRADA, CANCELADA]
    numero_sessao        INTEGER
    ano_sessao           INTEGER
    local                VARCHAR(255)
    transmitida_ao_vivo  BOOLEAN
    url_transmissao      TEXT
    ata_assinada         BOOLEAN
}
```

#### 8.1.7 PAUTA_SESSAO

```
PAUTA_SESSAO {
    id_pauta             UUID (PK)
    id_sessao            FK → SESSAO
    id_processo          FK → PROCESSO
    ordem                INTEGER
    tipo_pauta           ENUM [JULGAMENTO, LIMINAR, EMBARGOS, PEDIDO_VISTA]
    situacao             ENUM [AGUARDANDO, JULGADO, ADIADO, RETIRADO]
    resultado            ENUM [PROCEDENTE, IMPROCEDENTE, PARCIAL, PREJUDICADO,
                               PEDIDO_VISTA, NAO_CONHECIDO]
    relator_sessao       FK → MAGISTRADO
    sustentacao_oral     BOOLEAN
    publicado_pauta      BOOLEAN
    data_publicacao      DATE
}
```

#### 8.1.8 VOTO_MAGISTRADO

```
VOTO_MAGISTRADO {
    id_voto              UUID (PK)
    id_pauta             FK → PAUTA_SESSAO
    id_magistrado        FK → MAGISTRADO
    voto                 ENUM [ACOMPANHA_RELATOR, DIVERGE, IMPEDIDO, AUSENTE, ABSTENCAO]
    fundamentacao        TEXT         -- Quando diverge
    data_voto            TIMESTAMP
}
```

#### 8.1.9 PRAZO

```
PRAZO {
    id_prazo             UUID (PK)
    id_processo          FK → PROCESSO
    tipo_prazo           FK → TIPO_PRAZO
    descricao            VARCHAR(500)
    data_inicio          DATE
    data_fim_calculada   DATE
    data_fim_efetiva     DATE
    situacao             ENUM [ABERTO, CUMPRIDO, VENCIDO, SUSPENSO, CANCELADO]
    id_usuario_resp      FK → USUARIO
    dias_prazo           INTEGER
    dias_uteis           BOOLEAN
    criado_em            TIMESTAMP
}
```

#### 8.1.10 LOG_AUDITORIA

```
LOG_AUDITORIA {
    id_log               UUID (PK)
    id_usuario           FK → USUARIO
    acao                 ENUM [LOGIN, LOGOUT, LEITURA, CRIACAO, ALTERACAO, EXCLUSAO,
                               ASSINATURA, DOWNLOAD, IMPRESSAO]
    tabela_alvo          VARCHAR(100)
    id_registro          UUID
    dados_anteriores     JSONB        -- Estado anterior (para alterações)
    dados_novos          JSONB        -- Estado novo
    ip_origem            INET
    user_agent           TEXT
    data_hora            TIMESTAMP
    id_processo_contexto FK → PROCESSO (nullable)
}
```

### 8.2 Diagrama de Relacionamentos (Resumo)

```
PROCESSO ──< POLO_PROCESSUAL >── PARTE
    │                 │
    │                 └── ADVOGADO
    │
    ├──< MOVIMENTACAO
    ├──< DOCUMENTO
    ├──< PRAZO
    └──< PAUTA_SESSAO >── SESSAO
              │
              └──< VOTO_MAGISTRADO >── MAGISTRADO
```

### 8.3 Entidades de Suporte

| Entidade | Descrição |
|----------|-----------|
| MAGISTRADO | Cadastro de desembargadores e suas configurações |
| USUARIO | Cadastro de todos os usuários do sistema |
| ADVOGADO | Cadastro de advogados com número OAB |
| CLASSE_PROCESSUAL | Tabela CNJ de classes processuais |
| ASSUNTO | Tabela CNJ de assuntos processuais |
| TIPO_MOVIMENTO | Tabela CNJ de movimentos processuais |
| TIPO_DOCUMENTO | Categorias de documentos processuais |
| FERIADO | Calendário de feriados nacionais, estaduais e do TRE |
| IMPEDIMENTO | Registro de impedimentos e suspeições de magistrados |
| MODELO_DOCUMENTO | Templates de decisões, certidões e ofícios |

---

## 9. Integrações

### 9.1 PJe (Processo Judicial Eletrônico)

| Aspecto | Detalhe |
|---------|---------|
| **Direção** | Bidirecional |
| **Protocolo** | REST API + WebService SOAP (legado) |
| **Autenticação** | OAuth 2.0 / certificado mútuo TLS |
| **Funcionalidades** | Recebimento de processos remetidos do 1º grau; envio de acórdãos e decisões; sincronização de movimentações; intimações eletrônicas |
| **Frequência** | Tempo real (webhooks) + conciliação diária |
| **Formato** | JSON (API REST) / XML (legado SOAP) |

**Fluxo de Recebimento do PJe:**
```
PJe 1º Grau → (evento remessa) → SGP-2G Webhook Receiver
    → Validação de dados
    → Criação do processo no SGP-2G
    → Download dos documentos via PJe API
    → Confirmação de recebimento ao PJe
    → Triagem e distribuição no SGP-2G
```

### 9.2 DataJud / CNJ

| Aspecto | Detalhe |
|---------|---------|
| **Direção** | Saída (TRE-CE → CNJ) |
| **Protocolo** | REST API (API DataJud CNJ) |
| **Autenticação** | Token JWT fornecido pelo CNJ |
| **Funcionalidades** | Envio diário de movimentações processuais; alimentação de estatísticas para relatórios nacionais |
| **Frequência** | Diária (batch noturno) + reprocessamento sob demanda |
| **Base Normativa** | Resolução CNJ nº 331/2020 |

### 9.3 Diário da Justiça Eletrônico (DJE-CE)

| Aspecto | Detalhe |
|---------|---------|
| **Direção** | Saída (SGP-2G → DJE) |
| **Protocolo** | REST API interna do TRE-CE |
| **Funcionalidades** | Envio de textos para publicação; consulta de data de publicação efetiva; emissão de certidões de publicação |
| **Frequência** | Diária (fechamento da edição às 23h59) |

### 9.4 Gov.br (ConectaGov)

| Aspecto | Detalhe |
|---------|---------|
| **Direção** | Entrada (autenticação) |
| **Protocolo** | OpenID Connect / OAuth 2.0 |
| **Funcionalidades** | Login de usuários externos (advogados, partes); verificação de identidade (nível prata ou ouro) |
| **Base Normativa** | Decreto nº 10.900/2021 (ConectaGov) |

### 9.5 TSE (Tribunal Superior Eleitoral)

| Aspecto | Detalhe |
|---------|---------|
| **Direção** | Bidirecional |
| **Protocolo** | REST API / SFTP (para transferência de autos) |
| **Funcionalidades** | Recebimento de recursos do TSE; remessa de processos para o TSE; consulta de jurisprudência |
| **Frequência** | Sob demanda |

### 9.6 OAB Nacional (Cadastro de Advogados)

| Aspecto | Detalhe |
|---------|---------|
| **Direção** | Entrada (consulta) |
| **Protocolo** | REST API da OAB |
| **Funcionalidades** | Validação do número de inscrição na OAB; verificação de situação (ativo/suspenso/cancelado) |
| **Frequência** | Sob demanda (no momento de habilitação nos autos) |

### 9.7 Sistemas Internos do TRE-CE

| Sistema | Integração |
|---------|------------|
| Sistema de RH | Sincronização de cadastro de servidores e magistrados; revogação automática de acesso |
| AD / LDAP | Autenticação de usuários internos via Single Sign-On (SSO) |
| Sistema Financeiro | Consulta de guias de pagamento de custas (quando aplicável) |
| Sistema de Protocolo | Recebimento de petições protocoladas no balcão físico |

### 9.8 Diagrama de Integrações

```
                    ┌─────────────────────────┐
                    │       SGP-2G            │
                    │    (TRE-CE 2º Grau)     │
                    └─────────┬───────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ↓                    ↓                    ↓
    ┌────────┐          ┌──────────┐         ┌──────────┐
    │  PJe   │          │ DataJud  │         │  DJE-CE  │
    │ 1º Grau│          │   CNJ    │         │ (portal) │
    └────────┘          └──────────┘         └──────────┘
         ↓                                        
    ┌────────┐          ┌──────────┐         ┌──────────┐
    │  TSE   │          │  Gov.br  │         │   OAB    │
    │(recursos│         │(ConectaGov│         │Nacional  │
    └────────┘          └──────────┘         └──────────┘
         ↓
    ┌──────────────────────────────────────┐
    │         Sistemas Internos TRE-CE     │
    │  RH │ AD/LDAP │ Financeiro │ Prot.  │
    └──────────────────────────────────────┘
```

---

## 10. Sugestões Técnicas

### 10.1 Arquitetura Recomendada

Recomenda-se uma **arquitetura modular com backend monolítico segmentado (Modular Monolith)** para a fase inicial, com possibilidade de extração de microsserviços específicos conforme crescimento da demanda. Esta abordagem equilibra:

- **Simplicidade operacional:** menor overhead de infraestrutura comparado a microsserviços completos
- **Coesão e consistência:** transações distribuídas são críticas em sistemas judiciais
- **Evolução gradual:** módulos bem definidos permitem extração futura de serviços independentes

**Exceção:** Os serviços de **notificações/alertas**, **geração de relatórios** e **integração com sistemas externos** devem ser implementados como serviços independentes desde o início (workers assíncronos), por suas características de carga e disponibilidade distintas.

```
┌───────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO                 │
│  Web App (SPA)  │  Portal Público  │  API Mobile (futura) │
└─────────────────────────┬─────────────────────────────────┘
                          │ HTTPS / REST API
┌─────────────────────────▼─────────────────────────────────┐
│              API GATEWAY / AUTENTICAÇÃO                    │
│         (JWT + Gov.br + AD integration)                    │
└─────────────────────────┬─────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────┐
│              APLICAÇÃO PRINCIPAL (Modular Monolith)        │
│  ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────┐  │
│  │Distribuição│ │Gabinete │ │Secretaria│ │   Sessões    │  │
│  └──────────┘ └─────────┘ └──────────┘ └──────────────┘  │
│  ┌──────────┐ ┌─────────┐ ┌──────────┐                    │
│  │  Prazos  │ │  Docs   │ │Relatórios│                    │
│  └──────────┘ └─────────┘ └──────────┘                    │
└───────┬──────────────────────────────┬────────────────────┘
        │                              │
┌───────▼────────┐           ┌─────────▼────────────────────┐
│  BANCO DE DADOS │           │    WORKERS ASSÍNCRONOS        │
│   PostgreSQL    │           │  Notificações │ Integrações  │
│  (+ réplica)    │           │  Relatórios   │ DJE/CNJ      │
└─────────────────┘           └──────────────────────────────┘
        │
┌───────▼────────┐
│ OBJECT STORAGE  │
│  (documentos)   │
│  Min.IO / S3    │
└─────────────────┘
```

### 10.2 Tecnologias Sugeridas

#### Backend

| Componente | Tecnologia Sugerida | Justificativa |
|------------|--------------------|--------------------|
| Linguagem | Java 21 (LTS) + Spring Boot 3.x | Maturidade, suporte público, ecossistema judicial (PJe usa Java) |
| Alternativa | Python 3.12 + Django / FastAPI | Se equipe tiver expertise, menor verbosidade |
| ORM | JPA/Hibernate | Suporte a PostgreSQL, migrações com Flyway |
| Filas assíncronas | Apache Kafka ou RabbitMQ | Processamento de notificações e integrações |
| Cache | Redis | Sessões, cache de consultas frequentes |
| Busca full-text | PostgreSQL FTS ou Elasticsearch | Busca em documentos com OCR |

#### Frontend

| Componente | Tecnologia Sugerida | Justificativa |
|------------|--------------------|--------------------|
| Framework | React 18+ ou Angular 17+ | Ecossistema maduro, acessibilidade, SPA |
| UI Components | Design System Gov.br (DS.GOV) | Conformidade com padrões do governo federal, acessibilidade nativa |
| Estado global | Redux Toolkit ou Zustand | Gerenciamento de estado para aplicação complexa |
| Testes | Jest + Testing Library + Playwright (E2E) | Cobertura completa |

#### Infraestrutura

| Componente | Tecnologia Sugerida | Justificativa |
|------------|--------------------|--------------------|
| Banco de dados | PostgreSQL 16 | Confiabilidade, JSON nativo, extensões (pgcrypto) |
| Contêineres | Docker + Kubernetes ou OpenShift | Portabilidade, escalabilidade |
| CI/CD | GitLab CI ou Jenkins | Integração com repositório de código |
| Object Storage | MinIO (on-premises) ou AWS S3 (gov) | Armazenamento escalável de documentos |
| Monitoramento | Prometheus + Grafana + Alertmanager | Observabilidade em tempo real |
| Logs | ELK Stack (Elasticsearch + Logstash + Kibana) | Análise e auditoria de logs |
| WAF | ModSecurity ou solução de mercado | Proteção contra ataques web |

### 10.3 Considerações de Deploy

- **Implantação preferencial:** data center próprio do TRE-CE ou nuvem privada governamental (BNDES Nuvem, TRE-CE Cloud), evitando dependência de provedores estrangeiros para dados judiciais
- **Nuvem pública como alternativa:** se utilizados, apenas provedores com contrato com a Administração Pública Brasileira e sedes no Brasil (Decreto nº 10.046/2019)
- **Alta disponibilidade:** deploy em pelo menos 2 zonas de disponibilidade com failover automático
- **Plano de continuidade:** ambiente de DR (Disaster Recovery) com RPO de 1h e RTO de 4h

### 10.4 Estratégia de Implantação

Recomenda-se implantação faseada em **3 etapas:**

| Fase | Prazo Estimado | Escopo |
|------|---------------|--------|
| **Fase 1 — MVP** | 6 meses | Distribuição, Gabinete, Secretaria, Gestão Documental, Prazos básicos |
| **Fase 2 — Julgamento** | 4 meses | Sessões de Julgamento, Publicações, Intimações eletrônicas |
| **Fase 3 — Inteligência** | 4 meses | BI/Painel Gerencial, Integrações completas CNJ/DataJud, Portal Externo avançado |

---

## Apêndices

### Apêndice A — Glossário

| Termo | Definição |
|-------|-----------|
| Acórdão | Decisão colegiada proferida por órgão colegiado (câmara ou pleno) |
| Autuação | Registro formal da entrada de um processo no tribunal |
| Conclusão | Encaminhamento dos autos ao relator ou presidente para decisão |
| DataJud | Base Nacional de Dados do Poder Judiciário (CNJ) |
| DJE | Diário da Justiça Eletrônico |
| Ementa | Resumo da decisão judicial |
| Habeas Corpus (HC) | Ação para proteção de liberdade de locomoção |
| ICP-Brasil | Infraestrutura de Chaves Públicas Brasileira |
| Liminar | Decisão provisória antes do julgamento final |
| Mandado de Segurança (MS) | Ação para proteção de direito líquido e certo |
| Pauta | Lista de processos agendados para julgamento em sessão |
| Plenário | Órgão colegiado composto por todos os magistrados do tribunal |
| Prevenção | Vinculação de processo a relator anterior por fato relacionado |
| Relator | Magistrado responsável pela instrução e voto em determinado processo |
| Sustentação Oral | Exposição verbal do advogado perante o órgão julgador |
| Trânsito em Julgado | Situação em que a decisão não admite mais recursos |
| Vista | Prazo conferido a magistrado para análise do processo antes do julgamento |

### Apêndice B — Referências Normativas

| Norma | Descrição |
|-------|-----------|
| Resolução CNJ nº 185/2013 | Institui o Sistema Processo Judicial Eletrônico (PJe) |
| Resolução CNJ nº 331/2020 | Institui o DataJud — Base Nacional de Dados do Poder Judiciário |
| Resolução CNJ nº 354/2020 | Dispõe sobre o processo eletrônico |
| Resolução TSE nº 23.478/2016 | Regulamenta o PJe na Justiça Eleitoral |
| Portaria TSE nº 319/2018 | Tabelas Processuais Unificadas |
| Lei nº 13.709/2018 | Lei Geral de Proteção de Dados (LGPD) |
| Lei nº 11.419/2006 | Informatização do processo judicial |
| Decreto nº 10.900/2021 | ConectaGov — plataforma de autenticação do governo federal |
| eMAG 3.1 | Modelo de Acessibilidade em Governo Eletrônico |
| ABNT NBR ISO/IEC 27001 | Segurança da informação — Sistemas de gestão |

---

*Documento elaborado com base nas melhores práticas de sistemas judiciais eletrônicos, diretrizes do CNJ, TSE e requisitos legais aplicáveis. Este documento constitui a especificação funcional de referência e deve ser atualizado ao longo do processo de desenvolvimento com o refinamento dos requisitos junto às partes interessadas.*

**Fim do Documento**
