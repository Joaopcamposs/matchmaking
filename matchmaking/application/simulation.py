from __future__ import annotations

import random
from collections.abc import Callable
from datetime import datetime, UTC

from matchmaking.domain.entities import Match, MatchParticipant, new_match_action
from matchmaking.domain.enums import ActionType


class MatchSimulator:
    """Executa a simulação de eventos de uma partida."""

    def __init__(
        self, random_factory: Callable[[], random.Random] | None = None
    ) -> None:
        """Inicializa o simulador com uma fábrica opcional de aleatoriedade."""

        self._random_factory = random_factory or random.Random

    def simulate(self, match: Match) -> Match:
        """Processa uma partida completa sem esperar o tempo real transcorrer."""

        rng = self._random_factory()
        for second in range(match.duration_seconds):
            self._process_stun_ticks(match, second)
            actors = match.living_players() + match.living_npcs()
            rng.shuffle(actors)
            for actor in actors:
                if not actor.alive or actor.escaped:
                    continue
                self._process_actor_turn(match, actor, second, rng)
                if len(match.living_players()) <= 1:
                    break
            if len(match.living_players()) <= 1:
                break
        match.ended_at = datetime.now(UTC)
        return match

    @staticmethod
    def _process_stun_ticks(match: Match, second: int) -> None:
        """Aplica o decaimento de atordoamento dos jogadores."""

        for player in match.players:
            if not player.alive or not player.stunned:
                continue
            player.stunned_life -= 1
            killed = False
            if player.stunned_life <= 0:
                player.alive = False
                player.stunned = False
                player.deaths += 1
                killed = True
            match.actions.append(
                new_match_action(
                    match_id=match.id,
                    actor_id=player.id,
                    target_id=player.id,
                    action_type=ActionType.STUN_TICK,
                    damage=0,
                    killed=killed,
                    stunned=player.stunned,
                    happened_at_second=second,
                )
            )

    def _process_actor_turn(
        self,
        match: Match,
        actor: MatchParticipant,
        second: int,
        rng: random.Random,
    ) -> None:
        """Escolhe e executa a ação de um participante ativo."""

        if actor.is_npc:
            self._process_npc_turn(match, actor, second, rng)
            return

        if actor.stunned:
            return

        revive_candidates = [
            player
            for player in match.players
            if player.alive and player.stunned and player.id != actor.id
        ]
        escape_bias = max(0.02, 0.08 - actor.karma * 0.01)
        revive_bias = min(0.45, 0.15 + max(actor.karma, 0) * 0.04)

        roll = rng.random()
        if revive_candidates and roll < revive_bias:
            target = rng.choice(revive_candidates)
            self._revive_player(match, actor, target, second)
            return
        if roll < revive_bias + escape_bias:
            self._escape_match(match, actor, second)
            return
        self._process_player_attack(match, actor, second, rng)

    @staticmethod
    def _process_player_attack(
        match: Match,
        actor: MatchParticipant,
        second: int,
        rng: random.Random,
    ) -> None:
        """Executa um ataque de jogador com viés baseado em karma."""

        live_players = [
            player for player in match.living_players() if player.id != actor.id
        ]
        live_npcs = match.living_npcs()
        if not live_players and not live_npcs:
            return

        burst = rng.random() < 0.1
        player_target_bias = 0.55 if actor.karma < 0 else 0.20
        if burst:
            player_target_bias = 1.0 - player_target_bias

        should_attack_player = bool(live_players) and (
            not live_npcs or rng.random() < player_target_bias
        )
        target = rng.choice(live_players if should_attack_player else live_npcs)
        damage = rng.randint(18, 45)
        target.life -= damage

        killed = False
        stunned = False
        karma_delta = 0.0

        if target.is_npc:
            if target.life <= 0:
                target.alive = False
                target.deaths += 1
                actor.kills += 1
                killed = True
                karma_delta = 0.03
        else:
            if target.life <= 0 and not target.stunned:
                target.stunned = True
                target.stunned_life = 10
                target.life = 1
                stunned = True
            elif target.life <= 0 and target.stunned:
                target.alive = False
                target.deaths += 1
                actor.kills += 1
                killed = True
                karma_delta = -0.25

        actor.karma += karma_delta
        match.actions.append(
            new_match_action(
                match_id=match.id,
                actor_id=actor.id,
                target_id=target.id,
                action_type=ActionType.PLAYER_ATTACK,
                damage=damage,
                killed=killed,
                stunned=stunned,
                actor_karma_delta=karma_delta,
                happened_at_second=second,
            )
        )

    @staticmethod
    def _process_npc_turn(
        match: Match,
        actor: MatchParticipant,
        second: int,
        rng: random.Random,
    ) -> None:
        """Executa um ataque de NPC respeitando as regras de atordoamento."""

        targets = [player for player in match.living_players() if not player.stunned]
        if not targets:
            return
        target = rng.choice(targets)
        damage = rng.randint(10, max(12, int(16 + actor.difficulty * 8)))
        target.life -= damage
        stunned = False
        if target.life <= 0:
            target.stunned = True
            target.stunned_life = 8
            target.life = 1
            stunned = True
        match.actions.append(
            new_match_action(
                match_id=match.id,
                actor_id=actor.id,
                target_id=target.id,
                action_type=ActionType.NPC_ATTACK,
                damage=damage,
                stunned=stunned,
                happened_at_second=second,
            )
        )

    @staticmethod
    def _revive_player(
        match: Match,
        actor: MatchParticipant,
        target: MatchParticipant,
        second: int,
    ) -> None:
        """Remove o estado de atordoamento de um jogador e ajusta karma."""

        target.stunned = False
        target.stunned_life = 0
        target.life = max(target.life, 30)
        actor.revives += 1
        actor.karma += 0.20
        match.actions.append(
            new_match_action(
                match_id=match.id,
                actor_id=actor.id,
                target_id=target.id,
                action_type=ActionType.REVIVE,
                revived=True,
                actor_karma_delta=0.20,
                happened_at_second=second,
            )
        )

    @staticmethod
    def _escape_match(match: Match, actor: MatchParticipant, second: int) -> None:
        """Marca um jogador como fugitivo da partida."""

        actor.escaped = True
        match.actions.append(
            new_match_action(
                match_id=match.id,
                actor_id=actor.id,
                target_id=None,
                action_type=ActionType.ESCAPE,
                escaped=True,
                happened_at_second=second,
            )
        )
