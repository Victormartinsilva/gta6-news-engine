from datetime import datetime, timedelta, timezone

from newsengine.models import Item
from newsengine.scoring import agrupar, pontuar, ranquear, similaridade, tokens

AGORA = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)


def item(titulo, fonte="A", url=None, horas=1, oficial=False, engaj=0):
    return Item(fonte, titulo, url or f"http://{fonte}/{titulo}", AGORA - timedelta(hours=horas), "", oficial, engaj)


def test_tokens_ignoram_acento_stopword_e_o_proprio_nome_do_jogo():
    assert tokens("O lançamento de GTA 6 está próximo") == {"lancamento", "esta", "proximo"}


def test_titulos_do_mesmo_assunto_viram_um_topico():
    topicos = agrupar([
        item("Rockstar confirma novo trailer de GTA 6", "A"),
        item("Novo trailer de GTA 6 confirmado pela Rockstar", "B"),
        item("Preço do jogo vaza em loja", "C"),
    ])

    assert sorted(len(t.items) for t in topicos) == [1, 2]


def test_mesmo_link_repetido_conta_uma_vez():
    topicos = agrupar([item("Trailer novo", "A", url="http://x"), item("Trailer novo", "B", url="http://x")])

    assert len(topicos) == 1 and len(topicos[0].items) == 1


def test_status_confirmado_por_fonte_oficial_ou_duas_fontes():
    so_uma = agrupar([item("Boato de preço do jogo", "A")])[0]
    duas = agrupar([item("Preço do jogo confirmado em loja", "A"), item("Loja confirma preço do jogo", "B")])[0]
    oficial = agrupar([item("Comunicado sobre data", "Rockstar", oficial=True)])[0]

    assert so_uma.status == "boato"
    assert duas.status == "confirmado"
    assert oficial.status == "confirmado"


def test_mais_recente_vale_mais():
    novo = agrupar([item("Novo trailer revelado", horas=1)])[0]
    velho = agrupar([item("Novo trailer revelado", horas=72)])[0]

    assert pontuar(novo, AGORA) > pontuar(velho, AGORA)


def test_meia_vida_de_18h_corta_a_nota_pela_metade():
    um = agrupar([item("Novo trailer revelado", horas=0)])[0]
    outro = agrupar([item("Novo trailer revelado", horas=18)])[0]

    assert pontuar(outro, AGORA) == round(pontuar(um, AGORA) / 2, 3)


def test_boato_vale_menos_que_o_mesmo_assunto_confirmado():
    boato = agrupar([item("Trailer vazado", "A")])[0]
    confirmado = agrupar([item("Trailer vazado", "Rockstar", oficial=True)])[0]

    assert pontuar(confirmado, AGORA) > pontuar(boato, AGORA)


def test_mais_fontes_e_mais_engajamento_aumentam_a_nota():
    base = agrupar([item("Mapa de Vice City", "A")])[0]
    com_fontes = agrupar([item("Mapa de Vice City", "A"), item("Mapa de Vice City revelado", "B")])[0]
    com_engaj = agrupar([item("Mapa de Vice City", "A", engaj=5000)])[0]

    assert pontuar(com_fontes, AGORA) > pontuar(base, AGORA)
    assert pontuar(com_engaj, AGORA) > pontuar(base, AGORA)


def test_cada_fonte_independente_a_mais_soma_na_nota_mesmo_ja_confirmado():
    duas = agrupar([item("Mapa de Vice City", "A"), item("Mapa de Vice City revelado", "B")])[0]
    tres = agrupar([item("Mapa de Vice City", "A"), item("Mapa de Vice City revelado", "B"), item("Vice City mapa", "C")])[0]

    assert duas.status == tres.status == "confirmado"
    assert pontuar(tres, AGORA) > pontuar(duas, AGORA)


def test_similaridade_e_jaccard_e_titulo_curto_nao_engole_titulo_longo():
    assert similaridade({"a", "b"}, {"a", "b", "c", "d"}) == 0.5
    assert similaridade({"a"}, set()) == 0.0
    # um título que é só "trailer" não pode absorver uma notícia longa que apenas menciona trailer
    topicos = agrupar([item("Trailer", "A"), item("Trailer mostra mapa preço lançamento vazamento", "B")])

    assert len(topicos) == 2


def test_palavra_chave_forte_sobe_o_tema():
    forte = agrupar([item("Adiamento do lançamento anunciado", "A", url="u1")])[0]
    fraco = agrupar([item("Fã faz desenho bonito", "A", url="u2")])[0]

    assert pontuar(forte, AGORA) > pontuar(fraco, AGORA)


def test_ranking_vem_ordenado_e_respeita_o_limite():
    itens = [
        item("Fã faz desenho bonito", "A", horas=2),
        item("Adiamento do lançamento anunciado", "Rockstar", horas=2, oficial=True),
        item("Novo trailer revelado", "B", horas=2),
    ]
    topo = ranquear(itens, AGORA, limite=2)

    assert len(topo) == 2
    assert topo[0].title == "Adiamento do lançamento anunciado"
    assert topo[0].score >= topo[1].score
