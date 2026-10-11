from datetime import datetime, timezone

from newsengine.feeds import coletar, limpar, parse_feed
from newsengine.models import Source

AGORA = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)
FONTE = Source("Teste", "http://x")

RSS = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <item><title>Novo trailer de GTA 6 sai amanhã</title><link>http://a/1</link>
        <pubDate>Fri, 09 Oct 2026 10:00:00 GMT</pubDate>
        <description>&lt;p&gt;Resumo &lt;b&gt;com&lt;/b&gt; tags&amp;nbsp;aqui&lt;/p&gt;</description></item>
  <item><title>Sem link</title><pubDate>Fri, 09 Oct 2026 10:00:00 GMT</pubDate></item>
  <item><title>Data no futuro</title><link>http://a/3</link><pubDate>Mon, 01 Jan 2029 10:00:00 GMT</pubDate></item>
  <item><title>Data ilegível</title><link>http://a/4</link><pubDate>ontem</pubDate></item>
</channel></rss>"""

ATOM = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry><title>Mapa vazado de Vice City</title><link href="http://r/1"/>
         <updated>2026-10-10T09:30:00+00:00</updated><content>texto</content></entry>
</feed>"""


def test_rss_le_so_o_que_esta_completo_e_limpa_o_resumo():
    itens = parse_feed(RSS, FONTE, AGORA)

    assert [i.url for i in itens] == ["http://a/1"]  # sem link, no futuro e data ilegível ficam de fora
    assert itens[0].summary == "Resumo com tags aqui"
    assert itens[0].published == datetime(2026, 10, 9, 10, 0, tzinfo=timezone.utc)


AGREGADOR = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <item><title>Leaker volta com 24 minutos de gameplay - IGN Brasil</title><link>http://g/1</link>
        <pubDate>Fri, 09 Oct 2026 10:00:00 GMT</pubDate><source url="http://br.ign.com">IGN Brasil</source></item>
  <item><title>Trailer novo - 24h de espera - Exame</title><link>http://g/2</link>
        <pubDate>Fri, 09 Oct 2026 10:00:00 GMT</pubDate><source url="http://exame.com">Exame</source></item>
  <item><title>Título sem veículo - e sem tag</title><link>http://g/3</link>
        <pubDate>Fri, 09 Oct 2026 10:00:00 GMT</pubDate></item>
</channel></rss>"""


def test_agregador_vira_uma_fonte_por_veiculo_e_o_titulo_perde_o_sufixo():
    itens = parse_feed(AGREGADOR, Source("Google Notícias", "http://x"), AGORA)

    assert [i.source for i in itens] == ["IGN Brasil", "Exame", "Google Notícias"]
    assert itens[0].title == "Leaker volta com 24 minutos de gameplay"
    assert itens[1].title == "Trailer novo - 24h de espera"  # só o sufixo do veículo sai, o resto do título fica
    assert itens[2].title == "Título sem veículo - e sem tag"  # sem <source>, nada é cortado


def test_atom_do_reddit_tambem_e_lido():
    itens = parse_feed(ATOM, FONTE, AGORA)

    assert len(itens) == 1
    assert itens[0].title == "Mapa vazado de Vice City"
    assert itens[0].url == "http://r/1"


def test_xml_quebrado_nao_derruba():
    assert parse_feed("<rss><item>", FONTE, AGORA) == []
    assert parse_feed("", FONTE, AGORA) == []


def test_fonte_oficial_marca_os_itens():
    itens = parse_feed(RSS, Source("Rockstar", "http://x", official=True), AGORA)

    assert itens[0].official is True


def test_resumo_longo_e_cortado():
    assert len(limpar("palavra " * 200, 100)) <= 100
    assert limpar("curto") == "curto"
    assert limpar(None) == ""


def test_uma_fonte_que_falha_nao_derruba_as_outras():
    def baixador(f):
        if f.name == "ruim":
            raise TimeoutError("sem rede")
        return ATOM

    itens, erros = coletar([Source("boa", "u"), Source("ruim", "u")], baixador)

    assert len(itens) == 1
    assert list(erros) == ["ruim"]
    assert "TimeoutError" in erros["ruim"]
