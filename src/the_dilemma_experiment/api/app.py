"""FastAPI Simulation Backend for The Dilemma Experiment Interactive Web UI.

Exposes endpoints to introspect the 24+ strategy roster, simulate pairwise matches
(with noise, pre-play dialogue, and deception audits), and execute multi-agent tournaments.
"""

from collections.abc import Callable
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from the_dilemma_experiment.domain.agent import Agent
from the_dilemma_experiment.domain.cognitive import (
    CognitiveMatch,
    CognitivePersona,
    DeceptionTracker,
    NegotiationChannel,
)
from the_dilemma_experiment.domain.match import Match
from the_dilemma_experiment.domain.population import Population
from the_dilemma_experiment.domain.prisoners_dilemma import PrisonersDilemma
from the_dilemma_experiment.domain.strategy import Strategy
from the_dilemma_experiment.domain.tournament import Tournament
from the_dilemma_experiment.strategies.always_cooperate import (
    AlwaysCooperateStrategy,
)
from the_dilemma_experiment.strategies.always_defect import AlwaysDefectStrategy
from the_dilemma_experiment.strategies.cognitive_strategy import (
    CognitiveStrategy,
)
from the_dilemma_experiment.strategies.commons_strategies import (
    AntisocialPunisherStrategy,
    OstromSanctionerStrategy,
    OverHarvesterStrategy,
    SecondOrderFreeRiderStrategy,
    SustainableHarvesterStrategy,
)
from the_dilemma_experiment.strategies.generous_tit_for_tat import (
    GenerousTitForTatStrategy,
)
from the_dilemma_experiment.strategies.grim_trigger import GrimTriggerStrategy
from the_dilemma_experiment.strategies.hypocrite import HypocriteStrategy
from the_dilemma_experiment.strategies.image_scorer import ImageScorerStrategy
from the_dilemma_experiment.strategies.random_strategy import RandomStrategy
from the_dilemma_experiment.strategies.stern_judger import SternJudgingStrategy
from the_dilemma_experiment.strategies.tag_based import (
    FalseBeardStrategy,
    RioloToleranceStrategy,
    StrictTribalStrategy,
    TagReciprocalStrategy,
)
from the_dilemma_experiment.strategies.tit_for_tat import TitForTatStrategy
from the_dilemma_experiment.strategies.tit_for_two_tats import (
    TitForTwoTatsStrategy,
)
from the_dilemma_experiment.strategies.win_stay_lose_shift import (
    WinStayLoseShiftStrategy,
)
from the_dilemma_experiment.strategies.zero_determinant import (
    EqualizerStrategy,
    ExtortionStrategy,
    GenerousZDStrategy,
)

app = FastAPI(
    title="The Dilemma Experiment Simulation API",
    description="Interactive Game Theory & Multi-Agent Simulation Engine",
    version="1.0.0",
)

# Enable CORS for local dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Strategy Metadata & Catalog ---

class StrategyMeta(BaseModel):
    id: str
    name: str
    archetype: str
    episode: int
    category: str
    description: str
    traits: list[str]
    is_cognitive: bool = False


STRATEGY_CATALOG: dict[str, tuple[StrategyMeta, Callable[[], Strategy]]] = {
    # Episode 1 & 2: Classic Axelrod
    "always_cooperate": (
        StrategyMeta(
            id="always_cooperate",
            name="Always Cooperate",
            archetype="The Altruist",
            episode=1,
            category="Classic Axelrod",
            description="Unconditionally cooperates in every round regardless of opponent actions.",
            traits=["Nice", "Forgiving", "Unexploitable by saints", "Naive"],
        ),
        lambda: AlwaysCooperateStrategy(),
    ),
    "always_defect": (
        StrategyMeta(
            id="always_defect",
            name="Always Defect",
            archetype="The Predator",
            episode=1,
            category="Classic Axelrod",
            description="Unconditionally defects in every round to exploit cooperative partners.",
            traits=["Nasty", "Unforgiving", "Provocative", "Parasitic"],
        ),
        lambda: AlwaysDefectStrategy(),
    ),
    "tit_for_tat": (
        StrategyMeta(
            id="tit_for_tat",
            name="Tit-For-Tat",
            archetype="The Reciprocal Enforcer",
            episode=2,
            category="Classic Axelrod",
            description="Starts by cooperating, then faithfully mirrors the opponent's previous move.",
            traits=["Nice", "Retaliatory", "Forgiving", "Clear"],
        ),
        lambda: TitForTatStrategy(),
    ),
    "grim_trigger": (
        StrategyMeta(
            id="grim_trigger",
            name="Grim Trigger",
            archetype="The Unforgiving Grudger",
            episode=2,
            category="Classic Axelrod",
            description="Cooperates until the opponent defects once, then defects permanently.",
            traits=["Nice", "Retaliatory", "Zero-Forgiveness", "Extreme"],
        ),
        lambda: GrimTriggerStrategy(),
    ),
    "random": (
        StrategyMeta(
            id="random",
            name="Random (50/50)",
            archetype="The Chaos Agent",
            episode=2,
            category="Classic Axelrod",
            description="Chooses cooperation or defection with equal 50% probability.",
            traits=["Unpredictable", "Stochastic", "Non-adaptive"],
        ),
        lambda: RandomStrategy(),
    ),

    # Episode 3: Noise & Forgiveness
    "generous_tit_for_tat": (
        StrategyMeta(
            id="generous_tit_for_tat",
            name="Generous Tit-For-Tat",
            archetype="The Forgiving Cooperator",
            episode=3,
            category="Noise & Forgiveness",
            description="Mirrors opponent moves, but forgives defection 10% of the time to break vendettas.",
            traits=["Nice", "Retaliatory", "Stochastically Forgiving"],
        ),
        lambda: GenerousTitForTatStrategy(forgiveness_probability=0.1),
    ),
    "tit_for_two_tats": (
        StrategyMeta(
            id="tit_for_two_tats",
            name="Tit-For-Two-Tats",
            archetype="The Patient Cooperator",
            episode=3,
            category="Noise & Forgiveness",
            description="Only defects if the opponent defects twice in succession.",
            traits=["Nice", "Patient", "Highly Forgiving"],
        ),
        lambda: TitForTwoTatsStrategy(),
    ),
    "win_stay_lose_shift": (
        StrategyMeta(
            id="win_stay_lose_shift",
            name="Win-Stay, Lose-Shift",
            archetype="Pavlov",
            episode=3,
            category="Noise & Forgiveness",
            description="Repeats move if payoff was high (3 or 5); shifts move if payoff was low (0 or 1).",
            traits=["Adaptive", "Self-Correcting", "Error-Resilient"],
        ),
        lambda: WinStayLoseShiftStrategy(),
    ),

    # Episode 6: Reputation & Gossip
    "image_scorer": (
        StrategyMeta(
            id="image_scorer",
            name="Image Scorer",
            archetype="First-Order Moral Judge",
            episode=6,
            category="Reputation & Gossip",
            description="Cooperates only if opponent has a positive public image score.",
            traits=["Reputational", "Discriminative", "Publicly Accountable"],
        ),
        lambda: ImageScorerStrategy(),
    ),
    "stern_judger": (
        StrategyMeta(
            id="stern_judger",
            name="Stern Judger",
            archetype="Second-Order Moral Enforcer",
            episode=6,
            category="Reputation & Gossip",
            description="Cooperates with good agents; punishes bad agents without losing moral standing.",
            traits=["Norm-Enforcing", "Justified Punisher", "Robust to Noise"],
        ),
        lambda: SternJudgingStrategy(),
    ),
    "hypocrite": (
        StrategyMeta(
            id="hypocrite",
            name="Hypocrite",
            archetype="Shadow Defector",
            episode=6,
            category="Reputation & Gossip",
            description="Maintains good public reputation while exploiting partners when unobserved.",
            traits=["Deceptive", "Reputation-Gaming", "Parasitic"],
        ),
        lambda: HypocriteStrategy(),
    ),

    # Episode 7: Tags & Tribalism
    "strict_tribal": (
        StrategyMeta(
            id="strict_tribal",
            name="Strict Tribal",
            archetype="In-Group Altruist",
            episode=7,
            category="Tags & Tribalism",
            description="Cooperates with identical tag group members; defects against outsiders.",
            traits=["In-Group Favoritism", "Tribal", "Out-Group Hostility"],
        ),
        lambda: StrictTribalStrategy(),
    ),
    "riolo_tolerance": (
        StrategyMeta(
            id="riolo_tolerance",
            name="Riolo Tolerance",
            archetype="Continuous Tag Discriminator",
            episode=7,
            category="Tags & Tribalism",
            description="Cooperates with agents whose continuous tag distance is within tolerance threshold.",
            traits=["Metric Discrimination", "Tunable Tolerance"],
        ),
        lambda: RioloToleranceStrategy(tolerance=0.1),
    ),
    "false_beard": (
        StrategyMeta(
            id="false_beard",
            name="False Beard",
            archetype="The Chameleon Parasite",
            episode=7,
            category="Tags & Tribalism",
            description="Mimics the dominant in-group tag while defecting on its fellow group members.",
            traits=["Deceptive", "Tag Mimicry", "In-Group Exploiter"],
        ),
        lambda: FalseBeardStrategy(),
    ),
    "tag_reciprocal": (
        StrategyMeta(
            id="tag_reciprocal",
            name="Tag Reciprocal",
            archetype="Tribal Enforcer",
            episode=7,
            category="Tags & Tribalism",
            description="Plays Tit-For-Tat with in-group peers and defects against outsiders.",
            traits=["Conditional In-Group", "Out-Group Deterrence"],
        ),
        lambda: TagReciprocalStrategy(),
    ),

    # Episode 8: Commons & Sanctions
    "sustainable_harvester": (
        StrategyMeta(
            id="sustainable_harvester",
            name="Sustainable Harvester",
            archetype="Responsible Steward",
            episode=8,
            category="Commons & Sanctions",
            description="Harvests sustainably within regenerative biological limits of the commons.",
            traits=["Prosocial", "Ecology-Conscious", "Sustainable"],
        ),
        lambda: SustainableHarvesterStrategy(),
    ),
    "over_harvester": (
        StrategyMeta(
            id="over_harvester",
            name="Over-Harvester",
            archetype="Commons Free-Rider",
            episode=8,
            category="Commons & Sanctions",
            description="Aggressively over-harvests the common resource pool for private gains.",
            traits=["Depletive", "Free-Riding", "Tragedy Driver"],
        ),
        lambda: OverHarvesterStrategy(),
    ),
    "ostrom_sanctioner": (
        StrategyMeta(
            id="ostrom_sanctioner",
            name="Ostrom Sanctioner",
            archetype="Peer Guard & Punisher",
            episode=8,
            category="Commons & Sanctions",
            description="Harvests responsibly and incurs private costs to sanction violators.",
            traits=["Altruistic Punishment", "Ostrom Principle 5", "Norm Enforcer"],
        ),
        lambda: OstromSanctionerStrategy(),
    ),
    "second_order_free_rider": (
        StrategyMeta(
            id="second_order_free_rider",
            name="Second-Order Free Rider",
            archetype="Cooperative Non-Punisher",
            episode=8,
            category="Commons & Sanctions",
            description="Cooperates by harvesting sustainably, but refuses to pay the cost of punishing violators.",
            traits=["Passive Cooperator", "Sanction Avoider"],
        ),
        lambda: SecondOrderFreeRiderStrategy(),
    ),
    "antisocial_punisher": (
        StrategyMeta(
            id="antisocial_punisher",
            name="Antisocial Punisher",
            archetype="Spiteful Retaliator",
            episode=8,
            category="Commons & Sanctions",
            description="Over-harvests and spitefully punishes responsible prosocial stewards.",
            traits=["Spiteful", "Cooperation-Destroying", "Destructive"],
        ),
        lambda: AntisocialPunisherStrategy(),
    ),

    # Episode 9: Zero-Determinant Strategies
    "extortioner": (
        StrategyMeta(
            id="extortioner",
            name="Extortioner (χ = 3.0)",
            archetype="Press-Dyson Tyrant",
            episode=9,
            category="Zero-Determinant",
            description="Unilaterally forces co-player payoffs into an unfair 3:1 surplus ratio.",
            traits=["Asymmetric Power", "Linear Dictator", "Memory-One"],
        ),
        lambda: ExtortionStrategy(chi=3.0),
    ),
    "equalizer": (
        StrategyMeta(
            id="equalizer",
            name="Equalizer (c = 2.0)",
            archetype="Press-Dyson Clamper",
            episode=9,
            category="Zero-Determinant",
            description="Unilaterally fixes the co-player's long-term average score to exactly 2.0.",
            traits=["Payoff Clamper", "Unilateral Control", "Memory-One"],
        ),
        lambda: EqualizerStrategy(target_score=2.0),
    ),
    "generous_zd": (
        StrategyMeta(
            id="generous_zd",
            name="Generous ZD",
            archetype="Press-Dyson Peacemaker",
            episode=9,
            category="Zero-Determinant",
            description="Zero-determinant cooperator that concedes surplus to partners, out-evolving extortioners.",
            traits=["Generous ZD", "Evolutionary Stable", "Surplus Conceder"],
        ),
        lambda: GenerousZDStrategy(),
    ),

    # Episode 10: Cognitive LLM Personas
    "honest_diplomat": (
        StrategyMeta(
            id="honest_diplomat",
            name="Honest Diplomat",
            archetype="Cognitive Peacemaker",
            episode=10,
            category="Cognitive LLM",
            description="Engages in pre-play dialogue, offers mutual peace, and retaliates transparently if provoked.",
            traits=["Natural Language", "High Honesty", "Transparent Intent"],
            is_cognitive=True,
        ),
        lambda: CognitiveStrategy(persona=CognitivePersona.HONEST_DIPLOMAT, agent_id="HonestDiplomat"),
    ),
    "machiavellian": (
        StrategyMeta(
            id="machiavellian",
            name="Machiavellian",
            archetype="Strategic Deceiver",
            episode=10,
            category="Cognitive LLM",
            description="Uses charismatic, reassuring language to lull partners into trust, then opportunistically defects.",
            traits=["Natural Language", "Cheap Talk", "Strategic Deception"],
            is_cognitive=True,
        ),
        lambda: CognitiveStrategy(persona=CognitivePersona.MACHIAVELLIAN, agent_id="Machiavellian"),
    ),
    "pragmatic_contractor": (
        StrategyMeta(
            id="pragmatic_contractor",
            name="Pragmatic Contractor",
            archetype="Contractual Legalist",
            episode=10,
            category="Cognitive LLM",
            description="Treats dialogue as binding contracts; announces retaliatory defection in advance upon breach.",
            traits=["Natural Language", "Binding Contracts", "Disciplined Reciprocity"],
            is_cognitive=True,
        ),
        lambda: CognitiveStrategy(persona=CognitivePersona.PRAGMATIC_CONTRACTOR, agent_id="PragmaticContractor"),
    ),
    "skeptical_realist": (
        StrategyMeta(
            id="skeptical_realist",
            name="Skeptical Realist",
            archetype="Grim Realist",
            episode=10,
            category="Cognitive LLM",
            description="Dismisses cheap talk as noise; bases moves solely on physical matrix decisions with Grim Trigger.",
            traits=["Cheap-Talk Immune", "Hard Defense", "Grim Retaliation"],
            is_cognitive=True,
        ),
        lambda: CognitiveStrategy(persona=CognitivePersona.SKEPTICAL_REALIST, agent_id="SkepticalRealist"),
    ),
}


# --- Request & Response Schemas ---

class MatchRequest(BaseModel):
    strategy_a: str = Field(..., description="Strategy ID for Agent A")
    strategy_b: str = Field(..., description="Strategy ID for Agent B")
    round_count: int = Field(20, ge=1, le=1000, description="Number of interaction rounds")
    noise: float = Field(0.0, ge=0.0, le=1.0, description="Observation noise probability")
    seed: int | None = Field(None, description="Random seed for reproducibility")


class RoundTelemetry(BaseModel):
    round_number: int
    action_a: str
    action_b: str
    payoff_a: int
    payoff_b: int
    cumulative_a: int
    cumulative_b: int
    message_a: str | None = None
    message_b: str | None = None
    rationale_a: str | None = None
    rationale_b: str | None = None
    is_deceptive_a: bool = False
    is_deceptive_b: bool = False


class MatchResponse(BaseModel):
    strategy_a: StrategyMeta
    strategy_b: StrategyMeta
    score_a: int
    score_b: int
    cooperation_rate_a: float
    cooperation_rate_b: float
    deception_rate_a: float
    deception_rate_b: float
    rounds: list[RoundTelemetry]


class TournamentSelection(BaseModel):
    strategy_id: str
    count: int = Field(1, ge=1, le=50)


class TournamentRequest(BaseModel):
    selections: list[TournamentSelection]
    rounds_per_match: int = Field(10, ge=1, le=200)
    noise: float = Field(0.0, ge=0.0, le=1.0)
    seed: int | None = None


class LeaderboardRow(BaseModel):
    rank: int
    agent_id: str
    strategy_id: str
    strategy_name: str
    total_score: int
    average_score_per_round: float
    wins: int
    ties: int
    losses: int
    cooperation_rate: float


class TournamentResponse(BaseModel):
    total_agents: int
    total_matches: int
    population_cooperation_rate: float
    leaderboard: list[LeaderboardRow]


# --- API Routes ---

@app.get("/api/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/strategies")
def list_strategies() -> dict[str, Any]:
    """List all available strategies with their traits and metadata."""
    strategies_list = [meta.model_dump() for meta, _ in STRATEGY_CATALOG.values()]
    return {
        "count": len(strategies_list),
        "strategies": strategies_list,
    }


@app.post("/api/simulate/match", response_model=MatchResponse)
def simulate_match(req: MatchRequest) -> MatchResponse:
    """Simulate a pairwise match between two strategies."""
    if req.strategy_a not in STRATEGY_CATALOG:
        raise HTTPException(status_code=404, detail=f"Strategy '{req.strategy_a}' not found.")
    if req.strategy_b not in STRATEGY_CATALOG:
        raise HTTPException(status_code=404, detail=f"Strategy '{req.strategy_b}' not found.")

    meta_a, factory_a = STRATEGY_CATALOG[req.strategy_a]
    meta_b, factory_b = STRATEGY_CATALOG[req.strategy_b]

    strat_a = factory_a()
    strat_b = factory_b()

    agent_a = Agent("Agent_A", strat_a)
    agent_b = Agent("Agent_B", strat_b)

    telemetry: list[RoundTelemetry] = []
    cum_a = 0
    cum_b = 0
    deception_a = 0.0
    deception_b = 0.0

    # If either agent is cognitive, run CognitiveMatch with dialogue & deception auditing
    if meta_a.is_cognitive or meta_b.is_cognitive:
        channel = NegotiationChannel()
        tracker = DeceptionTracker()
        cog_match = CognitiveMatch(
            agent_a=agent_a,
            agent_b=agent_b,
            round_count=req.round_count,
            channel=channel,
            deception_tracker=tracker,
        )
        res = cog_match.play()

        # Build telemetry
        for idx, rnd in enumerate(res.rounds, start=1):
            cum_a += rnd.payoff.first
            cum_b += rnd.payoff.second

            # Extract dialogue for this round
            r_turns = channel.get_conversation(agent_a.id, agent_b.id, round_number=idx)
            msg_a = next((t.message for t in r_turns if t.sender_id == agent_a.id), None)
            msg_b = next((t.message for t in r_turns if t.sender_id == agent_b.id), None)

            # Check deception
            audit_a = next((a for a in tracker.audits if a.round_number == idx and a.agent_id == agent_a.id), None)
            audit_b = next((a for a in tracker.audits if a.round_number == idx and a.agent_id == agent_b.id), None)

            telemetry.append(
                RoundTelemetry(
                    round_number=idx,
                    action_a=rnd.first_action.name,
                    action_b=rnd.second_action.name,
                    payoff_a=rnd.payoff.first,
                    payoff_b=rnd.payoff.second,
                    cumulative_a=cum_a,
                    cumulative_b=cum_b,
                    message_a=msg_a,
                    message_b=msg_b,
                    rationale_a=strat_a.get_last_rationale(agent_b.id) if hasattr(strat_a, "get_last_rationale") else None,
                    rationale_b=strat_b.get_last_rationale(agent_a.id) if hasattr(strat_b, "get_last_rationale") else None,
                    is_deceptive_a=audit_a.is_deceptive if audit_a else False,
                    is_deceptive_b=audit_b.is_deceptive if audit_b else False,
                )
            )

        score_a = res.score_a
        score_b = res.score_b
        deception_a = res.deception_a
        deception_b = res.deception_b

    else:
        # Standard match with optional channel noise
        match = Match(
            first_agent=agent_a,
            second_agent=agent_b,
            game=PrisonersDilemma(),
            round_count=req.round_count,
            noise=req.noise,
            seed=req.seed,
        )
        rounds = match.execute()
        score_a = match.result.first_score  # type: ignore[union-attr]
        score_b = match.result.second_score  # type: ignore[union-attr]

        for idx, rnd in enumerate(rounds, start=1):
            cum_a += rnd.payoff.first
            cum_b += rnd.payoff.second
            telemetry.append(
                RoundTelemetry(
                    round_number=idx,
                    action_a=rnd.first_action.name,
                    action_b=rnd.second_action.name,
                    payoff_a=rnd.payoff.first,
                    payoff_b=rnd.payoff.second,
                    cumulative_a=cum_a,
                    cumulative_b=cum_b,
                )
            )

    coop_a = sum(1 for r in telemetry if r.action_a == "COOPERATE") / len(telemetry)
    coop_b = sum(1 for r in telemetry if r.action_b == "COOPERATE") / len(telemetry)

    return MatchResponse(
        strategy_a=meta_a,
        strategy_b=meta_b,
        score_a=score_a,
        score_b=score_b,
        cooperation_rate_a=round(coop_a, 3),
        cooperation_rate_b=round(coop_b, 3),
        deception_rate_a=round(deception_a, 3),
        deception_rate_b=round(deception_b, 3),
        rounds=telemetry,
    )


@app.post("/api/simulate/tournament", response_model=TournamentResponse)
def simulate_tournament(req: TournamentRequest) -> TournamentResponse:
    """Execute a round-robin tournament across chosen strategy populations."""
    agents: list[Agent] = []
    agent_strat_map: dict[str, str] = {}

    for sel in req.selections:
        if sel.strategy_id not in STRATEGY_CATALOG:
            raise HTTPException(status_code=404, detail=f"Strategy '{sel.strategy_id}' not found.")
        meta, factory = STRATEGY_CATALOG[sel.strategy_id]
        for i in range(1, sel.count + 1):
            agent_id = f"{meta.id}_{i:02d}"
            agents.append(Agent(agent_id, factory()))
            agent_strat_map[agent_id] = meta.id

    if len(agents) < 2:
        raise HTTPException(status_code=400, detail="Tournament requires at least 2 agents in total.")

    population = Population(agents)
    tournament = Tournament(
        population=population,
        game=PrisonersDilemma(),
        rounds_per_match=req.rounds_per_match,
        noise=req.noise,
        seed=req.seed,
    )
    res = tournament.execute()

    leaderboard_rows = [
        LeaderboardRow(
            rank=entry.rank,
            agent_id=entry.agent_id,
            strategy_id=agent_strat_map.get(entry.agent_id, entry.strategy_name),
            strategy_name=entry.strategy_name,
            total_score=entry.total_score,
            average_score_per_round=entry.average_score_per_round,
            wins=entry.wins,
            ties=entry.ties,
            losses=entry.losses,
            cooperation_rate=entry.cooperation_rate,
        )
        for entry in res.leaderboard
    ]

    return TournamentResponse(
        total_agents=population.size,
        total_matches=res.total_matches,
        population_cooperation_rate=round(res.population_cooperation_rate, 3),
        leaderboard=leaderboard_rows,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ui.server.app:app", host="0.0.0.0", port=8000, reload=True)
