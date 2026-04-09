# 🚀 Guia de Implantação (Deployment)

## Problema: Arquivos CSV muito grandes

Os arquivos CSV (especialmente do 2º Grau) são bastante grandes (~50MB no total) e não podem ser versionados diretamente no GitHub. 

**Solução**: O `data_loader.py` foi atualizado para:
1. **Localmente**: Buscar os CSVs na pasta `data/` (funciona quando clonado localmente)
2. **Streamlit Cloud**: Baixar os CSVs de um servidor remoto via URL

---

## ✅ Passo 1: Fazer commit e push para GitHub

Agora que `data/*.csv` está no `.gitignore`, você pode fazer commit sem problemas:

```powershell
cd c:\Projetos\pje_dashboard
git add .gitignore data_loader.py requirements.txt DEPLOYMENT.md
git commit -m "feat: hospedar dados externamente para Streamlit Cloud"
git push origin main
```

---

## 📁 Passo 2: Hospedar os CSVs em um serviço externo

Escolha uma opção abaixo:

### **Opção A: Google Drive (Recomendado para dados públicos)**

1. Crie uma pasta no Google Drive
2. Faça upload de todos os CSVs da pasta `data/`
3. Configure permissões para **"Visualizar"** (qualquer pessoa com link)
4. Para cada arquivo, obtenha o **ID do arquivo** (está na URL)
5. Construa URLs em formato de download direto:
   ```
   https://drive.google.com/file/d/13jku0xBXuyqU06lKfna845IcoR71PokE/view?usp=drive_link
   https://drive.google.com/file/d/1P69FKcXohwQwFku85bDxlyKY9L1Fj8Dq/view?usp=drive_link
   https://drive.google.com/file/d/12FxSZZZsBbe-hmVqR7m1nEqygcGkxUxd/view?usp=drive_link
   https://drive.google.com/file/d/1aORx-_q6fft64MSvwgkHtmhPO-nVMFfp/view?usp=drive_link
   https://drive.google.com/file/d/1OkZHZxQSTdSQwvog8-FvA_cuZVUStEQp/view?usp=drive_link
   https://drive.google.com/file/d/1kfoEWdLpukEfuvDZhPWFbAh5IxRhDk7p/view?usp=drive_link
   https://drive.google.com/file/d/12tHfIJjhDiKdx7FIO9SLclFs6S1PJg6_/view?usp=drive_link
   https://drive.google.com/file/d/1MLC6UK7i31NqNQkpqC11qE2UiZlWe1_f/view?usp=drive_link
   https://drive.google.com/file/d/1OkZHZxQSTdSQwvog8-FvA_cuZVUStEQp/view?usp=drive_link
   https://drive.google.com/file/d/1kfoEWdLpukEfuvDZhPWFbAh5IxRhDk7p/view?usp=drive_link
   https://drive.google.com/file/d/12tHfIJjhDiKdx7FIO9SLclFs6S1PJg6_/view?usp=drive_link
   https://drive.google.com/file/d/1MLC6UK7i31NqNQkpqC11qE2UiZlWe1_f/view?usp=drive_link
   https://drive.google.com/file/d/16pZKuRQPJF9GOzEaWltyJIHLECrq4sDq/view?usp=drive_link
   https://drive.google.com/file/d/10RakG89g2UEtvikl7ndSb6_HzO557tZ5/view?usp=drive_link
   https://drive.google.com/file/d/1Mh0qfL9XM-k2gMUQyeygzVZfPq1oiFnY/view?usp=drive_link
   https://drive.google.com/file/d/1xMnqZ6tBvC89pOLiFJoHtHjpXma-A0hf/view?usp=drive_link
   https://drive.google.com/file/d/1fY4ninnWvcr6AsFamd8RtOPHBBOu-bVO/view?usp=drive_link
   https://drive.google.com/file/d/1FiuQYzdGv2a75wGlMX3FXsP72JFTpzJi/view?usp=drive_link
   https://drive.google.com/file/d/1phjhfRjfRnnL5LCxZm1JmHFcYWIB0ovh/view?usp=drive_link
   https://drive.google.com/file/d/1_Ir_nYFUa7jeF_Imzd_4HmeQEGmqiYun/view?usp=drive_link
   https://drive.google.com/file/d/1gHwJmHR7RrMfV3Ti076Z-2nE1pVeOmux/view?usp=drive_link
   https://drive.google.com/file/d/1skzbfW1xBvB3SGZvF38K7G6EaFi_724T/view?usp=drive_link
   https://drive.google.com/file/d/1XxeuFXjXxuLqp0wRuHocUfjTGvdwkWj3/view?usp=drive_link
   https://drive.google.com/file/d/1Q2zYcqqntBtLSLhYUogq2fTi98uGoRTh/view?usp=drive_link
   ```
6. Atualize `BASE_URL` em `data_loader.py`:
   ```python
   BASE_URL = "https://drive.google.com/drive/folders/1Qpe9AKs1UvC2cmiftBjt6ItAJ_7VgsFJ"
   ```

Exemplo com Google Drive (se todos los arquivos estiverem em uma pasta compartilhada publica):
```python
BASE_URL = "https://drive.google.com/uc?export=download&id="  # Adicionar ID de cada arquivo
```

### **Opção B: Dropbox (Simples para compartilhamento)**

1. Faça upload dos CSVs para Dropbox
2. Gere URL compartilhável para cada arquivo
3. Troque `?dl=0` para `?dl=1` (download direto)
4. Configure `BASE_URL` em `data_loader.py`

### **Opção C: AWS S3 (Melhor para grandes volumes)**

1. Crie um bucket S3 público (ou com acesso restrito)
2. Faça upload dos CSVs
3. Configure permissões de leitura
4. Use URLs do S3:
   ```python
   BASE_URL = "https://seu-bucket.s3.amazonaws.com/dados/"
   ```

### **Opção D: Servidor FTP/HTTP da instituição**

Se o TRE-CE tiver um servidor interno:
```python
BASE_URL = "https://seu-intranet.tre-ce.gov.br/dados/pje/"
```

---

## 🔧 Passo 3: Atualizar BASE_URL

Edite `data_loader.py` e substitua a linha:

```python
BASE_URL = "https://seu-dominio.com/dados/"
```

Por a URL real do seu serviço:

```python
# Exemplo com Google Drive
BASE_URL = "https://drive.google.com/uc?export=download&id="
# Depois adicione o ID específico de cada arquivo

# OU Exemplo com Dropbox
BASE_URL = "https://dl.dropboxusercontent.com/s/seu-id/dados/"

# OU Exemplo com S3
BASE_URL = "https://seu-bucket.s3.amazonaws.com/dados/"
```

---

## 🧪 Passo 4: Testar localmente

Antes de fazer deploy, teste se o app tem acesso aos dados:

```powershell
streamlit run app.py
```

Se tudo funcionar com os CSVs locais, este é um bom sinal. ✅

---

## 🚀 Passo 5: Fazer deploy no Streamlit Cloud

1. Após atualizar `BASE_URL` e fazer push para GitHub:
   ```
   git add data_loader.py
   git commit -m "chore: adicionar URL dos dados remotos"
   git push origin main
   ```

2. Acesse [share.streamlit.io](https://share.streamlit.io)

3. Clique em "New app"

4. Conecte seu GitHub e selecione:
   - **Repo**: seu repositório
   - **Branch**: `main`
   - **Main file path**: `app.py`

5. Clique em "Deploy"

6. Aguarde 2-3 minutos para build completo

---

## 🐛 Solução de problemas

### "Erro ao baixar arquivo"
- Verifique se a URL é acessível publicamente
- Teste a URL em um navegador
- Confirme a codificação (UTF-8) e delimitador (`;`) dos CSVs

### "Timeout ao carregar dados"
- Os CSVs podem ser muito grandes
- Considere particionar em arquivos menores
- Aumente o timeout em `requests.get(url, timeout=30)`

### "Permission denied"
- Verifique permissões de leitura da URL
- Google Drive: certifique-se que é "Visualizar"
- S3: adicione CORS policy se necessário

---

## 📊 Otimizações futuras

Se os dados crescerem muito, considere:

1. **Comprimir dados**: Use Parquet (`pyarrow`) ao invés de CSV
   ```python
   pip install pyarrow
   df = pd.read_parquet(url)
   ```

2. **Cache no servidor**: Implemente cache Streamlit melhorado

3. **Banco de dados**: Migrar para PostgreSQL ou DuckDB

4. **Servidor próprio**: Hospedar os dados em um servidor FastAPI da instituição

---

## ❓ Dúvidas?

Consulte:
- [Streamlit Cloud Docs](https://docs.streamlit.io/deploy/streamlit-cloud)
- [Pandas read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [Requests Library](https://requests.readthedocs.io/)
