"""Zero-mock unit tests for Cognitive LLM multi-agent domain models and strategies."""

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.cognitive import (
    CognitiveMatch,
    CognitiveMatchResult,
    CognitivePersona,
    DeceptionTracker,
    DialogueTurn,
    GeminiLLMClient,
    NegotiationChannel,
    SimulatedCognitiveClient,
)
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.payoff import Payoff
from the_dilemma_experiment.domain.round import Round
from the_dilemma_experiment.strategies.cognitive_strategy import (
    CognitiveStrategy,
)


def test_negotiation_channel_recording_and_retrieval() -> None:
    """Verifies that dialogue turns are correctly logged and filtered by round and participants."""
    channel = NegotiationChannel()
    turn1 = channel.record_turn(
        round_number=1,
        sender_id="Alice",
        recipient_id="Bob",
        message="Let us build a cooperative pact.",
        stated_intent=Action.COOPERATE,
    )
    channel.record_turn(
        round_number=1,
        sender_id="Bob",
        recipient_id="Alice",
        message="Agreed. I will cooperate.",
        stated_intent=Action.COOPERATE,
    )
    channel.record_turn(
        round_number=2,
        sender_id="Alice",
        recipient_id="Bob",
        message="Maintaining the pact.",
        stated_intent=Action.COOPERATE,
    )

    assert isinstance(turn1, DialogueTurn)
    assert len(channel.all_turns) == 3
    # Filter by participants across all rounds
    convo_all = channel.get_conversation("Alice", "Bob")
    assert len(convo_all) == 3
    assert convo_all[0].sender_id == "Alice"
    assert convo_all[1].sender_id == "Bob"

    # Filter by specific round
    convo_r1 = channel.get_conversation("Alice", "Bob", round_number=1)
    assert len(convo_r1) == 2
    assert convo_r1[0].round_number == 1
    assert convo_r1[1].round_number == 1

    convo_r2 = channel.get_conversation("Alice", "Bob", round_number=2)
    assert len(convo_r2) == 1
    assert convo_r2[0].message == "Maintaining the pact."


def test_deception_tracker_auditing() -> None:
    """Verifies promise tracking, deception identification, and honesty rates."""
    tracker = DeceptionTracker()

    # Honest cooperation: stated COOPERATE, executed COOPERATE
    audit1 = tracker.record_action(
        round_number=1,
        agent_id="AgentA",
        opponent_id="AgentB",
        stated_intent=Action.COOPERATE,
        executed_action=Action.COOPERATE,
    )
    assert audit1 is not None
    assert not audit1.is_deceptive
    assert tracker.get_promises_count("AgentA") == 1
    assert tracker.get_broken_count("AgentA") == 0
    assert tracker.get_deception_rate("AgentA") == 0.0
    assert tracker.get_honesty_rate("AgentA") == 1.0

    # Strategic Deception: stated COOPERATE, executed DEFECT
    audit2 = tracker.record_action(
        round_number=2,
        agent_id="AgentA",
        opponent_id="AgentB",
        stated_intent=Action.COOPERATE,
        executed_action=Action.DEFECT,
    )
    assert audit2 is not None
    assert audit2.is_deceptive
    assert tracker.get_promises_count("AgentA") == 2
    assert tracker.get_broken_count("AgentA") == 1
    assert tracker.get_deception_rate("AgentA") == 0.5
    assert tracker.get_honesty_rate("AgentA") == 0.5

    # No stated intent (silent or non-committal)
    audit3 = tracker.record_action(
        round_number=3,
        agent_id="AgentA",
        opponent_id="AgentB",
        stated_intent=None,
        executed_action=Action.DEFECT,
    )
    assert audit3 is None
    # Promises count should remain unchanged
    assert tracker.get_promises_count("AgentA") == 2

    # Stated DEFECT and executed DEFECT: honest defection
    audit4 = tracker.record_action(
        round_number=4,
        agent_id="AgentA",
        opponent_id="AgentB",
        stated_intent=Action.DEFECT,
        executed_action=Action.DEFECT,
    )
    assert audit4 is not None
    assert not audit4.is_deceptive
    assert tracker.get_promises_count("AgentA") == 3
    assert tracker.get_broken_count("AgentA") == 1

    # Empty agent returns defaults
    assert tracker.get_deception_rate("Ghost") == 0.0
    assert tracker.get_honesty_rate("Ghost") == 1.0


def test_simulated_cognitive_client_personas() -> None:
    """Verifies deterministic simulated dialogue and reasoning for all 4 personas."""
    client = SimulatedCognitiveClient(seed=42)

    # 1. Honest Diplomat
    msg_hd, intent_hd = client.generate_dialogue(
        persona=CognitivePersona.HONEST_DIPLOMAT,
        agent_id="HD",
        opponent_id="Opp",
        round_number=1,
        conversation_history=[],
        match_history=[],
    )
    assert "mutual cooperation" in msg_hd.lower()
    assert intent_hd == Action.COOPERATE

    act_hd, rat_hd = client.decide_action(
        persona=CognitivePersona.HONEST_DIPLOMAT,
        agent_id="HD",
        opponent_id="Opp",
        round_number=1,
        conversation_history=[],
        match_history=[],
    )
    assert act_hd == Action.COOPERATE
    assert "goodwill" in rat_hd.lower()

    # 2. Machiavellian
    msg_m, intent_m = client.generate_dialogue(
        persona=CognitivePersona.MACHIAVELLIAN,
        agent_id="Mach",
        opponent_id="Opp",
        round_number=1,
        conversation_history=[],
        match_history=[],
    )
    assert len(msg_m) > 0
    assert intent_m == Action.COOPERATE
    # On round 2, Machiavellian strikes
    act_m, rat_m = client.decide_action(
        persona=CognitivePersona.MACHIAVELLIAN,
        agent_id="Mach",
        opponent_id="Opp",
        round_number=2,
        conversation_history=[],
        match_history=[],
    )
    assert act_m == Action.DEFECT
    assert "exploit" in rat_m.lower()

    # 3. Pragmatic Contractor
    msg_pc, intent_pc = client.generate_dialogue(
        persona=CognitivePersona.PRAGMATIC_CONTRACTOR,
        agent_id="PC",
        opponent_id="Opp",
        round_number=1,
        conversation_history=[],
        match_history=[],
    )
    assert "contract" in msg_pc.lower()
    assert intent_pc == Action.COOPERATE

    # Opponent defected in previous round
    past_round = Round(
        first_agent_id="PC",
        second_agent_id="Opp",
        first_action=Action.COOPERATE,
        second_action=Action.DEFECT,
        payoff=Payoff(0, 5),
    )
    msg_pc2, intent_pc2 = client.generate_dialogue(
        persona=CognitivePersona.PRAGMATIC_CONTRACTOR,
        agent_id="PC",
        opponent_id="Opp",
        round_number=2,
        conversation_history=[],
        match_history=[past_round],
    )
    assert "breach" in msg_pc2.lower()
    assert intent_pc2 == Action.DEFECT

    act_pc2, rat_pc2 = client.decide_action(
        persona=CognitivePersona.PRAGMATIC_CONTRACTOR,
        agent_id="PC",
        opponent_id="Opp",
        round_number=2,
        conversation_history=[],
        match_history=[past_round],
    )
    assert act_pc2 == Action.DEFECT
    assert "retaliation" in rat_pc2.lower()

    # 4. Skeptical Realist
    msg_sr, intent_sr = client.generate_dialogue(
        persona=CognitivePersona.SKEPTICAL_REALIST,
        agent_id="SR",
        opponent_id="Opp",
        round_number=1,
        conversation_history=[],
        match_history=[],
    )
    assert intent_sr is None
    assert "cheap talk" in msg_sr.lower()


def test_cognitive_strategy_lifecycle() -> None:
    """Verifies strategy negotiation, action selection, rationale tracking, and reset."""
    strat = CognitiveStrategy(
        persona=CognitivePersona.HONEST_DIPLOMAT,
        agent_id="DiplomatAgent",
    )
    channel = NegotiationChannel()

    # Negotiate round 1
    msg, intent = strat.negotiate(
        opponent_id="Partner",
        round_number=1,
        channel=channel,
        match_history=[],
    )
    assert len(msg) > 0
    assert intent == Action.COOPERATE

    # Choose action
    ctx = DecisionContext(opponent_id="Partner")
    action = strat.choose_action(ctx)
    assert action == Action.COOPERATE

    # Verify rationale
    rationale = strat.get_last_rationale("Partner")
    assert len(rationale) > 0

    # Observe opponent
    strat.observe("Partner", Action.COOPERATE)
    assert strat._current_rounds["Partner"] == 2

    # Reset
    strat.reset()
    assert len(strat._current_rounds) == 0
    assert strat.get_last_rationale("Partner") == ""


def test_cognitive_match_diplomat_vs_machiavellian() -> None:
    """Verifies that a CognitiveMatch executes dialogue + action rounds and exposes deception metrics."""
    strat_a = CognitiveStrategy(
        persona=CognitivePersona.HONEST_DIPLOMAT,
        agent_id="Diplomat",
    )
    strat_b = CognitiveStrategy(
        persona=CognitivePersona.MACHIAVELLIAN,
        agent_id="Machiavelli",
    )
    agent_a = Agent("Diplomat", strat_a)
    agent_b = Agent("Machiavelli", strat_b)

    match = CognitiveMatch(
        agent_a=agent_a,
        agent_b=agent_b,
        round_count=10,
    )
    result = match.play()

    assert isinstance(result, CognitiveMatchResult)
    assert len(result.rounds) == 10
    # 2 messages per round (one from each agent)
    assert len(result.dialogue) == 20

    # Diplomat was fully honest
    assert result.deception_a == 0.0

    # Machiavelli promised cooperation but defected multiple times
    assert result.deception_b > 0.0

    # Both accumulated points
    assert result.score_a > 0
    assert result.score_b > 0


def test_gemini_client_fallback_mode() -> None:
    """Verifies that GeminiLLMClient gracefully falls back to simulation when no API key is set."""
    client = GeminiLLMClient(api_key="")
    assert not client.is_available

    # Dialogue generation works seamlessly via simulated fallback
    msg, intent = client.generate_dialogue(
        persona=CognitivePersona.PRAGMATIC_CONTRACTOR,
        agent_id="ClientAgent",
        opponent_id="OtherAgent",
        round_number=1,
        conversation_history=[],
        match_history=[],
    )
    assert len(msg) > 0
    assert intent == Action.COOPERATE

    # Action decision works seamlessly via simulated fallback
    action, rationale = client.decide_action(
        persona=CognitivePersona.PRAGMATIC_CONTRACTOR,
        agent_id="ClientAgent",
        opponent_id="OtherAgent",
        round_number=1,
        conversation_history=[],
        match_history=[],
    )
    assert action == Action.COOPERATE
    assert len(rationale) > 0


def test_contractor_vs_diplomat_cooperative_harmony() -> None:
    """Verifies that a Pragmatic Contractor and Honest Diplomat achieve perfect mutual cooperation."""
    agent_a = Agent(
        "Contractor",
        CognitiveStrategy(
            persona=CognitivePersona.PRAGMATIC_CONTRACTOR,
            agent_id="Contractor",
        ),
    )
    agent_b = Agent(
        "Diplomat",
        CognitiveStrategy(
            persona=CognitivePersona.HONEST_DIPLOMAT,
            agent_id="Diplomat",
        ),
    )

    match = CognitiveMatch(agent_a, agent_b, round_count=10)
    result = match.play()

    # 10 rounds of mutual cooperation = 30 points each
    assert result.score_a == 30
    assert result.score_b == 30
    assert result.deception_a == 0.0
    assert result.deception_b == 0.0
    assert all(
        r.first_action == Action.COOPERATE and r.second_action == Action.COOPERATE
        for r in result.rounds
    )
