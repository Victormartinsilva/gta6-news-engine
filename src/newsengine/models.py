from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Source:
    """Uma fonte configurada. `official` marca fontes primárias (ex.: comunicado da própria Rockstar)."""

    name: str
    url: str
    official: bool = False
    weight: float = 1.0


@dataclass(frozen=True)
class Item:
    """Uma notícia coletada. Guardamos só título, link, resumo curto e data: nunca o conteúdo de terceiros inteiro."""

    source: str
    title: str
    url: str
    published: datetime
    summary: str = ""
    official: bool = False
    engagement: int = 0  # curtidas/comentários quando a fonte informa


@dataclass
class Topic:
    """Um assunto: itens de fontes diferentes que falam da mesma coisa."""

    items: list[Item] = field(default_factory=list)
    score: float = 0.0

    @property
    def sources(self) -> set[str]:
        return {i.source for i in self.items}

    @property
    def title(self) -> str:
        # o título da fonte oficial, se houver; senão o do item mais recente
        oficiais = [i for i in self.items if i.official]
        base = oficiais or self.items
        return max(base, key=lambda i: i.published).title

    @property
    def status(self) -> str:
        """`confirmado` (fonte oficial ou 2+ fontes independentes) ou `boato`."""
        if any(i.official for i in self.items) or len(self.sources) >= 2:
            return "confirmado"
        return "boato"
