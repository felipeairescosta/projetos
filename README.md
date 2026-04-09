# Dashboard PJe — TRE-CE

Dashboard interativo para análise de processos distribuídos no 1º e 2º Grau
do Tribunal Regional Eleitoral do Ceará, construído em Python + Streamlit.

## 📋 Pré-requisitos

- Python 3.10 ou superior (recomendado: 3.12)
- VS Code (opcional, mas recomendado)

## 🚀 Primeira execução (setup completo)

Abra um terminal na pasta do projeto (onde está o arquivo `app.py`) e siga
os passos abaixo:

### 1. Criar um ambiente virtual

Um "ambiente virtual" é uma pasta isolada onde as bibliotecas do projeto
ficam instaladas sem interferir no Python do sistema. É boa prática.

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Se der erro de execução de script, rode antes:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Linux / macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

Você saberá que o ambiente está ativo porque aparece `(venv)` no início do
prompt do terminal.

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

Isso instala Streamlit, Pandas e Plotly. Leva 1–2 minutos.

### 3. Colocar os CSVs do PJe

Copie todos os arquivos CSV do PJe para a pasta `data/` do projeto.
Os nomes esperados são:

- `pje-1o-totalidade-de-processos-autuados*.csv` (vários arquivos, um por ano)
- `pje-2o-processos-distribuidos-e-redistribuidos-por-periodo*.csv`

O código lê automaticamente todos os arquivos que seguem esse padrão.

### 4. Rodar o dashboard

```bash
streamlit run app.py
```

O Streamlit vai abrir automaticamente o dashboard no navegador, no endereço
`http://localhost:8501`. Pronto!

## 🔄 Execuções futuras

Toda vez que for usar o dashboard de novo, só precisa:

```bash
# Ativar o venv (Windows)
venv\Scripts\Activate.ps1

# Ou Linux/macOS
source venv/bin/activate

# Rodar
streamlit run app.py
```

## 🔁 Atualizando os dados

Quando receber CSVs novos do PJe, basta copiá-los para a pasta `data/`
(substituindo os antigos se quiser) e reiniciar o Streamlit.
O dashboard usa cache para não recarregar tudo a cada interação, mas
detecta mudanças nos arquivos automaticamente.

## 📁 Estrutura do projeto

```
pje_dashboard/
├── app.py              # Dashboard principal (interface Streamlit)
├── data_loader.py      # Funções de leitura e filtros dos CSVs
├── requirements.txt    # Lista de bibliotecas Python
├── README.md           # Este arquivo
└── data/               # Pasta para os CSVs do PJe
    └── (seus CSVs aqui)
```

## 🎯 Funcionalidades

- **Dois graus:** alterna entre 1º e 2º Grau
- **Filtros:** ano e órgão julgador (drill-down)
- **KPIs:** totais, arquivados, expedidos, em tramitação
- **Gráficos:** evolução temporal, top classes, top órgãos, situação atual,
  tipo de decisão, distribuição por unidade (CPROC / ASSESSORIA / OUTRAS)
- **Exclusão automática** de processos de Corregedoria no 2º Grau

## ✏️ Personalizando

Quer mudar as regras de classificação, adicionar filtros, criar novos gráficos?
Todo o código está em apenas dois arquivos:

- `data_loader.py` — mexe nos filtros e na leitura dos dados
- `app.py` — mexe na interface, nos KPIs e nos gráficos

É bem mais simples do que parece. Dá para fazer mudanças grandes em
minutos — ao contrário da versão HTML anterior, onde cada alteração
exigia regenerar o arquivo inteiro.
