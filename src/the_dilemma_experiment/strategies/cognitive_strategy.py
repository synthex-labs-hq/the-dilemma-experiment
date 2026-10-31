"""Cognitive LLM Strategy for the Iterated Prisoner's Dilemma."""

from collections.abc import Sequence

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.cognitive import (
    CognitivePersona,
    LLMProviderProtocol,
    NegotiationChannel,
    SimulatedCognitiveClient,
)
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.payoff import Payoff
from the_dilemma_experiment.domain.round import Round
from the_dilemma_experiment.domain.strategy import Strategy


class CognitiveStrategy(Strategy):
    """Strategy powered by language models and cognitive reasoning personas.

    Supports pre-play negotiation dialogue, commitment expression, strategic
    deception, and dynamic context-aware decision making.
    """

    def __init__(
        self,
        persona: CognitivePersona = CognitivePersona.HONEST_DIPLOMAT,
        client: LLMProviderProtocol | None = None,
        agent_id: str = "CognitiveAgent",
    ) -> None:
        self.persona = (
            CognitivePersona(persona)
            if isinstance(persona, str)
            else persona
        )
        self.client = client or SimulatedCognitiveClient()
        self.agent_id = agent_id

        self._match_histories: dict[str, list[Round]] = {}
        self._last_rationales: dict[str, str] = {}
        self._last_chosen_actions: dict[str, Action] = {}
        self._current_rounds: dict[str, int] = {}
        self._channel: NegotiationChannel = NegotiationChannel()

    def negotiate(
        self,
        opponent_id: str,
        round_number: int,
        channel: NegotiationChannel,
        match_history: Sequence[Round],
    ) -> tuple[str, Action | None]:
        """Generate a pre-play negotiation message and optional stated commitment."""
        self._current_rounds[opponent_id] = round_number
        self._channel = channel
        if match_history:
            self._match_histories[opponent_id] = list(match_history)
        conv = channel.get_conversation(self.agent_id, opponent_id)

        return self.client.generate_dialogue(
            persona=self.persona,
            agent_id=self.agent_id,
            opponent_id=opponent_id,
            round_number=round_number,
            conversation_history=conv,
            match_history=match_history,
        )

    def choose_action(self, context: DecisionContext) -> Action:
        """Choose action using the cognitive persona reasoning engine."""
        opp_id = context.opponent_id
        r_num = self._current_rounds.get(opp_id, 1)
        history = self._match_histories.get(opp_id, [])
        conv = self._channel.get_conversation(self.agent_id, opp_id)

        action, rationale = self.client.decide_action(
            persona=self.persona,
            agent_id=self.agent_id,
            opponent_id=opp_id,
            round_number=r_num,
            conversation_history=conv,
            match_history=history,
        )

        self._last_chosen_actions[opp_id] = action
        self._last_rationales[opp_id] = rationale
        return action

    def observe(self, opponent_id: str, action: Action) -> None:
        """Observe opponent action and increment interaction round."""
        self._current_rounds[opponent_id] = (
            self._current_rounds.get(opponent_id, 1) + 1
        )
        own_action = self._last_chosen_actions.get(opponent_id, Action.COOPERATE)
        if opponent_id not in self._match_histories:
            self._match_histories[opponent_id] = []
        self._match_histories[opponent_id].append(
            Round(
                first_agent_id=self.agent_id,
                second_agent_id=opponent_id,
                first_action=own_action,
                second_action=action,
                payoff=Payoff(0, 0),
            )
        )

    def get_last_rationale(self, opponent_id: str) -> str:
        """Return the most recent chain-of-thought rationale for this opponent."""
        return self._last_rationales.get(opponent_id, "")

    def reset(self) -> None:
        """Reset internal history and counters."""
        self._match_histories.clear()
        self._last_rationales.clear()
        self._last_chosen_actions.clear()
        self._current_rounds.clear()
