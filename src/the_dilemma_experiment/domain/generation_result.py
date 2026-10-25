from dataclasses import dataclass
from typing import Any

from the_dilemma_experiment.domain.tournament_result import TournamentResult


@dataclass(frozen=True)
class GenerationResult:
    """Immutable record of population state, fitness, and extinctions in an evolutionary generation."""

    generation: int
    population_counts: dict[str, int]
    population_shares: dict[str, float]
    average_fitness: dict[str, float]
    mean_population_fitness: float
    extinct_strategies: tuple[str, ...]
    newly_extinct: tuple[str, ...]
    active_strategies: tuple[str, ...]
    total_population: int
    tournament_result: TournamentResult | None = None

    def to_dict(self, include_tournament: bool = False) -> dict[str, Any]:
        """Convert GenerationResult to a JSON-serializable dictionary."""
        data: dict[str, Any] = {
            "generation": self.generation,
            "total_population": self.total_population,
            "population_counts": dict(self.population_counts),
            "population_shares": dict(self.population_shares),
            "average_fitness": dict(self.average_fitness),
            "mean_population_fitness": round(self.mean_population_fitness, 4),
            "extinct_strategies": list(self.extinct_strategies),
            "newly_extinct": list(self.newly_extinct),
            "active_strategies": list(self.active_strategies),
        }
        if include_tournament and self.tournament_result is not None:
            data["tournament"] = {
                "total_matches": self.tournament_result.total_matches,
                "total_rounds": self.tournament_result.total_rounds,
                "population_cooperation_rate": self.tournament_result.population_cooperation_rate,
                "noise": self.tournament_result.noise,
            }
        return data
