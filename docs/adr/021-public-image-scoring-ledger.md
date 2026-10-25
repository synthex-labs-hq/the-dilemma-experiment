# ADR-021: Public Image Scoring and Indirect Reciprocity Ledger

## Status

Accepted

## Context

In Episodes 1 through 5, cooperation relied on **Direct Reciprocity** (repeated encounters between the same pair of agents, $A \leftrightarrow B$) and **Spatial Locality** (fixed physical neighbors).

In human civilization, large-scale financial markets, digital platforms (e.g. Uber, Airbnb, eBay, open-source pull requests), and decentralized protocols:
1. Economic interactions are frequently **one-shot encounters between strangers** who may never interact again.
2. Direct reciprocity fails in the stranger regime because there is no future interaction shadow ($\delta = 0$).
3. Martin Nowak and Karl Sigmund (1998 *Nature*, 2005 *Nature*) proved that cooperation scales among strangers through **Indirect Reciprocity**:
   - *"I help you not because of what you did to me, but because of what you did to others."*
4. Indirect reciprocity requires a social mechanism for tracking an individual's past helpfulness: **Image Scoring**.

To simulate indirect reciprocity, we require a deterministic, isolated, standard-library domain abstraction for tracking public reputation scores and history.

## Decision

1. **Reputation Domain Ledger (`ReputationRegistry`)**:
   - A centralized, auditable ledger tracking public standing for all active agents.
   - For each agent $u \in \text{Agents}$:
     - `image_score(u) -> int`: Cumulative score reflecting public cooperative behavior.
     - `standing(u) -> MoralStanding`: Discrete moral classification (`GOOD` vs `BAD`).
     - `history(u) -> list[ReputationEvent]`: Chronological record of observed actions.
   - The ledger is independent of agent instances, preserving strategy immutability and isolation (ADR-001, ADR-010).

2. **First-Order Image Scoring Rules**:
   - An interaction between donor $u$ and recipient $v$ is observed with probability $p_{\text{obs}} \in [0.0, 1.0]$.
   - When public ($p_{\text{obs}} = 1$):
     - If donor $u$ plays `Action.COOPERATE`: $u$'s image score increases by $+1$:
       $$q_u(t+1) = \min(q_{\max}, q_u(t) + 1)$$
     - If donor $u$ plays `Action.DEFECT`: $u$'s image score decreases by $-1$:
       $$q_u(t+1) = \max(q_{\min}, q_u(t) - 1)$$
   - Image score is clamped to a bounded integer range $[-q_{\max}, +q_{\max}]$ (default $[-5, +5]$).
   - Initial image score for new agents is neutral ($q = 0$).

3. **Public vs Private Interactions**:
   - Each match interaction has an environment context attribute: `is_public: bool`.
   - Actions taken in **Private** interactions do not alter the public reputation ledger.
   - This architectural distinction provides the foundation for testing information asymmetry and opportunistic behavior (hypocrisy).

## Consequences

### Positive
- Enables multi-agent cooperation in one-shot matches between strangers without requiring repeated pairwise history.
- Pure standard library Python with zero external database or network dependencies.
- Completely deterministic under seed-controlled evaluation (ADR-003).

### Negative / Trade-offs
- First-order image scoring suffers from the **Enforcer's Dilemma**: defecting against a known bad actor reduces the enforcer's own image score. This necessitates second-order moral assessment (addressed in ADR-022).
