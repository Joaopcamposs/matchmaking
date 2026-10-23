# Projeto de simulador de matchmaking de jogos

## Objetivo

Simular partidas com um sistema de matchmaking para jogos.

## Stack
- Python
- SQLAlchemy
- SQLite

## Parametros
- iniciar uma partida, com tempo limite para acabar.
- 100 jogadores na partida, todos cadastrados previamente em um banco de dados sqlite.
- 10 tipos fixos de NPCs, previamente determinados.
- karma positivo, jogador que mata menos jogadores. Karma negativo, jogador que mata mais jogadores.
- acontecimentos aleatórios que podem afetar os jogadores e NPCs.
- jogadores podem causa dano a outros jogadores ou npcs. NPCs podem causar danos a outros jogadores, mas não a outros npcs.
- jogadores podem matar e levantar outros jogadores que estão atordoados. 
- NPCs podem atordoar jogadores, mas não podem causar dano a eles após estarem atordoados.
- NPCs morrem direto, não podem ser atordoados.
- Jogadores atordoados perdem 1 de vida atordoada por segundo. Ao final do tempo, se ainda estiverem atordoados, morrem.
- jogadores podem fugir da partida antes do tempo final.
- matar outros jogares causa diminuicão de karma.
- levantar outros jogadores que estão atordoados causa aumento de karma.
- as partidas devem levar em consideração os karmas, separando jogadores com maior karma para jogar entre si, e jogadores com menor karma para jogar entre si.
- há um fator aleatorio que pode colocar jogadores com baixo karma em partidas com jogadores de alto karma, e vice versa.

## Funcionamento
- varias partidas devem iniciar simultaneamente.
- o processamento deve ser realizado em paralelo para cada partida e os resultados sendo consolidados no banco de dados.
- processar cada partida deve ser realizado em uma thread separada.
- considerar os dados mais recentes na hora de iniciar uma partida.
- uma partida tem 5 minutos, mas não deve demorar isso, o simulador deve simular o avanço do tempo e gerar eventos aleatórios.
- os eventos devem ser totalmente aletaorios no inicio, mas depois devem tendenciar os status do jogador:
  - ex: jogador com mais karma tende a matar menos jogadores e mais NPCs. Jogador com menos karma tende a matar mais jogadores e menos NPCs.
  - porem há surtos, onde um jogador pode matar mais jogadores do que o esperado, ou menos jogadores do que o esperado.

