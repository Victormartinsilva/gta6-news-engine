"""Guarda o que foi coletado num SQLite local. Serve de histórico e evita reprocessar a mesma notícia."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import Item

SCHEMA = """
CREATE TABLE IF NOT EXISTS itens (
    url TEXT PRIMARY KEY,
    fonte TEXT NOT NULL,
    titulo TEXT NOT NULL,
    resumo TEXT NOT NULL,
    publicado TEXT NOT NULL,
    oficial INTEGER NOT NULL,
    engajamento INTEGER NOT NULL,
    coletado TEXT NOT NULL
)
"""


def abrir(caminho: str | Path) -> sqlite3.Connection:
    if str(caminho) != ":memory:":
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(caminho))
    con.execute(SCHEMA)
    return con


def salvar(con: sqlite3.Connection, itens: list[Item], agora: datetime | None = None) -> int:
    """Insere o que é novo e devolve quantos itens entraram de fato."""
    agora = (agora or datetime.now(timezone.utc)).isoformat()
    antes = con.total_changes
    con.executemany(
        "INSERT OR IGNORE INTO itens VALUES (?,?,?,?,?,?,?,?)",
        [(i.url, i.source, i.title, i.summary, i.published.isoformat(), int(i.official), i.engagement, agora) for i in itens],
    )
    con.commit()
    return con.total_changes - antes


def recentes(con: sqlite3.Connection, desde: datetime) -> list[Item]:
    linhas = con.execute(
        "SELECT fonte, titulo, url, publicado, resumo, oficial, engajamento FROM itens",
    ).fetchall()
    itens = [Item(f, t, u, datetime.fromisoformat(p), r, bool(o), e) for f, t, u, p, r, o, e in linhas]
    return [i for i in itens if i.published >= desde]  # compara datas de verdade, não texto
