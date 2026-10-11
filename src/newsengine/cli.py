from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from . import feeds, scoring, store
from .config import FONTES

BANCO = "data/news.db"


def cmd_coletar(args) -> int:
    itens, erros = feeds.coletar(FONTES)
    con = store.abrir(args.banco)
    novos = store.salvar(con, itens)
    print(f"{len(itens)} itens lidos, {novos} novos.")
    for fonte, erro in erros.items():
        print(f"  ! {fonte}: {erro}")
    return 0


def cmd_top(args) -> int:
    agora = datetime.now(timezone.utc)
    con = store.abrir(args.banco)
    itens = store.recentes(con, agora - timedelta(hours=args.horas))
    topicos = scoring.ranquear(itens, agora, args.n)
    if not topicos:
        print("Nada no período. Rode `newsengine coletar` primeiro.")
        return 0
    for pos, t in enumerate(topicos, 1):
        print(f"{pos:>2}. [{t.status}] {t.score:6.2f}  {t.title}  ({len(t.sources)} fonte(s))")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="newsengine", description="Notícias de GTA 6: coleta e ranking de temas.")
    p.add_argument("--banco", default=BANCO)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("coletar", help="baixa as fontes e guarda o que for novo").set_defaults(fn=cmd_coletar)
    t = sub.add_parser("top", help="mostra os temas do momento")
    t.add_argument("-n", type=int, default=10)
    t.add_argument("--horas", type=int, default=48)
    t.set_defaults(fn=cmd_top)
    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
