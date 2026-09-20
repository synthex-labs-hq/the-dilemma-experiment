import pytest

from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.population import Population
from the_dilemma_experiment.domain.prisoners_dilemma import PrisonersDilemma
from the_dilemma_experiment.domain.tournament import Tournament
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)
from the_dilemma_experiment.strategies.always_defect import (
    AlwaysDefectStrategy,
)
from the_dilemma_experiment.strategies.grim_trigger import (
    GrimTriggerStrategy,
)
from the_dilemma_experiment.strategies.tit_for_tat import (
    TitForTatStrategy,
)


def test_tournament_validation():
    """Verify input validation for Tournament initialization."""
    game = PrisonersDilemma()
    a1 = Agent("a1", AlwaysCooperateStrategy())
    single_pop = Population([a1])

    # Population size < 2 raises ValueError
    with pytest.raises(ValueError, match="at least 2 agents"):
        Tournament(population=single_pop, game=game, rounds_per_match=5)

    valid_pop = Population([a1, Agent("a2", AlwaysDefectStrategy())])

    # Invalid game raises TypeError
    with pytest.raises(TypeError, match="Game instance"):
        Tournament(population=valid_pop, game="not_a_game", rounds_per_match=5)  # type: ignore[arg-type]

    # rounds_per_match < 1 raises ValueError
    with pytest.raises(ValueError, match="rounds_per_match must be an integer >= 1"):
        Tournament(population=valid_pop, game=game, rounds_per_match=0)


def test_tournament_round_robin_match_count():
    """Verify standard N*(N-1)/2 pairing math per ADR-012."""
    game = PrisonersDilemma()

    # N = 4 agents -> 4*3/2 = 6 matches
    agents = [
        Agent(f"agent_{i}", AlwaysCooperateStrategy())
        for i in range(4)
    ]
    pop = Population(agents)
    tournament = Tournament(population=pop, game=game, rounds_per_match=3)

    assert tournament.result is None
    assert tournament.matches == ()

    result = tournament.execute()

    assert result.total_matches == 6
    assert len(tournament.matches) == 6
    assert result.total_rounds == 18


def test_tournament_reexecution_raises():
    """Verify executing an already completed tournament raises RuntimeError."""
    game = PrisonersDilemma()
    pop = Population([
        Agent("a1", AlwaysCooperateStrategy()),
        Agent("a2", AlwaysDefectStrategy()),
    ])
    tournament = Tournament(pop, game, rounds_per_match=2)
    tournament.execute()

    with pytest.raises(RuntimeError, match="already been executed"):
        tournament.execute()


def test_tournament_three_way_baseline():
    """Verify 3-way tournament among AlwaysCooperate, AlwaysDefect, and TitForTat.

    Matchups (5 rounds each):
    - Coop vs Defect: Coop gets 0, Defect gets 25
    - Coop vs TFT: Coop gets 15, TFT gets 15
    - Defect vs TFT: Defect gets 5+4=9, TFT gets 0+4=4
    Totals:
    - Defect: 25 + 9 = 34
    - TFT: 15 + 4 = 19
    - Coop: 0 + 15 = 15
    """
    game = PrisonersDilemma()
    coop = Agent("coop", AlwaysCooperateStrategy())
    defect = Agent("defect", AlwaysDefectStrategy())
    tft = Agent("tft", TitForTatStrategy())

    pop = Population([coop, defect, tft])
    tournament = Tournament(population=pop, game=game, rounds_per_match=5)
    result = tournament.execute()

    assert result.total_matches == 3
    assert result.total_rounds == 15

    # Check leaderboard
    assert len(result.leaderboard) == 3
    assert result.winner.agent_id == "defect"
    assert result.winner.total_score == 34
    assert result.winner.wins == 2

    entry_tft = result.get_entry("tft")
    assert entry_tft.rank == 2
    assert entry_tft.total_score == 19
    assert entry_tft.wins == 0
    assert entry_tft.ties == 1
    assert entry_tft.losses == 1

    entry_coop = result.get_entry("coop")
    assert entry_coop.rank == 3
    assert entry_coop.total_score == 15
    assert entry_coop.wins == 0
    assert entry_coop.losses == 1
    assert entry_coop.ties == 1


def test_tournament_cooperative_cluster_dominance():
    """Demonstrate Axelrod's insight: a cluster of reciprocal agents outscores a solitary defector.

    Population: 1 Defector vs 3 Tit-For-Tat agents (10 rounds per match).
    - TFT agents cooperate with each other: 10 * 3 = 30 pts per match.
    - TFT vs Defector: TFT gets 0 + 9*1 = 9 pts.
    - Total per TFT: 30 + 30 + 9 = 69 pts!
    - Defector vs each TFT: gets 5 + 9*1 = 14 pts per match.
    - Total for Defector: 14 * 3 = 42 pts!
    Result: Every TFT agent beats the Defector in total score!
    """
    game = PrisonersDilemma()
    pop = Population([
        Agent("defector", AlwaysDefectStrategy()),
        Agent("tft_1", TitForTatStrategy()),
        Agent("tft_2", TitForTatStrategy()),
        Agent("tft_3", TitForTatStrategy()),
    ])

    tournament = Tournament(population=pop, game=game, rounds_per_match=10)
    result = tournament.execute()

    # The top 3 are all TFT agents
    assert result.leaderboard[0].strategy_name == "TitForTatStrategy"
    assert result.leaderboard[1].strategy_name == "TitForTatStrategy"
    assert result.leaderboard[2].strategy_name == "TitForTatStrategy"
    assert result.leaderboard[3].agent_id == "defector"

    # TFT total scores: 69 pts each
    assert result.get_entry("tft_1").total_score == 69
    assert result.get_entry("tft_2").total_score == 69
    assert result.get_entry("tft_3").total_score == 69

    # Defector total score: 42 pts
    assert result.get_entry("defector").total_score == 42
    assert result.get_entry("defector").rank == 4


def test_tournament_with_grim_trigger():
    """Verify tournament dynamics including GrimTrigger (Grudger).

    GrimTrigger cooperates with TFT and Cooperate, but shuts down Defector after 1 round.
    """
    game = PrisonersDilemma()
    pop = Population([
        Agent("grim", GrimTriggerStrategy()),
        Agent("tft", TitForTatStrategy()),
        Agent("defect", AlwaysDefectStrategy()),
    ])

    tournament = Tournament(population=pop, game=game, rounds_per_match=5)
    result = tournament.execute()

    # Grim vs TFT: 5 rounds of mutual coop (15, 15)
    # Grim vs Defect: 1 round (0,5), 4 rounds (1,1) -> Grim=4, Defect=9
    # TFT vs Defect: 1 round (0,5), 4 rounds (1,1) -> TFT=4, Defect=9
    # Totals: Grim=19, TFT=19, Defect=18
    entry_grim = result.get_entry("grim")
    entry_tft = result.get_entry("tft")
    entry_defect = result.get_entry("defect")

    assert entry_grim.total_score == 19
    assert entry_tft.total_score == 19
    assert entry_defect.total_score == 18

    # Grim and TFT tie on total_score and wins; grim comes before tft alphabetically
    assert result.winner.strategy_name in ("GrimTriggerStrategy", "TitForTatStrategy")


def test_tournament_cooperation_rate_metrics():
    """Verify individual and population cooperation rate calculations."""
    game = PrisonersDilemma()
    pop = Population([
        Agent("all_coop", AlwaysCooperateStrategy()),
        Agent("all_defect", AlwaysDefectStrategy()),
    ])

    tournament = Tournament(pop, game, rounds_per_match=10)
    result = tournament.execute()

    entry_coop = result.get_entry("all_coop")
    assert entry_coop.cooperations == 10
    assert entry_coop.defections == 0
    assert entry_coop.cooperation_rate == 1.0

    entry_defect = result.get_entry("all_defect")
    assert entry_defect.cooperations == 0
    assert entry_defect.defections == 10
    assert entry_defect.cooperation_rate == 0.0

    # Overall population cooperation rate: 10 cooperations out of 20 total actions = 0.5
    assert result.population_cooperation_rate == 0.5
