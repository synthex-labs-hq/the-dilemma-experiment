# ADR-026: Costly Peer Punishment and Polycentric Sanctions

## Status
Accepted

## Context
In unconstrained Public Goods Games (PGG) and Common Pool Resource (CPR) environments, free-riding is the dominant Nash equilibrium. In classic laboratory experiments (Fehr & Gächter 2000, 2002), cooperation universally decays toward zero within 10 to 15 rounds when punishment is unavailable.

However, Fehr & Gächter demonstrated that when individuals are given the opportunity to punish free-riders—even when punishment is **costly to the punisher**—cooperation immediately surges and stabilizes near 100%.

In parallel, political economist **Elinor Ostrom** (Nobel Memorial Prize in Economic Sciences 2009) surveyed hundreds of real-world shared commons across irrigation systems, fisheries, and forests. Ostrom refuted Hardin's assumption that the commons inevitably collapse unless privatized or placed under central state tyranny. Instead, she identified 8 core design principles for self-governing institutions, chief among them:
1. **Clear boundaries and monitoring**: Users observe who extracts resources.
2. **Graduated sanctions**: Initial infractions trigger mild warnings; repeated violations incur severe, compounding fines.
3. **Conflict-resolution mechanisms**: Low-cost arenas to adjudicate disputes.

Yet peer punishment creates a secondary dilemma: **The Second-Order Free-Rider Problem**. If agent A pays cost $c_p$ to punish free-rider C, agent B (who cooperates but refuses to punish) benefits from C's reformed behavior without bearing the cost $c_p$. Over evolutionary time, second-order free-riders out-compete punishers, causing sanctions to collapse.

## Decision
1. **Sanction Domain Engine**:
   - Define `SanctionEvent`: Audit record containing `punisher_id`, `target_id`, `fine_cost`, `fine_amount`, and `round_number`.
   - Define `SanctionRegistry`: Manages execution of punitive fines ($c_p \to p$, e.g. punisher pays 1 to dock target 3 or 4 points).
2. **Sanction Regimes**:
   - `PEER_SANCTIONS`: Decentralized individual altruistic punishment (Fehr & Gächter).
   - `GRADUATED_SANCTIONS`: Escalating penalties proportional to prior violations (Ostrom Principle #5).
   - `COMMUNAL_POOL_SANCTION`: Institutional pool where enforcement costs are shared by all members.
3. **Classification & Metrics**:
   - `punishment_efficiency`: Ratio of cooperation restored to total cost expended: $\frac{\Delta \text{Coop}}{\sum c_p}$.
   - `second_order_free_riding_index`: Percentage of cooperating agents who refrain from paying sanction costs.
   - `antisocial_punishment_rate`: Frequency of malicious punishments directed at high contributors.

## Consequences
- Allows rigorous testing of Ostrom's polycentric governance principles against pure centralized or pure unregulated systems.
- Accurately captures the second-order free-rider vulnerability and conditions under which sanctions remain sustainable.
