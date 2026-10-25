"""Zero-mock unit tests for ReputationTournament stranger interactions."""

import random

import pytest

from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.reputation import (
    GossipChannel,
    ReputationRegistry,
)
from the_dilemma_experiment.domain.reputation_tournament import (
    ReputationTournament,
)
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)
from the_dilemma_experiment.strategies.always_defect import (
    AlwaysDefectStrategy,
)
from the_dilemma_experiment.strategies.hypocrite import HypocriteStrategy
from the_dilemma_experiment.strategies.image_scorer import ImageScorerStrategy
from the_dilemma_experiment.strategies.stern_judger import SternJudgingStrategy


def test_reputation_tournament_validation() -> None:
    """Tournament requires at least 2 agents and valid public_probability."""
    with pytest.raises(ValueError, match="at least 2 agents"):
        ReputationTournament(agents=[Agent("single", AlwaysCooperateStrategy())])

    with pytest.raises(ValueError, match=r"public_probability must be in \[0.0, 1.0\]"):
        ReputationTournament(
            agents=[
                Agent("a", AlwaysCooperateStrategy()),
                Agent("b", AlwaysCooperateStrategy()),
            ],
            public_probability=1.5,
        )


def test_strangers_without_reputation_collapse_into_predation() -> None:
    """Without reputation tracking (pure altruists vs predators), predators exploit altruists."""
    agents = [
        Agent("altruist_1", AlwaysCooperateStrategy()),
        Agent("altruist_2", AlwaysCooperateStrategy()),
        Agent("predator_1", AlwaysDefectStrategy()),
        Agent("predator_2", AlwaysDefectStrategy()),
    ]
    rng = random.Random(42)
    # Total privacy (is_public=0.0) -> effectively no reputation
    tourney = ReputationTournament(agents=agents, public_probability=0.0, rng=rng)
    res = tourney.run_stranger_rounds(pairings_per_agent=20, rounds_per_match=1)

    # Predators must out-score naive Altruists when no reputation exists
    scores = {entry.agent_id: entry.total_score for entry in res.leaderboard}
    pred_avg = (scores["predator_1"] + scores["predator_2"]) / 2
    alt_avg = (scores["altruist_1"] + scores["altruist_2"]) / 2
    assert pred_avg > alt_avg


def test_image_scoring_shields_strangers_from_predators() -> None:
    """In a public arena, ImageScorers isolate predators and cooperate with each other."""
    agents = [
        Agent(f"scorer_{i}", ImageScorerStrategy(threshold=0)) for i in range(7)
    ] + [Agent(f"predator_{i}", AlwaysDefectStrategy()) for i in range(3)]

    rng = random.Random(123)
    tourney = ReputationTournament(agents=agents, public_probability=1.0, rng=rng)
    res = tourney.run_stranger_rounds(pairings_per_agent=30, rounds_per_match=1)

    # Predators must have negative image scores
    predator_scores = [
        entry.final_image_score
        for entry in res.leaderboard
        if "predator" in entry.agent_id
    ]
    assert all(score < 0 for score in predator_scores)

    # ImageScorers must achieve higher average scores than Predators
    scorer_totals = [
        entry.total_score
        for entry in res.leaderboard
        if "scorer" in entry.agent_id
    ]
    predator_totals = [
        entry.total_score
        for entry in res.leaderboard
        if "predator" in entry.agent_id
    ]
    assert (sum(scorer_totals) / len(scorer_totals)) > (
        sum(predator_totals) / len(predator_totals)
    )


def test_hypocrite_public_cooperation_vs_private_defection() -> None:
    """Hypocrites cooperate under full visibility, but defect under privacy."""
    # Under 100% public visibility
    agents_pub = [Agent("hypo_1", HypocriteStrategy()), Agent("hypo_2", HypocriteStrategy())]
    t_pub = ReputationTournament(agents=agents_pub, public_probability=1.0, rng=random.Random(1))
    res_pub = t_pub.run_stranger_rounds(pairings_per_agent=10)
    assert res_pub.cooperation_rate == 1.0

    # Under 0% visibility (privacy)
    agents_priv = [Agent("hypo_1", HypocriteStrategy()), Agent("hypo_2", HypocriteStrategy())]
    t_priv = ReputationTournament(agents=agents_priv, public_probability=0.0, rng=random.Random(1))
    res_priv = t_priv.run_stranger_rounds(pairings_per_agent=10)
    assert res_priv.cooperation_rate == 0.0


def test_reputation_tournament_with_noisy_gossip() -> None:
    """Tournament functions deterministically with a noisy gossip channel."""
    agents = [
        Agent(f"judger_{i}", SternJudgingStrategy()) for i in range(4)
    ] + [Agent(f"predator_{i}", AlwaysDefectStrategy()) for i in range(4)]

    reg = ReputationRegistry()
    rng = random.Random(777)
    gossip = GossipChannel(registry=reg, error_rate=0.1, rng=random.Random(888))

    tourney = ReputationTournament(
        agents=agents,
        registry=reg,
        gossip_channel=gossip,
        public_probability=0.9,
        rng=rng,
    )
    res = tourney.run_stranger_rounds(pairings_per_agent=15)

    assert res.total_matches > 0
    assert len(res.leaderboard) == 8
