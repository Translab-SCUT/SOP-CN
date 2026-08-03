"""Deterministic genetic algorithm for annual internal-subsidy optimization."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np


@dataclass(frozen=True)
class GAConfig:
    lower_bound: float = 0.0
    upper_bound: float = 50_000.0
    step: float = 100.0
    population_size: int = 100
    crossover_probability: float = 0.7
    mutation_probability: float = 0.3
    mutation_sigma: float = 50.0
    mutation_gene_probability: float = 0.2
    tournament_size: int = 3
    maximum_generations: int = 100
    maximum_stalled_generations: int = 5
    minimum_improvement_cny: float = 1.0
    keep_one_zero_gene: bool = True


@dataclass(frozen=True)
class GAResult:
    subsidy: np.ndarray
    objective_cny: float
    seed: int
    seed_key: str
    generations: int
    objective_history: tuple[float, ...]


def stable_seed(seed_key: str) -> int:
    """Create the model's stable SHA-256 province-year random seed."""

    digest = hashlib.sha256(str(seed_key).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % (2**32)


def _validate_config(config: GAConfig, number_of_genes: int) -> None:
    if number_of_genes <= 0:
        raise ValueError("number_of_genes must be positive")
    if config.lower_bound < 0 or config.upper_bound < config.lower_bound:
        raise ValueError("Invalid subsidy bounds")
    if config.step <= 0 or config.population_size < 2:
        raise ValueError("step must be positive and population_size at least two")
    probabilities = (
        config.crossover_probability,
        config.mutation_probability,
        config.mutation_gene_probability,
    )
    if any(value < 0.0 or value > 1.0 for value in probabilities):
        raise ValueError("GA probabilities must remain between zero and one")


def _sanitize(candidate: Sequence[float], config: GAConfig) -> np.ndarray:
    values = np.asarray(candidate, dtype=float).copy()
    values = np.clip(values, config.lower_bound, config.upper_bound)
    values = np.round(values / config.step) * config.step
    if config.keep_one_zero_gene and len(values):
        values[int(np.argmin(values))] = 0.0
    return values


def optimize_internal_subsidy(
    objective: Callable[[np.ndarray], float],
    number_of_genes: int,
    seed_key: str,
    config: GAConfig | None = None,
) -> GAResult:
    """Maximize one province-year annual total manufacturer profit.

    The caller supplies the market-response and profit objective so that model
    parameters remain data inputs. The algorithm uses tournament selection,
    two-point crossover, Gaussian mutation, elitism and stalled-generation
    stopping, matching the research implementation's optimization structure.
    """

    settings = config or GAConfig()
    _validate_config(settings, number_of_genes)
    seed = stable_seed(seed_key)
    rng = random.Random(seed)
    grid_steps = int(round((settings.upper_bound - settings.lower_bound) / settings.step))

    def random_candidate() -> np.ndarray:
        values = [
            settings.lower_bound + rng.randint(0, grid_steps) * settings.step
            for _ in range(number_of_genes)
        ]
        return _sanitize(values, settings)

    population = [np.zeros(number_of_genes, dtype=float)]
    population.extend(
        random_candidate() for _ in range(settings.population_size - 1)
    )

    def score(candidate: np.ndarray) -> float:
        value = float(objective(candidate.copy()))
        if not np.isfinite(value):
            raise ValueError("GA objective must return a finite value")
        return value

    scores = [score(candidate) for candidate in population]
    best_index = int(np.argmax(scores))
    best = population[best_index].copy()
    best_score = scores[best_index]
    history = [best_score]
    stalled = 0
    generations = 0

    def tournament() -> np.ndarray:
        count = min(settings.tournament_size, len(population))
        contenders = rng.sample(range(len(population)), count)
        winner = max(contenders, key=lambda index: scores[index])
        return population[winner].copy()

    for generation in range(1, settings.maximum_generations + 1):
        next_population = [best.copy()]
        while len(next_population) < settings.population_size:
            child_a = tournament()
            child_b = tournament()
            if rng.random() < settings.crossover_probability and number_of_genes > 1:
                if number_of_genes == 2:
                    left, right = 1, 2
                else:
                    left, right = sorted(rng.sample(range(1, number_of_genes), 2))
                segment = child_a[left:right].copy()
                child_a[left:right] = child_b[left:right]
                child_b[left:right] = segment
            for child in (child_a, child_b):
                if rng.random() < settings.mutation_probability:
                    for gene in range(number_of_genes):
                        if rng.random() < settings.mutation_gene_probability:
                            child[gene] += rng.gauss(0.0, settings.mutation_sigma)
                next_population.append(_sanitize(child, settings))
                if len(next_population) == settings.population_size:
                    break

        population = next_population
        scores = [score(candidate) for candidate in population]
        generation_index = int(np.argmax(scores))
        generation_score = scores[generation_index]
        generations = generation
        if generation_score > best_score + settings.minimum_improvement_cny:
            best = population[generation_index].copy()
            best_score = generation_score
            stalled = 0
        else:
            stalled += 1
        history.append(best_score)
        if stalled >= settings.maximum_stalled_generations:
            break

    return GAResult(
        subsidy=best,
        objective_cny=float(best_score),
        seed=seed,
        seed_key=str(seed_key),
        generations=generations,
        objective_history=tuple(float(value) for value in history),
    )
