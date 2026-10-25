"""Zero-mock unit tests for CommonPoolResource, PublicGoodsPool, and SanctionRegistry (ADR-025, ADR-026)."""

import pytest

from the_dilemma_experiment.domain.commons import (
    CommonPoolResource,
    PublicGoodsPool,
    SanctionRegistry,
    SanctionType,
)


def test_common_pool_resource_harvest_and_regeneration() -> None:
    """Resource depletes on harvest and regenerates up to capacity."""
    cpr = CommonPoolResource(capacity=100.0, stock=80.0, regeneration_rate=0.25)
    assert cpr.fullness_percentage == 80.0

    # Harvest 30
    harvested = cpr.harvest(30.0)
    assert harvested == 30.0
    assert cpr.stock == 50.0

    # Regenerate 25% -> 50 * 1.25 = 62.5
    new_stock = cpr.regenerate()
    assert new_stock == 62.5
    assert cpr.stock == 62.5

    # Harvest exceeding stock clamps to available
    harvested_all = cpr.harvest(100.0)
    assert harvested_all == 62.5
    assert cpr.stock == 0.0
    assert cpr.is_depleted is True


def test_common_pool_resource_validation() -> None:
    """Resource validates capacity and non-negative parameters."""
    with pytest.raises(ValueError, match="capacity must be positive"):
        CommonPoolResource(capacity=-10.0)

    with pytest.raises(ValueError, match="regeneration_rate cannot be negative"):
        CommonPoolResource(regeneration_rate=-0.1)

    cpr = CommonPoolResource(capacity=50.0)
    with pytest.raises(ValueError, match="Harvest amount cannot be negative"):
        cpr.harvest(-5.0)


def test_public_goods_pool_payoff_resolution() -> None:
    """Public goods contributions are multiplied and shared equally."""
    # 4 players, endowment 10, multiplier 2.0 (individual marginal return = 2.0/4 = 0.5)
    pgg = PublicGoodsPool(endowment=10.0, multiplier=2.0)

    # 3 cooperators contribute 10, 1 free-rider contributes 0
    # Total pot: 30 -> Multiplied: 60 -> Share per player: 15
    contributions = {
        "coop_1": 10.0,
        "coop_2": 10.0,
        "coop_3": 10.0,
        "freerider": 0.0,
    }
    payoffs = pgg.resolve(contributions)

    # Cooperators keep 0 + 15 = 15
    assert payoffs["coop_1"] == 15.0
    assert payoffs["coop_2"] == 15.0
    assert payoffs["coop_3"] == 15.0
    # Free-rider keeps 10 + 15 = 25 (exploitation premium!)
    assert payoffs["freerider"] == 25.0


def test_public_goods_validation() -> None:
    """PublicGoodsPool validates endowment, multiplier, and player count."""
    with pytest.raises(ValueError, match="Endowment must be positive"):
        PublicGoodsPool(endowment=0.0)

    with pytest.raises(ValueError, match="strictly greater than 1.0"):
        PublicGoodsPool(multiplier=0.9)

    pgg = PublicGoodsPool()
    with pytest.raises(ValueError, match="at least 2 players"):
        pgg.resolve({"solo": 5.0})


def test_sanction_registry_peer_and_graduated_penalties() -> None:
    """SanctionRegistry calculates costs to punisher and fines to targets."""
    # Cost ratio: 0.33 (pay 1.0 to fine 3.0)
    reg = SanctionRegistry(cost_ratio=0.33)

    # Round 1: Alice fines Bob 3.0
    ev1 = reg.apply_sanction("alice", "bob", fine_amount=3.0, round_number=1)
    assert ev1.cost == pytest.approx(0.99, rel=1e-2)
    assert ev1.fine == 3.0
    assert ev1.sanction_type == SanctionType.PEER

    penalties = reg.compute_round_penalties(["alice", "bob", "charlie"], round_number=1)
    assert penalties["alice"] == pytest.approx(-0.99, rel=1e-2)  # punisher cost
    assert penalties["bob"] == -3.0  # target fine
    assert penalties["charlie"] == 0.0  # unaffected bystander
