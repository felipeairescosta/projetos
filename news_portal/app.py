"""Portal de Notícias - TSE e TREs"""
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, redirect, render_template, request, url_for

from scraper import DB_PATH, SOURCES, init_db, scrape_all, scrape_source, get_stats

app = Flask(__name__)

PAGE_SIZE = 20

# ---------------------------------------------------------------------------
# Scheduler – coleta automática a cada 2 horas
# ---------------------------------------------------------------------------
_scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
_scrape_lock = threading.Lock()
_scraping_status = {"running": False, "started_at": None}


def _scheduled_scrape():
    if _scrape_lock.locked():
        return
    with _scrape_lock:
        _scraping_status["running"] = True
        _scraping_status["started_at"] = datetime.now(timezone.utc).isoformat()
        try:
            scrape_all()
        finally:
            _scraping_status["running"] = False


_scheduler.add_job(_scheduled_scrape, "interval", hours=2, id="auto_scrape")
_scheduler.start()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def query_news(search="", source="", page=1):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    offset = (page - 1) * PAGE_SIZE

    where_clauses = []
    params = []

    if search:
        where_clauses.append("(LOWER(title) LIKE ? OR LOWER(summary) LIKE ?)")
        term = f"%{search.lower()}%"
        params.extend([term, term])

    if source:
        where_clauses.append("sigla = ?")
        params.append(source)

    where = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    total = conn.execute(f"SELECT COUNT(*) as c FROM news {where}", params).fetchone()["c"]
    rows = conn.execute(
        f"""SELECT * FROM news {where}
            ORDER BY
              CASE WHEN published != '' THEN 0 ELSE 1 END,
              published DESC,
              scraped_at DESC
            LIMIT ? OFFSET ?""",
        params + [PAGE_SIZE, offset],
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows], total


def format_date(iso_str: str) -> str:
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return iso_str[:10] if len(iso_str) >= 10 else iso_str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    init_db()
    search = request.args.get("q", "").strip()
    source = request.args.get("source", "").strip()
    page   = max(1, int(request.args.get("page", 1)))

    news, total = query_news(search, source, page)
    total_pages = max(1, -(-total // PAGE_SIZE))  # ceil division

    for n in news:
        n["published_fmt"] = format_date(n.get("published", ""))

    stats = get_stats()

    sources_list = [{"sigla": s["sigla"], "nome": s["nome"]} for s in SOURCES]

    return render_template(
        "index.html",
        news=news,
        total=total,
        page=page,
        total_pages=total_pages,
        search=search,
        source=source,
        sources_list=sources_list,
        stats=stats,
        scraping=_scraping_status["running"],
    )


@app.route("/scrape", methods=["POST"])
def trigger_scrape():
    """Dispara coleta manual em background."""
    if not _scrape_lock.locked():
        t = threading.Thread(target=_scheduled_scrape, daemon=True)
        t.start()
        return jsonify({"status": "started"})
    return jsonify({"status": "already_running"})


@app.route("/scrape/source/<sigla>", methods=["POST"])
def scrape_single(sigla):
    """Coleta notícias de uma fonte específica."""
    source = next((s for s in SOURCES if s["sigla"] == sigla), None)
    if not source:
        return jsonify({"error": "fonte não encontrada"}), 404
    result = scrape_source(source)
    return jsonify(result)


@app.route("/status")
def status():
    stats = get_stats()
    return jsonify({
        "scraping": _scraping_status,
        "stats": stats,
    })


@app.route("/api/news")
def api_news():
    search = request.args.get("q", "").strip()
    source = request.args.get("source", "").strip()
    page   = max(1, int(request.args.get("page", 1)))
    news, total = query_news(search, source, page)
    for n in news:
        n["published_fmt"] = format_date(n.get("published", ""))
    return jsonify({"total": total, "page": page, "results": news})


if __name__ == "__main__":
    init_db()
    # Coleta inicial se banco estiver vazio
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM news").fetchone()[0]
    conn.close()
    if count == 0:
        t = threading.Thread(target=_scheduled_scrape, daemon=True)
        t.start()
    app.run(debug=False, host="0.0.0.0", port=5000)
