"""
Leitura de peças processuais do PJe (PDF ou texto puro).

Para processos originários : lê a petição inicial.
Para recursos              : lê sentença, recurso/razões e contrarrazões.

Extração de PDF via PyMuPDF (fitz).  Se o arquivo enviado for texto simples
(txt), o conteúdo é usado diretamente.
"""

from __future__ import annotations

import io
from typing import Optional

from process_generator import (
    DocumentoProcessual,
    TipoProcesso,
    classificar_tipo_processo,
    pecas_requeridas,
)


# ---------------------------------------------------------------------------
# Extração de texto
# ---------------------------------------------------------------------------

def extrair_texto_pdf(pdf_bytes: bytes) -> str:
    """
    Extrai o texto de um PDF usando PyMuPDF (fitz).

    Retorna o texto concatenado de todas as páginas, com separadores de página.
    Lança RuntimeError se fitz não estiver disponível.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise RuntimeError(
            "PyMuPDF não está instalado. Execute: pip install pymupdf"
        ) from exc

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    paginas: list[str] = []
    for i, pagina in enumerate(doc, start=1):
        texto = pagina.get_text().strip()
        if texto:
            paginas.append(f"[Página {i}]\n{texto}")
    doc.close()
    return "\n\n".join(paginas)


def extrair_texto(arquivo_bytes: bytes, nome_arquivo: str) -> str:
    """
    Detecta o tipo de arquivo pelo nome e extrai o texto adequadamente.

    Suporta .pdf (via fitz) e .txt / outros (UTF-8 direto).
    """
    if nome_arquivo.lower().endswith(".pdf"):
        return extrair_texto_pdf(arquivo_bytes)
    return arquivo_bytes.decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Carregamento de peças em um objeto processo
# ---------------------------------------------------------------------------

def carregar_peca(
    documento: DocumentoProcessual,
    arquivo_bytes: bytes,
    nome_arquivo: str,
) -> DocumentoProcessual:
    """
    Preenche o campo `conteudo` de um DocumentoProcessual a partir de bytes.

    Retorna o mesmo objeto mutado (conveniente para uso em Streamlit).
    """
    documento.conteudo = extrair_texto(arquivo_bytes, nome_arquivo)
    documento.nome_arquivo = nome_arquivo
    return documento


# ---------------------------------------------------------------------------
# Fábrica: lista de peças esperadas para uma classe processual
# ---------------------------------------------------------------------------

def pecas_para_classe(classe: str) -> list[DocumentoProcessual]:
    """
    Atalho: a partir da classe processual (string), retorna a lista de
    DocumentoProcessual vazios prontos para ser preenchidos pelo usuário.

    Exemplo:
        pecas = pecas_para_classe("RECURSO ORDINÁRIO")
        # → [Sentença, Recurso/Razões, Contrarrazões]
    """
    tipo = classificar_tipo_processo(classe)
    return pecas_requeridas(tipo)


# ---------------------------------------------------------------------------
# Exportações públicas
# ---------------------------------------------------------------------------

__all__ = [
    "extrair_texto_pdf",
    "extrair_texto",
    "carregar_peca",
    "pecas_para_classe",
]
