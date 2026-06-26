#!/usr/bin/env python3
"""
Sincroniza o array TOPICS do manual_pje_dicas_docs.html com as fontes ao vivo:
  - PJe Dicas Eleitoral: https://pjeje.github.io/dicas/
  - Documentação CNJ:    https://docs.pje.jus.br/

Execução:
    python scripts/sync_pje_html.py [--html PATH] [--dry-run]

O script compara o que existe hoje na navegação de cada site com o que está
codificado no array TOPICS do HTML e imprime um diff. Se houver alterações
detectadas, reescreve o bloco TOPICS no arquivo.
"""

import argparse
import json
import re
import sys
import textwrap
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional


# ── Configuração ──────────────────────────────────────────────────────────────

HTML_FILE   = Path(__file__).parent.parent / "manual_pje_dicas_docs.html"
BASE_ELEIT  = "https://pjeje.github.io/dicas"
BASE_DOCS   = "https://docs.pje.jus.br"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; PJeSyncBot/1.0; "
        "+https://github.com/felipeairescosta/projetos)"
    )
}

# Timeout por requisição (segundos)
TIMEOUT = 20


# ── Utilitários HTTP ──────────────────────────────────────────────────────────

def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        charset = r.headers.get_content_charset() or "utf-8"
        return r.read().decode(charset, errors="replace")


# ── Parser genérico de links de nav ──────────────────────────────────────────

class NavLinkParser(HTMLParser):
    """Coleta todos os <a> dentro de elementos de navegação."""

    def __init__(self, nav_selectors: tuple[str, ...]):
        super().__init__()
        self._nav_selectors = nav_selectors
        self._depth         = 0      # profundidade dentro de um nav
        self._in_nav        = False
        self.links: list[tuple[str, str]] = []   # (text, href)
        self._cur_text: list[str] = []
        self._in_a   = False
        self._cur_href = ""

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        cls = attrs_d.get("class", "")
        role = attrs_d.get("role", "")
        tag_lower = tag.lower()

        # Detecta abertura de bloco de nav
        if tag_lower in ("nav", "aside") or any(s in cls for s in self._nav_selectors) or role == "navigation":
            self._in_nav = True
            self._depth += 1
            return

        if self._in_nav:
            if tag_lower in ("nav", "ul", "ol", "li", "div", "section"):
                self._depth += 1
            if tag_lower == "a":
                self._in_a = True
                self._cur_href = attrs_d.get("href", "")
                self._cur_text = []

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if self._in_nav:
            if tag_lower == "a" and self._in_a:
                text = " ".join("".join(self._cur_text).split())
                if text and self._cur_href and not self._cur_href.startswith(("http://", "https://", "mailto:", "#")):
                    self.links.append((text, self._cur_href))
                self._in_a = False
                self._cur_href = ""
                self._cur_text = []
            if tag_lower in ("nav", "ul", "ol", "li", "div", "section", "aside"):
                self._depth -= 1
                if self._depth <= 0:
                    self._in_nav = False
                    self._depth = 0

    def handle_data(self, data):
        if self._in_a:
            self._cur_text.append(data)


# ── Raspagem — PJe Dicas Eleitoral ───────────────────────────────────────────

def _scrape_eleit_index() -> list[dict]:
    """
    Raspa a página inicial do PJe Dicas Eleitoral e retorna lista de tópicos
    com (id, t, cat, url, subs).
    """
    html = fetch(BASE_ELEIT + "/")

    # Extrai links de navegação (sidebar/nav)
    parser = NavLinkParser(("sidebar", "nav", "menu", "toc"))
    parser.feed(html)

    topics = []
    seen_paths: set[str] = set()

    # Mapeia categorias por padrões de path
    CAT_MAP = [
        ("/acesso",          "Acesso"),
        ("/advogados",       "Usuários"),
        ("/atos",            "Processamento"),
        ("/autos",           "Processamento"),
        ("/autuacao",        "Autuação"),
        ("/classes",         "Autuação"),
        ("/comunicacao",     "Comunicação"),
        ("/consulta",        "Consulta"),
        ("/defensorias",     "Usuários"),
        ("/distribuicao",    "Autuação"),
        ("/etiquetas",       "Gestão"),
        ("/papeis",          "Gestão"),
        ("/prazos",          "Processamento"),
        ("/procuradorias",   "Usuários"),
        ("/recursos",        "Processamento"),
        ("/remessa",         "Processamento"),
        ("/sessaojulg",      "Julgamento"),
        ("/sigilo",          "Segurança"),
        ("/manual",          "Apoio"),
        ("/automacao",       "Automação"),
        ("/tramitacao",      "Gestão"),
        ("/peticionamento",  "Eleitoral"),
        ("/wiki",            "Apoio"),
    ]

    def guess_cat(path: str) -> str:
        for prefix, cat in CAT_MAP:
            if path.startswith(prefix):
                return cat
        return "Geral"

    idx = 1
    for text, href in parser.links:
        # Normaliza href: deve começar com /
        path = href if href.startswith("/") else "/" + href
        # Filtra: só paths de primeiro nível (ex: /acesso/ e não /acesso/mfa/)
        segments = [s for s in path.strip("/").split("/") if s]
        if len(segments) != 1:
            continue
        if path in seen_paths:
            continue
        seen_paths.add(path)

        topic_id = f"e{idx}"
        topics.append({
            "id":    topic_id,
            "src":   "eleit",
            "t":     text,
            "cat":   guess_cat(path),
            "url":   path + "/" if not path.endswith("/") else path,
        })
        idx += 1

    return topics


def _scrape_eleit_subs(topic_url: str) -> list[list[str]]:
    """Raspa subtópicos de uma página de tópico do PJe Dicas."""
    try:
        html = fetch(BASE_ELEIT + topic_url)
    except Exception:
        return []

    parser = NavLinkParser(("sidebar", "nav", "menu", "toc", "subnav"))
    parser.feed(html)

    subs = []
    seen: set[str] = set()
    base_seg = topic_url.strip("/")

    for text, href in parser.links:
        path = href if href.startswith("/") else "/" + href
        segs = [s for s in path.strip("/").split("/") if s]
        # Sub-página: dois segmentos, primeiro igual ao da URL-pai
        if len(segs) == 2 and segs[0] == base_seg:
            if path not in seen:
                seen.add(path)
                subs.append([text, path + "/"])

    return subs


# ── Raspagem — Docs CNJ ───────────────────────────────────────────────────────

def _scrape_docs_index() -> list[dict]:
    """Raspa o índice do docs.pje.jus.br e retorna tópicos de nível 1."""
    html = fetch(BASE_DOCS + "/")

    parser = NavLinkParser(("sidebar", "nav", "menu", "toc", "navbar"))
    parser.feed(html)

    topics: list[dict] = []
    seen: set[str] = set()

    CAT_MAP_DOCS = [
        ("/manuais-de-uso",             "Manuais"),
        ("/manuais-basicos",            "Técnico"),
        ("/configurações-do-pje",       "Configuração"),
        ("/configuracoes-do-pje",       "Configuração"),
        ("/release-notes",              "Técnico"),
        ("/manuais-de-inicializacao",   "Técnico"),
        ("/servicos-negociais",         "Técnico"),
    ]

    def guess_cat_docs(path: str) -> str:
        lp = path.lower()
        for prefix, cat in CAT_MAP_DOCS:
            if lp.startswith(prefix.lower()):
                return cat
        return "Geral"

    idx = 1
    for text, href in parser.links:
        path = href if href.startswith("/") else "/" + href
        segments = [s for s in path.strip("/").split("/") if s]
        if not segments:
            continue
        # Nível raiz ou primeiro nível
        if len(segments) > 1:
            continue
        if path in seen:
            continue
        seen.add(path)

        topic_id = f"d{idx}"
        topics.append({
            "id":  topic_id,
            "src": "docs",
            "t":   text,
            "cat": guess_cat_docs(path),
            "url": path + "/" if not path.endswith("/") else path,
        })
        idx += 1

    return topics


def _scrape_docs_subs(topic_url: str) -> list[list[str]]:
    """Raspa subtópicos de uma seção do docs.pje.jus.br."""
    try:
        html = fetch(BASE_DOCS + topic_url)
    except Exception:
        return []

    parser = NavLinkParser(("sidebar", "nav", "menu", "toc"))
    parser.feed(html)

    subs = []
    seen: set[str] = set()
    base_seg = topic_url.strip("/").split("/")[0] if topic_url.strip("/") else ""

    for text, href in parser.links:
        path = href if href.startswith("/") else "/" + href
        segs = [s for s in path.strip("/").split("/") if s]
        if segs and segs[0].lower() == base_seg.lower() and len(segs) >= 2:
            if path not in seen:
                seen.add(path)
                subs.append([text, path])

    return subs[:8]   # limita para não poluir


# ── Leitura / escrita do HTML ─────────────────────────────────────────────────

_TOPICS_RE = re.compile(
    r"(const TOPICS\s*=\s*\[)(.*?)(\];)",
    re.DOTALL,
)


def _js_to_json(raw: str) -> str:
    """
    Converte JS object literal para JSON válido:
    - Remove comentários // e /* */
    - Troca aspas simples por duplas (fora de aspas duplas)
    - Coloca aspas em chaves não-quoted
    - Remove trailing commas
    """
    # Remove comentários de bloco
    raw = re.sub(r"/\*.*?\*/", "", raw, flags=re.DOTALL)
    # Remove comentários de linha
    raw = re.sub(r"//[^\n]*", "", raw)

    # Converte aspas simples → duplas (string-aware)
    result = []
    i = 0
    in_double = False
    in_single = False
    while i < len(raw):
        ch = raw[i]
        if in_double:
            result.append(ch)
            if ch == "\\" :
                i += 1
                if i < len(raw):
                    result.append(raw[i])
            elif ch == '"':
                in_double = False
        elif in_single:
            if ch == "\\":
                i += 1
                if i < len(raw):
                    nc = raw[i]
                    # Escapes válidos em JSON
                    result.append("\\" + nc)
                else:
                    result.append("\\")
            elif ch == "'":
                result.append('"')
                in_single = False
            else:
                result.append(ch)
        else:
            if ch == '"':
                in_double = True
                result.append(ch)
            elif ch == "'":
                in_single = True
                result.append('"')
            else:
                result.append(ch)
        i += 1
    raw = "".join(result)

    # Coloca aspas em chaves JS não-quoted: {key: → {"key":
    raw = re.sub(r'([{,])\s*([A-Za-z_]\w*)\s*:', r'\1"\2":', raw)

    # Remove trailing commas antes de ] ou }
    raw = re.sub(r",\s*([\]}])", r"\1", raw)

    return raw


def read_current_topics(html_path: Path) -> list[dict]:
    """Extrai o array TOPICS atual do HTML como lista de dicts."""
    text = html_path.read_text(encoding="utf-8")
    m = _TOPICS_RE.search(text)
    if not m:
        raise ValueError("Não foi possível encontrar 'const TOPICS' no HTML.")

    raw = "[" + m.group(2) + "]"
    json_str = _js_to_json(raw)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # Mostra contexto do erro para debug
        lines = json_str.splitlines()
        err_line = e.lineno - 1
        ctx = "\n".join(lines[max(0, err_line-2):err_line+3])
        raise ValueError(f"Falha ao parsear TOPICS como JSON (linha {e.lineno}): {e}\n{ctx}") from e


def _topic_to_js(t: dict, indent: str = "  ") -> str:
    """Serializa um tópico para JS literal (uma linha por campo)."""

    def js_str(s):
        return json.dumps(s, ensure_ascii=False)

    def js_arr_str(lst):
        inner = ",".join(js_str(x) for x in lst)
        return f"[{inner}]"

    def js_arr_arr(lst):
        items = ",".join(f"[{js_str(a)},{js_str(b)}]" for a, b in lst)
        return f"[{items}]"

    subs    = t.get("subs", [])
    related = t.get("related", [])

    lines = [
        f"{indent}{{id:{js_str(t['id'])}, src:{js_str(t['src'])}, t:{js_str(t['t'])}, cat:{js_str(t['cat'])}, url:{js_str(t['url'])},",
        f"{indent} desc:{js_str(t.get('desc',''))},",
        f"{indent} subs:{js_arr_arr(subs)},",
        f"{indent} related:{js_arr_arr(related)}}}",
    ]
    return "\n".join(lines)


def build_topics_js(topics_eleit: list[dict], topics_docs: list[dict]) -> str:
    """Monta o bloco TOPICS completo em JavaScript."""
    parts = ["  // ════════ PJe ELEITORAL ════════"]
    parts += [_topic_to_js(t) + "," for t in topics_eleit]
    parts += ["  // ════════ DOCS CNJ ════════"]
    parts += [_topic_to_js(t) + "," for t in topics_docs]
    # Remove a última vírgula
    if parts and parts[-1].endswith(","):
        parts[-1] = parts[-1][:-1]
    return "\n".join(parts)


def patch_html(html_path: Path, topics_js: str) -> None:
    text = html_path.read_text(encoding="utf-8")
    replacement = r"\g<1>\n" + topics_js + r"\n\g<3>"
    new_text = _TOPICS_RE.sub(replacement, text)
    html_path.write_text(new_text, encoding="utf-8")


# ── Merge: preserva desc/related do HTML atual e adiciona novos tópicos ───────

def merge_topics(
    current: list[dict],
    scraped_eleit: list[dict],
    scraped_docs: list[dict],
) -> tuple[list[dict], list[dict], list[str]]:
    """
    Combina os tópicos raspados com os dados existentes:
    - Preserva desc e related do HTML atual (que são editados à mão)
    - Detecta novos tópicos e sinaliza tópicos removidos
    - Atualiza t (título) e subs se mudaram

    Retorna (merged_eleit, merged_docs, changelog).
    """
    changelog: list[str] = []

    # Indexa atuais por URL (chave estável)
    cur_by_url = {t["url"]: t for t in current}

    def merge_list(scraped: list[dict], src: str) -> list[dict]:
        out = []
        for new in scraped:
            key = new["url"]
            old = cur_by_url.get(key)
            entry = dict(new)
            if old:
                # Preserva campos manuais
                entry["desc"]    = old.get("desc", "")
                entry["related"] = old.get("related", [])
                # Preserva id original (para não quebrar localStorage)
                entry["id"] = old["id"]
                # Detecta mudança de título
                if old.get("t") != new["t"]:
                    changelog.append(f"[{src}] título mudou: '{old['t']}' → '{new['t']}' ({key})")
                # Detecta mudança de subtópicos
                old_subs = [s[1] for s in old.get("subs", [])]
                new_subs = [s[1] for s in new.get("subs", [])]
                if set(new_subs) - set(old_subs):
                    added = set(new_subs) - set(old_subs)
                    changelog.append(f"[{src}] novos subtópicos em '{new['t']}': {added}")
                if set(old_subs) - set(new_subs):
                    removed = set(old_subs) - set(new_subs)
                    changelog.append(f"[{src}] subtópicos removidos em '{new['t']}': {removed}")
            else:
                changelog.append(f"[{src}] NOVO tópico: '{new['t']}' ({key})")
                entry["desc"]    = ""
                entry["related"] = []

            out.append(entry)

        # Detecta tópicos removidos
        scraped_urls = {t["url"] for t in scraped}
        for old in current:
            if old.get("src") == src and old["url"] not in scraped_urls:
                changelog.append(f"[{src}] tópico REMOVIDO: '{old['t']}' ({old['url']})")

        return out

    merged_eleit = merge_list(scraped_eleit, "eleit")
    merged_docs  = merge_list(scraped_docs,  "docs")
    return merged_eleit, merged_docs, changelog


# ── Fallback: quando scraping falha, mantém dados atuais ─────────────────────

def split_current(current: list[dict]) -> tuple[list[dict], list[dict]]:
    eleit = [t for t in current if t.get("src") == "eleit"]
    docs  = [t for t in current if t.get("src") == "docs"]
    return eleit, docs


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Sincroniza TOPICS do PJe HTML com as fontes ao vivo.")
    parser.add_argument("--html", default=str(HTML_FILE), help="Caminho para o HTML")
    parser.add_argument("--dry-run", action="store_true", help="Apenas mostra diff, não salva")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    html_path = Path(args.html)
    if not html_path.exists():
        print(f"ERRO: arquivo não encontrado: {html_path}", file=sys.stderr)
        sys.exit(1)

    # 1. Lê estado atual
    print("→ Lendo TOPICS atual do HTML...")
    current = read_current_topics(html_path)
    cur_eleit, cur_docs = split_current(current)
    print(f"  Atual: {len(cur_eleit)} eleit + {len(cur_docs)} docs = {len(current)} tópicos")

    # 2. Raspa PJe Dicas Eleitoral
    scraped_eleit: list[dict] = []
    try:
        print(f"→ Raspando {BASE_ELEIT}/...")
        scraped_eleit = _scrape_eleit_index()
        print(f"  Encontrados: {len(scraped_eleit)} tópicos de nível 1")

        for t in scraped_eleit:
            if args.verbose:
                print(f"    Subtópicos de {t['url']}...")
            t["subs"] = _scrape_eleit_subs(t["url"])

    except Exception as e:
        print(f"  AVISO: falha ao raspar PJe Eleitoral ({e}). Mantendo dados atuais.", file=sys.stderr)
        scraped_eleit = cur_eleit

    # 3. Raspa Docs CNJ
    scraped_docs: list[dict] = []
    try:
        print(f"→ Raspando {BASE_DOCS}/...")
        scraped_docs = _scrape_docs_index()
        print(f"  Encontrados: {len(scraped_docs)} tópicos de nível 1")

        for t in scraped_docs:
            if args.verbose:
                print(f"    Subtópicos de {t['url']}...")
            t["subs"] = _scrape_docs_subs(t["url"])

    except Exception as e:
        print(f"  AVISO: falha ao raspar Docs CNJ ({e}). Mantendo dados atuais.", file=sys.stderr)
        scraped_docs = cur_docs

    # 4. Merge
    merged_eleit, merged_docs, changelog = merge_topics(current, scraped_eleit, scraped_docs)

    # 5. Relatório
    if changelog:
        print("\n── Alterações detectadas ─────────────────────────────────────")
        for line in changelog:
            print(" •", line)
        print()
    else:
        print("✓ Nenhuma alteração detectada.")

    # 6. Salva (se houver mudanças e não for dry-run)
    if changelog and not args.dry_run:
        print("→ Atualizando HTML...")
        topics_js = build_topics_js(merged_eleit, merged_docs)
        patch_html(html_path, topics_js)
        print(f"✓ {html_path} atualizado ({len(merged_eleit)} eleit + {len(merged_docs)} docs)")
    elif args.dry_run and changelog:
        print("(dry-run: arquivo não modificado)")
    elif not changelog:
        print("✓ HTML já está sincronizado.")


if __name__ == "__main__":
    main()
