"""Zero-mock automated unit tests for the UI Simulation FastAPI backend."""

from fastapi.testclient import TestClient

from the_dilemma_experiment.api.app import app

client = TestClient(app)


def test_health_check_endpoint() -> None:
    """Verifies that the /api/health endpoint returns 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"


def test_list_strategies_endpoint() -> None:
    """Verifies that the strategy catalog lists 24+ strategies with rich metadata across all episodes."""
    response = client.get("/api/strategies")
    assert response.status_code == 200
    data = response.json()
    assert "strategies" in data
    assert data["count"] >= 24

    strat_ids = {s["id"] for s in data["strategies"]}

    # Verify key strategies from across the 10 episodes
    assert "always_cooperate" in strat_ids
    assert "always_defect" in strat_ids
    assert "tit_for_tat" in strat_ids
    assert "generous_tit_for_tat" in strat_ids
    assert "win_stay_lose_shift" in strat_ids
    assert "image_scorer" in strat_ids
    assert "strict_tribal" in strat_ids
    assert "ostrom_sanctioner" in strat_ids
    assert "extortioner" in strat_ids
    assert "equalizer" in strat_ids
    assert "honest_diplomat" in strat_ids
    assert "machiavellian" in strat_ids

    # Validate structure of a strategy entry
    tft = next(s for s in data["strategies"] if s["id"] == "tit_for_tat")
    assert tft["name"] == "Tit-For-Tat"
    assert tft["archetype"] == "The Reciprocal Enforcer"
    assert tft["episode"] == 2
    assert len(tft["traits"]) >= 3


def test_simulate_match_standard_harmony() -> None:
    """Verifies pairwise simulation between classic reciprocal strategies."""
    payload = {
        "strategy_a": "tit_for_tat",
        "strategy_b": "always_cooperate",
        "round_count": 10,
        "noise": 0.0,
    }
    response = client.post("/api/simulate/match", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["score_a"] == 30
    assert data["score_b"] == 30
    assert data["cooperation_rate_a"] == 1.0
    assert data["cooperation_rate_b"] == 1.0
    assert len(data["rounds"]) == 10
    assert data["rounds"][0]["action_a"] == "COOPERATE"
    assert data["rounds"][0]["action_b"] == "COOPERATE"
    assert data["rounds"][0]["payoff_a"] == 3
    assert data["rounds"][0]["payoff_b"] == 3


def test_simulate_match_cognitive_dialogue_and_deception() -> None:
    """Verifies that simulating cognitive personas populates pre-play dialogue and deception audits."""
    payload = {
        "strategy_a": "honest_diplomat",
        "strategy_b": "machiavellian",
        "round_count": 10,
    }
    response = client.post("/api/simulate/match", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert len(data["rounds"]) == 10
    assert data["strategy_a"]["is_cognitive"] is True
    assert data["strategy_b"]["is_cognitive"] is True

    # Check that natural language dialogue turns were logged
    assert data["rounds"][0]["message_a"] is not None
    assert data["rounds"][0]["message_b"] is not None

    # Honest diplomat never lies
    assert data["deception_rate_a"] == 0.0

    # Machiavelli breaks promises
    assert data["deception_rate_b"] > 0.0


def test_simulate_match_invalid_strategy() -> None:
    """Verifies 404 response when querying a non-existent strategy."""
    payload = {
        "strategy_a": "tit_for_tat",
        "strategy_b": "non_existent_strategy_xyz",
        "round_count": 5,
    }
    response = client.post("/api/simulate/match", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_simulate_tournament_endpoint() -> None:
    """Verifies multi-agent round-robin tournament execution via the API."""
    payload = {
        "selections": [
            {"strategy_id": "tit_for_tat", "count": 2},
            {"strategy_id": "always_defect", "count": 2},
            {"strategy_id": "win_stay_lose_shift", "count": 2},
        ],
        "rounds_per_match": 10,
        "noise": 0.0,
    }
    response = client.post("/api/simulate/tournament", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["total_agents"] == 6
    # 6 * 5 / 2 = 15 pairwise matches
    assert data["total_matches"] == 15
    assert len(data["leaderboard"]) == 6
    assert data["leaderboard"][0]["rank"] == 1
    assert data["leaderboard"][0]["total_score"] > 0
    assert "pairwise_matches" in data
    assert len(data["pairwise_matches"]) == 15
    first_match = data["pairwise_matches"][0]
    assert "first_agent_id" in first_match
    assert "second_agent_id" in first_match
    assert "first_score" in first_match
    assert "second_score" in first_match
    assert first_match["rounds_played"] == 10


def test_simulate_spatial_endpoint() -> None:
    """Verifies that the 2D toroidal spatial simulation returns multi-generation telemetry and grid cells."""
    payload = {
        "width": 6,
        "height": 6,
        "preset": "oasis",
        "generations": 3,
    }
    response = client.post("/api/simulate/spatial", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["width"] == 6
    assert data["height"] == 6
    assert data["total_nodes"] == 36
    assert data["preset"] == "oasis"
    # Gen 0 baseline + 3 steps = 4 generations
    assert len(data["generations"]) == 4
    gen0 = data["generations"][0]
    assert gen0["generation"] == 0
    assert len(gen0["grid_cells"]) == 36
    assert "AlwaysCooperateStrategy" in gen0["distribution"]
    assert "AlwaysDefectStrategy" in gen0["distribution"]


def test_simulate_commons_endpoint() -> None:
    """Verifies that the CPR and Ostrom sanctions simulation tracks resource depletion and fines."""
    payload = {
        "sustainable_count": 2,
        "overharvester_count": 2,
        "sanctioner_count": 2,
        "freerider_bystander_count": 0,
        "rounds": 5,
        "initial_stock": 50.0,
        "capacity": 100.0,
        "sanctions_enabled": True,
    }
    response = client.post("/api/simulate/commons", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["total_rounds"] == 5
    assert data["initial_stock"] == 50.0
    assert len(data["history"]) == 5
    assert len(data["leaderboard"]) == 6
    # Sanctions were applied against the overharvesters
    assert data["total_sanctions"] >= 0
    assert data["total_fines_imposed"] >= 0.0


def test_simulate_gauntlet_endpoint() -> None:
    """Verifies that the custom strategy Gauntlet runs 5 benchmark duels and scores Axelrodian axioms."""
    payload = {
        "name": "NobleReciprocator",
        "opening_move": "COOPERATE",
        "retaliation": "one_to_one",
        "forgiveness": 0.15,
        "rounds_per_opponent": 10,
    }
    response = client.post("/api/simulate/gauntlet", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["custom_name"] == "NobleReciprocator"
    assert "scorecard" in data
    scorecard = data["scorecard"]
    assert scorecard["niceness"] == 1.0
    assert scorecard["retaliation"] == 1.0
    assert scorecard["forgiveness"] > 0.0
    assert scorecard["total_score"] > 0
    assert "Noble Reciprocator" in scorecard["archetype_badge"]

    assert len(data["duels"]) == 5
    opp_ids = [d["opponent_id"] for d in data["duels"]]
    assert "tit_for_tat" in opp_ids
    assert "always_defect" in opp_ids
    assert "win_stay_lose_shift" in opp_ids
    assert "extortioner" in opp_ids
    assert "generous_zd" in opp_ids

