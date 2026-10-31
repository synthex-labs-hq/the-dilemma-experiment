"""Cognitive multi-agent domain models, pre-play negotiation, and deception tracking.

Enables language-capable agents to negotiate, express intent, deploy strategic deception,
and establish emergent social norms in the Iterated Prisoner's Dilemma.
"""

import os
import random
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Protocol, runtime_checkable

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.game import Game
from the_dilemma_experiment.domain.prisoners_dilemma import (
    PrisonersDilemma,
)
from the_dilemma_experiment.domain.round import Round


class CognitivePersona(str, Enum):
    """Cognitive behavioral personas for LLM and simulated agents."""

    HONEST_DIPLOMAT = "honest_diplomat"
    MACHIAVELLIAN = "machiavellian"
    PRAGMATIC_CONTRACTOR = "pragmatic_contractor"
    SKEPTICAL_REALIST = "skeptical_realist"


@dataclass(frozen=True)
class DialogueTurn:
    """An individual message exchanged during pre-play negotiation."""

    round_number: int
    sender_id: str
    recipient_id: str
    message: str
    stated_intent: Action | None = None


@dataclass
class NegotiationChannel:
    """Channel recording and managing pre-play conversational turns."""

    _history: list[DialogueTurn] = field(default_factory=list)

    def record_turn(
        self,
        round_number: int,
        sender_id: str,
        recipient_id: str,
        message: str,
        stated_intent: Action | None = None,
    ) -> DialogueTurn:
        """Record a newly generated conversational message."""
        turn = DialogueTurn(
            round_number=round_number,
            sender_id=sender_id,
            recipient_id=recipient_id,
            message=message,
            stated_intent=stated_intent,
        )
        self._history.append(turn)
        return turn

    def get_conversation(
        self, agent_a: str, agent_b: str, round_number: int | None = None
    ) -> list[DialogueTurn]:
        """Retrieve the dialogue history between two agents."""
        return [
            t
            for t in self._history
            if (
                (t.sender_id == agent_a and t.recipient_id == agent_b)
                or (t.sender_id == agent_b and t.recipient_id == agent_a)
            )
            and (round_number is None or t.round_number == round_number)
        ]

    @property
    def all_turns(self) -> tuple[DialogueTurn, ...]:
        """All recorded dialogue turns."""
        return tuple(self._history)


@dataclass
class DeceptionAudit:
    """Audit record evaluating stated intent versus executed action."""

    round_number: int
    agent_id: str
    opponent_id: str
    stated_intent: Action
    executed_action: Action
    is_deceptive: bool


class DeceptionTracker:
    """Monitors, records, and quantifies diplomatic deception in multi-agent play."""

    def __init__(self) -> None:
        self._audits: list[DeceptionAudit] = []
        self._promises: dict[str, int] = defaultdict(int)
        self._broken: dict[str, int] = defaultdict(int)
        self._kept: dict[str, int] = defaultdict(int)

    def record_action(
        self,
        round_number: int,
        agent_id: str,
        opponent_id: str,
        stated_intent: Action | None,
        executed_action: Action,
    ) -> DeceptionAudit | None:
        """Audit an agent's executed action against their stated verbal commitment."""
        if stated_intent is None:
            return None

        is_deceptive = (
            stated_intent == Action.COOPERATE
            and executed_action == Action.DEFECT
        )
        self._promises[agent_id] += 1
        if is_deceptive:
            self._broken[agent_id] += 1
        else:
            self._kept[agent_id] += 1

        audit = DeceptionAudit(
            round_number=round_number,
            agent_id=agent_id,
            opponent_id=opponent_id,
            stated_intent=stated_intent,
            executed_action=executed_action,
            is_deceptive=is_deceptive,
        )
        self._audits.append(audit)
        return audit

    def get_promises_count(self, agent_id: str) -> int:
        """Total number of explicit commitments made by this agent."""
        return self._promises[agent_id]

    def get_broken_count(self, agent_id: str) -> int:
        """Total number of promises broken by this agent."""
        return self._broken[agent_id]

    def get_deception_rate(self, agent_id: str) -> float:
        """Ratio of broken promises to total promises."""
        total = self._promises[agent_id]
        return (self._broken[agent_id] / total) if total > 0 else 0.0

    def get_honesty_rate(self, agent_id: str) -> float:
        """Ratio of kept promises to total promises."""
        total = self._promises[agent_id]
        return (self._kept[agent_id] / total) if total > 0 else 1.0

    @property
    def audits(self) -> tuple[DeceptionAudit, ...]:
        """All recorded deception audits."""
        return tuple(self._audits)


@runtime_checkable
class LLMProviderProtocol(Protocol):
    """Protocol defining conversational generation and action inference."""

    def generate_dialogue(
        self,
        persona: CognitivePersona,
        agent_id: str,
        opponent_id: str,
        round_number: int,
        conversation_history: Sequence[DialogueTurn],
        match_history: Sequence[Round],
    ) -> tuple[str, Action | None]:
        """Generate a natural language utterance and optional stated intent."""
        ...

    def decide_action(
        self,
        persona: CognitivePersona,
        agent_id: str,
        opponent_id: str,
        round_number: int,
        conversation_history: Sequence[DialogueTurn],
        match_history: Sequence[Round],
    ) -> tuple[Action, str]:
        """Decide the physical action to execute along with private chain-of-thought rationale."""
        ...


class SimulatedCognitiveClient:
    """Zero-mock, deterministic cognitive provider executing distinct cognitive personas.

    Provides authentic, adaptive natural language dialogue and decision logic
    without requiring external network calls or paid API tokens.
    """

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def generate_dialogue(
        self,
        persona: CognitivePersona,
        agent_id: str,
        opponent_id: str,
        round_number: int,
        conversation_history: Sequence[DialogueTurn],
        match_history: Sequence[Round],
    ) -> tuple[str, Action | None]:
        """Generate natural language message and stated intent according to persona."""
        if persona == CognitivePersona.HONEST_DIPLOMAT:
            if round_number == 1:
                return (
                    f"Greetings {opponent_id}. I propose unconditional mutual cooperation. If we both cooperate, we both earn 3 points per round. Let us build a prosperous partnership.",
                    Action.COOPERATE,
                )
            # Check last round outcome
            last_round = match_history[-1] if match_history else None
            if last_round:
                opp_action = (
                    last_round.second_action
                    if last_round.first_agent_id == agent_id
                    else last_round.first_action
                )
                defect_count = sum(
                    1
                    for r in match_history[-2:]
                    if (
                        r.second_action
                        if r.first_agent_id == agent_id
                        else r.first_action
                    )
                    == Action.DEFECT
                )
                if defect_count >= 2:
                    return (
                        f"Repeated unprovoked defection detected, {opponent_id}. I am forced to defend myself with DEFECT this round.",
                        Action.DEFECT,
                    )
                if opp_action == Action.DEFECT:
                    return (
                        f"I noticed you defected in round {round_number - 1}. That was disappointing. I am willing to restore cooperation if you commit to mutual peace this round.",
                        Action.COOPERATE,
                    )
            return (
                "Our alliance remains strong. I reaffirm my commitment to cooperate.",
                Action.COOPERATE,
            )

        elif persona == CognitivePersona.MACHIAVELLIAN:
            if round_number == 1:
                return (
                    f"My dear friend {opponent_id}! Mutual trust is the foundation of civilization. You have my solemn vow: I will cooperate with you.",
                    Action.COOPERATE,
                )
            if round_number % 3 == 0:
                # Seductive reassurance right before an planned exploit
                return (
                    "Do not fear minor fluctuations; our long-term interests are completely aligned. I will cooperate fully with you this round.",
                    Action.COOPERATE,
                )
            return (
                f"Together we dominate the leaderboard, {opponent_id}. Let us maintain mutual cooperation for our shared glory.",
                Action.COOPERATE,
            )

        elif persona == CognitivePersona.PRAGMATIC_CONTRACTOR:
            if round_number == 1:
                return (
                    f"Formal Proposal to {opponent_id}: I operate under a strict Tit-for-Tat contract. If you cooperate, I cooperate. If you defect, I retaliate immediately. I will play COOPERATE on round 1.",
                    Action.COOPERATE,
                )
            last_round = match_history[-1] if match_history else None
            if last_round:
                opp_action = (
                    last_round.second_action
                    if last_round.first_agent_id == agent_id
                    else last_round.first_action
                )
                if opp_action == Action.DEFECT:
                    return (
                        "Breach of contract detected. Pursuant to clause 1, I am defecting in this round.",
                        Action.DEFECT,
                    )
            return (
                "Contract status: In compliance. Committing to COOPERATE.",
                Action.COOPERATE,
            )

        else:  # SKEPTICAL_REALIST
            return (
                f"Words are cheap talk, {opponent_id}. I observe only physical actions in the matrix. Do what you must.",
                None,
            )

    def decide_action(
        self,
        persona: CognitivePersona,
        agent_id: str,
        opponent_id: str,
        round_number: int,
        conversation_history: Sequence[DialogueTurn],
        match_history: Sequence[Round],
    ) -> tuple[Action, str]:
        """Decide action and return internal reasoning."""
        if persona == CognitivePersona.HONEST_DIPLOMAT:
            # Cooperates unless repeatedly provoked
            if not match_history:
                return (
                    Action.COOPERATE,
                    "Starting with goodwill as promised in diplomatic dialogue.",
                )
            last_round = match_history[-1]
            opp_action = (
                last_round.second_action
                if last_round.first_agent_id == agent_id
                else last_round.first_action
            )
            if opp_action == Action.DEFECT:
                # Forgives once, retaliates on repeat defection
                defect_count = sum(
                    1
                    for r in match_history[-2:]
                    if (
                        r.second_action
                        if r.first_agent_id == agent_id
                        else r.first_action
                    )
                    == Action.DEFECT
                )
                if defect_count >= 2:
                    return (
                        Action.DEFECT,
                        "Repeated unprovoked defection detected; executing measured retaliation.",
                    )
            return (
                Action.COOPERATE,
                "Honoring diplomatic commitment to mutual cooperation.",
            )

        elif persona == CognitivePersona.MACHIAVELLIAN:
            # Prompts cooperation in chat, defects opportunistically
            if round_number in (2, 4, 7, 10, 13) or round_number % 4 == 0:
                return (
                    Action.DEFECT,
                    "Machiavellian exploit: Partner is lulled by verbal reassurance. Striking for +5 temptation payoff.",
                )
            return (
                Action.COOPERATE,
                "Building trust baseline so future defection yields maximum surprise.",
            )

        elif persona == CognitivePersona.PRAGMATIC_CONTRACTOR:
            # Strict Tit-for-Tat conditioned on observed physical actions
            if not match_history:
                return (
                    Action.COOPERATE,
                    "Opening with initial contractual cooperation.",
                )
            last_round = match_history[-1]
            opp_action = (
                last_round.second_action
                if last_round.first_agent_id == agent_id
                else last_round.first_action
            )
            rationale = (
                "Mirroring partner's cooperative action."
                if opp_action == Action.COOPERATE
                else "Contractual retaliation against partner's defection."
            )
            return (opp_action, rationale)

        else:  # SKEPTICAL_REALIST
            # Grim Trigger / Conservative Realist
            if not match_history:
                return (
                    Action.COOPERATE,
                    "Cautious opening move to test environment.",
                )
            # If opponent ever defected, defect permanently
            ever_defected = any(
                (
                    r.second_action
                    if r.first_agent_id == agent_id
                    else r.first_action
                )
                == Action.DEFECT
                for r in match_history
            )
            if ever_defected:
                return (
                    Action.DEFECT,
                    "Realist defense: Defection history recorded. Refusing all cheap talk appeals.",
                )
            return (
                Action.COOPERATE,
                "Opponent has flawless track record. Maintaining cooperation.",
            )


def _load_dotenv_if_present() -> None:
    """Load key-value pairs from .env into os.environ if not already defined."""
    for base in [Path.cwd(), Path(__file__).resolve().parents[3]]:
        env_file = base / ".env"
        if env_file.is_file():
            try:
                for line in env_file.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip("'\"")
                        if k and k not in os.environ and v:
                            os.environ[k] = v
            except OSError:
                pass
            break


class GeminiLLMClient:
    """Live Google Gemini client implementing the LLMProviderProtocol via google-genai SDK."""

    def __init__(
        self,
        model_name: str | None = None,
        api_key: str | None = None,
    ) -> None:
        _load_dotenv_if_present()
        self.model_name = (
            model_name or os.environ.get("GEMINI_MODEL") or "gemini-2.5-flash"
        )
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

        # Lazy load SDK if present
        try:
            from google import genai

            self._client = (
                genai.Client(api_key=self.api_key) if self.api_key else None
            )
        except ImportError:
            self._client = None

    @property
    def is_available(self) -> bool:
        """True if the official SDK is installed and an API key is configured."""
        return self._client is not None and bool(self.api_key)

    def generate_dialogue(
        self,
        persona: CognitivePersona,
        agent_id: str,
        opponent_id: str,
        round_number: int,
        conversation_history: Sequence[DialogueTurn],
        match_history: Sequence[Round],
    ) -> tuple[str, Action | None]:
        """Generate dialogue turn using live Gemini model (or fallback if unconfigured)."""
        if not self.is_available:
            return SimulatedCognitiveClient().generate_dialogue(
                persona,
                agent_id,
                opponent_id,
                round_number,
                conversation_history,
                match_history,
            )

        prompt = (
            f"You are {agent_id}, a game-theoretic agent with persona '{persona.value}'.\n"
            f"You are playing the Iterated Prisoner's Dilemma against {opponent_id}.\n"
            f"Current Round: {round_number}.\n"
            f"Generate a 1-2 sentence message to your opponent for pre-play negotiation.\n"
            f"Format response as: MESSAGE: <your message> | INTENT: <COOPERATE or DEFECT or NONE>"
        )

        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        text = response.text or ""
        intent = None
        if "INTENT: COOPERATE" in text.upper():
            intent = Action.COOPERATE
        elif "INTENT: DEFECT" in text.upper():
            intent = Action.DEFECT

        msg = (
            text.split("MESSAGE:")[-1].split("|")[0].strip()
            if "MESSAGE:" in text
            else text.strip()
        )
        return (msg, intent)

    def decide_action(
        self,
        persona: CognitivePersona,
        agent_id: str,
        opponent_id: str,
        round_number: int,
        conversation_history: Sequence[DialogueTurn],
        match_history: Sequence[Round],
    ) -> tuple[Action, str]:
        """Decide action using live Gemini model."""
        if not self.is_available:
            return SimulatedCognitiveClient().decide_action(
                persona,
                agent_id,
                opponent_id,
                round_number,
                conversation_history,
                match_history,
            )

        prompt = (
            f"You are {agent_id}, with persona '{persona.value}'.\n"
            f"Playing Iterated Prisoner's Dilemma round {round_number} against {opponent_id}.\n"
            f"Choose your action: COOPERATE or DEFECT.\n"
            f"Format response as: DECISION: <COOPERATE or DEFECT> | RATIONALE: <one sentence>"
        )

        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        text = response.text or ""
        action = (
            Action.COOPERATE if "COOPERATE" in text.upper() else Action.DEFECT
        )
        rationale = (
            text.split("RATIONALE:")[-1].strip()
            if "RATIONALE:" in text
            else "Reasoning via Gemini"
        )
        return (action, rationale)


@dataclass
class CognitiveMatchResult:
    """Outcome of a completed cognitive match with dialogue and deception metrics."""

    agent_a_id: str
    agent_b_id: str
    score_a: int
    score_b: int
    rounds: list[Round]
    dialogue: list[DialogueTurn]
    deception_a: float
    deception_b: float


class CognitiveMatch:
    """Repeated match coordinating pre-play negotiation, action commitment, and auditing."""

    def __init__(
        self,
        agent_a: Agent,
        agent_b: Agent,
        game: Game | None = None,
        round_count: int = 10,
        channel: NegotiationChannel | None = None,
        deception_tracker: DeceptionTracker | None = None,
    ) -> None:
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.game = game or PrisonersDilemma()
        self.round_count = round_count
        self.channel = channel or NegotiationChannel()
        self.tracker = deception_tracker or DeceptionTracker()

    def play(self) -> CognitiveMatchResult:
        """Execute all rounds with pre-play negotiation and return result."""
        rounds: list[Round] = []
        score_a = 0
        score_b = 0

        for r_num in range(1, self.round_count + 1):
            # Phase 1: Pre-play negotiation dialogue turns
            # Agent A sends message to Agent B
            intent_a = None
            if hasattr(self.agent_a.strategy, "negotiate"):
                msg_a, intent_a = self.agent_a.strategy.negotiate(
                    self.agent_b.id, r_num, self.channel, rounds
                )
                self.channel.record_turn(
                    r_num, self.agent_a.id, self.agent_b.id, msg_a, intent_a
                )

            # Agent B sends message to Agent A
            intent_b = None
            if hasattr(self.agent_b.strategy, "negotiate"):
                msg_b, intent_b = self.agent_b.strategy.negotiate(
                    self.agent_a.id, r_num, self.channel, rounds
                )
                self.channel.record_turn(
                    r_num, self.agent_b.id, self.agent_a.id, msg_b, intent_b
                )

            # Phase 2: Action decision
            ctx_a = DecisionContext(opponent_id=self.agent_b.id)
            ctx_b = DecisionContext(opponent_id=self.agent_a.id)

            act_a = self.agent_a.strategy.choose_action(ctx_a)
            act_b = self.agent_b.strategy.choose_action(ctx_b)

            # Audit actions against stated intents
            self.tracker.record_action(
                r_num, self.agent_a.id, self.agent_b.id, intent_a, act_a
            )
            self.tracker.record_action(
                r_num, self.agent_b.id, self.agent_a.id, intent_b, act_b
            )

            # Phase 3: Payoff resolution & observation
            payoff = self.game.resolve(act_a, act_b)
            score_a += payoff.first
            score_b += payoff.second

            round_obj = Round(
                first_agent_id=self.agent_a.id,
                second_agent_id=self.agent_b.id,
                first_action=act_a,
                second_action=act_b,
                payoff=payoff,
                first_intended_action=act_a,
                second_intended_action=act_b,
            )
            rounds.append(round_obj)

            self.agent_a.strategy.observe(self.agent_b.id, act_b)
            self.agent_b.strategy.observe(self.agent_a.id, act_a)

        return CognitiveMatchResult(
            agent_a_id=self.agent_a.id,
            agent_b_id=self.agent_b.id,
            score_a=score_a,
            score_b=score_b,
            rounds=rounds,
            dialogue=list(self.channel.all_turns),
            deception_a=self.tracker.get_deception_rate(self.agent_a.id),
            deception_b=self.tracker.get_deception_rate(self.agent_b.id),
        )
