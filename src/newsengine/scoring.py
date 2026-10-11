"""Agrupa notícias do mesmo assunto e dá uma nota a cada assunto.

A nota combina: força das palavras-chave, recência, quantas fontes independentes falam do assunto
e engajamento. Tudo explícito e testável, nada de caixa-preta.
"""

from __future__ import annotations

import math
import re
import unicodedata
from datetime import datetime, timezone

from .models import Item, Topic

STOPWORDS = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "no", "na", "nos", "nas", "um", "uma",
    "para", "por", "com", "que", "se", "ao", "the", "of", "and", "to", "in", "on", "for", "is", "gta", "vi", "6",
}

# peso por palavra-chave: o que costuma mover audiência neste assunto
PALAVRAS_CHAVE = {
    "trailer": 3.0, "lancamento": 3.0, "release": 3.0, "data": 2.0, "adiado": 3.5, "adiamento": 3.5, "delay": 3.5,
    "preco": 2.5, "price": 2.5, "mapa": 2.0, "map": 2.0, "vazamento": 2.0, "leak": 2.0, "gameplay": 2.0,
    "lucia": 1.5, "jason": 1.5, "vice": 1.5, "pre-venda": 2.5, "preorder": 2.5, "pc": 1.5, "online": 1.5,
}


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.lower()


def tokens(titulo: str) -> set[str]:
    palavras = re.findall(r"[a-z0-9\-]+", normalizar(titulo))
    return {p for p in palavras if p not in STOPWORDS and len(p) > 1}


def similaridade(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def agrupar(itens: list[Item], limiar: float = 0.4) -> list[Topic]:
    """Junta títulos parecidos (Jaccard sobre palavras) no mesmo assunto. Também descarta o mesmo link repetido."""
    topicos: list[tuple[set[str], Topic]] = []
    vistos: set[str] = set()
    for item in sorted(itens, key=lambda i: i.published, reverse=True):
        if item.url in vistos:
            continue
        vistos.add(item.url)
        toks = tokens(item.title)
        for base, topico in topicos:
            if similaridade(toks, base) >= limiar:
                topico.items.append(item)
                base |= toks
                break
        else:
            topicos.append((set(toks), Topic(items=[item])))
    return [t for _, t in topicos]


def pontuar(topico: Topic, agora: datetime | None = None, meia_vida_h: float = 18.0) -> float:
    """Nota = (palavras-chave + fontes + engajamento) × recência × fator de confirmação."""
    agora = agora or datetime.now(timezone.utc)
    mais_recente = max(i.published for i in topico.items)
    horas = max((agora - mais_recente).total_seconds() / 3600, 0)
    recencia = 0.5 ** (horas / meia_vida_h)

    palavras = {p for i in topico.items for p in tokens(i.title)}
    chave = sum(PALAVRAS_CHAVE.get(p, 0) for p in palavras)
    fontes = 2.0 * (len(topico.sources) - 1)  # a 1ª fonte não conta; cada fonte extra, sim
    engaj = math.log10(1 + sum(i.engagement for i in topico.items))

    confirmacao = 1.25 if topico.status == "confirmado" else 0.6  # boato rende menos até ser confirmado
    topico.score = round((chave + fontes + engaj + 1) * recencia * confirmacao, 3)
    return topico.score


def ranquear(itens: list[Item], agora: datetime | None = None, limite: int = 10) -> list[Topic]:
    topicos = agrupar(itens)
    for t in topicos:
        pontuar(t, agora)
    return sorted(topicos, key=lambda t: t.score, reverse=True)[:limite]
