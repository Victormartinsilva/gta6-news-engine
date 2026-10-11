"""Fontes de notícia. Edite aqui para trocar ou somar fontes; nada fica escondido no código."""

from .models import Source

FONTES = [
    Source("Google Notícias", "https://news.google.com/rss/search?q=%22GTA+6%22&hl=pt-BR&gl=BR&ceid=BR:pt-419"),
    Source("Reddit r/GTA6", "https://www.reddit.com/r/GTA6/top/.rss?t=day"),
    Source("Reddit r/GamingLeaksAndRumours", "https://www.reddit.com/r/GamingLeaksAndRumours/search.rss?q=GTA+6&restrict_sr=1&sort=new"),
]
