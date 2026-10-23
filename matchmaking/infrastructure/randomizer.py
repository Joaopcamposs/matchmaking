from __future__ import annotations

import random
from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")


class Randomizer:
    """Encapsula operações aleatórias para facilitar testes e evolução."""

    def __init__(self, seed: int | None = None) -> None:
        """Inicializa o gerador pseudoaleatório opcionalmente com seed."""

        self._random = random.Random(seed)

    def shuffle(self, values: list[T]) -> None:
        """Embaralha uma lista em memória."""

        self._random.shuffle(values)

    def choice(self, values: list[T]) -> T:
        """Seleciona um item da lista informada."""

        return self._random.choice(values)

    def random(self) -> float:
        """Retorna um valor de 0 a 1."""

        return self._random.random()

    def randint(self, start: int, end: int) -> int:
        """Retorna um inteiro dentro do intervalo fornecido."""

        return self._random.randint(start, end)

    def sample(self, values: Iterable[T], size: int) -> list[T]:
        """Seleciona uma amostra aleatória sem repetição."""

        return self._random.sample(list(values), size)
