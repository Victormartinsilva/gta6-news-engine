# gta6-news-engine

Pipeline **semiautomático** de notícias e análises de GTA 6 em português: coleta fontes públicas, agrupa as notícias por assunto, dá uma nota a cada assunto e (nas próximas partes) gera roteiro, voz, legenda e vídeo para uma fila de aprovação.

> **Status:** Parte 1 de 6 concluída (coleta e ranking de temas). Veja o [roadmap](docs/ROADMAP.md).

## Por que existe

Canais de notícia de games ganham na **velocidade e na constância**. O trabalho braçal (acompanhar fontes, decidir o que vale, escrever, narrar, legendar, editar) dá para automatizar. O julgamento final não: o pipeline termina numa **fila de aprovação**, porque:

- IA inventa fato, e em notícia de jogo, boato falso queima o canal;
- as plataformas desmonetizam conteúdo repetitivo, em massa e sem revisão humana;
- cada vídeo precisa de uma contribuição própria (análise, contexto, opinião), não só reempacotar o texto de terceiros.

As regras do projeto estão em [docs/POLITICA.md](docs/POLITICA.md): de onde pode vir o conteúdo e o que nunca se faz.

## O que a Parte 1 faz

```
Google Notícias ─┐
Reddit r/GTA6 ───┼─► coletar ─► SQLite ─► agrupar por assunto ─► pontuar ─► ranking
Outras fontes ───┘
```

- **Coleta** feeds RSS/Atom (só biblioteca padrão do Python, sem dependências). Uma fonte que falha não derruba as outras.
- **Fontes independentes:** o Google Notícias é um agregador, então cada veículo conta como uma fonte própria.
- **Agrupamento:** títulos parecidos viram um assunto só (similaridade de Jaccard sobre as palavras).
- **Status do assunto:** `confirmado` (fonte oficial ou 2+ veículos independentes) ou `boato`. Boato rende menos na nota até ser confirmado.
- **Nota** = (palavras-chave + fontes extras + engajamento) × recência × fator de confirmação. A recência cai pela metade a cada 18 horas. Tudo está em [`scoring.py`](src/newsengine/scoring.py), sem caixa-preta.
- **Guarda só o necessário:** título, link, resumo curto e data. Nunca o texto inteiro de terceiros.

## Como usar

Requer Python 3.10+.

```bash
git clone https://github.com/Victormartinsilva/gta6-news-engine.git
cd gta6-news-engine
pip install -e ".[dev]"

newsengine coletar        # baixa as fontes e guarda o que for novo
newsengine top            # os temas do momento
newsengine top -n 5 --horas 24
```

No Windows, se `newsengine` não for reconhecido (a pasta de scripts do Python fora do PATH), use `python -m newsengine coletar` e `python -m newsengine top`.

Exemplo de saída:

```
 1. [confirmado]   3.38  GTA 6 revela seis rádios e confirma podcasts inéditos  (2 fonte(s))
 2. [boato]        3.32  Cyberleek pode vazar versão de GTA 6 antes da data de lançamento  (1 fonte(s))
 3. [confirmado]   2.80  A Rockstar não se limitou ao Google Maps para criar GTA 6  (2 fonte(s))
```

Para trocar ou somar fontes, edite [`config.py`](src/newsengine/config.py). Algumas fontes limitam acessos seguidos (o Reddit responde `429`); o `coletar` informa isso e segue com as demais.

## Testes

```bash
pytest
```

24 testes, todos offline (os feeds de exemplo estão embutidos). A suíte foi validada com **testes de mutação manuais**: 11 defeitos provocados no código (recência, confirmação, similaridade, deduplicação, filtro de data...), e todos foram pegos pelos testes.

## Estrutura

```
src/newsengine/
  models.py    Item, Topic, Source
  feeds.py     leitura de RSS/Atom
  scoring.py   agrupamento e nota
  store.py     SQLite
  cli.py       comandos
  config.py    fontes
tests/         testes offline
docs/          política de conteúdo e roadmap
```

## Licença

MIT. O conteúdo coletado pertence aos seus autores; este projeto guarda apenas metadados e links.
