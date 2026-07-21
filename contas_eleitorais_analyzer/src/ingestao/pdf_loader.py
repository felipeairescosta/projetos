"""Extração de texto dos documentos do PJe (processos de prestação de contas).

O que já funciona: `extrair_texto_de_pdfs` abre todos os PDFs de uma pasta
(ex.: `docs_pje/`) e devolve o texto bruto de cada um — útil para inspecionar
manualmente como o PJe formata os documentos (demonstrativo de receitas e
despesas, recibos eleitorais, extratos etc.) antes de escrever um parser.

O que é um ponto de extensão: `construir_prestacao_de_pdfs` ainda não sabe
mapear esse texto para os campos de `PrestacaoContas`, porque o layout exato
dos documentos do PJe usados neste caso concreto ainda não foi fornecido.
Assim que os documentos forem colocados em `docs_pje/`, use
`extrair_texto_de_pdfs` para ver o texto real extraído e então implemente as
expressões regulares/mapeamentos necessários nesta função — o motor de
regras (`src/regras.py`) e o relatório já funcionam com qualquer
`PrestacaoContas` corretamente montada, independentemente da origem dos dados.
"""

from __future__ import annotations

from pathlib import Path

from ..modelos import PrestacaoContas


def extrair_texto_de_pdfs(pasta: str | Path) -> dict[str, str]:
    """Extrai o texto de cada PDF encontrado em `pasta`.

    Retorna um dicionário {nome_do_arquivo: texto_extraido}.
    """
    import pdfplumber

    pasta = Path(pasta)
    textos: dict[str, str] = {}
    for caminho_pdf in sorted(pasta.glob("*.pdf")):
        with pdfplumber.open(caminho_pdf) as pdf:
            paginas = [pagina.extract_text() or "" for pagina in pdf.pages]
        textos[caminho_pdf.name] = "\n".join(paginas)
    return textos


def construir_prestacao_de_pdfs(pasta: str | Path) -> PrestacaoContas:
    """Ponto de extensão: monta uma `PrestacaoContas` a partir dos PDFs do PJe.

    Ainda não implementado — depende do layout real dos documentos que serão
    colocados em `docs_pje/`. Para implementar:

    1. Rode `extrair_texto_de_pdfs(pasta)` e inspecione o texto de um
       documento real (demonstrativo de receitas/despesas, recibo eleitoral
       etc.).
    2. Escreva expressões regulares/parsing para localizar candidato/comitê,
       cada receita e cada despesa dentro do texto.
    3. Monte os objetos `Doador`, `Receita`, `Despesa` e `CandidatoOuComite`
       (ver `src/modelos.py`) e devolva a `PrestacaoContas` completa — ela
       pode ser passada diretamente para `analisar()` em `src/analisador.py`.
    """
    raise NotImplementedError(
        "Extração estruturada dos PDFs do PJe ainda não implementada — "
        "layout dos documentos reais ainda não disponível. Veja o docstring "
        "desta função para os passos de implementação."
    )
