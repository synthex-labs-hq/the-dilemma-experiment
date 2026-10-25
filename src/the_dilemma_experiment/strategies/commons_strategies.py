"""Commons strategies: Sustainable harvesters, free-riders, Ostrom sanctioners, and bystanders."""

from dataclasses import dataclass

from the_dilemma_experiment.domain.action import Action
from the_dilemma_experiment.domain.context import DecisionContext
from the_dilemma_experiment.domain.strategy import Strategy


@dataclass
class SustainableHarvesterStrategy(Strategy):
    """Harvests sustainably within natural regeneration limits and fully funds public goods."""

    harvest_quota: float = 3.0
    contribution_ratio: float = 1.0  # 100% of endowment

    def choose_action(self, context: DecisionContext) -> Action:
        # For standard 2-player dilemma integration
        return Action.COOPERATE

    def decide_harvest(self, stock: float, capacity: float, group_size: int) -> float:
        """Calculate sustainable extraction share."""
        fair_share = stock / max(1, group_size)
        return min(self.harvest_quota, fair_share)

    def decide_contribution(self, endowment: float) -> float:
        """Contribute full ratio of endowment."""
        return endowment * self.contribution_ratio


@dataclass
class OverHarvesterStrategy(Strategy):
    """Greedy free-rider: Extracts maximum quota and contributes zero to public goods."""

    max_extract: float = 10.0

    def choose_action(self, context: DecisionContext) -> Action:
        return Action.DEFECT

    def decide_harvest(self, stock: float, capacity: float, group_size: int) -> float:
        return self.max_extract

    def decide_contribution(self, endowment: float) -> float:
        return 0.0


@dataclass
class OstromSanctionerStrategy(Strategy):
    """Altruistic enforcer: Harvests sustainably, funds public goods, and fines free-riders."""

    harvest_quota: float = 3.0
    contribution_ratio: float = 1.0
    sanction_threshold: float = 5.0  # Fines anyone contributing less than 50%
    fine_amount: float = 3.0

    def choose_action(self, context: DecisionContext) -> Action:
        return Action.COOPERATE

    def decide_harvest(self, stock: float, capacity: float, group_size: int) -> float:
        fair_share = stock / max(1, group_size)
        return min(self.harvest_quota, fair_share)

    def decide_contribution(self, endowment: float) -> float:
        return endowment * self.contribution_ratio

    def should_sanction(self, target_id: str, target_contribution: float) -> bool:
        """Sanction target if contribution falls below acceptable threshold."""
        return target_contribution < self.sanction_threshold


@dataclass
class SecondOrderFreeRiderStrategy(Strategy):
    """Silent bystander: Cooperates in harvest and public goods, but refuses to pay sanction costs."""

    harvest_quota: float = 3.0
    contribution_ratio: float = 1.0

    def choose_action(self, context: DecisionContext) -> Action:
        return Action.COOPERATE

    def decide_harvest(self, stock: float, capacity: float, group_size: int) -> float:
        fair_share = stock / max(1, group_size)
        return min(self.harvest_quota, fair_share)

    def decide_contribution(self, endowment: float) -> float:
        return endowment * self.contribution_ratio

    def should_sanction(self, target_id: str, target_contribution: float) -> bool:
        # Never pays punishment cost
        return False


@dataclass
class AntisocialPunisherStrategy(Strategy):
    """Spiteful free-rider: Over-extracts and punishes high contributors (Herrmann et al. 2008)."""

    max_extract: float = 10.0

    def choose_action(self, context: DecisionContext) -> Action:
        return Action.DEFECT

    def decide_harvest(self, stock: float, capacity: float, group_size: int) -> float:
        return self.max_extract

    def decide_contribution(self, endowment: float) -> float:
        return 0.0

    def should_sanction(self, target_id: str, target_contribution: float) -> bool:
        # Spitefully fines agents who contributed generously
        return target_contribution >= 7.0
