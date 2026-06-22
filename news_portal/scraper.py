"""
Scraper para notícias do TSE e TREs.
Estratégia: tenta RSS primeiro, fallback para HTML (Plone CMS).
"""
import re
import sqlite3
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "news.db"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# TSE + 27 TREs
SOURCES = [
    {"sigla": "TSE", "nome": "Tribunal Superior Eleitoral", "base_url": "https://www.tse.jus.br"},
    {"sigla": "TRE-AC", "nome": "TRE do Acre",              "base_url": "https://www.tre-ac.jus.br"},
    {"sigla": "TRE-AL", "nome": "TRE de Alagoas",           "base_url": "https://www.tre-al.jus.br"},
    {"sigla": "TRE-AM", "nome": "TRE do Amazonas",          "base_url": "https://www.tre-am.jus.br"},
    {"sigla": "TRE-AP", "nome": "TRE do Amapá",             "base_url": "https://www.tre-ap.jus.br"},
    {"sigla": "TRE-BA", "nome": "TRE da Bahia",             "base_url": "https://www.tre-ba.jus.br"},
    {"sigla": "TRE-CE", "nome": "TRE do Ceará",             "base_url": "https://www.tre-ce.jus.br"},
    {"sigla": "TRE-DF", "nome": "TRE do Distrito Federal",  "base_url": "https://www.tre-df.jus.br"},
    {"sigla": "TRE-ES", "nome": "TRE do Espírito Santo",    "base_url": "https://www.tre-es.jus.br"},
    {"sigla": "TRE-GO", "nome": "TRE de Goiás",             "base_url": "https://www.tre-go.jus.br"},
    {"sigla": "TRE-MA", "nome": "TRE do Maranhão",          "base_url": "https://www.tre-ma.jus.br"},
    {"sigla": "TRE-MG", "nome": "TRE de Minas Gerais",      "base_url": "https://www.tre-mg.jus.br"},
    {"sigla": "TRE-MS", "nome": "TRE do Mato Grosso do Sul","base_url": "https://www.tre-ms.jus.br"},
    {"sigla": "TRE-MT", "nome": "TRE do Mato Grosso",       "base_url": "https://www.tre-mt.jus.br"},
    {"sigla": "TRE-PA", "nome": "TRE do Pará",              "base_url": "https://www.tre-pa.jus.br"},
    {"sigla": "TRE-PB", "nome": "TRE da Paraíba",           "base_url": "https://www.tre-pb.jus.br"},
    {"sigla": "TRE-PE", "nome": "TRE de Pernambuco",        "base_url": "https://www.tre-pe.jus.br"},
    {"sigla": "TRE-PI", "nome": "TRE do Piauí",             "base_url": "https://www.tre-pi.jus.br"},
    {"sigla": "TRE-PR", "nome": "TRE do Paraná",            "base_url": "https://www.tre-pr.jus.br"},
    {"sigla": "TRE-RJ", "nome": "TRE do Rio de Janeiro",    "base_url": "https://www.tre-rj.jus.br"},
    {"sigla": "TRE-RN", "nome": "TRE do Rio Grande do Norte","base_url": "https://www.tre-rn.jus.br"},
    {"sigla": "TRE-RO", "nome": "TRE de Rondônia",          "base_url": "https://www.tre-ro.jus.br"},
    {"sigla": "TRE-RR", "nome": "TRE de Roraima",           "base_url": "https://www.tre-rr.jus.br"},
    {"sigla": "TRE-RS", "nome": "TRE do Rio Grande do Sul", "base_url": "https://www.tre-rs.jus.br"},
    {"sigla": "TRE-SC", "nome": "TRE de Santa Catarina",    "base_url": "https://www.tre-sc.jus.br"},
    {"sigla": "TRE-SE", "nome": "TRE de Sergipe",           "base_url": "https://www.tre-se.jus.br"},
    {"sigla": "TRE-SP", "nome": "TRE de São Paulo",         "base_url": "https://www.tre-sp.jus.br"},
    {"sigla": "TRE-TO", "nome": "TRE do Tocantins",         "base_url": "https://www.tre-to.jus.br"},
]

# Caminhos de RSS conhecidos para Plone CMS (jus.br)
RSS_PATHS = [
    "/comunicacao/noticias/RSS",
    "/comunicacao/noticias/rss.xml",
    "/comunicacao/noticias/feed",
    "/RSS",
    "/noticias/RSS",
]

NEWS_HTML_PATHS = [
    "/comunicacao/noticias",
    "/noticias",
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            sigla      TEXT NOT NULL,
            nome       TEXT NOT NULL,
            title      TEXT NOT NULL,
            summary    TEXT,
            url        TEXT UNIQUE NOT NULL,
            image_url  TEXT,
            published  TEXT,
            scraped_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS scrape_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            sigla      TEXT NOT NULL,
            status     TEXT NOT NULL,
            method     TEXT,
            count      INTEGER DEFAULT 0,
            error      TEXT,
            ran_at     TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_articles(articles):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    inserted = 0
    for a in articles:
        try:
            c.execute(
                """INSERT OR IGNORE INTO news
                   (sigla, nome, title, summary, url, image_url, published, scraped_at)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (a["sigla"], a["nome"], a["title"], a.get("summary"), a["url"],
                 a.get("image_url"), a.get("published"), datetime.now(timezone.utc).isoformat()),
            )
            if c.rowcount:
                inserted += 1
        except Exception as e:
            logger.warning("DB insert error: %s", e)
    conn.commit()
    conn.close()
    return inserted


def log_scrape(sigla, status, method=None, count=0, error=None):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO scrape_log (sigla, status, method, count, error, ran_at) VALUES (?,?,?,?,?,?)",
        (sigla, status, method, count, error, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def _get(url, timeout=15):
    resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
    resp.raise_for_status()
    return resp


def _parse_date(raw: str) -> str:
    """Normaliza data para ISO 8601. Retorna string original se falhar."""
    if not raw:
        return ""
    raw = raw.strip()
    # RFC 822 (RSS)
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(raw, fmt).isoformat()
        except ValueError:
            continue
    return raw


# ---------------------------------------------------------------------------
# RSS scraper
# ---------------------------------------------------------------------------

def _scrape_rss(source) -> list[dict] | None:
    base = source["base_url"]
    for path in RSS_PATHS:
        url = base + path
        try:
            resp = _get(url)
            ct = resp.headers.get("Content-Type", "")
            body = resp.text
            if "<rss" not in body and "<feed" not in body and "<channel" not in body:
                continue
            articles = _parse_rss(body, source)
            if articles:
                logger.info("[%s] RSS ok via %s (%d itens)", source["sigla"], path, len(articles))
                return articles
        except Exception:
            continue
    return None


def _parse_rss(xml_text: str, source: dict) -> list[dict]:
    articles = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return articles

    ns = {"atom": "http://www.w3.org/2005/Atom",
          "media": "http://search.yahoo.com/mrss/",
          "dc": "http://purl.org/dc/elements/1.1/"}

    # RSS 2.0
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link  = (item.findtext("link") or "").strip()
        desc  = (item.findtext("description") or "").strip()
        pub   = item.findtext("pubDate") or item.findtext("dc:date", namespaces=ns) or ""
        if not title or not link:
            continue
        desc_clean = BeautifulSoup(desc, "lxml").get_text(" ", strip=True)[:500] if desc else ""
        articles.append({
            "sigla": source["sigla"],
            "nome":  source["nome"],
            "title": title,
            "summary": desc_clean,
            "url":   _abs_url(link, source["base_url"]),
            "image_url": None,
            "published": _parse_date(pub),
        })

    # Atom
    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
        link_el = entry.find("{http://www.w3.org/2005/Atom}link[@rel='alternate']")
        if link_el is None:
            link_el = entry.find("{http://www.w3.org/2005/Atom}link")
        link = (link_el.get("href") if link_el is not None else "") or ""
        summary = (entry.findtext("{http://www.w3.org/2005/Atom}summary") or "").strip()
        pub = entry.findtext("{http://www.w3.org/2005/Atom}published") or \
              entry.findtext("{http://www.w3.org/2005/Atom}updated") or ""
        if not title or not link:
            continue
        articles.append({
            "sigla": source["sigla"],
            "nome":  source["nome"],
            "title": title,
            "summary": BeautifulSoup(summary, "lxml").get_text(" ", strip=True)[:500] if summary else "",
            "url":   _abs_url(link, source["base_url"]),
            "image_url": None,
            "published": _parse_date(pub),
        })

    return articles


# ---------------------------------------------------------------------------
# HTML scraper (Plone CMS)
# ---------------------------------------------------------------------------

def _scrape_html(source) -> list[dict] | None:
    base = source["base_url"]
    for path in NEWS_HTML_PATHS:
        url = base + path
        try:
            resp = _get(url)
            articles = _parse_html(resp.text, source, base)
            if articles:
                logger.info("[%s] HTML ok via %s (%d itens)", source["sigla"], path, len(articles))
                return articles
        except Exception as exc:
            logger.debug("[%s] HTML path %s failed: %s", source["sigla"], path, exc)
            continue
    return None


def _parse_html(html: str, source: dict, base_url: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    articles = []

    # Seletores em ordem de preferência (Plone 4/5, variantes jus.br)
    selectors = [
        ("article.tileItem",  "a.summary.url",      ".description",    "img",          ".documentPublished, .Date"),
        ("article",           "h2 a, h3 a",          "p.description",   "img",          "time, .date, [class*=date]"),
        ("li.tileItem",       ".tileHeadline a",     ".description",    ".tileImage img","span.documentPublished"),
        (".news-item",        "h2 a, h3 a, a.title", ".description, p", "img",          ".date, time"),
        (".noticias li",      "a",                   "p",               "img",          ".data"),
        ("div.item",          "h2 a, h3 a",          "p",               "img",          ".date, time"),
    ]

    for container_sel, title_sel, desc_sel, img_sel, date_sel in selectors:
        containers = soup.select(container_sel)
        if not containers:
            continue
        for ct in containers[:30]:
            title_el = ct.select_one(title_sel)
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link  = _abs_url(title_el.get("href", ""), base_url)
            if not title or not link or link == base_url:
                continue
            desc_el = ct.select_one(desc_sel)
            desc = desc_el.get_text(" ", strip=True)[:500] if desc_el else ""
            img_el = ct.select_one(img_sel)
            img_url = _abs_url(img_el.get("src", ""), base_url) if img_el else None
            date_el = ct.select_one(date_sel)
            pub = _parse_date(date_el.get_text(strip=True)) if date_el else ""
            articles.append({
                "sigla": source["sigla"],
                "nome":  source["nome"],
                "title": title,
                "summary": desc,
                "url":   link,
                "image_url": img_url,
                "published": pub,
            })
        if articles:
            break

    # Fallback genérico: qualquer <a> com texto razoável dentro da área principal
    if not articles:
        main = soup.select_one("main, #content, .content, #portal-column-content")
        if main:
            for a in main.find_all("a", href=True)[:40]:
                text = a.get_text(strip=True)
                href = _abs_url(a["href"], base_url)
                if len(text) > 20 and base_url in href:
                    articles.append({
                        "sigla": source["sigla"],
                        "nome":  source["nome"],
                        "title": text,
                        "summary": "",
                        "url":   href,
                        "image_url": None,
                        "published": "",
                    })
    return articles


def _abs_url(href: str, base: str) -> str:
    href = href.strip()
    if href.startswith("http"):
        return href
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return base.rstrip("/") + href
    return href


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def scrape_source(source: dict) -> dict:
    sigla = source["sigla"]
    articles = None
    method = None

    try:
        articles = _scrape_rss(source)
        if articles:
            method = "rss"
    except Exception as e:
        logger.warning("[%s] RSS exception: %s", sigla, e)

    if not articles:
        try:
            articles = _scrape_html(source)
            if articles:
                method = "html"
        except Exception as e:
            logger.warning("[%s] HTML exception: %s", sigla, e)

    if articles:
        saved = save_articles(articles)
        log_scrape(sigla, "ok", method, saved)
        return {"sigla": sigla, "status": "ok", "method": method, "count": saved}
    else:
        log_scrape(sigla, "error", None, 0, "nenhuma notícia encontrada")
        return {"sigla": sigla, "status": "error", "count": 0}


def scrape_all(delay_seconds: float = 1.5) -> list[dict]:
    init_db()
    results = []
    for source in SOURCES:
        result = scrape_source(source)
        results.append(result)
        logger.info("  -> %s", result)
        sleep(delay_seconds)
    return results


def get_stats() -> dict:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    total = conn.execute("SELECT COUNT(*) as c FROM news").fetchone()["c"]
    by_source = conn.execute(
        "SELECT sigla, COUNT(*) as c FROM news GROUP BY sigla ORDER BY sigla"
    ).fetchall()
    last_scrape = conn.execute(
        "SELECT MAX(ran_at) as t FROM scrape_log WHERE status='ok'"
    ).fetchone()["t"]
    conn.close()
    return {
        "total": total,
        "by_source": [dict(r) for r in by_source],
        "last_scrape": last_scrape,
    }
