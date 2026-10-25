"""The Dilemma Experiment simulation framework."""

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.evolutionary_tournament import (
    EvolutionaryTournament,
)
from the_dilemma_experiment.domain.game import Game
from the_dilemma_experiment.domain.generation_result import GenerationResult
from the_dilemma_experiment.domain.match import Match
from the_dilemma_experiment.domain.match_result import MatchResult
from the_dilemma_experiment.domain.network_graph import NetworkGraph
from the_dilemma_experiment.domain.payoff import Payoff
from the_dilemma_experiment.domain.population import Population
from the_dilemma_experiment.domain.prisoners_dilemma import (
    DEFAULT_PAYOFF_MATRIX,
    PrisonersDilemma,
)
from the_dilemma_experiment.domain.reputation import (
    GossipChannel,
    MoralStanding,
    ReputationEvent,
    ReputationRegistry,
)
from the_dilemma_experiment.domain.reputation_tournament import (
    ReputationLeaderboardEntry,
    ReputationTournament,
    ReputationTournamentResult,
)
from the_dilemma_experiment.domain.round import Round
from the_dilemma_experiment.domain.spatial_grid import ToroidalGrid2D
from the_dilemma_experiment.domain.spatial_tournament import (
    FitnessMode,
    SpatialGenerationResult,
    SpatialTournament,
    SpatialTournamentResult,
)
from the_dilemma_experiment.domain.strategy import Strategy
from the_dilemma_experiment.domain.tag import (
    TagKind,
    TagProfile,
    calculate_shannon_diversity,
    categorical_tag_distance,
    compute_tag_distance,
    continuous_tag_distance,
)
from the_dilemma_experiment.domain.tag_tournament import (
    TagEvolutionaryTournament,
    TagGenerationMetrics,
    TagLeaderboardEntry,
    TagTournament,
    TagTournamentResult,
)
from the_dilemma_experiment.domain.topology import (
    Coordinate2D,
    NeighborhoodType,
    SpatialTopology,
)
from the_dilemma_experiment.domain.tournament import Tournament
from the_dilemma_experiment.domain.tournament_result import (
    LeaderboardEntry,
    TournamentResult,
)
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)
from the_dilemma_experiment.strategies.always_defect import (
    AlwaysDefectStrategy,
)
from the_dilemma_experiment.strategies.generous_tit_for_tat import (
    GenerousTitForTatStrategy,
)
from the_dilemma_experiment.strategies.grim_trigger import (
    GrimTriggerStrategy,
)
from the_dilemma_experiment.strategies.hypocrite import (
    HypocriteStrategy,
)
from the_dilemma_experiment.strategies.image_scorer import (
    ImageScorerStrategy,
)
from the_dilemma_experiment.strategies.random_strategy import (
    RandomStrategy,
)
from the_dilemma_experiment.strategies.stern_judger import (
    SternJudgingStrategy,
)
from the_dilemma_experiment.strategies.tag_based import (
    FalseBeardStrategy,
    RioloToleranceStrategy,
    StrictTribalStrategy,
    TagReciprocalStrategy,
)
from the_dilemma_experiment.strategies.tit_for_tat import (
    TitForTatStrategy,
)
from the_dilemma_experiment.strategies.tit_for_two_tats import (
    TitForTwoTatsStrategy,
)
from the_dilemma_experiment.strategies.win_stay_lose_shift import (
    WinStayLoseShiftStrategy,
)

__all__ = [
    "DEFAULT_PAYOFF_MATRIX",
    "Action",
    "Agent",
    "AlwaysCooperateStrategy",
    "AlwaysDefectStrategy",
    "Coordinate2D",
    "DecisionContext",
    "EvolutionaryTournament",
    "FalseBeardStrategy",
    "FitnessMode",
    "Game",
    "GenerationResult",
    "GenerousTitForTatStrategy",
    "GossipChannel",
    "GrimTriggerStrategy",
    "HypocriteStrategy",
    "ImageScorerStrategy",
    "LeaderboardEntry",
    "Match",
    "MatchResult",
    "MoralStanding",
    "NeighborhoodType",
    "NetworkGraph",
    "Payoff",
    "Population",
    "PrisonersDilemma",
    "RandomStrategy",
    "ReputationEvent",
    "ReputationLeaderboardEntry",
    "ReputationRegistry",
    "ReputationTournament",
    "ReputationTournamentResult",
    "RioloToleranceStrategy",
    "Round",
    "SpatialGenerationResult",
    "SpatialTopology",
    "SpatialTournament",
    "SpatialTournamentResult",
    "SternJudgingStrategy",
    "Strategy",
    "StrictTribalStrategy",
    "TagEvolutionaryTournament",
    "TagGenerationMetrics",
    "TagKind",
    "TagLeaderboardEntry",
    "TagProfile",
    "TagReciprocalStrategy",
    "TagTournament",
    "TagTournamentResult",
    "TitForTatStrategy",
    "TitForTwoTatsStrategy",
    "ToroidalGrid2D",
    "Tournament",
    "TournamentResult",
    "WinStayLoseShiftStrategy",
    "calculate_shannon_diversity",
    "categorical_tag_distance",
    "compute_tag_distance",
    "continuous_tag_distance",
]
