from datetime import datetime, timedelta, timezone

from newsengine import cli, store
from newsengine.models import Item

AGORA = datetime.now(timezone.utc)


def item(url, horas=1, titulo="Novo trailer revelado"):
    return Item("A", titulo, url, AGORA - timedelta(hours=horas))


def test_so_o_que_e_novo_entra_e_repetir_nao_duplica():
    con = store.abrir(":memory:")

    assert store.salvar(con, [item("u1"), item("u2")]) == 2
    assert store.salvar(con, [item("u2"), item("u3")]) == 1
    assert con.execute("SELECT COUNT(*) FROM itens").fetchone()[0] == 3


def test_recentes_filtra_por_data_real():
    con = store.abrir(":memory:")
    store.salvar(con, [item("novo", horas=1), item("velho", horas=100)])

    urls = {i.url for i in store.recentes(con, AGORA - timedelta(hours=48))}

    assert urls == {"novo"}


def test_dados_voltam_iguais_do_banco():
    con = store.abrir(":memory:")
    original = Item("Rockstar", "Comunicado", "u", AGORA - timedelta(hours=2), "resumo", True, 7)
    store.salvar(con, [original])

    assert store.recentes(con, AGORA - timedelta(days=1)) == [original]


def test_cli_top_sem_dados_orienta_o_usuario(tmp_path, capsys):
    assert cli.main(["--banco", str(tmp_path / "n.db"), "top"]) == 0

    assert "newsengine coletar" in capsys.readouterr().out


def test_cli_top_lista_os_temas(tmp_path, capsys):
    banco = tmp_path / "n.db"
    store.salvar(store.abrir(banco), [item("u1", titulo="Adiamento do lançamento anunciado")])

    cli.main(["--banco", str(banco), "top"])

    saida = capsys.readouterr().out
    assert "Adiamento do lançamento anunciado" in saida
    assert "[boato]" in saida
