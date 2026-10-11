# Roadmap

O projeto é montado parte a parte. Cada parte termina com testes, documentação e um vídeo curto explicando.

| # | Parte | Entrega | Estado |
|---|---|---|---|
| 1 | **Coleta e ranking de temas** | Feeds, SQLite, agrupamento, nota, CLI | ✅ pronta |
| 2 | **Roteiro em PT-BR** | Roteiro curto a partir do tema, com fontes citadas e checagem de fatos contra o material coletado (Claude API) | ⬜ |
| 3 | **Voz e legendas** | Narração (edge-tts), legenda palavra a palavra (Whisper) | ⬜ |
| 4 | **Vídeo** | Montagem vertical e horizontal com FFmpeg, templates fixos, imagens oficiais com crédito | ⬜ |
| 5 | **Fila de aprovação** | Revisão do roteiro e do vídeo em um clique, com histórico | ⬜ |
| 6 | **Publicação e métricas** | Agendamento (YouTube, TikTok, Instagram), banco de métricas por vídeo que realimenta a escolha de temas | ⬜ |

## Antes de automatizar de vez

A Parte 6 só entra depois que os canais existirem e houver 10–15 vídeos publicados com sinal de engajamento. Automatizar o que ainda não se sabe se funciona é gastar esforço à toa.

## Ideias para depois

- Outros idiomas (inglês primeiro, que tem a maior audiência).
- Mais fontes: canais oficiais no YouTube, comunicados da Rockstar Newswire.
- Detecção de reaproveitamento: avisar se um roteiro ficou parecido demais com o texto da fonte.
