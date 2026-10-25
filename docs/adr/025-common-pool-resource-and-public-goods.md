# ADR-025: Common Pool Resource and Public Goods Abstractions

## Status
Accepted

## Context
In Episodes 1 through 7, all interactions were strictly dyadic (pairwise: $A \leftrightarrow B$). Whether through direct reciprocity, image scoring ledgers, spatial neighbors, or tag matching, payoffs were resolved between two agents.

However, many of the most critical challenges in economics, ecology, and distributed computing involve **$N$-player collective action dilemmas** where individual actions affect an entire community or shared resource pool:
1. **The Tragedy of the Commons** (Garrett Hardin 1968): A finite, depletable shared resource pool (e.g., pasture, water, fish stocks, shared AI GPU clusters, network bandwidth). Each agent benefits directly from harvesting more, while the cost of depletion is distributed equally among all users.
2. **The Public Goods Dilemma** (Olson 1965): $N$ agents each receive an endowment $e$ and choose how much $c_i \in [0, e]$ to contribute to a common pool. Total contributions are multiplied by an efficiency factor $r$ ($1 < r < N$) and divided equally among all members.

In both formulations, individual marginal return is strictly less than 1 ($r/N < 1$). Selfish rationality dictates zero contribution ($c_i = 0$) and maximum extraction, inevitably leading to complete systemic collapse ("The Tragedy").

## Decision
1. **Domain Models**:
   - `CommonPoolResource`: Represents a replenishing stock $S_t \in [0, K]$ with logistic or linear regeneration rate $\rho$ and carrying capacity $K$:
     $$S_{t+1} = \min\left(K, \max\left(0, (S_t - \sum h_i) \times (1 + \rho)\right)\right)$$
     where $h_i$ is agent $i$'s harvest.
   - `PublicGoodsPool`: Evaluates contributions $\sum c_i$, applies multiplier $r$, and returns equal share $\frac{r}{N}\sum c_i$ to each agent. Payoff for agent $i$:
     $$\pi_i = e - c_i + \frac{r}{N}\sum_{j=1}^N c_j$$
2. **Context Extension**:
   - Enhance `DecisionContext` with optional `resource_stock`, `group_size`, and `endowment` fields, maintaining 100% backwards compatibility with previous dyadic games.
3. **Strategies**:
   - `SustainableHarvesterStrategy`: Harvests within the replenishment yield; fully contributes to public goods.
   - `OverHarvesterStrategy`: The free-rider. Extracts maximum quota; contributes zero.
   - `OstromSanctionerStrategy`: Harvests sustainably and invests resources to punish free-riders (ADR-026).
   - `SecondOrderFreeRiderStrategy`: Cooperates sustainably, but avoids paying the cost of enforcing sanctions.

## Consequences
- Extends the simulation framework beyond $2$-player matrix games into $N$-player macro-economic dilemmas.
- Allows rigorous modeling of shared compute resource contention in autonomous multi-agent networks.
- Motivates the introduction of institutional and peer sanctions in ADR-026.
