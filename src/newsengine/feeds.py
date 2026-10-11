"""Leitura de feeds RSS/Atom. Só biblioteca padrão: fácil de rodar em qualquer lugar e de testar."""

from __future__ import annotations

import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from .models import Item, Source

USER_AGENT = "gta6-news-engine/0.1 (+https://github.com/Victormartinsilva)"
ATOM = "{http://www.w3.org/2005/Atom}"


def limpar(texto: str | None, limite: int = 280) -> str:
    """Tira tags HTML e entidades e corta o resumo: guardamos um trecho curto, não o texto do autor."""
    if not texto:
        return ""
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = html.unescape(texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto if len(texto) <= limite else texto[: limite - 1].rstrip() + "…"


def _data(valor: str | None) -> datetime | None:
    if not valor:
        return None
    valor = valor.strip()
    try:
        d = parsedate_to_datetime(valor)  # RSS (RFC 822)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(valor.replace("Z", "+00:00"))  # Atom (ISO 8601)
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _texto(no: ET.Element, nome: str) -> str:
    achado = no.find(nome)
    return (achado.text or "").strip() if achado is not None and achado.text else ""


def parse_feed(xml_texto: str, fonte: Source, agora: datetime | None = None) -> list[Item]:
    """Converte RSS ou Atom em `Item`s. Entradas sem título, link ou data legível (ou com data no futuro) são descartadas."""
    agora = agora or datetime.now(timezone.utc)
    try:
        raiz = ET.fromstring(xml_texto)
    except ET.ParseError:
        return []

    itens: list[Item] = []

    for e in raiz.iter("item"):  # RSS
        titulo, link = _texto(e, "title"), _texto(e, "link")
        data = _data(_texto(e, "pubDate"))
        if titulo and link and data and data <= agora:
            # Agregadores (Google Notícias) informam o veículo de cada matéria em <source>. Cada veículo é uma
            # fonte independente: sem isso, nenhum assunto seria "confirmado por 2 fontes".
            veiculo = _texto(e, "source")
            if veiculo and titulo.endswith(f" - {veiculo}"):
                titulo = titulo[: -len(f" - {veiculo}")]
            itens.append(Item(veiculo or fonte.name, limpar(titulo, 200), link, data, limpar(_texto(e, "description")), fonte.official))

    for e in raiz.iter(f"{ATOM}entry"):  # Atom (o Reddit usa)
        titulo = _texto(e, f"{ATOM}title")
        ln = e.find(f"{ATOM}link")
        link = ln.get("href", "") if ln is not None else ""
        data = _data(_texto(e, f"{ATOM}updated") or _texto(e, f"{ATOM}published"))
        if titulo and link and data and data <= agora:
            itens.append(Item(fonte.name, limpar(titulo, 200), link, data, limpar(_texto(e, f"{ATOM}content")), fonte.official))

    return itens


def baixar(fonte: Source, timeout: int = 15) -> str:
    req = urllib.request.Request(fonte.url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (URLs vêm da configuração do usuário)
        return r.read().decode("utf-8", errors="replace")


def coletar(fontes: list[Source], baixador=baixar) -> tuple[list[Item], dict[str, str]]:
    """Coleta todas as fontes. Uma fonte que falha não derruba as outras: o erro vai no relatório."""
    itens: list[Item] = []
    erros: dict[str, str] = {}
    for f in fontes:
        try:
            itens.extend(parse_feed(baixador(f), f))
        except Exception as exc:  # rede, HTTP, codificação
            erros[f.name] = f"{type(exc).__name__}: {exc}"
    return itens, erros
