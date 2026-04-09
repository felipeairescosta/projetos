# Dashboard PJe — TRE-CE

Dashboard interativo para análise de processos distribuídos no 1º e 2º Grau
do Tribunal Regional Eleitoral do Ceará, construído em Python + Streamlit.

Os CSVs do PJe ficam hospedados numa pasta pública do Google Drive e são
baixados automaticamente na primeira execução do app.

## 🚀 Rodar localmente

### 1. Criar ambiente virtual e instalar dependências

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se der erro de execução de script no Activate.ps1, rode antes:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Linux / macOS:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Rodar o dashboard

```bash
streamlit run app.py
```

Na **primeira execução**, o app baixa automaticamente os CSVs do Google Drive
para a pasta `data/` (leva 1–2 minutos, mostra um spinner).

Nas execuções seguintes, como os arquivos já estão em cache, o dashboard
abre imediatamente.

O navegador abre automaticamente em `http://localhost:8501`.

## ☁️ Publicar no Streamlit Cloud

1. Suba este projeto para um repositório no GitHub (o `.gitignore` já está
   configurado para não incluir o `venv/` nem os CSVs).
2. Acesse https://share.streamlit.io/ e conecte sua conta GitHub.
3. Clique em "New app", selecione o repositório, e aponte para `app.py`.
4. O Streamlit Cloud vai instalar as dependências, detectar o `runtime.txt`
   (Python 3.12), e na primeira execução vai baixar os CSVs do Drive.
5. Pronto — o dashboard fica disponível numa URL pública do Streamlit Cloud.

## 🔁 Atualizando os dados

Quando tiver CSVs novos do PJe:

1. Substitua os arquivos na pasta do Google Drive (mantendo os mesmos nomes)
2. No dashboard rodando, clique em "Clear cache" no menu hambúrguer (canto
   superior direito) e depois recarregue a página
3. O app vai baixar os novos arquivos automaticamente

## 📁 Estrutura do projeto

```
pje_dashboard/
├── app.py              # Dashboard principal (interface Streamlit)
├── data_loader.py      # Leitura dos CSVs + download do Google Drive
├── requirements.txt    # Bibliotecas Python
├── runtime.txt         # Fixa Python 3.12 no Streamlit Cloud
├── README.md           # Este arquivo
├── .gitignore          # Arquivos que não vão para o git
└── data/               # Vazia no repositório (CSVs são baixados em runtime)
    └── .gitkeep
```

## 🎯 Funcionalidades

- **Dois graus:** alterna entre 1º e 2º Grau
- **Filtros:** ano e órgão julgador (drill-down)
- **KPIs:** totais, arquivados, expedidos, em tramitação
- **Gráficos:** evolução temporal, top classes, top órgãos, situação atual,
  tipo de decisão, distribuição por unidade (CPROC / ASSESSORIA / OUTRAS)
- **Exclusão automática** de processos de Corregedoria no 2º Grau

## ✏️ Personalizando

- `data_loader.py` — filtros, classificações, leitura dos dados
- `app.py` — interface, KPIs, gráficos
