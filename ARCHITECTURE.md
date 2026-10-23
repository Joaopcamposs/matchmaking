# Matchmaking Simulator Architecture

## Overview

This project simulates multiple game matches in parallel using a DDD-inspired structure with separation between domain, application, and infrastructure.

## Layers

### Domain

- `matchmaking/domain/entities.py`
  - Core entities for `Player`, `NPCProfile`, `MatchParticipant`, `MatchAction`, and `Match`.
- `matchmaking/domain/enums.py`
  - Enumerations for action types and participant kinds.
- `matchmaking/domain/services.py`
  - `MatchFactory` responsible for creating match aggregates.

### Application

- `matchmaking/application/interfaces.py`
  - Repository contracts.
- `matchmaking/application/simulation.py`
  - Match event simulation engine with random behavior influenced by karma.
- `matchmaking/application/matchmaking_service.py`
  - Match grouping, async orchestration, thread-based match processing, and player consolidation.

### Infrastructure

- `matchmaking/infrastructure/database.py`
  - SQLAlchemy engine and session management for SQLite.
- `matchmaking/infrastructure/orm.py`
  - ORM models for players, NPC profiles, matches, and actions.
- `matchmaking/infrastructure/repositories.py`
  - Concrete repository implementations.
- `matchmaking/infrastructure/randomizer.py`
  - Random utility wrapper for easier evolution and tests.

## Matchmaking flow

1. Bootstrap creates 100 players if the database is empty.
2. Bootstrap creates 10 fixed NPC types if they do not exist.
3. Players are sorted by karma.
4. A random noise factor swaps some players between nearby karma bands.
5. Players are split into groups and each group becomes one match.
6. NPC profiles are distributed across the matches.
7. Each match is simulated concurrently through `asyncio.to_thread`.
8. Each thread simulates the full timeline without waiting in real time.
9. Results are consolidated back into SQLite.

## Simulation rules implemented

- Players may attack players or NPCs.
- Low-karma players are more likely to attack players.
- High-karma players are more likely to attack NPCs and revive stunned players.
- Random bursts invert expected behavior occasionally.
- NPCs attack only players.
- NPCs can stun players but do not directly kill them after stun.
- NPCs die immediately when their life reaches zero.
- Stunned players lose stun life every simulated second and die if not revived in time.
- Players can flee a match.
- Killing players decreases karma.
- Reviving players increases karma.

## Persistence

SQLite stores:

- players
- npc_profiles
- matches
- match_actions

The application always reads the latest persisted player state before starting a matchmaking cycle.

## Tests

- Unit tests for simulation behavior.
- Repository tests for seeding and persistence setup.
- Integration test covering bootstrap, async execution, and persistence.

## Entry point

Run:

```bash
python main.py
```

This creates the SQLite database, seeds initial data, runs the simulation, and prints a summary.
