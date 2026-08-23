import pytest

from the_dilemma_experiment import AlwaysDefectStrategy, Payoff
from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.match import Match
from the_dilemma_experiment.domain.prisoners_dilemma import PrisonersDilemma
from the_dilemma_experiment.domain.strategy import Strategy
from the_dilemma_experiment.strategies.tit_for_tat import TitForTatStrategy


class AlwaysCooperateStrategy(Strategy):
    def choose_action(self, context: DecisionContext) -> Action:
        return Action.COOPERATE


class RecordingStrategy(Strategy):
    """Test strategy that records decision context and observations."""

    def __init__(self, action: Action) -> None:
        self.action = action
        self.decision_contexts: list[DecisionContext] = []
        self.observations: list[tuple[str, Action]] = []

    def choose_action(self, context: DecisionContext) -> Action:
        self.decision_contexts.append(context)
        return self.action

    def observe(self, opponent_id: str, action: Action) -> None:
        self.observations.append((opponent_id, action))


class OrderTrackingStrategy(Strategy):
    """Test strategy that records decision and observation events."""

    def __init__(self, action: Action, events: list[str], name: str) -> None:
        self.action = action
        self.events = events
        self.name = name

    def choose_action(self, context: DecisionContext) -> Action:
        self.events.append(f"{self.name}:choose")
        return self.action

    def observe(self, opponent_id: str, action: Action) -> None:
        self.events.append(f"{self.name}:observe")


class CountingStrategy(Strategy):
    """Test strategy that counts decisions and observations."""

    def __init__(self) -> None:
        self.decision_count = 0
        self.observation_count = 0

    def choose_action(self, context: DecisionContext) -> Action:
        self.decision_count += 1
        return Action.COOPERATE

    def observe(self, opponent_id: str, action: Action) -> None:
        self.observation_count += 1


def test_match_can_be_created():
    """Verify a valid Match can be constructed."""
    first_agent = Agent(id="agent_1", strategy=AlwaysCooperateStrategy())
    second_agent = Agent(id="agent_2", strategy=AlwaysCooperateStrategy())
    game = PrisonersDilemma()

    match = Match(
        first_agent=first_agent, second_agent=second_agent, game=game, round_count=3
    )

    assert match.rounds == ()


def test_match_rejects_non_integer_round_count():
    """Verify Match rejects a non-integer round count."""
    first_agent = Agent("agent_1", AlwaysCooperateStrategy())
    second_agent = Agent("agent_2", AlwaysCooperateStrategy())
    game = PrisonersDilemma()

    with pytest.raises(TypeError, match="round_count must be an integer"):
        Match(
            first_agent=first_agent,
            second_agent=second_agent,
            game=game,
            round_count="3",  # type: ignore[arg-type]
        )


def test_match_rejects_boolean_round_count():
    """Verify Match rejects bool even though bool is an int subclass."""
    first_agent = Agent("agent_1", AlwaysCooperateStrategy())
    second_agent = Agent("agent_2", AlwaysCooperateStrategy())
    game = PrisonersDilemma()

    with pytest.raises(TypeError, match="round_count must be an integer"):
        Match(
            first_agent=first_agent,
            second_agent=second_agent,
            game=game,
            round_count=True,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("round_count", [0, -1, -10])
def test_match_rejects_non_positive_round_count(round_count):
    """Verify Match rejects zero and negative round counts."""
    first_agent = Agent("agent_1", AlwaysCooperateStrategy())
    second_agent = Agent("agent_2", AlwaysCooperateStrategy())
    game = PrisonersDilemma()

    with pytest.raises(
        ValueError,
        match="round_count must be greater than zero",
    ):
        Match(
            first_agent=first_agent,
            second_agent=second_agent,
            game=game,
            round_count=round_count,
        )


def test_match_rejects_self_interaction():
    """Verify Match rejects two agents with the same ID."""
    first_agent = Agent("agent_1", AlwaysCooperateStrategy())
    second_agent = Agent("agent_1", AlwaysCooperateStrategy())
    game = PrisonersDilemma()

    with pytest.raises(
        ValueError,
        match="two agents with different IDs",
    ):
        Match(
            first_agent=first_agent,
            second_agent=second_agent,
            game=game,
            round_count=3,
        )


def test_match_executes_one_round():
    """Verify Match executes one complete interaction round."""
    first_strategy = RecordingStrategy(Action.COOPERATE)
    second_strategy = RecordingStrategy(Action.DEFECT)

    first_agent = Agent("agent_1", first_strategy)
    second_agent = Agent("agent_2", second_strategy)

    match = Match(
        first_agent=first_agent,
        second_agent=second_agent,
        game=PrisonersDilemma(),
        round_count=1,
    )

    results = match.execute()

    assert len(results) == 1

    round_result = results[0]

    assert round_result.first_agent_id == "agent_1"
    assert round_result.second_agent_id == "agent_2"

    assert round_result.first_action == Action.COOPERATE
    assert round_result.second_action == Action.DEFECT

    assert round_result.payoff.first == 0
    assert round_result.payoff.second == 5


def test_match_provides_correct_opponent_context():
    """Verify each strategy receives the other agent's ID as its opponent."""
    first_strategy = RecordingStrategy(Action.COOPERATE)
    second_strategy = RecordingStrategy(Action.DEFECT)

    first_agent = Agent("agent_1", first_strategy)
    second_agent = Agent("agent_2", second_strategy)

    match = Match(
        first_agent=first_agent,
        second_agent=second_agent,
        game=PrisonersDilemma(),
        round_count=1,
    )

    match.execute()

    assert len(first_strategy.decision_contexts) == 1
    assert len(second_strategy.decision_contexts) == 1

    assert first_strategy.decision_contexts[0].opponent_id == "agent_2"
    assert second_strategy.decision_contexts[0].opponent_id == "agent_1"


def test_match_notifies_each_strategy_of_opponent_action():
    """Verify each strategy observes the opponent's completed action."""
    first_strategy = RecordingStrategy(Action.COOPERATE)
    second_strategy = RecordingStrategy(Action.DEFECT)

    first_agent = Agent("agent_1", first_strategy)
    second_agent = Agent("agent_2", second_strategy)

    match = Match(
        first_agent=first_agent,
        second_agent=second_agent,
        game=PrisonersDilemma(),
        round_count=1,
    )

    match.execute()

    assert first_strategy.observations == [
        ("agent_2", Action.DEFECT),
    ]

    assert second_strategy.observations == [
        ("agent_1", Action.COOPERATE),
    ]


def test_match_observes_only_after_both_agents_choose():
    """Verify both decisions occur before either strategy observes."""
    events: list[str] = []

    first_strategy = OrderTrackingStrategy(
        action=Action.COOPERATE,
        events=events,
        name="first",
    )
    second_strategy = OrderTrackingStrategy(
        action=Action.DEFECT,
        events=events,
        name="second",
    )

    first_agent = Agent("agent_1", first_strategy)
    second_agent = Agent("agent_2", second_strategy)

    match = Match(
        first_agent=first_agent,
        second_agent=second_agent,
        game=PrisonersDilemma(),
        round_count=1,
    )

    match.execute()

    assert events == [
        "first:choose",
        "second:choose",
        "first:observe",
        "second:observe",
    ]


def test_match_executes_configured_number_of_rounds():
    """Verify Match executes exactly the configured number of rounds."""
    first_strategy = RecordingStrategy(Action.COOPERATE)
    second_strategy = RecordingStrategy(Action.DEFECT)

    first_agent = Agent("agent_1", first_strategy)
    second_agent = Agent("agent_2", second_strategy)

    match = Match(
        first_agent=first_agent,
        second_agent=second_agent,
        game=PrisonersDilemma(),
        round_count=3,
    )

    results = match.execute()

    assert len(results) == 3
    assert len(match.rounds) == 3

    assert len(first_strategy.decision_contexts) == 3
    assert len(second_strategy.decision_contexts) == 3

    assert len(first_strategy.observations) == 3
    assert len(second_strategy.observations) == 3


def test_match_reuses_strategy_instances_across_rounds():
    """Verify the same Strategy instances participate in every round."""
    first_strategy = CountingStrategy()
    second_strategy = CountingStrategy()

    first_agent = Agent("agent_1", first_strategy)
    second_agent = Agent("agent_2", second_strategy)

    match = Match(
        first_agent=first_agent,
        second_agent=second_agent,
        game=PrisonersDilemma(),
        round_count=4,
    )

    match.execute()

    assert first_strategy.decision_count == 4
    assert second_strategy.decision_count == 4

    assert first_strategy.observation_count == 4
    assert second_strategy.observation_count == 4

    assert first_agent.strategy is first_strategy
    assert second_agent.strategy is second_strategy


def test_match_cannot_be_executed_twice():
    """Verify a Match cannot be executed more than once."""
    first_agent = Agent("agent_1", AlwaysCooperateStrategy())
    second_agent = Agent("agent_2", AlwaysCooperateStrategy())

    match = Match(
        first_agent=first_agent,
        second_agent=second_agent,
        game=PrisonersDilemma(),
        round_count=2,
    )

    first_results = match.execute()

    assert len(first_results) == 2

    with pytest.raises(
        RuntimeError,
        match="A match can only be executed once",
    ):
        match.execute()

    # History must not have been duplicated.
    assert len(match.rounds) == 2


def test_match_supports_tit_for_tat_against_always_defect():
    """Verify Tit-for-Tat responds to an Always Defect opponent across rounds."""
    first_agent = Agent(
        id="agent_tft",
        strategy=TitForTatStrategy(),
    )
    second_agent = Agent(
        id="agent_defect",
        strategy=AlwaysDefectStrategy(),
    )
    game = PrisonersDilemma()

    match = Match(
        first_agent=first_agent,
        second_agent=second_agent,
        game=game,
        round_count=3,
    )

    rounds = match.execute()

    assert len(rounds) == 3

    assert rounds[0].first_action == Action.COOPERATE
    assert rounds[0].second_action == Action.DEFECT
    assert rounds[0].payoff == Payoff(0, 5)

    assert rounds[1].first_action == Action.DEFECT
    assert rounds[1].second_action == Action.DEFECT
    assert rounds[1].payoff == Payoff(1, 1)

    assert rounds[2].first_action == Action.DEFECT
    assert rounds[2].second_action == Action.DEFECT
    assert rounds[2].payoff == Payoff(1, 1)
